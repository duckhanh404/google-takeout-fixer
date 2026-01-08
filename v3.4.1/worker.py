from pathlib import Path
from metadata import ExifToolRead
from json_index import find_by_prefix

def worker_task(args):
    """
    args = (
        media_name,
        root_path,
        json_by_prefix,
        processed_media
    )
    """
    media_name, root, json_by_prefix = args
    media_path = root / media_name

    # 1️⃣ try EXIF
    exif = ExifToolRead()
    ts = exif.extract_time_from_file(media_path)
    exif.close()
    if ts:
        return media_name, ts.strftime("%Y:%m:%d %H:%M:%S")

    # 2️⃣ prefix fallback
    meta = find_by_prefix(media_name, json_by_prefix)
    if meta:
        return media_name, meta.timestamp

    return None
