from pathlib import Path
from datetime import datetime
from metadata import (
    ExifToolRead,
    ExifToolWrite,
    get_all_json,
    get_all_media,
)
from json_index import build_json_index, find_by_prefix

# ================= CONFIG =================
ROOT = Path("/Users/hannada/Downloads/2019")

# ================= START ==================
t0 = datetime.now()

all_json = get_all_json(ROOT)
all_media = get_all_media(ROOT)

print(f"JSON: {len(all_json)} | MEDIA: {len(all_media)}")

print("🔹 Building JSON index...")
json_by_title, json_by_prefix = build_json_index(ROOT, all_json)

processed_media = set()
processed_json = set()

exif_write = ExifToolWrite()

# ================= PHASE 1 =================
print("🔹 Phase 1: exact title match")
for title, meta in json_by_title.items():
    if title in all_media:
        exif_write.write_datetime(ROOT / title, meta.timestamp)
        processed_media.add(title)
        processed_json.add(meta.json_name)

# ================= PHASE 2 =================
print("🔹 Phase 2: read EXIF timestamp")
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
print("🔹 Phase 3: prefix fallback")
for media in all_media - processed_media:
    meta = find_by_prefix(media, json_by_prefix)
    if meta:
        exif_write.write_datetime(ROOT / media, meta.timestamp)
        processed_media.add(media)
        processed_json.add(meta.json_name)

# ================= DONE ===================
exif_write.close()

t1 = datetime.now()
print("✅ DONE")
print(f"Processed media: {len(processed_media)}/{len(all_media)}")
print(f"Time taken: {t1 - t0}")
