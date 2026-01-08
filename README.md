# Google Takeout Media Timestamp Fixer – v4.0
(Tiếng Việt ở phía dưới)

**Please note that the current version 4.0 is only for Python users and can only handle one folder at a time. In version 4.1, I will create a GUI interface and add functionality for handling multiple folders.**

A Python tool to **restore and synchronize timestamps for media files (photos & videos)** exported from **Google Takeout**, using metadata stored in the accompanying JSON files.

Version **v4.0** is fully redesigned using an **index-based architecture**, optimized for:
- Large datasets (tens of thousands of files)
- High performance
- Long-running stability

---

## 🚀 Key Features

- ✅ Write correct EXIF timestamps for photos and videos
- ✅ Prefer timestamps from JSON (`photoTakenTime`, `creationTime`)
- ✅ Fallback to reading timestamps directly from media metadata
- ✅ Prefix-based JSON matching for renamed / duplicated files
- ✅ Uses **ExifTool stay_open** mode (fast & stable)
- ✅ Unicode NFC normalization (macOS & Vietnamese filenames)
- ✅ Scales well with large Google Takeout exports

---

## 🧠 Processing Architecture (v4.0)

### Overall Pipeline

```

1. Build JSON index (once)
2. Phase 1: Exact media ↔ JSON match (O(1))
3. Phase 2: Read timestamp directly from media EXIF
4. Phase 3: Prefix-based JSON fallback matching
5. Write metadata using ExifTool stay_open

```

### Differences from v3.x

| Aspect | v3.x | v4.0 |
|-----|-----|------|
| JSON loading | Multiple times | **Once only** |
| Prefix matching | O(N³) | **O(N·L)** |
| ExifTool usage | Repeated calls | **stay_open mode** |
| Large datasets | ❌ | ✅ |
| Stability | Medium | **High** |

---

## 📁 Project Structure

```

.
├── main_v4.0.py        # Entry point
├── metadata.py         # ExifTool + helpers
├── json_index.py       # JSON indexing & matching logic
└── README.md

````

---

## ⚙️ System Requirements

- Python **3.10+** (recommended)
- ExifTool installed on your system

### Install ExifTool

**macOS (Homebrew):**
```bash
brew install exiftool
````

**Ubuntu / Debian:**

```bash
sudo apt install libimage-exiftool-perl
```

**Windows:**

