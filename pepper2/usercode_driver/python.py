"""Python Usercode Driver."""

import logging
from signal import SIGCHLD, SIGKILL, SIGTERM, Signals, getsignal, signal
from subprocess import DEVNULL, Popen, TimeoutExpired
from threading import Thread
from time import sleep
from types import FrameType
from typing import TYPE_CHECKING, Optional

from pepper2.drives import Drive

from .usercode_driver import UserCodeDriver

if TYPE_CHECKING:
    # _HANDLER is only available in typeshed.
    from signal import _HANDLER


LOGGER = logging.getLogger(__name__)


class LoggerThread(Thread):
    """
    A thread that will log the output of the process.

    This thread does not modify any data in the program, it simply
    logs the output of the child process to the appropriate
    destinations. This is used as a more flexible, pure-python
    alternative to solutions such as ``script``.
    """

    def __init__(self, process: Popen, drive: Drive):
        super().__init__(daemon=True)
        self._process = process
        self._log_file = open(
            drive.mount_path.joinpath("log.txt"),
            "w",
        )
        self.log = True

    def run(self) -> None:
        """Log the process."""
        LOGGER.info("Logger Thread Started.")
        self._log_line_to_file("=== LOG STARTED ===")
        while self.log:
            print("logging")
            sleep(0.5)
        self._log_line_to_file("=== LOG FINISHED ===")
        self._log_file.close()
        LOGGER.info("Logger Thread Exiting.")

    def stop(self) -> None:
        """Stop logging."""
        self.log = False

    def _log_line_to_file(self, line: str) -> None:
        """Log a line to the logfile."""
        self._log_file.write(f"{line}\n")
        self._log_file.flush()


class PythonDriver(UserCodeDriver):
    """
    Usercode driver to execute Python.

    TODO: Name this class something better.
    """

    _process: Optional[Popen]
    _logger: Optional[LoggerThread]

    def __init__(self, drive: Drive):
        self.drive = drive

        self._process = None
        self._logger = None

        self._original_sigchld: _HANDLER = getsignal(SIGCHLD)

    def start_execution(self) -> None:
        """Start the execution of the code."""
        signal(SIGCHLD, self.sigchld_handler)
        self._process = Popen(
            ["python3", "main.py"],
            stdin=DEVNULL,
            cwd=self.drive.mount_path,
            start_new_session=True,  # Put the process in a new process group
        )
        self._logger = LoggerThread(self._process, self.drive)
        self._logger.start()

        LOGGER.info(f"Usercode process started with pid {self._process.pid}")

    def stop_execution(self) -> None:
        """Stop the execution of the code."""
        self._reset_sigchld()

        if self._process is not None:
            LOGGER.info(f"Sent SIGTERM to pid {self._process.pid}")
            self._process.send_signal(SIGTERM)
            try:
                self._process.communicate(timeout=5)
            except TimeoutExpired:
                pass
            LOGGER.info(f"Sent SIGKILL to pid {self._process.pid}")
            self._process.send_signal(SIGKILL)
            self._cleanup()
        else:
            LOGGER.info("No usercode process to stop.")

    def sigchld_handler(self, _: Signals, __: FrameType) -> None:
        """
        Handler for SIGCHLD.

        This is called when the child process of this process dies.
        """
        self._reset_sigchld()

        if self._process is not None:
            return_code = self._process.poll()

            if return_code == 0:
                LOGGER.info("Usercode finished successfully.")
            else:
                LOGGER.info(
                    f"Usercode finished unsuccessfully (return code: {return_code}).",
                )
            self._cleanup()

    def _reset_sigchld(self) -> None:
        """Reset the SIGCHLD handler to the original."""
        signal(SIGCHLD, self._original_sigchld)

    def _cleanup(self) -> None:
        """Clean up from a running process."""
        self._process = None

        if self._logger is not None:
            self._logger.stop()
