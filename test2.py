import subprocess
import json
from pathlib import Path
from datetime import datetime
import unicodedata


def get_media_create_timestamp(path: Path | str) -> int | None:
    """Lấy timestamp tạo media từ ExifTool."""

    # Normalize path Windows cho ExifTool
    path = unicodedata.normalize("NFC", str(path))

    cmd = [
        "exiftool",
        "-charset", "filename=utf8",   # FIX QUAN TRỌNG CHO WINDOWS
        "-j",
        "-DateTimeOriginal",
        "-CreateDate",
        "-MediaCreateDate",
        "-ModifyDate",
        "-FileModifyDate",
        path
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )

    if result.returncode != 0:
        print("=== STDERR ===")
        print(result.stderr)
        return None

    try:
        data = json.loads(result.stdout)[0]
    except:
        return None

    # Ưu tiên theo thứ tự
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
        except:
            pass

    return None
test_path = r"C:\Users\DucKhanhPC\Desktop\test\Ảnh từ năm 2019 lỗi\57378655740__7A5E02D2-6E50-48C9-9A3C-47D273FC5A.JPG"

print(get_media_create_timestamp(test_path))
