from pathlib import Path
import shutil
from typing import List, Iterable



def move_to_error(file_path: str|Path)-> None:
    """
    Di chuyển file vào thư mục /error cùng cấp với file.
    Hỗ trợ macOS / Linux / Windows.
    Đầu vào yêu cầu là đường dẫn file đầy đủ hoặc Path object.
    """
    file_path = Path(file_path)
    if not file_path.is_file():
        print(f"❌ File không tồn tại: {file_path}")
        return
    folder = file_path.parent
    error_dir = folder / "error"
    error_dir.mkdir(exist_ok=True)
    new_path = error_dir / file_path.name
    shutil.move(str(file_path), str(new_path))
    print(f"✅ Đã di chuyển {file_path.name} → {new_path}")


def move_back(file_path: str|Path)->None:
    """
    Di chuyển file từ thư mục /error lên thư mục cha.
    Ví dụ:
    /path/to/folder/error/hello.txt  →  /path/to/folder/hello.txt
    """
    file_path = Path(file_path)
    if not file_path.is_file():
        print(f"❌ File không tồn tại: {file_path}")
        return False

    parent_dir = file_path.parent.parent  # lên 1 cấp: từ /error → folder
    new_path = parent_dir / file_path.name
    # Nếu file trùng tên, tự động đổi tên để tránh lỗi
    if new_path.exists():
        new_path = parent_dir / f"{file_path.stem}_copy{file_path.suffix}"
    shutil.move(str(file_path), str(new_path))
    # print(f"✅ Đã di chuyển {file_path.name} lên {parent_dir}")
    return True


def copy_files_from_lists(
    source_dir: str | Path,
    dest_dir: str | Path,
    file_lists: Iterable[Iterable[str]]
) -> None:
    """
    Copy các file từ source_dir sang dest_dir dựa trên nhiều list tên file.

    - source_dir: thư mục chứa file gốc
    - dest_dir: thư mục đích
    - file_lists: iterable các list tên file (vd: [list1, list2, ...])
    """

    source_dir = Path(source_dir)
    dest_dir = Path(dest_dir)

    if not source_dir.is_dir():
        raise ValueError(f"Source directory không tồn tại: {source_dir}")

    dest_dir.mkdir(parents=True, exist_ok=True)

    for file_list in file_lists:
        for filename in file_list:
            src_path = source_dir / filename
            dst_path = dest_dir / filename

            if not src_path.is_file():
                print(f"⚠️ Không tìm thấy file: {src_path}")
                continue

            try:
                shutil.copy2(src_path, dst_path)
                print(f"✅ Copied: {filename}")
            except Exception as e:
                print(f"❌ Lỗi khi copy {filename}: {e}")

if __name__ == "__main__":
    test_file = r"C:\Users\khanh\Downloads\Takeout\error\hello.txt"
    move_back(test_file)
