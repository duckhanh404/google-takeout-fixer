from pathlib import Path
import unicodedata

def normalize_existing_path(path: str | Path) -> Path:
    """
    Trả về Path với từng thành phần được
    normalize theo đúng tên có thật trong filesystem.
    """
    p = Path(path)

    parts = []
    current = Path(p.anchor) if p.anchor else Path("")

    for part in p.parts[1:]:
        normalized = unicodedata.normalize("NFC", part)

        # duyệt thư mục thật và tìm tên match (NFC/NFD)
        found = None
        if current.exists():
            for real in current.iterdir():
                if unicodedata.normalize("NFC", real.name) == normalized:
                    found = real.name
                    break

        parts.append(found if found else normalized)
        current = current / (found if found else normalized)

    return Path(*([p.anchor] + parts)) if p.anchor else Path(*parts)