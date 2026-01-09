from pathlib import Path
from datetime import datetime
from metadata import (
    ExifToolRead,
    ExifToolWrite,
    get_all_json,
    get_all_media,
    move_files_to_error,
    get_all_subfolders,
    normalize_folder_names,
)
from json_index import build_json_index, find_by_prefix

# ================= CONFIG =================
# English: Set your root folder here. (etc: /Users/Username/Downloads/MyPhotos)
# Tiếng Việt: Điền thư mục của bạn vào đây. (VD: /Users/Username/Downloads/MyPhotos)
root_folder = Path('/Path/To/Your/RootFolder') 

# ================= START ==================

new_root_folder = normalize_folder_names(root_folder)
folders = get_all_subfolders(new_root_folder)
begin_time = datetime.now()

for ROOT in folders:
    print("========================================")
    print(f"\n📁 Processing folder: {ROOT}")
    print(f"JSON: {len(all_json)} | MEDIA: {len(all_media)}")
    t0 = datetime.now()
    all_json = get_all_json(ROOT)
    all_media = get_all_media(ROOT)
    print("🔹 Building JSON index...")
    json_by_title, json_by_prefix = build_json_index(ROOT, all_json)

    processed_media = set()
    processed_json = set()

    exif_write = ExifToolWrite()

    # ================= PHASE 1 =================
    print(f"🔹 Phase 1: Find media files that contain JSON (Exact match) - {len(all_media)} media files")
    for title, meta in json_by_title.items():
        if title in all_media:
            exif_write.write_datetime(ROOT / title, meta.timestamp)
            processed_media.add(title)
            processed_json.add(meta.json_name)

    # ================= PHASE 2 =================
    print("🔹 Phase 2: Processing media files that already have timestamps.")
    exif_read = ExifToolRead()
    for media in all_media - processed_media:
        ts = exif_read.extract_time_from_file(ROOT / media)
        if ts:
            exif_write.write_datetime(
                ROOT / media,
                ts.strftime("%Y:%m:%d %H:%M:%S")
            )
            processed_media.add(media)
    exif_read.close()

    # ================= PHASE 3 =================
    print(f"🔹 Phase 3: Handling files without timestamps and JSON")
    for media in all_media - processed_media:
        meta = find_by_prefix(media, json_by_prefix)
        if meta:
            exif_write.write_datetime(ROOT / media, meta.timestamp)
            processed_media.add(media)
            processed_json.add(meta.json_name)

    # ================= DONE ===================
    exif_write.close()
    error_media = all_media - processed_media
    if len(error_media) > 0:
        print(f"⚠️  Moving {len(error_media)} unprocessed media to error folder...")
        move_files_to_error(new_root_folder, ROOT, error_media)
    t1 = datetime.now()
    print(f"✅ DONE for folder: {ROOT}|{len(processed_media)}/{len(all_media)}")
    print(f"Success rate: {len(processed_media)}/{len(all_media)} - Time taken: {t1 - t0}")
end_time = datetime.now()
print(f"✅ ALL DONE")
print(f"Time taken: {end_time - begin_time}")