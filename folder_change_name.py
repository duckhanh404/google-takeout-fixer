import unicodedata
import re
from pathlib import Path

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
            # Chuyển sang ASCII
            new_name = unicodedata.normalize('NFD', old_name)
            new_name = new_name.encode('ascii', 'ignore').decode('ascii')
            # Thay dấu cách, ký tự lạ thành khoảng trắng
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
        except Exception as e:
            print(f'❌ Lỗi khi rename root "{old_name}" -> "{new_name}": {e}')
if __name__ == "__main__":
    test_folder = r"E:\Takeout"
    normalize_folder_names(test_folder)