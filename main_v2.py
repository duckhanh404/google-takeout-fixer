import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from metadatafix import *
from jsonWork import *
from move import *
from errorHandler import *



# ----------------------------------------
start_time = time.time()

folder_path = Path(r"/Users/hannada/Downloads/test")

# ==========================
# 1️⃣ Di chuyển file lỗi
# ==========================
json_list = get_all_json(folder_path)
media_list = get_all_media(folder_path)
valid_media_files = []

for json_file in json_list:
    json_path = folder_path / json_file
    try:
        title = extract_title(json_path)
    except Exception as e:
        move_to_error(json_path)
        continue

    if title not in media_list:
        move_to_error(str(json_path))
    else:
        valid_media_files.append(title)

# Media không có JSON → lỗi
error_media = set(media_list) - set(valid_media_files)
for media_file in error_media:
    move_to_error(str(folder_path / media_file))

# Làm mới danh sách sau khi lọc lỗi
json_list = get_all_json(folder_path)
media_list = get_all_media(folder_path)


# ==========================
# 2️⃣ Hàm xử lý từng JSON
# ==========================
def handle_json(json_filename):
    json_path = folder_path / json_filename
    time_and_title = extract_title_time(str(json_path))
    media_path = folder_path / time_and_title['title']
    process_media_lite(int(time_and_title["time"]), str(media_path))
    return json_filename  # để báo progress


# ==========================
# 3️⃣ Xử lý JSON song song
# ==========================
total = len(json_list)
done = 0

with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(handle_json, j): j for j in json_list}

    for future in as_completed(futures):
        done += 1
        sys.stdout.write(f"\rProgress: {done}/{total}")
        sys.stdout.flush()


# # ==========================
# # 4️⃣ Xử lý thư mục lỗi
# # ==========================
error_dir = folder_path / "error"
if error_dir.is_dir() and any(error_dir.iterdir()):
    error_handler_1(folder_path)


# ==========================
# 5️⃣ Kết thúc
# ==========================
print(f"\nTổng cộng có {len(json_list)} file JSON.")
end_time = time.time()
print(f"Thời gian chạy: {end_time - start_time:.2f} giây")
