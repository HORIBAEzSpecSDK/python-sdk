import json
from itertools import count
from typing import Any, Dict, List, Optional, final


class Command:
    """
    Represents a command to be sent to the server.

    Class Attributes:
        _id_counter (iterator): An iterator to generate unique IDs.

    Instance Attributes:
        id (int): Unique identifier for the command.
        command (str): The command string.
        parameters (Dict[str, Any]): Parameters for the command.

    Methods:
        json(): Converts the command to a JSON string.
    """

    _id_counter = count(start=1)  # Starts counting from 1

    def __init__(self, command: str, parameters: Dict[str, Any]):
        self.id = next(self._id_counter)  # Automatically assigns the next unique ID
        self.command = command
        self.parameters = parameters

    def json(self) -> str:
        """Converts the command object to a JSON string."""
        return json.dumps({'id': self.id, 'command': self.command, 'parameters': self.parameters})


class Response:
    """
    Represents a response received from the server.

    Attributes:
        id (int): Unique identifier matching the command's ID.
        command (str): The command string echoed back from the server.
        results (Optional[Dict[str, Any]]): Results returned by the server.
        errors (Optional[List]): List of errors returned by the server.
    """

    def __init__(
        self, id: int, command: str, results: Optional[Dict[str, Any]] = None, errors: Optional[List[str]] = None
    ):
        self.id = id
        self.command = command
        self.results = results or {}
        self.errors = errors or []


@final
class JSONResponse(Response):
    """Represents a JSON response received from the server.

    Attributes:
        json_response (str): JSON response string
    """

    def __init__(self, json_response: str):
        data = json.loads(json_response)
        super().__init__(id=data['id'], command=data['command'], results=data.get('results'), errors=data.get('errors'))


@final
class BinaryResponse:
    """Represents a Binary response received from the server.

    Attributes:
        binary_data (bytes): Response in binary format
    """

    def __init__(self, binary_data: bytes):
        self._binary_data = binary_data


# # Example usage
# command = Command("example_command", {"key1": "value1", "key2": "value2"})
# command_json = command.to_json()
#
# response_json = '{"id": 1357, "command": "example_command","results": ..
# ..{"key1": "value1", "key2": "value2"}, "errors":[]}'
# response = JSONResponse(response_json)
#
# # You can now access attributes like response.id, response.command, etc.
