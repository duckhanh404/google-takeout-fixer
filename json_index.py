from pathlib import Path
import json
import unicodedata
from dataclasses import dataclass
from metadata import extract_time_from_json

@dataclass
class JsonMeta:
    json_name: str
    title: str
    base: str
    ext: str
    timestamp: str

def build_json_index(folder: Path, json_files: set[str]):
    by_title: dict[str, JsonMeta] = {}
    by_prefix: dict[str, list[JsonMeta]] = {}

    for jf in json_files:
        jp = folder / jf
        with jp.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # -----------------------------------------
        # Skip non-media JSON (album / memory)
        # -----------------------------------------
        try:
            ts = extract_time_from_json(jp)
        except ValueError:
            continue

        raw_title = data.get("title", "")
        if not isinstance(raw_title, str):
            continue  # media JSON luôn là str

        title = unicodedata.normalize("NFC", raw_title)

        base = Path(title).stem
        ext = Path(title).suffix.lower()

        meta = JsonMeta(jf, title, base, ext, ts)
        by_title[title] = meta

        for i in range(1, len(base) + 1):
            prefix = base[:i]
            by_prefix.setdefault(prefix, []).append(meta)

    return by_title, by_prefix


def find_by_prefix(media_name: str, by_prefix: dict) -> JsonMeta | None:
    base = Path(media_name).stem
    ext = Path(media_name).suffix.lower()

    for i in range(len(base), 0, -1):
        prefix = base[:i]
        for meta in by_prefix.get(prefix, []):
            if meta.ext == ext:
                return meta
    return None
