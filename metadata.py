import subprocess
import json
import unicodedata
from pathlib import Path
from datetime import datetime
from typing import Optional
import shutil
from typing import List
import re


# ======================== Read ExifTool ========================
class ExifToolRead:
    def __init__(self):
        self.process = subprocess.Popen(
            ["exiftool", "-stay_open", "True", "-@", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )

    def execute(self, args: list[str]) -> list[dict]:
        cmd = "\n".join(args + ["-execute\n"])
        self.process.stdin.write(cmd.encode("utf-8"))
        self.process.stdin.flush()

        output = b""
        while True:
            line = self.process.stdout.readline()
            if line == b"{ready}\n":
                break
            output += line

        return json.loads(output.decode("utf-8", errors="replace")) if output else []

    def extract_time_from_file(self, path: Path | str) -> Optional[datetime]:
        path_str = unicodedata.normalize("NFC", str(path))
        try:
            result = self.execute([
                "-j",
                "-DateTimeOriginal",
                "-CreateDate",
                "-MediaCreateDate",
                "-ModifyDate",
                "-FileModifyDate",
                path_str
            ])
        except Exception:
            return None

        if not result:
            return None

        data = result[0]
        for key in (
            "DateTimeOriginal",
            "CreateDate",
            "MediaCreateDate",
            "ModifyDate",
            "FileModifyDate",
        ):
            if key in data:
                try:
                    return datetime.strptime(data[key], "%Y:%m:%d %H:%M:%S")
                except Exception:
                    pass
        return None

    def close(self):
        self.process.stdin.write(b"-stay_open\nFalse\n")
        self.process.stdin.flush()
        self.process.wait()


# ======================== Write ExifTool ========================
class ExifToolWrite:
    def __init__(self):
        self.process = subprocess.Popen(
            ["exiftool", "-stay_open", "True", "-overwrite_original", "-@", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True
        )
        self.counter = 0

    def write_datetime(self, media_path: Path | str, datetime_str: str):
        self.process.stdin.write(
            f"-FileCreateDate={datetime_str}\n"
            f"-FileModifyDate={datetime_str}\n"
            f"{media_path}\n"
            "-execute\n"
        )
        self.counter += 1
        if self.counter % 50 == 0:
            self.process.stdin.flush()

    def close(self):
        self.process.stdin.write("-stay_open\nFalse\n")
        self.process.stdin.flush()
        self.process.wait()


# ======================== Helpers ========================
def get_all_json(folder: Path) -> set[str]:
    """
    Docstring for get_all_json
    
    :param folder: Description
    :type folder: Path
    :return: Description
    :rtype: set[str]
    """
    return {
        unicodedata.normalize("NFC", f.name)
        for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() == ".json"
    }

def get_all_media(folder: Path) -> set[str]:
    return {
        unicodedata.normalize("NFC", f.name)
        for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() != ".json"
    }

def extract_time_from_json(json_path: Path) -> str:
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if "photoTakenTime" in data:
        ts = int(data["photoTakenTime"]["timestamp"])
    elif "creationTime" in data:
        ts = int(data["creationTime"]["timestamp"])
    else:
        raise ValueError(f"No timestamp: {json_path}")

    return datetime.fromtimestamp(ts).strftime("%Y:%m:%d %H:%M:%S")

def move_files_to_error(
    root_path: Path | str,
    source_path: Path | str,
    filenames: set[str],
    verbose: bool = True
) -> List[Path]:
    """
    Di chuyển danh sách file từ source_path vào root_path/error

    - Tự tạo folder error nếu chưa tồn tại
    - Tránh ghi đè file trùng tên (_dup1, _dup2...)
    - Bỏ qua file không tồn tại
    - Trả về list Path file đã move
    """

    root_path = Path(root_path)
    source_path = Path(source_path)

    error_dir = root_path / "error"
    error_dir.mkdir(parents=True, exist_ok=True)

    moved_files: List[Path] = []

    for name in filenames:
        src = source_path / name

        if not src.exists():
            if verbose:
                print(f"[SKIP] Not found: {src}")
            continue

        dst = error_dir / src.name

        # Tránh overwrite
        if dst.exists():
            counter = 1
            while True:
                new_name = f"{src.stem}_dup{counter}{src.suffix}"
                dst = error_dir / new_name
                if not dst.exists():
                    break
                counter += 1

        shutil.move(src, dst)
        moved_files.append(dst)

    #     if verbose:
    #         print(f"[MOVE] {src} -> {dst}")

    # return print(f"Đã di chuyển {len(moved_files)} file vào {error_dir}")

def get_all_subfolders(
    root_folder: Path | str,
    exclude_error: bool = True
) -> List[Path]:
    """
    Lấy tất cả folder con (đệ quy) trong root_folder

    - Trả về list Path của toàn bộ folder con, cháu...
    - Loại bỏ folder có tên 'error' (mặc định)
    """

    root_folder = Path(root_folder)
    folders: List[Path] = []

    for path in root_folder.rglob("*"):
        if not path.is_dir():
            continue

        if exclude_error and path.name == "error":
            continue

        folders.append(path)
    folders.append(root_folder)
    return folders

def normalize_folder_names(folder_path: str | Path):
    """
    Chuyển tất cả tên thư mục (folder) trong folder_path và folder_path gốc
    từ Unicode sang dạng ASCII "thường" để ExifTool không bị lỗi.
    
    Ví dụ: "Ảnh của tôi" -> "Anh cua toi"
    
    LƯU Ý:
    - Chỉ rename thư mục, không động đến file bên trong.
    """
    folder_path = Path(folder_path)

    # Duyệt folder theo chiều sâu (deepest first) để tránh lỗi rename parent trước child
    for p in sorted(folder_path.rglob('*'), key=lambda x: -len(x.parts)):
        if p.is_dir():
            old_name = p.name
            new_name = unicodedata.normalize('NFD', old_name)
            new_name = new_name.encode('ascii', 'ignore').decode('ascii')
            new_name = re.sub(r'\s+', ' ', new_name).strip()

            if new_name != old_name and new_name:
                new_path = p.parent / new_name
                try:
                    p.rename(new_path)
                    print(f'✅ Renamed: "{old_name}" -> "{new_name}"')
                except Exception as e:
                    print(f'❌ Lỗi khi rename "{old_name}" -> "{new_name}": {e}')

    # Cuối cùng rename folder gốc nếu cần
    old_name = folder_path.name
    new_name = unicodedata.normalize('NFD', old_name)
    new_name = new_name.encode('ascii', 'ignore').decode('ascii')
    new_name = re.sub(r'\s+', ' ', new_name).strip()

    if new_name != old_name and new_name:
        new_path = folder_path.parent / new_name
        try:
            folder_path.rename(new_path)
            print(f'✅ Renamed root: "{old_name}" -> "{new_name}"')
            folder_path = new_path   # 🔑 cập nhật path gốc
        except Exception as e:
            print(f'❌ Lỗi khi rename root "{old_name}" -> "{new_name}": {e}')

    return folder_path


if __name__ == "__main__":
    root = Path('/Users/hannada/Desktop/đồng hồ')
    subfolders = get_all_subfolders(root)
    for folder in subfolders:
        print(folder)