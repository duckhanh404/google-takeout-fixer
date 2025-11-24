import json
import unicodedata
from pathlib import Path 
from datetime import datetime
import re
from openpyxl import Workbook


def extract_title(json_path:Path|str)->str:
    """
    trích xuất title từ file json
    - đầu vào là Path hoặc string đường dẫn đến file json
    - trả về là string đã chuẩn hóa NFC
    """
    json_path = Path(json_path)  # đảm bảo luôn là Path
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    title = data.get("title", None)
    # trả về string đã chuẩn hóa NFC
    return unicodedata.normalize("NFC", title)

def extract_title_not(json_path:Path|str)->str:
    """
    trích xuất title từ file json
    - đầu vào là Path hoặc string đường dẫn đến file json
    - trả về là string chưa chuẩn hóa NFC
    """
    json_path = Path(json_path)  # đảm bảo luôn là Path
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    title = data.get("title", None)
    # trả về string đã chuẩn hóa NFC
    return title

def extract_time(json_path:Path|str)->str:
    """
    Trích xuất thời gian từ file json
    - đầu vào là Path hoặc string đường dẫn đến file json
    - trả về là timestamp dưới dạng string theo định dạng EXIF: YYYY:MM:DD HH:MM:SS
    Ở đây ưu tiên "photoTakenTime" hơn "creationTime".
    """
    json_path = Path(json_path)
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # ưu tiên đúng thứ tự
    if "photoTakenTime" in data and "timestamp" in data["photoTakenTime"]:
        ts = int(data["photoTakenTime"]["timestamp"])
    elif "creationTime" in data and "timestamp" in data["creationTime"]:
        ts = int(data["creationTime"]["timestamp"])
    else:
        raise ValueError(f"Không có timestamp hợp lệ trong JSON: {json_path}")
    # EXIF format bắt buộc: YYYY:MM:DD HH:MM:SS
    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%Y:%m:%d %H:%M:%S")

def get_all_json(folder_path:Path|str):
    """
    Lấy tất cả file json trong thư mục
    - đầu vào là Path hoặc string đường dẫn đến thư mục
    - trả về là danh sách tên file json chưa chuẩn hóa
    """
    folder_path = Path(folder_path)
    if not folder_path.is_dir():
        raise ValueError("Đường dẫn không phải thư mục hợp lệ!")

    # return [
    #     unicodedata.normalize("NFC", filename.name)
    #     for filename in folder_path.iterdir()
    #     if filename.is_file() and filename.suffix.lower() == ".json"
    # ]
    return [
        filename.name
        for filename in folder_path.iterdir()
        if filename.is_file() and filename.suffix.lower() == ".json"
    ]

def get_all_media(folder_path:Path|str):
    """
    lấy tất cả file media (không phải json) trong thư mục
    - đầu vào là Path hoặc string đường dẫn đến thư mục
    - trả về là danh sách tên file media chưa chuẩn hóa
    """
    folder_path = Path(folder_path)
    if not folder_path.is_dir():
        raise ValueError("Đường dẫn không hợp lệ!")

    # return [
    #     unicodedata.normalize("NFC", file.name)
    #     for file in folder_path.iterdir()
    #     if file.is_file() and file.suffix.lower() != ".json"
    # ]
    return [
        file.name
        for file in folder_path.iterdir()
        if file.is_file() and file.suffix.lower() != ".json"
    ]

def is_that_cloned(file_name: str) -> bool:
    """
    Kiểm tra tên file có đuôi dạng (số) ngay trước extension hay không.
    Hỗ trợ cả trường hợp có khoảng trắng: "image (1).jpg"
    trả về True nếu đúng là có đuôi (số), ngược lại False.
    Trả về chuỗi "(n)" nếu tên file có dạng (n) ngay trước extension.
    Nếu không có, trả về 0.
    """
    name = Path(file_name).stem

    # Tìm dạng: optional-space + (digits) + end
    match = re.search(r"\s*\(\d+\)$", name)
    if match:
        return match.group().strip()  # return "(2)" (loại bỏ space nếu có)
    return "original"

def lists_to_excel(output_path="output.xlsx", **kwargs):
    """
    Ghi nhiều list vào file Excel.
    Tên mỗi cột chính là tên biến list được truyền vào.
    
    Ví dụ gọi hàm:
    lists_to_excel(output="out.xlsx", list1=a, list2=b, my_data=c)
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Data"

    # Lấy danh sách tên cột (keys) và dữ liệu (values)
    headers = list(kwargs.keys())
    columns = list(kwargs.values())

    # Ghi tiêu đề cột
    for col_idx, header in enumerate(headers, start=1):
        ws.cell(row=1, column=col_idx, value=header)

    # Tìm số dòng tối đa (list dài nhất)
    max_len = max(len(col) for col in columns)

    # Ghi dữ liệu
    for row_idx in range(max_len):
        for col_idx, col_data in enumerate(columns, start=1):
            if row_idx < len(col_data):
                ws.cell(row=row_idx + 2, column=col_idx, value=col_data[row_idx])

    wb.save(output_path)
    print(f"✔ Đã tạo file Excel: {output_path}")


if __name__ == "__main__":
    test = Path("E:\json")
    get_all_file_name = [file for file in test.iterdir()]
    print(len(get_all_file_name))