import threading
import time
import os
import signal
import atexit
import sys
from ipywidgets import Button
from IPython.utils import py3compat
from subprocess import Popen, PIPE

STDOUT, STDERR = 1, 2

class ServerWidget(Button):
    def __init__(self, cmd, *args, **kwargs):
        super(ServerWidget, self).__init__(*args, **kwargs)
        self.cmd = cmd
        self.description = cmd
        self.button_style = "success"
        self.on_click(callback=self._on_click_handler)

    def _write_to_console(self, fd, string):
        os.write(fd, py3compat.str_to_bytes(string, encoding = 'utf-8'))

    def _forward_process_stdout(self, process, cmd):
        while True:
            output = process.stdout.readline()
            if output == b"" or process.poll() is not None:
                break
            self._write_to_console(STDOUT, "[{} {}] {}\n".format(process.pid, cmd, output))

    def _forward_process_stderr(self, process, cmd):
        while True:
            output = process.stderr.readline()
            if output == b"" or process.poll() is not None:
                break
            self._write_to_console(STDERR, "[{} {}] {}\n".format(process.pid, cmd, output))

    def _check_proccess_status(self, process):
        while process.poll() is None:
            time.sleep(0.1)
        if self.description in ("Stopping...", "Terminating...", "Killing..."):
            self.button_style = "success"
        else: # something happened
            self.button_style = "danger"
        self.description = self.cmd

    def _on_click_handler(self, _):
        if self.description == self.cmd:
            self._start_process()
        elif self.description == "Stopping...":
            self.description = "Terminating..."
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
        elif self.description == "Terminating...":
            self.description = "Killing..."
            os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
        else:
            self.description = "Stopping..."
            self.button_style = "danger"
            os.killpg(os.getpgid(self.process.pid), signal.SIGINT)

    def _start_process(self):
        self.process = Popen(self.cmd, shell=True, stdout=PIPE, stderr=PIPE, preexec_fn=os.setsid)

        self.description = "{} {}".format(self.process.pid, self.cmd)
        self.button_style="warning"

        forward_process_stdout_thread = threading.Thread(target=self._forward_process_stdout,
                                              name="forward_process_stdout", args=(self.process, self.cmd))
        forward_process_stdout_thread.setDaemon(True)
        forward_process_stdout_thread.start()

        forward_process_stderr_thread = threading.Thread(target=self._forward_process_stderr,
                                              name="forward_process_stderr", args=(self.process, self.cmd))
        forward_process_stderr_thread.setDaemon(True)
        forward_process_stderr_thread.start()

        check_proccess_status_thread = threading.Thread(target=self._check_proccess_status,
                                                        name="check_proccess_status", args=(self.process,))
        check_proccess_status_thread.setDaemon(True)
        check_proccess_status_thread.start()

        def atexit_hook():
            try:
                if self.process.poll() is None:
                    self._write_to_console(STDOUT, "Stopping [{}: {}]\n".format(self.process.pid, self.cmd))
                    os.killpg(os.getpgid(self.process.pid), signal.SIGINT)
                    time.sleep(0.1)
                if self.process.poll() is None:
                    self._write_to_console(STDOUT, "Terminating [{}: {}]\n".format(self.process.pid, self.cmd))
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                    time.sleep(0.1)
                if self.process.poll() is None:
                    self._write_to_console(STDOUT, "Killing [{}: {}]\n".format(self.process.pid, self.cmd))
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                    time.sleep(0.1)
                if self.process.poll() is None:
                    self._write_to_console(STDERR, "Couldn't kill [{}: {}]\n".format(self.process.pid, self.cmd))
            except OSError:
                pass
            except Exception as e:
                self._write_to_console("Error while terminating subprocess (pid=%i): %s\n" % (self.process.pid, e))

        atexit.register(atexit_hook)
