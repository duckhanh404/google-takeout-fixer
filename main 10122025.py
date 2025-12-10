from jsonWork import *
from errorHandler import *
from metadatafix import *
from move import *
from test import normalize_existing_path


# test lỗi đường dẫn khi tìm timestamp trong file media

raw_path = r'/Users/hannada/Downloads/Ảnh từ năm 2018'
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

for media in all_media:
    timestamp = get_media_create_timestamp(working_path/media)
    if timestamp is None:
        print(f'No timestamp found for media: {media}')
        continue
    else:
        processed_media.append(media)
error_media = [x for x in all_media if x not in processed_media]
print(f'-----------------------------------')
print(f'Media count: {len(processed_media)}+{len(error_media)}={len(processed_media)+len(error_media)} vs {len(all_media)}')
print(f'JSON count: {len(processed_json)}+{len(error_json)}={len(processed_json)+len(error_json)} vs {len(all_json)}')
print(f'processed json: {len(processed_json)}')
print(f'error json: {len(error_json)}')
print(f'processed media: {len(processed_media)}')
print(f'error media: {len(error_media)}')
print("------------------------------------")
for item in error_media:
    print(item)
