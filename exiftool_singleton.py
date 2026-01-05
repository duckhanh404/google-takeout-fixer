import subprocess
import json
import unicodedata
from datetime import datetime
from pathlib import Path

class ExifToolSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._start()
        return cls._instance

    def _start(self):
        self.process = subprocess.Popen(
            [
                "exiftool",
                "-stay_open", "True",
                "-@", "-"
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )

    def execute(self, args: list[str]) -> list[dict]:
        """
        Gửi lệnh cho exiftool đang chạy
        """
        cmd = "\n".join(args + ["-execute\n"])
        self.process.stdin.write(cmd.encode("utf-8"))
        self.process.stdin.flush()

        output = b""
        while True:
            line = self.process.stdout.readline()
            if line == b"{ready}\n":
                break
            output += line

        return json.loads(output.decode("utf-8", errors="replace"))

    def close(self):
        if self.process:
            self.process.stdin.write(b"-stay_open\nFalse\n")
            self.process.stdin.flush()
            self.process.wait()