* Download from [https://exiftool.org](https://exiftool.org)
* Add ExifTool to your system PATH

---

## ▶️ Usage

### 1️⃣ Prepare your folder

The target folder must contain:

* Media files (`.jpg`, `.png`, `.heic`, `.mp4`, etc.)
* Corresponding Google Takeout JSON files

Example:

```
/Photos/
├── IMG_0001.jpg
├── IMG_0001.jpg.json
├── IMG_0002(1).jpg
├── IMG_0002.jpg.json
```

---

### 2️⃣ Configure path

Edit `main_v4.0.py`:

```python
ROOT = Path("/path/to/google-takeout-folder")
```

---

### 3️⃣ Run the script

```bash
python main_v4.0.py
```

---

## 🔍 Processing Phases Explained

### Phase 1 – Exact Match

* Match media ↔ JSON by exact `title`
* Fastest and most reliable

### Phase 2 – EXIF Fallback

* Extract timestamp directly from media metadata
* Used when JSON is missing or mismatched

### Phase 3 – Prefix Fallback

* Gradually shortens filename to find a matching JSON
* Handles:

  * Duplicates `(1)`, `(2)`
  * Truncated filenames
  * Encoding differences

---

## ⚠️ Important Notes

* **Metadata is overwritten in-place**
* Always **backup your files before running**
* ExifTool runs with `-overwrite_original`

---

## ⏱️ Performance (Reference)

| Dataset size  | Time           |
| ------------- | -------------- |
| ~3,000 media  | ~30–40 seconds |
| ~10,000 media | ~1–2 minutes   |

(Tested on macOS M1/M2, SSD)

---

## ❓ Why not multiprocessing?

* This workload is **I/O-bound**
* ExifTool is a subprocess → spawning multiple instances is expensive
* Single-process + `stay_open` gives the best real-world performance

👉 Multiprocessing does **not** significantly improve execution time here.

---

## 🛠️ Future Improvements

* [ ] Resume / checkpoint mode
* [ ] Progress bar
* [ ] CLI interface (`python fixdate.py <folder>`)
* [ ] Trie-based prefix index
* [ ] Multiple ExifTool pipelines

---

## 📜 License

MIT License

---

## 🙌 Credits

* ExifTool – Phil Harvey
* Google Takeout
* ChatGPT
---

## 💡 Contributions

Issues and Pull Requests are welcome ✨
If you run this tool on very large datasets, feel free to share benchmarks!

===============================
========= Tiếng Việt ==========
===============================

***Lưu ý, Phiên bản 4.0 hiện tại chỉ có cho người biết sử dụng python và xử lý 1 folder tại 1 thời điểm. Trong phiên bản 4.1 tôi sẽ làm giao diện GUI cũng như bổ sung thêm tính năng xử lý nhiều folder.***

# Google Takeout Media Timestamp Fixer – v4.0

Công cụ Python giúp **khôi phục / đồng bộ lại timestamp cho file media (ảnh, video)** được export từ **Google Takeout**, dựa trên metadata trong file JSON đi kèm.

Phiên bản **v4.0** được thiết kế lại hoàn toàn theo **kiến trúc index**, tối ưu cho:
- Dataset lớn (hàng chục nghìn file)
- Hiệu năng cao
- Độ ổn định khi chạy lâu

---

## 🚀 Tính năng chính

- ✅ Ghi timestamp chuẩn EXIF cho ảnh / video
- ✅ Ưu tiên timestamp từ JSON (`photoTakenTime`, `creationTime`)
- ✅ Fallback đọc timestamp trực tiếp từ metadata media
- ✅ Fallback match JSON bằng prefix (tên file bị cắt / clone)
- ✅ Sử dụng **ExifTool stay_open** (nhanh & ổn định)
- ✅ Chuẩn hóa Unicode NFC (hỗ trợ tiếng Việt, macOS)
- ✅ Chạy tốt với dataset >10.000 file

---

## 🧠 Kiến trúc xử lý (v4.0)

### Tổng quan pipeline



Build JSON index (1 lần)

- Phase 1: Match chính xác media ↔ JSON (O(1))
- Phase 2: Đọc timestamp trực tiếp từ media EXIF
- Phase 3: Fallback prefix match JSON

Ghi metadata bằng ExifTool stay_open


### Điểm khác biệt so với v3.x

| Vấn đề       | v3.x       | v4.0               |
| ------------ | ---------- | ------------------ |
| Đọc JSON     | Nhiều lần  | **1 lần duy nhất** |
| Prefix match | O(N³)      | **O(N·L)**         |
| ExifTool     | gọi lặp    | **stay_open**      |
| Scale lớn    | ❌          | ✅                  |
| Độ ổn định   | Trung bình | **Cao**            |

---

## 📁 Cấu trúc project
```
.
├── main_v4.0.py # Entry point
├── metadata.py # ExifTool + helper functions
├── json_index.py # JSON index & matching logic
└── README.md
```

---

## ⚙️ Yêu cầu hệ thống

- Python **3.10+** (khuyến nghị)
- ExifTool (đã cài sẵn trong hệ thống)

### Cài ExifTool

**macOS (Homebrew):**
```bash
brew install exiftool
```

**Ubuntu / Debian:**
```Ubuntu / Debian:
sudo apt install libimage-exiftool-perl
```

**Windows:**

- Tải từ: https://exiftool.org
- Thêm vào PATH

## ▶️ Cách sử dụng
## 1️⃣ Chuẩn bị thư mục

Thư mục cần xử lý phải chứa:
- File media (.jpg, .png, .heic, .mp4, ...)
- File JSON tương ứng do Google Takeout xuất

Ví dụ:
```
/Photos/
├── IMG_0001.jpg
├── IMG_0001.jpg.json
├── IMG_0002(1).jpg
├── IMG_0002.jpg.json
```

### 2️⃣ Cấu hình đường dẫn

Mở main_v4.0.py và sửa:
```
ROOT = Path("/path/to/google-takeout-folder")
```

### 3️⃣ Chạy chương trình
```
python main_v4.0.py
```

## 🔍 Chi tiết các phase
### Phase 1 – Exact match
- Match media ↔ JSON theo title
- Nhanh nhất, chính xác tuyệt đối
### Phase 2 – EXIF fallback
- Đọc timestamp trực tiếp từ metadata media
- Dùng khi JSON bị thiếu hoặc không khớp

### Phase 3 – Prefix fallback
- Giảm dần tên file để match JSON
- Xử lý trường hợp:
	- File bị clone (1), (2)
	- Tên bị cắt
	- Khác encoding

## ⚠️ Lưu ý quan trọng

- File gốc sẽ bị ghi đè metadata
- Nên backup trước khi chạy
- ExifTool chạy ở chế độ -overwrite_original

## ⏱️ Hiệu năng thực tế (tham khảo)

| Dataset       | Thời gian   |
| ------------- | ----------- |
| ~3.000 media  | ~30–40 giây |
| ~10.000 media | ~1–2 phút   |
(macOS M1/M2, SSD)

## ❓ Vì sao không dùng multiprocessing?

- Bài toán này IO-bound
- ExifTool là subprocess → spawn rất tốn thời gian
- Single-thread + stay_open cho hiệu năng tốt nhất
👉 Multiprocessing không mang lại lợi ích đáng kể cho trường hợp này.

## 🛠️ Hướng phát triển tiếp theo

 - [ ] Resume mode (chạy tiếp khi bị gián đoạn)
 - [ ] Progress bar
 - [ ] CLI (python fixdate.py <folder>)
- [ ] Trie-based prefix index
- [ ] Multi ExifTool pipeline

## 🙌 Credits
- ExifTool – Phil Harvey
- Google Takeout
- ChatGPT

## 💡 Góp ý & đóng góp
- Pull Request và Issue luôn được hoan nghênh ✨
- Nếu bạn dùng tool này cho dataset lớn, đừng ngại chia sẻ benchmark!
