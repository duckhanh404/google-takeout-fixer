from jsonWork import *
from draft.errorHandler import *
from metadatafix import *
from move import *

path = r"/Users/hannada/Downloads/test"
working_path = Path(path)
all_json = get_all_json(working_path)
all_media = get_all_media(working_path)
error_json = []
error_media = []
processed_media = []
processed_json = []

for json_file in all_json:
    title = extract_title_not(working_path/json_file)
    if title in all_media:
        processed_media.append(title)
        processed_json.append(json_file)
        all_media.remove(title)
    else:
        error_json.append(json_file)

error_media = all_media[:]
all_json.clear()
all_media.clear()
for  media_file in error_media:
    name, ext = os.path.splitext(media_file)
    for i in range(len(name), 0, -1):
        guess_json = f"{name[:i]}.json"         # tên gốc cắt dần
        # guess_2 = make_filename_safe(guess_1)
        if guess_json in error_json:
            processed_json.append(guess_json)
            processed_media.append(media_file)
            break

error_json = [x for x in error_json if x not in processed_json]
error_media = [x for x in error_media if x not in processed_media]

print('-----------------------------------')
print(f"Processed JSON files:, {len(processed_json)}")
print(processed_json)
print(f"Processed media files:, {len(processed_media)}")
print(processed_media)
print('-----------------------------------')
print(f"Error JSON files:, {len(error_json)}")
print(error_json)
print(f"Error media files:, {len(error_media)}")
print(error_media)
print('-----------------------------------')
print(f"All JSON files:, {len(all_json)}")
print(all_json)
print(f"All media files:, {len(all_media)}")
print(all_media)
