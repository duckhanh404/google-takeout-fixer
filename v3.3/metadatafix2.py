import subprocess
from pathlib import Path
from jsonWork2 import extract_time, convert_timestamp
import unicodedata
import datetime
import json

# =====================================================
# ExifToolBatch
# =====================================================

class ExifToolBatch:
    def __init__(self):
        self.process = subprocess.Popen(
            ["exiftool", "-overwrite_original", "-@", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True
        )

    def write_datetime(self, media_path: Path | str, datetime_str: str):
        media_path = Path(media_path)

        self.process.stdin.write(
            f"-FileCreateDate={datetime_str}\n"
            f"-FileModifyDate={datetime_str}\n"
            f"{media_path}\n"
            "-execute\n"
        )
        self.process.stdin.flush()   # ⚠️ rất quan trọng

    def close(self):
        if self.process.stdin:
            self.process.stdin.write("-stay_open\nFalse\n")
            self.process.stdin.flush()
            self.process.stdin.close()
        self.process.wait()

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
# =====================================================
# Singleton instance (QUAN TRỌNG)
# =====================================================


def get_exiftool() -> ExifToolBatch:
    global _instance
    if _instance is None:
        _instance = ExifToolBatch()
    return _instance
def close_exiftool():
    global _instance
    if _instance:
        _instance.close()
        _instance = None


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

    try:
        data = _instance.execute([
            "-j",
            "-charset", "filename=utf8",
            "-DateTimeOriginal",
            "-CreateDate",
            "-MediaCreateDate",
            "-ModifyDate",
            "-DateCreated",
            path_str
        ])[0]
    except Exception:
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
        "%Y:%m:%d %H:%M:%S.%f%z"
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(dt_str, fmt)
            return int(dt.timestamp())
        except Exception:
            pass

    return None

if __name__ == "__main__":
    _instance = ExifToolBatch()
    a=get_media_create_timestamp("/Users/hannada/Downloads/2019/IMG_2096(1).HEIC")
    print(a)