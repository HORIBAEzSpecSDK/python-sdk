from abc import ABC, abstractmethod
from typing import Any

from horiba_sdk.communication import Command, Response
from horiba_sdk.icl_error import AbstractError, AbstractErrorDB
from horiba_sdk.sync.communication.abstract_communicator import AbstractCommunicator


class AbstractDevice(ABC):
    """
    Abstract base class representing a generic device.

    This class provides an interface for device-specific operations. Concrete implementations should provide specific
    functionalities for each of the abstract methods.

    Attributes:
        _id (int):
        _communicator (WebsocketCommunicator):
    """

    def __init__(self, device_id: int, communicator: AbstractCommunicator, error_db: AbstractErrorDB) -> None:
        self._id: int = device_id
        self._error_db: AbstractErrorDB = error_db
        self._communicator: AbstractCommunicator = communicator

    def id(self) -> int:
        """Return the ID of the device.

        Returns:
            int: ID of the device.
        """
        return self._id

    @abstractmethod
    def open(self) -> None:
        """
        Open a connection to the device.

        Returns:
            Result: Result object indicating success or failure.
        """
        if not self._communicator.opened():
            self._communicator.open()

    @abstractmethod
    def close(self) -> None:
        """
        Close the connection to the device.

        Returns:
            Result: Result object indicating success or failure.
        """
        pass

    def _execute_command(self, command_name: str, parameters: dict[Any, Any], timeout_in_s: float = 5) -> Response:
        """
        Creates a command from the command name, and it's parameters
        Executes a command and handles the response.

        Args:
            command_name (str): The name of the command to execute.
            parameters (dict): The parameters for the command.
            timeout_in_s (float, optional): The timeout in seconds.

        Returns:
            Response: The response from the device.

        Raises:
            Exception: When an error occurred on the device side.
        """
        response: Response = self._communicator.request_with_response(Command(command_name, parameters), timeout_in_s)
        if response.errors:
            self._handle_errors(response.errors)
        return response

    def _handle_errors(self, errors: list[str]) -> None:
        """
        Handles errors, logs them, and may take corrective actions.

        Args:
            errors (Exception): The exception or error to handle.
        """
        for error in errors:
            icl_error: AbstractError = self._error_db.error_from(error)
            icl_error.log()
            # TODO: [saga] only throw depending on the log level, tbd
            raise Exception(f'Error from the ICL: {icl_error.message()}')
