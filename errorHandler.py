# from pathlib import Path
from jsonWork import *
from metadatafix import *
from move import *
import re
import os


# ----------------------------------------
# Hàm loại bỏ ký tự cấm (Windows / macOS / Linux)
def make_filename_safe(filename: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', '', filename)


# ----------------------------------------
# 1️⃣ Xử lý JSON → tìm media
def error_handler_1(folder_path:Path|str)->None:
    """
    Xử lý lỗi bên trong thư mục error
    Đầu vào là đường dẫn đến thư cha mục chứa thư mục error
    function xử lý 
    """
    folder = Path(folder_path)/ "error"
    json_list = get_all_json(folder)
    media_list = get_all_media(folder)
    #xử lý lỗi tên trong json khác với media do thừa ký tự
    for json_file in json_list:
        json_path = folder / json_file
        original_name = extract_title(json_path)
        name, ext = os.path.splitext(original_name)
        for i in range(len(name), 0, -1):
            guess_1 = f"{name[:i]}{ext}"         # tên gốc cắt dần
            guess_2 = make_filename_safe(guess_1)
            if guess_1 in media_list:
                media_path = folder / guess_1
                process_media(json_path,media_path)
                move_back(str(json_path))
                move_back(str(media_path))
                break

            if guess_2 in media_list:
                media_path = folder / guess_2
                process_media(json_path,media_path)
                move_back(str(json_path))
                move_back(str(media_path))
                break


# ----------------------------------------
# 2️⃣ Xử lý media → tìm JSON
# def error_handler_2(folder_path):
    # folder = Path(folder_path)
    # json_list = get_all_json(folder)
    # media_list = get_all_media(folder)
    # # xử lý lỗi tên trong json khác với media do encode
    # for index, json_file in enumerate(json_list):
    #     json_path = folder_path / json_file
    #     time_and_title = extract_title_time(json_path)
    #     media_filename = unicodedata.normalize("NFC",time_and_title["title"])
    #     print(media_filename)
    #     print(type(media_filename))
    #     media_path = folder_path / media_filename
    #     process_media(json_path, media_path)
    #     move_back(str(json_path))
    #     move_back(str(media_path))
    # # xóa bớt ký tự cấm khỏi tên media để dò tìm JSON
    # for media in media_list:
    #     name, ext = os.path.splitext(media)

    #     for i in range(len(name), 0, -1):
    #         guess_json = f"{name[:i]}.json"

    #         if guess_json in json_list:
    #             json_path = folder / guess_json
    #             media_path = folder / media

    #             time_and_title = extract_title_time(str(json_path))

    #             process_media_lite(int(time_and_title["time"]), str(media_path))

    #             move_back(str(json_path))
    #             move_back(str(media_path))
    #             break


# ----------------------------------------
if __name__ == "__main__":
    # ==========================
    # 4️⃣ Xử lý thư mục lỗi
    # ==========================
    path = Path(r"/Users/hannada/Downloads/test")
    error_handler_1(path)