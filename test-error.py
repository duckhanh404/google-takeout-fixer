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

    # Lấy & sort file để đảm bảo thứ tự khớp ExifTool
    files = sorted([f for f in input_dir.iterdir() if f.is_file()])
    total_files = len(files)

    if total_files == 0:
        raise ValueError("Thư mục không có file")

    print(f"🔍 Tổng số file: {total_files}")

    # Gọi ExifTool cho cả thư mục
    cmd = [
        "exiftool",
        "-j",
        "-charset", "filename=utf8",
        *[f"-{field}" for field in EXIF_FIELDS],
        str(input_dir),
    ]

    print("🚀 Đang chạy ExifTool...")
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

    print("📝 Ghi dữ liệu ra Excel...")

    for idx, (f, item) in enumerate(zip(files, data), start=1):
        file_name = f.name

        row = [file_name]
        for field in EXIF_FIELDS:
            row.append(item.get(field))

        ws.append(row)

        # ✅ In tiến độ
        print(f"[{idx}/{total_files}] Đã xử lý: {file_name}")

    wb.save(output_xlsx)

    print(f"✅ Hoàn tất! File Excel đã lưu tại: {output_xlsx}")


if __name__ == "__main__":
    extract_metadata_to_excel(
        input_dir=r"E:\Takeout\Google Photos\Anh tu nam 2019",
        output_xlsx="test-error-all.xlsx",
    )
