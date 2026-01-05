# main_v3.2.py
# Sử dụng set thay thế cho list để tăng tốc độ tìm kiếm phần tử
# loại bỏ print 
# thời gian chạy còn 58 giây
from jsonWork import get_all_media, get_all_json, is_that_cloned, extract_title_not, unicodedata, get_media_create_timestamp
from metadatafix import process_media, convert_timestamp, write_metadata_with_exiftool
from datetime import datetime
from decreaseName import find_matching_json
from pathlib import Path

# test lỗi đường dẫn khi tìm timestamp trong file media
beginning_time = datetime.now()
path = r'/Users/hannada/Downloads/2018'
working_path = Path(path)
all_json = get_all_json(working_path)
all_media = get_all_media(working_path)
# print(f"Total JSON files:, {len(all_json)}")
# print(f"Total media files:, {len(all_media)}")

error_json = set()
error_media = set()
processed_media = set()
processed_json = set()

print('-----------------------------------')    
print("Xử lý các trường hợp có file json")
for json in all_json:
    suffix = is_that_cloned(json)
    if suffix == "original":
        # trường hợp title trong file json có xuất hiện trong all_media
        title = extract_title_not(working_path/json)
        if title in all_media:
            # print(f'Processing: {index}/{len(all_json)} - OK')
            processed_json.add(json)
            processed_media.add(title)
            json_path = Path(path,json)
            media_path = Path(path , title)
            process_media(json_path, media_path)
        elif unicodedata.normalize("NFC", title) in all_media: # kiểm tra thêm trường hợp unicode
            # print(f'Processing: {index}/{len(all_json)} - OK - NFC')
            processed_json.add(json)
            processed_media.add(unicodedata.normalize("NFC", title))
            json_path = Path(path , json)
            media_path = Path(path , unicodedata.normalize("NFC", title))
            process_media(json_path, media_path)
        else:
            # print(f'Processing: {index}/{len(all_json)} - Not Found')
            continue


# tạo danh sách lỗi (file có trong all nhưng không có trong processed)
error_json = all_json - processed_json
error_media = all_media - processed_media
# print(f'error json:{len(error_json)}')
# print(f'error media: {len(error_media)}')


# media_with_timestamp = []
print('-----------------------------------')
print("Xử lý trường hợp media có sẵn timestamp")
for media in error_media:
    timestamp = get_media_create_timestamp(working_path/media)
    if timestamp is None:
        # print(f'Processing Error: {index}/{len(error_media)} - None')
        continue
    else:
        media_path = Path(path , media)
        dt = convert_timestamp(timestamp)
        # print(f'Processing Error: {index}/{len(error_media)} - {dt}')
        write_metadata_with_exiftool(media_path, dt)
        processed_media.add(media)

error_json = all_json - processed_json
error_media = all_media - processed_media
# print(f'error json:{len(error_json)}')
# print(f'error media: {len(error_media)}')

print('-----------------------------------')
print('xử lý các trường hợp lỗi còn lại bằng cách giảm dần tên media để tìm json khớp')
for media in error_media:
        matching_json = find_matching_json(path, media, all_json)
        if matching_json:
            json_path = Path(path , matching_json)
            media_path = Path(path , media)
            process_media(json_path, media_path)
            processed_media.add(media)
            processed_json.add(matching_json)
        # print(f'Tìm json cho media: {index}/{len(error_media)} - {matching_json}')


error_json = all_json - processed_json
error_media = all_media - processed_media
# print(f'error json:{len(error_json)}')
# print(f'error media: {len(error_media)}')

# print(f'Media count: {len(processed_media)}+{len(error_media)}={len(processed_media)+len(error_media)} vs {len(all_media)}')
# print(f'JSON count: {len(processed_json)}+{len(error_json)}={len(processed_json)+len(error_json)} vs {len(all_json)}')
# print(f'processed json: {len(processed_json)}')
# print(f'error json: {len(error_json)}')
# print(f'processed media: {len(processed_media)}')
# print(f'error media: {len(error_media)}')

end_time =  datetime.now()
print(f'Total time taken: {end_time - beginning_time}')
# print(error_media)
# print(error_json)
