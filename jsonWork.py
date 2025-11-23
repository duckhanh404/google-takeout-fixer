import json
import unicodedata
from pathlib import Path 
from datetime import datetime

def extract_title(json_path:Path|str):
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

def extract_title_not(json_path:Path|str):
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




if __name__ == "__main__":
    test_json = Path("C:/Takeout/Google Photos/2018/.com.google.Chrome.ag4I1L.supplemental-metadat.json")

