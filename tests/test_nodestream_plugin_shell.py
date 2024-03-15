import subprocess
from unittest.mock import patch

import pytest

from nodestream_plugin_shell import Shell


@pytest.fixture
def command():
    return "command"


@pytest.fixture
def arguments():
    return ["arg1", "arg2"]


@pytest.fixture
def options():
    return {"o": "value1", "longoption": "value2"}


@pytest.fixture
def flags():
    return ["f", "longflag"]


@pytest.fixture
def ignore_stdout():
    return False


@pytest.fixture
def shell_instance(command, arguments, options, flags, ignore_stdout):
    return Shell(command, arguments, options, flags, ignore_stdout)


@patch.object(subprocess, "Popen")
def test_run_command(mocked_popen, shell_instance):
    stdout, stderr, return_code = b'[{"key1": "value1"}, {"key2": "value2"}]', b"", 0

    mocked_popen.return_value.communicate.return_value = (stdout, stderr)
    mocked_popen.return_value.returncode = return_code

    cmd = shell_instance.build_command()
    assert "-o value1" in cmd
    assert "--longoption=value2" in cmd
    assert "-f" in cmd
    assert "--longflag" in cmd

    response = shell_instance.run_command(cmd)

    assert response == stdout


@pytest.mark.asyncio
@patch.object(subprocess, "Popen")
async def test_extract_records(mocked_popen, shell_instance):
    stdout, stderr, return_code = b'[{"key1": "value1"}, {"key2": "value2"}]', b"", 0

    mocked_popen.return_value.communicate.return_value = (stdout, stderr)
    mocked_popen.return_value.returncode = return_code

    records = []

    async for record in shell_instance.extract_records():
        records.append(record)

    assert len(records) == 2
    assert records[0] == {"key1": "value1"}
    assert records[1] == {"key2": "value2"}
