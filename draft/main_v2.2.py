from metadatafix import *
from jsonWork import *
from move import *
import sys
import time
from pathlib import Path
from draft.errorHandler import error_handler_1
from concurrent.futures import ThreadPoolExecutor, as_completed

start_time = time.time()
folder_path = Path(r"C:\Takeout\Google Photos\2020").resolve()

# ------------------------------------------------------
# Load danh sách JSON + Media
# ------------------------------------------------------
json_list = get_all_json(folder_path)
media_list = get_all_media(folder_path)
media_set = set(media_list)


# ======================================================
# 1) BATCH + MULTITHREAD: kiểm tra JSON → media tồn tại
# ======================================================
def check_json(json_file):
    json_path = folder_path / json_file
    title_err = extract_title_not(json_path)

    if title_err in media_set:
        return ("VALID", title_err)
    else:
        move_to_error(json_path)
        return ("INVALID", None)


valid_media = set()

batch_size = 300
for i in range(0, len(json_list), batch_size):
    batch = json_list[i : i + batch_size]

    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(check_json, jf) for jf in batch]

        for f in as_completed(futures):
            status, title = f.result()
            if status == "VALID":
                valid_media.add(title)


# ------------------------------------------------------
# 2) Media không có JSON → đưa vào error
# ------------------------------------------------------
error_media = media_set - valid_media

def move_media(media_file):
    move_to_error(folder_path / media_file)

with ThreadPoolExecutor(max_workers=12) as executor:
    executor.map(move_media, error_media)


# ======================================================
# 3) BATCH + MULTITHREAD: xử lý metadata
# ======================================================
json_list = get_all_json(folder_path)
total = len(json_list)

def process_single(json_file):
    json_path = folder_path / json_file
    media_filename = extract_title(json_path)
    media_path = folder_path / media_filename
    process_media(json_path, media_path)


for i in range(0, total, batch_size):
    batch = json_list[i : i + batch_size]

    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(process_single, jf) for jf in batch]

        for idx, f in enumerate(as_completed(futures), start=i):
            sys.stdout.write(f"\rProgress: {idx+1}/{total}")
            sys.stdout.flush()


print(f"\nTổng cộng có {total} file JSON.")

error_handler_1(folder_path)

end_time = time.time()
print(f"⏱ Thời gian chạy: {end_time - start_time:.2f} giây")
