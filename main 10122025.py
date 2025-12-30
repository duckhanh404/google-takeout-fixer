from jsonWork import *
from errorHandler import *
from metadatafix import *
from move import *
from test import normalize_existing_path
from datetime import datetime

beginning_time = datetime.now()

# test lỗi đường dẫn khi tìm timestamp trong file media

raw_path = r"E:\Takeout\Google Photos\Anh tu nam 2019"
path = normalize_existing_path(raw_path)
working_path = Path(path)
all_json = get_all_json(working_path)
all_media = get_all_media(working_path)
print(f"Total JSON files:, {len(all_json)}")
print(f"Total media files:, {len(all_media)}")

error_json = []
error_media = []
processed_media = []
processed_json = []

print('-----------------------------------')    
print("Matching JSON files with media files...")

for index, json in enumerate(all_json):
    suffix = is_that_cloned(json)
    print(f'Processing: {index}/{len(all_json)}')
    # lọc nếu file json là bản sao
    if suffix == "original":
        # trường hợp title trong file json có xuất hiện trong all_media
        title = extract_title_not(working_path/json)
        if title in all_media:
            processed_json.append(json)
            processed_media.append(title)
        elif unicodedata.normalize("NFC", title) in all_media: # kiểm tra thêm trường hợp unicode
            processed_json.append(json)
            processed_media.append(unicodedata.normalize("NFC", title))



error_media = [x for x in all_media if x not in processed_media]
error_json = [x for x in all_json if x not in processed_json]

for index, media in enumerate( error_media):
    timestamp = get_media_create_timestamp(working_path/media)
    # print(f'Processing media: {media}, timestamp: {timestamp}')
    print(f'{index}/{len(error_media)}')
    if timestamp is None:
        print(f'No timestamp found for media: {media}')
        continue
    else:
        # # Cần bật lại khi chạy thực tế
        # process_media_lite(timestamp=timestamp, media_path=working_path/media)
        processed_media.append(media)
error_media = [x for x in all_media if x not in processed_media]
error_json = [x for x in all_json if x not in processed_json]
print(f'-----------------------------------')
print(f'Media count: {len(processed_media)}+{len(error_media)}={len(processed_media)+len(error_media)} vs {len(all_media)}')
print(f'JSON count: {len(processed_json)}+{len(error_json)}={len(processed_json)+len(error_json)} vs {len(all_json)}')
print(f'processed json: {len(processed_json)}')
print(f'error json: {len(error_json)}')
print(f'processed media: {len(processed_media)}')
print(f'error media: {len(error_media)}')
end_time =  datetime.now()
print(f'Total time taken: {end_time - beginning_time}')
# print("------------------------------------")
# for item in error_media:
#     print(item)
lists_to_excel(output_path="main 10122025.xlsx", all_media=all_media,all_json=all_json,processed_media=processed_media,processed_json=processed_json,error_json=error_json, error_media=error_media)
