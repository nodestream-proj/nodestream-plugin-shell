import json
import subprocess
from io import StringIO
from logging import getLogger
from typing import Any, AsyncGenerator, Dict, Optional, Set

from nodestream.pipeline import Extractor


class Shell(Extractor):
    """Run shell command and provide output to pipeline"""

    def __init__(
        self,
        command: str,
        arguments: Optional[Set[str]] = None,
        options: Optional[Dict[str, str]] = None,
        flags: Optional[Set[str]] = None,
        ignore_stdout: Optional[bool] = False,
    ):
        """Initializes the instance of the extractor.
        Expects stdout in json format.

        Args:
            command (str): The command for the execution call.
            arguments ([str]): The arguments used in the command.
            options (dict): The Options used in the command.
            flags ([str]): Flags to use in the command.
            ignore_stdout (bool): Don't pass stdout to pipeline.
        """
        self.command = command
        self.arguments = arguments if arguments is not None else set()
        self.options = options if options is not None else dict()
        self.flags = flags if flags is not None else set()
        self.ignore_stdout = ignore_stdout
        self.logger = getLogger(self.__class__.__name__)

    def read_from_file(self) -> StringIO:
        with open(self.output_file, "r") as file:
            return StringIO(file.read().strip())

    def build_command(self):
        cmd = [self.command]
        cmd.extend(self.arguments)
        for k, v in self.options.items():
            if len(k) == 1:
                cmd.append(f"-{k} {v}")
            else:
                cmd.append(f"--{k}={v}")
        for flag in self.flags:
            flag = f"-{flag}" if len(flag) == 1 else f"--{flag}"
            cmd.append(flag)
        return cmd

    def run_command(self, cmd):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise SystemError(
                f"Error running shell command: {' '.join(cmd)}, error: {stderr.decode()}, return code: {process.returncode}"
            )
        return stdout

    async def extract_records(self) -> AsyncGenerator[Any, Any]:
        cmd = self.build_command()
        stdout = self.run_command(cmd)
        output = stdout.decode().strip()
        if self.ignore_stdout:
            yield {}
        else:
            try:
                results = json.loads(output)
                for item in results:
                    yield item
            except json.JSONDecodeError:
                self.logger.warn(
                    f"Stdout not in json format, step yielding no data, set ignore_stdout to True to ignore this warning. Stdout: {output}"
                )
                yield {}
