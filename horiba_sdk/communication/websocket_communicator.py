import asyncio
import contextlib
from types import TracebackType
from typing import Any, Callable, Optional, final

import websockets
from loguru import logger
from overrides import override
from websockets.legacy.client import WebSocketClientProtocol

from .abstract_communicator import AbstractCommunicator
from .communication_exception import CommunicationException
from .messages import BinaryResponse, Command, JSONResponse, Response


@final
class WebsocketCommunicator(AbstractCommunicator):
    """
    The WebsocketCommunicator implements the `horiba_sdk.communication.AbstractCommunicator` via websockets.
    A background task listens continuously for incoming binary data.

    It supports Asynchronous Context Managers and can be used like the following::

        websocket_communicator: WebsocketCommunicator = WebsocketCommunicator(uri)
        async with websocket_communicator:
            assert websocket_communicator.opened()

            request: str = '{"command": "some_command"}'
            await websocket_communicator.send(request)
            response = await websocket_communicator.response()
            # do something with the response...

    """

    def __init__(self, uri: str = 'ws://127.0.0.1:25010') -> None:
        self.uri: str = uri
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.listen_task: Optional[asyncio.Task[Any]] = None
        self.json_message_queue: asyncio.Queue[str] = asyncio.Queue()
        self.binary_message_queue: asyncio.Queue[bytes] = asyncio.Queue()
        self.binary_message_callback: Optional[Callable[[bytes], Any]] = None
        self.icl_info: dict[str, Any] = {}

    async def __aenter__(self) -> 'WebsocketCommunicator':
        await self.open()
        return self

    async def __aexit__(
        self, exc_type: type[BaseException], exc_value: BaseException, traceback: Optional[TracebackType]
    ) -> None:
        await self.close()

    @override
    async def open(self) -> None:
        """
        Opens the WebSocket connection and starts listening for binary data.

        Raises:
            CommunicationException: When the websocket is already opened or
            there is an issue with the underlying websockets connection attempt.
        """
        if self.opened():
            raise CommunicationException(None, 'websocket already opened')

        try:
            self.websocket = await websockets.connect(self.uri, max_size=None)  # type: ignore
            # self.flush_incoming_messages(self)  # Flush any incoming messages (if any

        except websockets.WebSocketException as e:
            raise CommunicationException(None, 'websocket connection issue') from e

        logger.debug(f'Websocket connection established to {self.uri}')
        self.listen_task = asyncio.create_task(self._receive_data())

    async def send(self, command: Command) -> None:
        """
        Sends a command to the WebSocket server.

        Args:
            command (Command): The command to send to the server.

        Raises:
            CommunicationException: When trying to send a command while the websocket is closed.

        """
        if not self.opened():
            raise CommunicationException(None, 'WebSocket is not opened.')

        try:
            # mypy cannot infer the check from self.opened() done above
            logger.debug(f'Sending JSON command: {command.json()}')
            await self.websocket.send(command.json())  # type: ignore
        except websockets.exceptions.ConnectionClosed as e:
            raise CommunicationException(None, 'Trying to send data while websocket is closed') from e

    @override
    def opened(self) -> bool:
        """
        Returns if the websocket connection is open or not

        Returns:
            bool: True if the websocket connection is open, False otherwise
        """
        return self.websocket is not None and self.websocket.open

    async def response(self) -> Response:
        """Fetches the next response

        Returns:
            Response: The response from the server

        Raises:
            CommunicationException: When the connection terminated with an error
        """
        try:
            response: str = await self.json_message_queue.get()
            return JSONResponse(response)
        except asyncio.CancelledError as e:
            raise CommunicationException(None, 'Response reception was canceled') from e

    @override
    async def binary_response(self) -> BinaryResponse:
        """Fetches the next binary response.

        Returns:
            BinaryResponse: The binary response from the server

        Raises:
            CommunicationException: When the connection terminated with an error
            or the binary data failed to be processed.

        .. todo:: `[saga]` is this still needed?
        """
        try:
            response: bytes = await self.binary_message_queue.get()
            logger.debug(f'Received binary response: {response!r}')
            return BinaryResponse(response)
        except asyncio.CancelledError as e:
            raise CommunicationException(None, 'Response reception was canceled') from e

    @override
    async def close(self) -> None:
        """
        Closes the WebSocket connection.

        Raises:
            CommunicationException: When the websocket is already closed
        """
        if not self.opened():
            raise CommunicationException(None, 'cannot close already closed websocket')
        if self.binary_message_callback:
            self.binary_message_callback = None
        if self.websocket:
            logger.debug('Waiting websocket close...')
            await self.websocket.close()
            self.websocket = None

        if self.listen_task:
            logger.debug('Canceling listening task...')
            self.listen_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                logger.debug('Await listening task...')
                await self.listen_task

        logger.debug('Websocket connection closed')

    def register_binary_message_callback(self, callback: Callable[[bytes], Any]) -> None:
        """Registers a callback to be called with every incoming binary message."""
        logger.debug('Binary message callback registered.')
        self.binary_message_callback = callback

    async def _receive_data(self) -> None:
        try:
            async for message in self.websocket:  # type: ignore
                logger.debug(f'Received message: {message!r}')
                if isinstance(message, str):
                    await self.json_message_queue.put(message)
                elif isinstance(message, bytes):
                    if self.binary_message_callback:
                        await asyncio.create_task(self.binary_message_callback(message))  # Call the callback
                else:
                    raise CommunicationException(None, f'Unknown type of message {type(message)}')
        except websockets.ConnectionClosedOK:
            logger.debug('websocket connection terminated properly')
        except websockets.ConnectionClosedError as e:
            raise CommunicationException(None, 'connection terminated with error') from e
        except Exception as e:
            raise CommunicationException(None, 'failure to process binary data') from e

    @override
    async def request_with_response(self, command: Command, timeout: int = 5) -> Response:
        """
        Concrete method to fetch a response from a command.

        Args:
            command (Command): Command for which a response is desired
            timeout (int): Maximum time to wait for a response

        Returns:
            Response: The response corresponding to the sent command.

        Raises:
            Exception: When an error occurred with the communication channel
        """
        # send the command with the send function and wait a maximum of 5 seconds for the response
        await self.send(command)
        try:
            async with asyncio.timeout(timeout):
                response: Response = await self.response()
        except TimeoutError as te:
            raise CommunicationException(None, f'Timeout of {timeout}s while waiting for response.') from te

        return response
