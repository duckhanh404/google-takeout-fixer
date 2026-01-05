import unicodedata
from pathlib import Path
from tqdm import tqdm   # pip install tqdm

def normalize_filenames_to_nfc(folder_path: str | Path):
    folder_path = Path(folder_path)

    # Lấy toàn bộ path trước để đếm tổng số phần tử
    all_paths = sorted(
        folder_path.rglob("*"),
        key=lambda p: -len(p.parts)   # xử lý từ sâu nhất
    )

    print(f"Tổng số mục cần xử lý: {len(all_paths)}")
    renamed_count = 0

    for path in tqdm(all_paths, desc="Đang đổi tên", unit="mục"):
        normalized_name = unicodedata.normalize("NFC", path.name)

        # Nếu không đổi tên thì bỏ qua
        if normalized_name == path.name:
            continue

        new_path = path.with_name(normalized_name)

        try:
            path.rename(new_path)
            print(f'Tên mới: {new_path}')
            renamed_count += 1
        except Exception as e:
            print(f"\n❌ Lỗi khi rename {path}: {e}")

    print(f"\n✔️ Hoàn tất! Đã đổi tên {renamed_count} mục.")

if __name__ == "__main__":
    target_folder = r"C:\Users\DucKhanhPC\Desktop\test 2"
    normalize_filenames_to_nfc(target_folder)
