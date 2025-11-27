import unicodedata
import platform
from pathlib import Path


class PathManager:
    """
    Module xử lý Unicode path đa nền tảng:
    - Windows: dùng NFC (Windows/Ntfs không hỗ trợ NFD)
    - macOS: normalize NFD (APFS/HFS+ lưu theo decomposed)
    - Linux: vẫn dùng NFC
    """

    @staticmethod
    def normalize(path: str | Path) -> Path:
        """
        Normalize đường dẫn theo OS hiện tại.
        """

        if isinstance(path, Path):
            path = str(path)

        system = platform.system()

        # --- macOS ---
        # Filesystem lưu dạng decomposed (NFD)
        if system == "Darwin":
            norm = "NFD"

        # --- Windows ---
        # Luôn dùng NFC, Windows không hỗ trợ NFD
        elif system == "Windows":
            norm = "NFC"

        # --- Linux ---
        else:
            norm = "NFC"

        normalized = unicodedata.normalize(norm, path)
        return Path(normalized)

    @staticmethod
    def exists(path: str | Path) -> bool:
        """
        Kiểm tra tồn tại → luôn normalize đúng OS trước.
        """
        return PathManager.normalize(path).exists()

    @staticmethod
    def list_dir(path: str | Path) -> list[Path]:
        """
        Trả về danh sách file trong folder (tự normalize).
        """
        p = PathManager.normalize(path)
        return [PathManager.normalize(x) for x in p.iterdir()]

    @staticmethod
    def resolve(path: str | Path) -> Path:
        """
        Trả về đường dẫn tuyệt đối đã normalize.
        """
        return PathManager.normalize(path).resolve()

    @staticmethod
    def join(*parts) -> Path:
        """
        Gộp path → normalize.
        """
        p = Path(parts[0])
        for part in parts[1:]:
            p = p / str(part)
        return PathManager.normalize(p)

    @staticmethod
    def safe_compare(a: str | Path, b: str | Path) -> bool:
        """
        So sánh tên file nhưng KHÔNG bị lỗi NFC/NFD.
        """
        return str(PathManager.normalize(a)) == str(PathManager.normalize(b))
if __name__ == "__main__":
    nfc = "Ảnh.jpg"
    nfd = "Ảnh.jpg"
    if nfc == nfd:
        print("Equal")
    else:
        print("Not equal")

    