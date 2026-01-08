import subprocess
import json
import unicodedata
from pathlib import Path
from datetime import datetime
from typing import Optional

# ======================== Read ExifTool ========================
class ExifToolRead:
    def __init__(self):
        self.process = subprocess.Popen(
            ["exiftool", "-stay_open", "True", "-@", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )

    def execute(self, args: list[str]) -> list[dict]:
        cmd = "\n".join(args + ["-execute\n"])
        self.process.stdin.write(cmd.encode("utf-8"))
        self.process.stdin.flush()

        output = b""
        while True:
            line = self.process.stdout.readline()
            if line == b"{ready}\n":
                break
            output += line

        return json.loads(output.decode("utf-8", errors="replace")) if output else []

    def extract_time_from_file(self, path: Path | str) -> Optional[datetime]:
        path_str = unicodedata.normalize("NFC", str(path))
        try:
            result = self.execute([
                "-j",
                "-DateTimeOriginal",
                "-CreateDate",
                "-MediaCreateDate",
                "-ModifyDate",
                "-FileModifyDate",
                path_str
            ])
        except Exception:
            return None

        if not result:
            return None

        data = result[0]
        for key in (
            "DateTimeOriginal",
            "CreateDate",
            "MediaCreateDate",
            "ModifyDate",
            "FileModifyDate",
        ):
            if key in data:
                try:
                    return datetime.strptime(data[key], "%Y:%m:%d %H:%M:%S")
                except Exception:
                    pass
        return None

    def close(self):
        self.process.stdin.write(b"-stay_open\nFalse\n")
        self.process.stdin.flush()
        self.process.wait()


# ======================== Write ExifTool ========================
class ExifToolWrite:
    def __init__(self):
        self.process = subprocess.Popen(
            ["exiftool", "-stay_open", "True", "-overwrite_original", "-@", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True
        )
        self.counter = 0

    def write_datetime(self, media_path: Path | str, datetime_str: str):
        self.process.stdin.write(
            f"-FileCreateDate={datetime_str}\n"
            f"-FileModifyDate={datetime_str}\n"
            f"{media_path}\n"
            "-execute\n"
        )
        self.counter += 1
        if self.counter % 50 == 0:
            self.process.stdin.flush()

    def close(self):
        self.process.stdin.write("-stay_open\nFalse\n")
        self.process.stdin.flush()
        self.process.wait()


# ======================== Helpers ========================
def get_all_json(folder: Path) -> set[str]:
    return {
        unicodedata.normalize("NFC", f.name)
        for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() == ".json"
    }

def get_all_media(folder: Path) -> set[str]:
    return {
        unicodedata.normalize("NFC", f.name)
        for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() != ".json"
    }

def extract_time_from_json(json_path: Path) -> str:
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if "photoTakenTime" in data:
        ts = int(data["photoTakenTime"]["timestamp"])
    elif "creationTime" in data:
        ts = int(data["creationTime"]["timestamp"])
    else:
        raise ValueError(f"No timestamp: {json_path}")

    return datetime.fromtimestamp(ts).strftime("%Y:%m:%d %H:%M:%S")
