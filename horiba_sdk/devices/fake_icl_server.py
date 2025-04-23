import json
import os

import websockets
from loguru import logger


class FakeICLServer:
    def __init__(self, fake_icl_host: str = 'localhost', fake_icl_port: int = 8765):
        self._fake_icl_host: str = fake_icl_host
        self._fake_icl_port: int = fake_icl_port
        self._server = None

        current_directory = os.path.dirname(__file__)
        fake_responses_path = os.path.join(current_directory, 'fake_responses')

        icl_fake_responses_path = os.path.join(fake_responses_path, 'icl.json')
        with open(icl_fake_responses_path) as json_file:
            self.icl_responses = json.load(json_file)

        monochromator_fake_responses_path = os.path.join(fake_responses_path, 'monochromator.json')
        with open(monochromator_fake_responses_path) as json_file:
            self.monochromator_responses = json.load(json_file)

        ccd_fake_responses_path = os.path.join(fake_responses_path, 'ccd.json')
        with open(ccd_fake_responses_path) as json_file:
            self.ccd_responses = json.load(json_file)

        spectracq3_fake_responses_path = os.path.join(fake_responses_path, 'spectracq3.json')
        with open(spectracq3_fake_responses_path) as json_file:
            self.spectracq3_responses = json.load(json_file)

    async def echo(self, websocket):
        async for message in websocket:
            logger.info('received: {message}', message=message)
            command = json.loads(message)
            if 'command' not in command:
                logger.info('unknown message format, responding with message')
                await websocket.send(message)

            if command['command'].startswith('icl_'):
                response = json.dumps(self.icl_responses[command['command']])
                await websocket.send(response)
            elif command['command'].startswith('mono_'):
                response = json.dumps(self.monochromator_responses[command['command']])
                await websocket.send(response)
            elif command['command'].startswith('ccd_'):
                response = json.dumps(self.ccd_responses[command['command']])
                await websocket.send(response)
            elif command['command'].startswith('saq3_'):
                response = json.dumps(self.spectracq3_responses[command['command']])
                await websocket.send(response)
            else:
                logger.info('unknown command, responding with message')
                await websocket.send(message)

    async def start(self):
        self._server = await websockets.serve(self.echo, self._fake_icl_host, self._fake_icl_port)

    async def stop(self):
        if self._server:
            self._server.close()
            await self._server.wait_closed()
