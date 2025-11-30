import subprocess
from pathlib import Path
from jsonWork import extract_time, convert_timestamp


# =====================================================
# 1) Ghi metadata bằng exiftool
# =====================================================
def write_metadata_with_exiftool(media_path: Path|str, datetime_str: str):
    """
    Ghi metadata theo chuẩn EXIF + FILETIME.
    đầu vào là links tới file media và chuỗi datetime theo định dạng "YYYY:MM:DD HH:MM:SS".
    """
    media_path = Path(media_path)
    cmd = [ "exiftool",
        #    f"-EXIF:DateTimeOriginal={datetime_str}", 
        #    f"-EXIF:CreateDate={datetime_str}", 
        #    f"-EXIF:ModifyDate={datetime_str}", 
        #    f"-XMP:DateCreated={datetime_str}", 
        #    f"-XMP:CreateDate={datetime_str}", 
        #    f"-XMP:ModifyDate={datetime_str}", 
        #    f"-XMP:MetadataDate={datetime_str}", 
        #    f"-QuickTime:CreateDate={datetime_str}", 
        #    f"-QuickTime:ModifyDate={datetime_str}", 
        #    f"-QuickTime:TrackCreateDate={datetime_str}", 
        #    f"-QuickTime:TrackModifyDate={datetime_str}", 
        #    f"-QuickTime:MediaCreateDate={datetime_str}", 
        #    f"-QuickTime:MediaModifyDate={datetime_str}", 
           f"-FileCreateDate={datetime_str}", 
           f"-FileModifyDate={datetime_str}",
           "-overwrite_original", 
           media_path, 
           ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# =====================================================
# 2) Xử lý FULL JSON + MEDIA
# =====================================================
def process_media(json_path: Path|str, media_path: Path|str)->None:
    """
    Xử lý 1 cặp JSON + ảnh/video (full).
    Đầu vào là links tới file JSON và file media.
    Có thể sử dụng cho link string hoặc Path object.
    """
    json_path = Path(json_path)
    media_path = Path(media_path)

    dt = extract_time(json_path)
    # print(f"-> Setting {media_path.name} to {dt}")
    write_metadata_with_exiftool(media_path, dt)

def process_media_lite(timestamp:str, media_path: Path|str)->None:
    """
    Xử lý 1 cặp JSON + ảnh/video (full).
    Đầu vào là timestamp string và file media.
    Có thể sử dụng cho link string hoặc Path object.
    """
    media_path = Path(media_path)
    dt = convert_timestamp(timestamp)
    # print(f"-> Setting {media_path.name} to {dt}")
    write_metadata_with_exiftool(media_path, dt)
# =====================================================
# 3) Test
# =====================================================
if __name__ == "__main__":
    # json_path = Path(r"C:\Users\DucKhanhPC\Desktop\2015\IMG_5727.JPG.supplemental-metadata.json")
    media_path = Path(r"C:\Users\DucKhanhPC\Desktop\test 2\Ảnh từ năm 2023\IMG_8479.MP4")

    process_media_lite("860154321", media_path)
    # input("\nPress Enter to exit...")