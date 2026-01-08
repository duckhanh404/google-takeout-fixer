# main_v3.4.py
# sửa exiftool -> tạo 2 class đọc và ghi metadata riêng biệt
# tối ưu xuống 0,43s cho folder 2018 (996 files)
# tối ưu xuống 15s cho folder 2019 ~20000 files - thời gian trước là ~4 phút

from datetime import datetime
from decreaseName import find_matching_json
from pathlib import Path
from metadata import *



# test lỗi đường dẫn khi tìm timestamp trong file media
beginning_time = datetime.now()
last_time = beginning_time
path = r'/Users/hannada/Downloads/2019'
working_path = Path(path)
all_json = get_all_json(working_path)
all_media = get_all_media(working_path)

title_json_dict = {
    json: extract_title(f'{path}/{json}') for json in all_json
}

error_json = set()
error_media = set()
processed_media = set()
processed_json = set()

print('-----------------------------------')    
print("1. Xử lý các trường hợp có file json - số lượng media:", len(all_media))
# for json in all_json:
exifWrite = ExifToolWrite()
for json,title in title_json_dict.items():
    suffix = is_that_cloned(json)
    if suffix == "original":
        if title in all_media:
            # print(f'Processing: {index}/{len(all_json)} - OK')
            processed_json.add(json)
            processed_media.add(title)
            json_path = Path(path,json)
            media_path = Path(path , title)
            process_media(exif=exifWrite, json_path=json_path, media_path=media_path)
        else:
            continue

error_json = all_json - processed_json
error_media = all_media - processed_media

end_time =  datetime.now()
print(f'Time taken: {end_time - last_time}')
last_time = end_time

print('-----------------------------------')
print("2. Xử lý trường hợp media có sẵn timestamp - số lượng media lỗi:", len(error_media))
exifRead = ExifToolRead()
for media in error_media:
    timestamp = exifRead.extract_time_from_file(working_path/media)
    if timestamp is None:
        continue
    else:
        media_path = Path(path , media)
        exifWrite.write_datetime(media_path, timestamp)
        processed_media.add(media)
exifRead.close()
error_json = all_json - processed_json
error_media = all_media - processed_media
end_time =  datetime.now()
print(f'Time taken: {end_time - last_time}')
last_time = end_time

print('-----------------------------------')
print('3. Xử lý các trường hợp lỗi còn lại bằng cách giảm dần tên media để tìm json khớp - số lượng media lỗi:', len(error_media))
for media in error_media:
        matching_json = find_matching_json(media_filename=media, json_dict=title_json_dict)
        if matching_json:
            json_path = Path(path , matching_json)
            media_path = Path(path , media)
            process_media(exif=exifWrite, json_path=json_path, media_path=media_path)
            processed_media.add(media)
            processed_json.add(matching_json)

error_json = all_json - processed_json
error_media = all_media - processed_media

print('Xử lý xong.')
end_time =  datetime.now()
print(f'Time taken: {end_time - last_time}')
print('Đang đóng exifWrite...')
exifWrite.close()
end_time =  datetime.now()
print(f'Time taken: {end_time - last_time}')
print('-----------------------------------')
print(f'Total time taken: {end_time - beginning_time}')


