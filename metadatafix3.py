import subprocess
from pathlib import Path
from jsonWork import extract_time, convert_timestamp
import unicodedata
from datetime import datetime
import json

# =====================================================
# ExifTool batch singleton
# =====================================================
class ExifToolBatch:
    def __init__(self):
        self.process = subprocess.Popen(
            ["exiftool", "-stay_open", "True", "-@", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,   # ⬅ PHẢI CÓ
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1
)

    def write_datetime(self, media_path: Path | str, datetime_str: str):
        media_path = Path(media_path)

        self.process.stdin.write(
            f"-FileCreateDate={datetime_str}\n"
            f"-FileModifyDate={datetime_str}\n"
            f"{media_path}\n"
            "-execute\n"
        )

    def read_datetime(self, media_path: Path | str) -> dict | None:
        media_path = Path(media_path)

        cmd = (
            "-j\n"
            "-charset\n"
            "filename=utf8\n"
            "-DateTimeOriginal\n"
            "-CreateDate\n"
            "-MediaCreateDate\n"
            "-ModifyDate\n"
            "-DateCreated\n"
            f"{media_path}\n"
            "-execute\n"
        )

        self.process.stdin.write(cmd)
        self.process.stdin.flush()

        # đọc output cho tới {ready}
        output = ""
        while True:
            line = self.process.stdout.readline()
            if not line:
                break
            if line.strip() == "{ready}":
                break
            output += line

        try:
            return json.loads(output)[0]
        except Exception:
            return None

    def close(self):
        if self.process.stdin:
            self.process.stdin.close()
        self.process.wait()


# =====================================================
# Singleton instance (QUAN TRỌNG)
# =====================================================
_exiftool = None


def get_exiftool() -> ExifToolBatch:
    global _exiftool
    if _exiftool is None:
        _exiftool = ExifToolBatch()
    return _exiftool


def close_exiftool():
    global _exiftool
    if _exiftool:
        _exiftool.close()
        _exiftool = None


# =====================================================
# API dùng cho main
# =====================================================
def write_metadata_with_exiftool(media_path: Path | str, datetime_str: str):
    exif = get_exiftool()
    exif.write_datetime(media_path, datetime_str)


def process_media(json_path: Path | str, media_path: Path | str) -> None:
    json_path = Path(json_path)
    dt = extract_time(json_path)
    write_metadata_with_exiftool(media_path, dt)


def process_media_lite(timestamp: str | int, media_path: Path | str) -> None:
    dt = convert_timestamp(timestamp)
    write_metadata_with_exiftool(media_path, dt)


def get_media_create_timestamp(path: Path | str) -> int | None:
    path_str = unicodedata.normalize("NFC", str(path))

    exif = get_exiftool()
    data = exif.read_datetime(path_str)

    if not data:
        return None

    for key in [
        "DateTimeOriginal",
        "CreateDate",
        "MediaCreateDate",
        "ModifyDate",
        "FileModifyDate"
    ]:
        if key in data:
            dt_str = data[key]
            break
    else:
        return None

    formats = [
        "%Y:%m:%d %H:%M:%S",
        "%Y:%m:%d %H:%M:%S%z",
        "%Y:%m:%d %H:%M:%S.%f",
        "%Y:%m:%d %H:%M:%S.%f%z",
    ]

    for fmt in formats:
        try:
            return int(datetime.strptime(dt_str, fmt).timestamp())
        except Exception:
            continue

    return None
