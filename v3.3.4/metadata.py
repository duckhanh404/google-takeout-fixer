import subprocess
import json
import unicodedata
from pathlib import Path
from datetime import datetime
import re
from typing import Optional

# ======================== Read ExifTool Class ========================
class ExifToolRead:
    def __init__(self):
        self.process = subprocess.Popen(
            ["exiftool", "-stay_open", "True", "-@", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )

    def execute(self, args: list[str]) -> list[dict]:
        cmd = "\n".join(args + ["-execute\n"])
        self.process.stdin.write(cmd.encode("utf-8"))
        self.process.stdin.flush()

        output = b""
        while True:
            line = self.process.stdout.readline()
            if line == b"{ready}\n":
                break
            output += line

        if not output:
            return []

        return json.loads(output.decode("utf-8", errors="replace"))

    def extract_time_from_file(self, path: Path | str) -> Optional[datetime]:
        """
        Đọc metadata thời gian từ file media bằng ExifTool

        :param path: đường dẫn file media
        :return: datetime hoặc None
        """
        path_str = unicodedata.normalize("NFC", str(path))

        try:
            result = self.execute([
                "-j",
                "-charset", "filename=utf8",
                "-DateTimeOriginal",
                "-CreateDate",
                "-MediaCreateDate",
                "-ModifyDate",
                "-FileModifyDate",
                path_str
            ])
            if not result:
                return None

            data = result[0]
        except Exception:
            return None

        # Thứ tự ưu tiên
        for key in (
            "DateTimeOriginal",
            "CreateDate",
            "MediaCreateDate",
            "ModifyDate",
            "FileModifyDate",
        ):
            dt_str = data.get(key)
            if dt_str:
                break
        else:
            return None

        formats = (
            "%Y:%m:%d %H:%M:%S",
            "%Y:%m:%d %H:%M:%S%z",
            "%Y:%m:%d %H:%M:%S.%f",
            "%Y:%m:%d %H:%M:%S.%f%z",
        )

        for fmt in formats:
            try:
                return datetime.strptime(dt_str, fmt)
            except ValueError:
                continue

        return None

    def close(self):
        if self.process:
            self.process.stdin.write(b"-stay_open\nFalse\n")
            self.process.stdin.flush()
            self.process.wait()


# ========================= Write ExifTool Class ========================
class ExifToolWrite:
    def __init__(self):
        self.process = subprocess.Popen(
            ["exiftool", "-stay_open", "True", "-overwrite_original", "-@", "-"],
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
        # self.process.stdin.flush()

    def close(self):
        if self.process:
            self.process.stdin.write("-stay_open\nFalse\n")
            self.process.stdin.flush()
            self.process.stdin.close()
            self.process.wait()

# ========================= Functions =========================
def get_all_json(folder_path:Path|str)->set[str]:
    """
    Lấy tất cả file json trong thư mục
    - đầu vào là Path hoặc string đường dẫn đến thư mục
    - trả về là set tên file json chuẩn hóa
    """
    folder_path = Path(folder_path)
    if not folder_path.is_dir():
        raise ValueError("Đường dẫn không phải thư mục hợp lệ!")

    return {
        unicodedata.normalize("NFC", filename.name)
        for filename in folder_path.iterdir()
        if filename.is_file() and filename.suffix.lower() == ".json"
    }
    # return {
    #     filename.name
    #     for filename in folder_path.iterdir()
    #     if filename.is_file() and filename.suffix.lower() == ".json"
    # }

def get_all_media(folder_path:Path|str)->set[str]:
    """
    lấy tất cả file media (không phải json) trong thư mục
    - đầu vào là Path hoặc string đường dẫn đến thư mục
    - trả về là set tên file media chuẩn hóa
    """
    folder_path = Path(folder_path)
    if not folder_path.is_dir():
        raise ValueError("Đường dẫn không hợp lệ!")

    return {
        unicodedata.normalize("NFC", file.name)
        for file in folder_path.iterdir()
        if file.is_file() and file.suffix.lower() != ".json"
    }
    # return {
    #     file.name
    #     for file in folder_path.iterdir()
    #     if file.is_file() and file.suffix.lower() != ".json"
    # }

def extract_title(json_path:Path|str)->str:
    """
    trích xuất title từ file json
    - đầu vào là Path hoặc string đường dẫn đến file json
    - trả về là string chuẩn hóa NFC
    """
    json_path = Path(json_path)  # đảm bảo luôn là Path
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    title = data.get("title", None)
    # trả về string đã chuẩn hóa NFC
    return unicodedata.normalize("NFC",title)

def is_that_cloned(file_name: str) -> str:
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

def process_media(exif:ExifToolWrite, json_path: Path | str, media_path: Path | str) -> None:
    """
    Ghi đè metadata thời gian vào file media dựa trên file json
    - đầu vào:
    :param exif: exiftool write instance
    :type exif: ExifToolWrite
    :param json_path: Description
    :type json_path: Path | str
    :param media_path: Description
    :type media_path: Path | str
    """
    json_path = Path(json_path)
    dt = extract_time_from_json(json_path)
    # write_metadata_with_exiftool(media_path, dt)
    exif.write_datetime(media_path, dt)

def extract_time_from_json(json_path:Path|str)->str:
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




if __name__ == "__main__":
    hello = ExifToolRead()
    ts = hello.extract_time_from_file("/Users/hannada/Downloads/2019/IMG_2096(1).HEIC")
    print(ts)
    # 1551433902 laf timestamp cua ngay 2019/03/01 10:11:42
    hello2 = ExifToolWrite()
    ts2 = hello2.write_datetime("/Users/hannada/Downloads/2019/IMG_2096(1).HEIC", "2023:03:01 10:11:42")
    print(ts)