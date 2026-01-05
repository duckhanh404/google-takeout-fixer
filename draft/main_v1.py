from metadatafix import *
from jsonWork import *
from move import *
import sys
import time
from pathlib import Path
from draft.errorHandler import error_handler_1

start_time = time.time()

# SỬA ĐƯỜNG DẪN: luôn dùng Path
folder_path = Path(r"/Users/hannada/Downloads/test").expanduser().resolve()

# ---------------------------
# Lấy danh sách JSON + Media
# ---------------------------
json_list = get_all_json(folder_path)
media_list = get_all_media(folder_path)

valid_media_files = []

# ---------------------------------------
# 1. Xử lý file JSON – kiểm tra file media
# ---------------------------------------
for json_file in json_list:
    json_path = folder_path / json_file
    # title = extract_title(json_path)
    title_error = extract_title_not(json_path)
    # if title not in media_list:
    #     # move_to_error(json_path)
    #     print(f"❌ Không tìm thấy tittle {title} trong media list")
    # else:
    #     # valid_media_files.append(title)
    #     print(f"✅ Tìm thấy tittle {title} trong media list")
    if title_error not in media_list:
        move_to_error(json_path)
        # print(f"❌ Không tìm thấy tittle_error {title_error} trong media list")
    else:
        valid_media_files.append(title_error)
        # print(f"✅ Tìm thấy tittle_error {title_error} trong media list")

# ---------------------------------------------------------
# 2. Những file media không nằm trong JSON → đưa vào error
# ---------------------------------------------------------
error_media = set(media_list) - set(valid_media_files)

for media_file in error_media:
    move_to_error(folder_path / media_file)

# -----------------------------
# Load lại dữ liệu sau khi clean
# -----------------------------
json_list = get_all_json(folder_path)
media_list = get_all_media(folder_path)

# --------------------------------------
# 3. Xử lý metadata cho từng file JSON
# --------------------------------------
for index, json_file in enumerate(json_list):
    json_path = folder_path / json_file

    media_filename = extract_title(json_path)
    media_path = folder_path / media_filename

    process_media(json_path, media_path)

    sys.stdout.write(f"\rProgress: {index + 1}/{len(json_list)}")
    sys.stdout.flush()

print(f"\nTổng cộng có {len(json_list)} file JSON.")
error_handler_1(folder_path)


end_time = time.time()
print(f"Thời gian chạy: {end_time - start_time:.2f} giây")
