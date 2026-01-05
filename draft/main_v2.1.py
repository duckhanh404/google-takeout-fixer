from metadatafix import *
from jsonWork import *
from move import *
import sys
import time
from pathlib import Path
from draft.errorHandler import error_handler_1

start_time = time.time()

# Thư mục cần xử lý
folder_path = Path(r"C:\Takeout\Google Photos\2019").resolve()

# ------------------------------------------------------
# 1. Load danh sách JSON + Media (1 lần duy nhất)
# ------------------------------------------------------
json_list = get_all_json(folder_path)
media_list = get_all_media(folder_path)

# Tối ưu bằng set
media_set = set(media_list)
valid_media = set()

# ------------------------------------------------------
# 2. Kiểm tra sự tồn tại của media tương ứng với JSON
# ------------------------------------------------------
for json_file in json_list:
    json_path = folder_path / json_file

    title_error = extract_title_not(json_path)

    if title_error in media_set:
        valid_media.add(title_error)
    else:
        move_to_error(json_path)

# ------------------------------------------------------
# 3. Media không có JSON → đưa vào error
# ------------------------------------------------------
error_media = media_set - valid_media
for media_file in error_media:
    move_to_error(folder_path / media_file)

# ------------------------------------------------------
# 4. Xử lý metadata cho từng JSON hợp lệ
# ------------------------------------------------------
# Load lại JSON sau khi chuyển bớt file đi
json_list = get_all_json(folder_path)

total = len(json_list)

for index, json_file in enumerate(json_list):
    json_path = folder_path / json_file
    media_filename = extract_title(json_path)
    media_path = folder_path / media_filename

    process_media(json_path, media_path)

    # In tiến độ
    sys.stdout.write(f"\rProgress: {index + 1}/{total}")
    sys.stdout.flush()

print(f"\nTổng cộng có {total} file JSON.")

# ------------------------------------------------------
# 5. Gọi error handler lần cuối
# ------------------------------------------------------
error_handler_1(folder_path)

end_time = time.time()
print(f"⏱ Thời gian chạy: {end_time - start_time:.2f} giây")
