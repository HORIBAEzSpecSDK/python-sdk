from horiba_sdk.communication import Command


def test_command_to_json_with_string_parameter():
    # arrange
    command: Command = Command('test_command', {'test': 'some_test'})

    # act
    json = command.json()

    # assert
    assert json == '{"id": 1, "command": "test_command", "parameters": {"test": "some_test"}}'


def test_command_to_json_with_bool_parameter():
    # arrange
    command = Command('ccd_setAcquisitionStart', {'index': 1, 'parameters': {'openShutter': True}})

    # act
    json = command.json()

    # assert
    assert json == (
        '{"id": 2, "command": "ccd_setAcquisitionStart", "parameters":'
        ' {"index": 1, "parameters": {"openShutter": true}}}'
    )
