from pathlib import Path
import unicodedata
from typing import List, Optional, Any
from pathlib import Path
import json
from metadata import get_all_media, get_all_json






# def find_matching_json(
#     path: str|Path,
#     media_filename: str,
#     json_files: List[str]
# ) -> Optional[str]:
#     """
#     Tìm file json có tên bắt đầu bằng media name (giảm dần từng ký tự).
#     Trả về tên file json nếu tìm thấy, ngược lại trả None.
#     """

#     # Chuẩn hóa Unicode (rất quan trọng với tiếng Việt)
#     media_filename = unicodedata.normalize("NFC", media_filename)
#     json_files = [unicodedata.normalize("NFC", f) for f in json_files]

#     # Bỏ extension media

#     base_name = Path(media_filename).stem
#     media_ext = Path(media_filename).suffix.lower()

#     # Giảm dần từng ký tự trong media name để tìm
#     for i in range(len(base_name), 0, -1):
#         prefix = base_name[:i]
#         for json_file in json_files:
#             # Nằm ở đầu
#             if json_file.startswith(prefix):
#                 try:
#                     json_path = Path(path, json_file)
#                     with open(json_path, "r", encoding="utf-8") as f:
#                         data = json.load(f)
#                 except Exception:
#                     continue
#                 title = data.get("title")
#                 if Path(title).suffix.lower() == media_ext:
#                     return json_file

#     return None

def find_matching_json(
    json_dict : dict[str, Any], # json:title
    media_filename: str,
) -> Optional[str]:
    """
    Tìm file json có tên bắt đầu bằng media name (giảm dần từng ký tự).
    Trả về tên file json nếu tìm thấy, ngược lại trả None.
    Đầu vào là tên 1 media cần tìm json và tên toàn bộ json dưới dạng set
    """
    # Lấy base name của media
    base_name = Path(media_filename).stem
    # Lấy extension của media
    media_ext = Path(media_filename).suffix.lower()

    # Giảm dần từng ký tự trong media name để tìm (đảm bảo có ít nhất 5 ký tự)
    for i in (range(len(base_name)-5), 0, -1):
        prefix = base_name[:i]
        for json_file in json_dict.keys():
            # Nằm ở đầu
            if json_file.startswith(prefix):
                # json:title
                if Path(json_dict[json_file]).suffix.lower() == media_ext:
                    return json_file

    return None


if __name__ == "__main__":
    path = r'/Users/hannada/Desktop/Bản sao last error'
    working_path = Path(path)

    # Bỏ header + lấy cột đầu tiên
    media_files = get_all_media(working_path)
    json_files = get_all_json(working_path)
    success_count = 0
    success_media = []
    # matched_json = []
    for media in media_files:
        matching_json = find_matching_json(path, media, json_files)
        if matching_json:
            print(f"Media: {media} -> Matching JSON: {matching_json}")
            success_count += 1
            success_media.append(media)
            success_media.append(matching_json)
            # matched_json.append(matching_json)
        else:
            print(f"Media: {media} -> No matching JSON found.")
    print(f"Loaded {len(media_files)} media files and {len(json_files)} json files.")
    print(f"Total matched: {success_count} out of {len(media_files)}")
