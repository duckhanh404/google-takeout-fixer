from pathlib import Path
from datetime import datetime
from multiprocessing import Pool, cpu_count, freeze_support
from metadata import (
    ExifToolWrite,
    get_all_json,
    get_all_media,
)
from json_index import build_json_index
from worker import worker_task


def main():
    ROOT = Path("/Users/hannada/Downloads/2019")
    WORKERS = min(8, max(4, cpu_count() - 1))

    t0 = datetime.now()

    all_json = get_all_json(ROOT)
    all_media = get_all_media(ROOT)

    print(f"JSON: {len(all_json)} | MEDIA: {len(all_media)}")

    print("🔹 Building JSON index...")
    json_by_title, json_by_prefix = build_json_index(ROOT, all_json)

    processed_media = set()

    exif_write = ExifToolWrite()

    # ================= PHASE 1 =================
    print("🔹 Phase 1: exact match")
    for title, meta in json_by_title.items():
        if title in all_media:
            exif_write.write_datetime(ROOT / title, meta.timestamp)
            processed_media.add(title)

    remaining_media = list(all_media - processed_media)
    print(f"🔹 Phase 2+3 multiprocessing: {len(remaining_media)} files")

    # ================= MULTIPROCESS =================
    tasks = [(m, ROOT, json_by_prefix) for m in remaining_media]

    with Pool(WORKERS) as pool:
        for result in pool.imap_unordered(worker_task, tasks, chunksize=20):
            if not result:
                continue
            media_name, ts = result
            exif_write.write_datetime(ROOT / media_name, ts)
            processed_media.add(media_name)

    exif_write.close()

    t1 = datetime.now()
    print("✅ DONE")
    print(f"Processed: {len(processed_media)}/{len(all_media)}")
    print(f"Time taken: {t1 - t0}")


if __name__ == "__main__":
    freeze_support()  # an toàn cho macOS / Windows
    main()
