from pathlib import Path
import shutil

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


if __name__ == "__main__":
    test_file = r"C:\Users\khanh\Downloads\Takeout\error\hello.txt"
    move_back(test_file)
