import subprocess
import json
import unicodedata
from pathlib import Path


def normalize_path(path: str) -> str:
    """Normalize path về dạng NFC để tránh lỗi Unicode trên Windows."""
    return unicodedata.normalize("NFC", path)


def get_metadata(file_path: str | Path) -> dict:
    """Đọc metadata của 1 file bất kỳ bằng ExifTool và trả về dictionary."""

    # Convert Path -> string và normalize
    file_path = normalize_path(str(Path(file_path)))

    # Lệnh ExifTool
    cmd = [
        "exiftool",
        "-j",               # xuất JSON
        "-api", "largefilesupport=1",  # hỗ trợ file lớn >4GB
        file_path
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False  # luôn OFF để tránh lỗi wildcard
        )

        # Nếu ExifTool trả lỗi
        if result.returncode != 0:
            print("❌ ExifTool error:")
            print(result.stderr.strip())
            return {}

        # Parse JSON
        data = json.loads(result.stdout)

        if isinstance(data, list) and len(data) > 0:
            return data[0]  # ExifTool trả list
        return {}

    except Exception as e:
        print("❌ Exception khi chạy ExifTool:", e)
        return {}
if __name__ == "__main__":
    # Ví dụ sử dụng
    metadata = get_metadata(r"C:\Takeout\Google Photos\2021\IMG_3108.MP4")
    print(json.dumps(metadata, indent=4, ensure_ascii=False))