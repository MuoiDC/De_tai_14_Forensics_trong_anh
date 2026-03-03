import piexif
import exifread
import os
import time
import shutil
from datetime import datetime
from PIL import Image
import platform

def clear_screen():
    """Xóa màn hình terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def change_to_rational(number):
    """Hàm phụ trợ để đổi số thập phân sang dạng phân số cho GPS"""
    f = float(number)
    return (int(f * 1000000), 1000000)

def parse_datetime_input(date_str):
    """Chuyển đổi input ngày giờ sang định dạng EXIF"""
    try:
        # Thử parse nhiều định dạng khác nhau
        formats = [
            "%Y:%m:%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%d-%m-%Y %H:%M:%S",
            "%Y/%m/%d %H:%M:%S"
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y:%m:%d %H:%M:%S")
            except:
                continue
        
        raise ValueError("Định dạng không hợp lệ")
    except:
        return None

def change_datetime_original(exif_dict):
    """Thay đổi ngày giờ chụp ảnh"""
    print("\n" + "="*50)
    print("THAY DOI NGAY GIO CHUP ANH")
    print("="*50)
    print("Dinh dang: YYYY:MM:DD HH:MM:SS hoac YYYY-MM-DD HH:MM:SS")
    print("Vi du: 2026:12:25 08:30:00 hoac 2026-12-25 08:30:00")
    
    date_input = input("\nNhap ngay gio chup: ").strip()
    
    parsed_date = parse_datetime_input(date_input)
    if parsed_date:
        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = parsed_date.encode()
        exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = parsed_date.encode()
        exif_dict["0th"][piexif.ImageIFD.DateTime] = parsed_date.encode()
        print(f"Da cap nhat DateTimeOriginal: {parsed_date}")
        return parsed_date
    else:
        print("Dinh dang ngay gio khong hop le!")
        return None

def change_location(exif_dict):
    """Thay đổi vị trí GPS"""
    print("\n" + "="*50)
    print("THAY DOI VI TRI GPS")
    print("="*50)
    print("Nhap toa do theo dinh dang thap phan")
    print("Vi du: Ha Noi: 21.028511, 105.852180")
    print("       Sydney: -33.8688, 151.2093")
    
    try:
        latitude = float(input("\nNhap vi do (Latitude): ").strip())
        longitude = float(input("Nhap kinh do (Longitude): ").strip())
        
        # Xác định hướng
        lat_ref = b"N" if latitude >= 0 else b"S"
        lng_ref = b"E" if longitude >= 0 else b"W"
        
        # Chuyển đổi sang dạng rational
        lat_rational = change_to_rational(abs(latitude))
        lng_rational = change_to_rational(abs(longitude))
        
        # Cập nhật GPS
        exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = lat_ref
        exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] = [lat_rational, (0, 1), (0, 1)]
        exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = lng_ref
        exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] = [lng_rational, (0, 1), (0, 1)]
        
        print(f"Da cap nhat GPS: {latitude}, {longitude}")
        print(f"Huong: {lat_ref.decode()}, {lng_ref.decode()}")
        return True
    except ValueError:
        print("Toa do khong hop le!")
        return False

def change_camera_info(exif_dict):
    """Thay đổi thông tin máy ảnh"""
    print("\n" + "="*50)
    print("THAY DOI THONG TIN MAY ANH")
    print("="*50)
    
    make = input("Nhap hang may anh (Make) [Enter de bo qua]: ").strip()
    if make:
        exif_dict["0th"][piexif.ImageIFD.Make] = make.encode()
        print(f"Da cap nhat Make: {make}")
    
    model = input("Nhap model may anh (Model) [Enter de bo qua]: ").strip()
    if model:
        exif_dict["0th"][piexif.ImageIFD.Model] = model.encode()
        print(f"Da cap nhat Model: {model}")
    
    lens = input("Nhap ten ong kinh (LensModel) [Enter de bo qua]: ").strip()
    if lens:
        exif_dict["Exif"][piexif.ExifIFD.LensModel] = lens.encode()
        print(f"Da cap nhat LensModel: {lens}")
    
    return True

def change_camera_settings(exif_dict):
    """Thay đổi thông số chụp"""
    print("\n" + "="*50)
    print("THAY DOI THONG SO CHUP")
    print("="*50)
    
    try:
        # ISO
        iso = input("Nhap ISO (vi du: 100, 400, 800) [Enter de bo qua]: ").strip()
        if iso:
            exif_dict["Exif"][piexif.ExifIFD.ISOSpeedRatings] = int(iso)
            print(f"Da cap nhat ISO: {iso}")
        
        # Khẩu độ (F-number)
        fnumber = input("Nhap khau do (vi du: 2.8, 5.6, 11) [Enter de bo qua]: ").strip()
        if fnumber:
            f_val = float(fnumber)
            exif_dict["Exif"][piexif.ExifIFD.FNumber] = (int(f_val * 10), 10)
            print(f"Da cap nhat F-number: f/{fnumber}")
        
        # Tốc độ màn trập
        shutter = input("Nhap toc do man trap (vi du: 200 cho 1/200s) [Enter de bo qua]: ").strip()
        if shutter:
            exif_dict["Exif"][piexif.ExifIFD.ExposureTime] = (1, int(shutter))
            print(f"Da cap nhat ExposureTime: 1/{shutter}s")
        
        # Tiêu cự
        focal = input("Nhap tieu cu (mm) [Enter de bo qua]: ").strip()
        if focal:
            exif_dict["Exif"][piexif.ExifIFD.FocalLength] = (int(focal), 1)
            print(f"Da cap nhat FocalLength: {focal}mm")
        
        return True
    except ValueError:
        print("Gia tri khong hop le!")
        return False

def change_author_info(exif_dict):
    """Thay đổi thông tin tác giả"""
    print("\n" + "="*50)
    print("THAY DOI THONG TIN TAC GIA")
    print("="*50)
    
    artist = input("Nhap ten tac gia (Artist) [Enter de bo qua]: ").strip()
    if artist:
        exif_dict["0th"][piexif.ImageIFD.Artist] = artist.encode()
        print(f"Da cap nhat Artist: {artist}")
    
    copyright_text = input("Nhap thong tin ban quyen (Copyright) [Enter de bo qua]: ").strip()
    if copyright_text:
        exif_dict["0th"][piexif.ImageIFD.Copyright] = copyright_text.encode()
        print(f"Da cap nhat Copyright: {copyright_text}")
    
    software = input("Nhap phan mem chinh sua (Software) [Enter de bo qua]: ").strip()
    if software:
        exif_dict["0th"][piexif.ImageIFD.Software] = software.encode()
        print(f"Da cap nhat Software: {software}")
    
    return True

def change_file_dates(filename, datetime_str):
    """Thay đổi ngày giờ của file hệ thống"""
    print("\n" + "="*50)
    print("THAY DOI NGAY GIO FILE HE THONG")
    print("="*50)
    
    try:
        # Chuyển đổi datetime string sang timestamp
        dt = datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")
        timestamp = time.mktime(dt.timetuple())
        
        # Thay đổi access time và modified time
        os.utime(filename, (timestamp, timestamp))
        
        print(f"Da cap nhat thoi gian file:")
        print(f"   - File Modified Date: {datetime_str}")
        print(f"   - File Access Date: {datetime_str}")
        
        # Lưu ý: FileInodeChangeDate không thể thay đổi trực tiếp trên Windows
        if platform.system() != "Windows":
            print(f"   - File Inode Change Date: {datetime_str}")
        else:
            print("   Luu y: FileInodeChangeDate khong the thay doi tren Windows")
        
        return True
    except Exception as e:
        print(f"Loi khi thay doi ngay gio file: {e}")
        return False

def view_current_exif(filename):
    """Xem EXIF hiện tại với exifread - chi tiết và đầy đủ"""
    print("\n" + "="*80)
    print("THONG TIN EXIF CHI TIET")
    print("="*80)
    
    try:
        with open(filename, 'rb') as f:
            tags = exifread.process_file(f, details=True)
        
        if not tags:
            print("\nKhong tim thay du lieu EXIF trong file!")
            input("\nNhan Enter de tiep tuc...")
            return
        
        print(f"\nFile: {filename}")
        print(f"Tong so EXIF tags: {len(tags)}")
        print("="*80)
        
        # Nhóm 1: THÔNG TIN FILE CƠ BẢN
        print("\n[1] THONG TIN FILE CO BAN")
        print("-"*80)
        file_stats = os.stat(filename)
        print(f"Kich thuoc file: {file_stats.st_size} bytes ({file_stats.st_size / 1024:.2f} KB)")
        print(f"Ngay tao file: {datetime.fromtimestamp(file_stats.st_ctime).strftime('%Y:%m:%d %H:%M:%S')}")
        print(f"Ngay sua doi: {datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y:%m:%d %H:%M:%S')}")
        print(f"Ngay truy cap: {datetime.fromtimestamp(file_stats.st_atime).strftime('%Y:%m:%d %H:%M:%S')}")
        
        # Nhóm 2: THÔNG TIN HÌNH ẢNH
        print("\n[2] THONG TIN HINH ANH")
        print("-"*80)
        image_tags = {
            'Image Make': 'Hang san xuat',
            'Image Model': 'Model may anh',
            'Image Orientation': 'Huong anh',
            'Image XResolution': 'Do phan giai X',
            'Image YResolution': 'Do phan giai Y',
            'Image ResolutionUnit': 'Don vi do phan giai',
            'Image Software': 'Phan mem',
            'Image DateTime': 'Ngay gio chinh sua',
            'Image Artist': 'Tac gia',
            'Image Copyright': 'Ban quyen',
            'Image ExifOffset': 'EXIF Offset',
        }
        
        for tag, label in image_tags.items():
            if tag in tags:
                print(f"{label:30s}: {tags[tag]}")
        
        # Nhóm 3: THÔNG SỐ CHỤP ẢNH (EXIF)
        print("\n[3] THONG SO CHUP ANH")
        print("-"*80)
        exif_tags = {
            'EXIF DateTimeOriginal': 'Ngay gio chup goc',
            'EXIF DateTimeDigitized': 'Ngay gio so hoa',
            'EXIF ExposureTime': 'Toc do man trap',
            'EXIF FNumber': 'Khau do',
            'EXIF ExposureProgram': 'Chuong trinh phoi sang',
            'EXIF ISOSpeedRatings': 'ISO',
            'EXIF ShutterSpeedValue': 'Gia tri toc do man trap',
            'EXIF ApertureValue': 'Gia tri khau do',
            'EXIF BrightnessValue': 'Do sang',
            'EXIF ExposureBiasValue': 'Bu phoi sang',
            'EXIF MaxApertureValue': 'Khau do toi da',
            'EXIF MeteringMode': 'Che do do sang',
            'EXIF Flash': 'Den flash',
            'EXIF FocalLength': 'Tieu cu',
            'EXIF ColorSpace': 'Khong gian mau',
            'EXIF ExifImageWidth': 'Chieu rong anh',
            'EXIF ExifImageLength': 'Chieu cao anh',
            'EXIF FocalPlaneXResolution': 'Do phan giai mat phang X',
            'EXIF FocalPlaneYResolution': 'Do phan giai mat phang Y',
            'EXIF FocalPlaneResolutionUnit': 'Don vi do phan giai',
            'EXIF ExposureMode': 'Che do phoi sang',
            'EXIF WhiteBalance': 'Can bang trang',
            'EXIF SceneCaptureType': 'Loai canh chup',
            'EXIF Contrast': 'Do tuong phan',
            'EXIF Saturation': 'Do bao hoa',
            'EXIF Sharpness': 'Do sac net',
        }
        
        for tag, label in exif_tags.items():
            if tag in tags:
                print(f"{label:30s}: {tags[tag]}")
        
        # Nhóm 4: THÔNG TIN ỐNG KÍNH
        print("\n[4] THONG TIN ONG KINH")
        print("-"*80)
        lens_tags = {
            'EXIF LensSpecification': 'Thong so ong kinh',
            'EXIF LensMake': 'Hang ong kinh',
            'EXIF LensModel': 'Model ong kinh',
            'EXIF LensSerialNumber': 'Serial ong kinh',
        }
        
        lens_found = False
        for tag, label in lens_tags.items():
            if tag in tags:
                print(f"{label:30s}: {tags[tag]}")
                lens_found = True
        
        if not lens_found:
            print("Khong co thong tin ong kinh")
        
        # Nhóm 5: THÔNG TIN GPS
        print("\n[5] THONG TIN VI TRI GPS")
        print("-"*80)
        gps_tags = {
            'GPS GPSVersionID': 'Phien ban GPS',
            'GPS GPSLatitudeRef': 'Tham chieu vi do',
            'GPS GPSLatitude': 'Vi do',
            'GPS GPSLongitudeRef': 'Tham chieu kinh do',
            'GPS GPSLongitude': 'Kinh do',
            'GPS GPSAltitudeRef': 'Tham chieu do cao',
            'GPS GPSAltitude': 'Do cao',
            'GPS GPSTimeStamp': 'Thoi gian GPS',
            'GPS GPSSpeedRef': 'Don vi toc do',
            'GPS GPSSpeed': 'Toc do',
            'GPS GPSImgDirectionRef': 'Tham chieu huong anh',
            'GPS GPSImgDirection': 'Huong anh',
            'GPS GPSDestBearingRef': 'Tham chieu phuong vi',
            'GPS GPSDestBearing': 'Phuong vi',
            'GPS GPSDateStamp': 'Ngay GPS',
        }
        
        gps_found = False
        for tag, label in gps_tags.items():
            if tag in tags:
                print(f"{label:30s}: {tags[tag]}")
                gps_found = True
        
        if not gps_found:
            print("Khong co thong tin GPS")
        
        # Nhóm 6: THÔNG TIN THUMBNAIL
        print("\n[6] THONG TIN THUMBNAIL")
        print("-"*80)
        thumbnail_tags = {
            'Thumbnail Compression': 'Nen thumbnail',
            'Thumbnail XResolution': 'Do phan giai X',
            'Thumbnail YResolution': 'Do phan giai Y',
            'Thumbnail ResolutionUnit': 'Don vi do phan giai',
            'Thumbnail JPEGInterchangeFormat': 'Dinh dang JPEG',
            'Thumbnail JPEGInterchangeFormatLength': 'Do dai JPEG',
        }
        
        thumbnail_found = False
        for tag, label in thumbnail_tags.items():
            if tag in tags:
                print(f"{label:30s}: {tags[tag]}")
                thumbnail_found = True
        
        if not thumbnail_found:
            print("Khong co thong tin thumbnail")
        
        # Nhóm 7: THÔNG TIN MAKERNOTE (Nếu có)
        print("\n[7] THONG TIN MAKERNOTE")
        print("-"*80)
        makernote_found = False
        for tag in tags:
            if 'MakerNote' in tag or tag.startswith('Image Tag '):
                print(f"{tag:30s}: {tags[tag]}")
                makernote_found = True
        
        if not makernote_found:
            print("Khong co thong tin MakerNote")
        
        # Nhóm 8: CÁC TAG KHÁC
        print("\n[8] CAC TAG KHAC")
        print("-"*80)
        
        displayed_tags = set()
        for tag_dict in [image_tags, exif_tags, lens_tags, gps_tags, thumbnail_tags]:
            displayed_tags.update(tag_dict.keys())
        
        other_tags_found = False
        for tag in sorted(tags.keys()):
            if (tag not in displayed_tags and 
                not tag.startswith('MakerNote') and 
                not tag.startswith('Image Tag ') and
                tag not in ['JPEGThumbnail', 'TIFFThumbnail']):
                print(f"{tag:30s}: {tags[tag]}")
                other_tags_found = True
        
        if not other_tags_found:
            print("Khong co tag khac")
        
        print("\n" + "="*80)
        print("HOAN THANH HIEN THI EXIF")
        print("="*80)
        
    except FileNotFoundError:
        print(f"\nLoi: Khong tim thay file {filename}")
    except Exception as e:
        print(f"\nLoi khi doc EXIF: {e}")
    
    input("\nNhan Enter de tiep tuc...")

def save_changes(filename, exif_dict):
    """Lưu thay đổi - ghi đè trực tiếp lên file gốc"""
    try:
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, filename)
        print(f"\nDa luu thanh cong vao file: {filename}")
        return True
    except Exception as e:
        print(f"\nLoi khi luu file: {e}")
        return False

def main_menu():
    """Menu chính"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║   CHUONG TRINH CHINH SUA EXIF METADATA                     ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    # Nhập đường dẫn ảnh
    duong_dan_anh = input("Nhap duong dan file anh can chinh sua: ").strip()
    
    # Xóa dấu ngoặc kép nếu có (khi kéo thả file)
    duong_dan_anh = duong_dan_anh.strip('"').strip("'")
    
    if not os.path.exists(duong_dan_anh):
        print(f"Loi: File {duong_dan_anh} khong ton tai!")
        print("\nHuong dan:")
        print("1. Dat anh vao thu muc hien tai")
        print("2. Nhap ten file (vi du: image.jpg)")
        print("3. Hoac nhap duong dan day du")
        return
    
    filename = duong_dan_anh
    
    # Tải EXIF hiện có
    try:
        exif_dict = piexif.load(filename)
    except:
        exif_dict = {"0th":{}, "Exif":{}, "GPS":{}, "1st":{}, "thumbnail":None}
    
    datetime_original = None  # Lưu lại datetime để sync với file system
    
    while True:
        clear_screen()
        print("="*50)
        print("        CHINH SUA EXIF METADATA")
        print("="*50)
        print(f"File: {os.path.basename(filename)}")
        print(f"Duong dan: {filename}")
        print("="*50)
        print("\nChon thao tac:")
        print("1. Thay doi ngay gio chup anh (DateTimeOriginal)")
        print("2. Thay doi vi tri GPS (Location)")
        print("3. Thay doi thong tin may anh (Make, Model, Lens)")
        print("4. Thay doi thong so chup (ISO, F-number, Shutter, Focal Length)")
        print("5. Thay doi thong tin tac gia (Artist, Copyright, Software)")
        print("6. Dong bo ngay gio file voi DateTimeOriginal")
        print("7. Xem thong tin EXIF hien tai")
        print("8. Luu tat ca thay doi")
        print("0. Thoat")
        print("="*50)
        
        choice = input("\nNhap lua chon cua ban: ").strip()
        
        if choice == "1":
            result = change_datetime_original(exif_dict)
            if result:
                datetime_original = result
            input("\nNhan Enter de tiep tuc...")
            
        elif choice == "2":
            change_location(exif_dict)
            input("\nNhan Enter de tiep tuc...")
            
        elif choice == "3":
            change_camera_info(exif_dict)
            input("\nNhan Enter de tiep tuc...")
            
        elif choice == "4":
            change_camera_settings(exif_dict)
            input("\nNhan Enter de tiep tuc...")
            
        elif choice == "5":
            change_author_info(exif_dict)
            input("\nNhan Enter de tiep tuc...")
            
        elif choice == "6":
            if datetime_original:
                change_file_dates(filename, datetime_original)
            else:
                print("\nVui long thiet lap DateTimeOriginal truoc (Chon 1)")
            input("\nNhan Enter de tiep tuc...")
            
        elif choice == "7":
            # Xem EXIF chi tiết
            view_current_exif(filename)
            
        elif choice == "8":
            if save_changes(filename, exif_dict):
                print("Hoan tat!")
            input("\nNhan Enter de tiep tuc...")
            
        elif choice == "0":
            print("\nCam on ban da su dung chuong trinh!")
            break
            
        else:
            print("\nLua chon khong hop le!")
            input("\nNhan Enter de tiep tuc...")

if __name__ == "__main__":
    main_menu()