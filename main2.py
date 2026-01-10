# main.py
import sys
from pathlib import Path

def main(folder_path: Path):
    print("📂 Folder nhận được:", folder_path)

    files = list(folder_path.glob("*"))
    print(f"🔍 Tìm thấy {len(files)} file")

    for i, f in enumerate(files, 1):
        print(f"[{i}/{len(files)}] Xử lý: {f.name}")

    print("✅ Hoàn tất")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Thiếu folder path")
        print("👉 Cách dùng: python main.py <folder_path>")
        sys.exit(1)

    folder = Path(sys.argv[1])

    if not folder.exists() or not folder.is_dir():
        print("❌ Path không hợp lệ:", folder)
        sys.exit(1)

    main(folder)
