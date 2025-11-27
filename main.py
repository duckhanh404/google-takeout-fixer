from jsonWork import *
from errorHandler import *
from metadatafix import *
from move import *




path = r"E:\Takeout\Google Photos\Ảnh từ năm 2019"
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

for json in all_json:
    suffix = is_that_cloned(json)
    if suffix != "original":
        # trường hợp đặc biệt: file json là bản sao (có đuôi (số))
        title = extract_title_not(working_path/json)
        name, ext = os.path.splitext(title)
        guess_title = f"{name}{suffix}{ext}"
        if guess_title in all_media:
            processed_json.append(json)
            processed_media.append(guess_title)        
    else:
        title = extract_title_not(working_path/json)
        if title in all_media:
            processed_json.append(json)
            processed_media.append(title)

error_json = [x for x in all_json if x not in processed_json]
error_media = [x for x in all_media if x not in processed_media]


print(f'Media count: {len(processed_media)}+{len(error_media)}={len(processed_media)+len(error_media)} vs {len(all_media)}')
print(f'JSON count: {len(processed_json)}+{len(error_json)}={len(processed_json)+len(error_json)} vs {len(all_json)}')
print(f'processed json: {len(processed_json)}')
print(f'error json: {len(error_json)}')
print(f'processed media: {len(processed_media)}')
print(f'error media: {len(error_media)}')

# lists_to_excel(output_path="check_errors.xlsx", all_media=all_media, all_json=all_json, processed_media=processed_media, processed_json=processed_json, error_media=error_media, error_json=error_json )

# if __name__ == "__main__":
#     lists_to_excel(
#         processed_media,
#         error_media,
#         all_media,
#         output_path="matched_files.xlsx"
#     )