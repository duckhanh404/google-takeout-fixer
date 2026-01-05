import subprocess
import json
import unicodedata
from pathlib import Path
from datetime import datetime
from jsonWork import extract_time, convert_timestamp

# =====================================================
# EXIFTOOL SINGLETON (DÙNG CHUNG TOÀN MODULE)
# =====================================================
_exiftool_proc = None


def _get_exiftool():
    global _exiftool_proc
    if _exiftool_proc is None:
        _exiftool_proc = subprocess.Popen(
            ["exiftool", "-stay_open", "True", "-@", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    return _exiftool_proc


def _exiftool_execute(args: list[str]) -> str:
    proc = _get_exiftool()
    assert proc.stdin and proc.stdout

    for arg in args:
        proc.stdin.write((arg + "\n").encode("utf-8"))

    proc.stdin.write(b"-execute\n")
    proc.stdin.flush()

    output = b""
    while True:
        line = proc.stdout.readline()
        if line.strip() == b"{ready}":
            break
        output += line

    return output.decode("utf-8", errors="replace")


def close_exiftool():
    global _exiftool_proc
    if _exiftool_proc and _exiftool_proc.stdin:
        _exiftool_proc.stdin.write(b"-stay_open\nFalse\n")
        _exiftool_proc.stdin.flush()
        _exiftool_proc.wait()
        _exiftool_proc = None


# =====================================================
# GHI METADATA (KHÔNG ĐỔI API)
# =====================================================
def write_metadata_with_exiftool(media_path: Path | str, datetime_str: str):
    media_path = Path(media_path)

    _exiftool_execute([
        f"-FileCreateDate={datetime_str}",
        f"-FileModifyDate={datetime_str}",
        "-overwrite_original",
        str(media_path)
    ])


# =====================================================
# ĐỌC TIMESTAMP (ĐÃ TỐI ƯU)
# =====================================================
def get_media_create_timestamp(path: Path | str) -> int | None:
    path_str = unicodedata.normalize("NFC", str(path))

    output = _exiftool_execute([
        "-j",
        "-charset", "filename=utf8",
        "-DateTimeOriginal",
        "-CreateDate",
        "-MediaCreateDate",
        "-ModifyDate",
        "-DateCreated",
        path_str
    ])

    try:
        data = json.loads(output)[0]
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
        "%Y:%m:%d %H:%M:%S.%f%z",
    ]

    for fmt in formats:
        try:
            return int(datetime.strptime(dt_str, fmt).timestamp())
        except Exception:
            continue

    return None


# =====================================================
# XỬ LÝ MEDIA (GIỮ NGUYÊN API)
# =====================================================
def process_media(json_path: Path | str, media_path: Path | str) -> None:
    dt = extract_time(json_path)
    write_metadata_with_exiftool(media_path, dt)


def process_media_lite(timestamp: str | int, media_path: Path | str) -> None:
    dt = convert_timestamp(timestamp)
    write_metadata_with_exiftool(media_path, dt)
