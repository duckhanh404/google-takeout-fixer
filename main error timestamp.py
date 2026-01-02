from jsonWork import *
from errorHandler import *
from metadatafix import *
from move import *
from datetime import datetime
from decreaseName import find_matching_json

# test lỗi đường dẫn khi tìm timestamp trong file media
beginning_time = datetime.now()
path = r"E:\Takeout\Google Photos\Anh tu nam 2019"
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
print("Xử lý các trường hợp có file json")

for index, json in enumerate(all_json):
    suffix = is_that_cloned(json)
    print(f'Processing: {index}/{len(all_json)}')
    if suffix != "original":
        continue
    elif suffix == "original":
        # trường hợp title trong file json có xuất hiện trong all_media
        title = extract_title_not(working_path/json)
        if title in all_media:
            processed_json.append(json)
            processed_media.append(title)
        elif unicodedata.normalize("NFC", title) in all_media: # kiểm tra thêm trường hợp unicode
            processed_json.append(json)
            processed_media.append(unicodedata.normalize("NFC", title))


# tạo danh sách lỗi (file có trong all nhưng không có trong processed)
error_json = [x for x in all_json if x not in processed_json]
error_media = [x for x in all_media if x not in processed_media]

# print(f'Media count: {len(processed_media)}+{len(error_media)}={len(processed_media)+len(error_media)} vs {len(all_media)}')
# print(f'JSON count: {len(processed_json)}+{len(error_json)}={len(processed_json)+len(error_json)} vs {len(all_json)}')
# print(f'processed json: {len(processed_json)}')
# print(f'error json: {len(error_json)}')
# print(f'processed media: {len(processed_media)}')
# print(f'error media: {len(error_media)}')



# media_with_timestamp = []
print('-----------------------------------')
print("Xử lý trường hợp media có sẵn timestamp")
for media in error_media:
    timestamp = get_media_create_timestamp(working_path/media)
    # print(f'Processing media: {media}, timestamp: {timestamp}')
    if timestamp is None:
        print(f'No timestamp found for media: {media}')
        continue
    else:
        # # Cần bật lại khi chạy thực tế
        # process_media_lite(timestamp=timestamp, media_path=working_path/media)
        processed_media.append(media)
        # media_with_timestamp.append(media)

error_json = [x for x in all_json if x not in processed_json]
error_media = [x for x in all_media if x not in processed_media] 

# print(f'Media count: {len(processed_media)}+{len(error_media)}={len(processed_media)+len(error_media)} vs {len(all_media)}')
# print(f'JSON count: {len(processed_json)}+{len(error_json)}={len(processed_json)+len(error_json)} vs {len(all_json)}')
# print(f'processed json: {len(processed_json)}')
# print(f'error json: {len(error_json)}')
# print(f'processed media: {len(processed_media)}')
# print(f'error media: {len(error_media)}')

print('xử lý các trường hợp lỗi còn lại')
for media in error_media:
        matching_json = find_matching_json(path, media, all_json)
        if matching_json:
            print(f"Media: {media} -> Matching JSON: {matching_json}")
            success_count += 1
            process_media.append(media)
            # success_media.append(matching_json)
            # matched_json.append(matching_json)
        # else:
            # print(f"Media: {media} -> No matching JSON found.")



end_time =  datetime.now()
print(f'Total time taken: {end_time - beginning_time}')


lists_to_excel(output_path="main error timestamp.xlsx", all_media=all_media, all_json=all_json, processed_media=processed_media, processed_json=processed_json, error_media=error_media, error_json=error_json)
# copy_files_from_lists(source_dir=working_path, dest_dir=Path(r"C:\Users\DucKhanhPC\Desktop\last error"), file_lists=[error_media,all_json])