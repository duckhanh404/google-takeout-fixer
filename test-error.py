import subprocess
import json
import unicodedata
from pathlib import Path
from openpyxl import Workbook


EXIF_FIELDS = [
    "DateTimeOriginal",
    "CreateDate",
    "MediaCreateDate",
    "ModifyDate",
    "FileModifyDate",
    "DateCreated",
]


def extract_metadata_to_excel(input_dir, output_xlsx):
    input_dir = Path(input_dir)
    output_xlsx = Path(output_xlsx)

    # ✅ LẤY FILE TRỰC TIẾP TỪ FOLDER
    files = [f for f in input_dir.iterdir() if f.is_file()]
    if not files:
        raise ValueError("Thư mục không có file")

    # Chuẩn hóa Unicode path
    file_paths = [unicodedata.normalize("NFC", str(f)) for f in files]

    cmd = [
        "exiftool",
        "-j",
        "-charset", "filename=utf8",
        *[f"-{field}" for field in EXIF_FIELDS],
        *file_paths,
    ]

    result = subprocess.run(cmd, capture_output=True)

    try:
        output = result.stdout.decode("utf-8")
    except UnicodeDecodeError:
        output = result.stdout.decode("cp1252", errors="replace")

    data = json.loads(output)

    wb = Workbook()
    ws = wb.active
    ws.title = "metadata"

    ws.append(["file_name", *EXIF_FIELDS])

    # ⚠️ QUAN TRỌNG:
    # ExifTool trả JSON theo đúng thứ tự file truyền vào
    for f, item in zip(files, data):
        file_name = f.name  # ✅ LẤY TRỰC TIẾP TỪ FILESYSTEM

        row = [file_name]
        for field in EXIF_FIELDS:
            row.append(item.get(field))

        ws.append(row)

    wb.save(output_xlsx)

if __name__ == "__main__":
    extract_metadata_to_excel(
        input_dir="/Users/hannada/Desktop/loi",
        output_xlsx="test-error.xlsx",
    )
