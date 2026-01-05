import subprocess
from pathlib import Path
from jsonWork import extract_time, convert_timestamp


# =====================================================
# ExifTool batch singleton
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

