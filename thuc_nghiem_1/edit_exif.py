import piexif
import os
import time
from datetime import datetime
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
            "%d-%m-%Y %H:%M:%S"
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
    print("THAY ĐỔI NGÀY GIỜ CHỤP ẢNH")
    print("="*50)
    print("Định dạng: YYYY:MM:DD HH:MM:SS hoặc YYYY-MM-DD HH:MM:SS")
    print("Ví dụ: 2026:12:25 08:30:00 hoặc 2026-12-25 08:30:00")
    
    date_input = input("\nNhập ngày giờ chụp: ").strip()
    
    parsed_date = parse_datetime_input(date_input)
    if parsed_date:
        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = parsed_date.encode()
        exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = parsed_date.encode()
        exif_dict["0th"][piexif.ImageIFD.DateTime] = parsed_date.encode()
        print(f"✅ Đã cập nhật DateTimeOriginal: {parsed_date}")
        return parsed_date
    else:
        print("❌ Định dạng ngày giờ không hợp lệ!")
        return None

def change_location(exif_dict):
    """Thay đổi vị trí GPS"""
    print("\n" + "="*50)
    print("THAY ĐỔI VỊ TRÍ GPS")
    print("="*50)
    print("Nhập tọa độ theo định dạng thập phân")
    print("Ví dụ: Hà Nội: 21.028511, 105.852180")
    
    try:
        latitude = float(input("\nNhập vĩ độ (Latitude): ").strip())
        longitude = float(input("Nhập kinh độ (Longitude): ").strip())
        
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
        
        print(f"✅ Đã cập nhật GPS: {latitude}, {longitude}")
        return True
    except ValueError:
        print("❌ Tọa độ không hợp lệ!")
        return False

def change_camera_info(exif_dict):
    """Thay đổi thông tin máy ảnh"""
    print("\n" + "="*50)
    print("THAY ĐỔI THÔNG TIN MÁY ẢNH")
    print("="*50)
    
    make = input("Nhập hãng máy ảnh (Make) [Enter để bỏ qua]: ").strip()
    if make:
        exif_dict["0th"][piexif.ImageIFD.Make] = make.encode()
        print(f"✅ Đã cập nhật Make: {make}")
    
    model = input("Nhập model máy ảnh (Model) [Enter để bỏ qua]: ").strip()
    if model:
        exif_dict["0th"][piexif.ImageIFD.Model] = model.encode()
        print(f"✅ Đã cập nhật Model: {model}")
    
    lens = input("Nhập tên ống kính (LensModel) [Enter để bỏ qua]: ").strip()
    if lens:
        exif_dict["Exif"][piexif.ExifIFD.LensModel] = lens.encode()
        print(f"✅ Đã cập nhật LensModel: {lens}")
    
    return True

def change_camera_settings(exif_dict):
    """Thay đổi thông số chụp"""
    print("\n" + "="*50)
    print("THAY ĐỔI THÔNG SỐ CHỤP")
    print("="*50)
    
    try:
        # ISO
        iso = input("Nhập ISO [Enter để bỏ qua]: ").strip()
        if iso:
            exif_dict["Exif"][piexif.ExifIFD.ISOSpeedRatings] = int(iso)
            print(f"✅ Đã cập nhật ISO: {iso}")
        
        # Khẩu độ (F-number)
        fnumber = input("Nhập khẩu độ (ví dụ: 2.8) [Enter để bỏ qua]: ").strip()
        if fnumber:
            f_val = float(fnumber)
            exif_dict["Exif"][piexif.ExifIFD.FNumber] = (int(f_val * 10), 10)
            print(f"✅ Đã cập nhật F-number: f/{fnumber}")
        
        # Tốc độ màn trập
        shutter = input("Nhập tốc độ màn trập (ví dụ: 200 cho 1/200s) [Enter để bỏ qua]: ").strip()
        if shutter:
            exif_dict["Exif"][piexif.ExifIFD.ExposureTime] = (1, int(shutter))
            print(f"✅ Đã cập nhật ExposureTime: 1/{shutter}s")
        
        # Tiêu cự
        focal = input("Nhập tiêu cự (mm) [Enter để bỏ qua]: ").strip()
        if focal:
            exif_dict["Exif"][piexif.ExifIFD.FocalLength] = (int(focal), 1)
            print(f"✅ Đã cập nhật FocalLength: {focal}mm")
        
        return True
    except ValueError:
        print("❌ Giá trị không hợp lệ!")
        return False

def change_author_info(exif_dict):
    """Thay đổi thông tin tác giả"""
    print("\n" + "="*50)
    print("THAY ĐỔI THÔNG TIN TÁC GIẢ")
    print("="*50)
    
    artist = input("Nhập tên tác giả (Artist) [Enter để bỏ qua]: ").strip()
    if artist:
        exif_dict["0th"][piexif.ImageIFD.Artist] = artist.encode()
        print(f"✅ Đã cập nhật Artist: {artist}")
    
    copyright_text = input("Nhập thông tin bản quyền (Copyright) [Enter để bỏ qua]: ").strip()
    if copyright_text:
        exif_dict["0th"][piexif.ImageIFD.Copyright] = copyright_text.encode()
        print(f"✅ Đã cập nhật Copyright: {copyright_text}")
    
    software = input("Nhập phần mềm chỉnh sửa (Software) [Enter để bỏ qua]: ").strip()
    if software:
        exif_dict["0th"][piexif.ImageIFD.Software] = software.encode()
        print(f"✅ Đã cập nhật Software: {software}")
    
    return True

def change_file_dates(filename, datetime_str):
    """Thay đổi ngày giờ của file hệ thống"""
    print("\n" + "="*50)
    print("THAY ĐỔI NGÀY GIỜ FILE HỆ THỐNG")
    print("="*50)
    
    try:
        # Chuyển đổi datetime string sang timestamp
        dt = datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")
        timestamp = time.mktime(dt.timetuple())
        
        # Thay đổi access time và modified time
        os.utime(filename, (timestamp, timestamp))
        
        print(f"✅ Đã cập nhật thời gian file:")
        print(f"   - File Modified Date: {datetime_str}")
        print(f"   - File Access Date: {datetime_str}")
        
        # Lưu ý: FileInodeChangeDate không thể thay đổi trực tiếp trên Windows
        if platform.system() != "Windows":
            print(f"   - File Inode Change Date: {datetime_str}")
        else:
            print("   ⚠️ FileInodeChangeDate không thể thay đổi trên Windows")
        
        return True
    except Exception as e:
        print(f"❌ Lỗi khi thay đổi ngày giờ file: {e}")
        return False

def view_current_exif(exif_dict):
    """Xem EXIF hiện tại"""
    print("\n" + "="*50)
    print("THÔNG TIN EXIF HIỆN TẠI")
    print("="*50)
    
    # Thông tin máy ảnh
    print("\n📷 THÔNG TIN MÁY ẢNH:")
    if piexif.ImageIFD.Make in exif_dict["0th"]:
        print(f"   Make: {exif_dict['0th'][piexif.ImageIFD.Make].decode()}")
    if piexif.ImageIFD.Model in exif_dict["0th"]:
        print(f"   Model: {exif_dict['0th'][piexif.ImageIFD.Model].decode()}")
    
    # Thông số chụp
    print("\n⚙️ THÔNG SỐ CHỤP:")
    if piexif.ExifIFD.DateTimeOriginal in exif_dict["Exif"]:
        print(f"   DateTimeOriginal: {exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode()}")
    if piexif.ExifIFD.ISOSpeedRatings in exif_dict["Exif"]:
        print(f"   ISO: {exif_dict['Exif'][piexif.ExifIFD.ISOSpeedRatings]}")
    if piexif.ExifIFD.FNumber in exif_dict["Exif"]:
        f_val = exif_dict['Exif'][piexif.ExifIFD.FNumber]
        print(f"   F-number: f/{f_val[0]/f_val[1]}")
    
    # GPS
    print("\n📍 VỊ TRÍ GPS:")
    if piexif.GPSIFD.GPSLatitude in exif_dict["GPS"]:
        lat = exif_dict["GPS"][piexif.GPSIFD.GPSLatitude][0]
        lat_ref = exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef].decode()
        print(f"   Latitude: {lat[0]/lat[1]} {lat_ref}")
    if piexif.GPSIFD.GPSLongitude in exif_dict["GPS"]:
        lng = exif_dict["GPS"][piexif.GPSIFD.GPSLongitude][0]
        lng_ref = exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef].decode()
        print(f"   Longitude: {lng[0]/lng[1]} {lng_ref}")
    
    input("\nNhấn Enter để tiếp tục...")

def save_changes(filename, exif_dict):
    """Lưu thay đổi vào file"""
    try:
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, filename)
        print("\n✅ Đã lưu tất cả thay đổi vào file!")
        return True
    except Exception as e:
        print(f"\n❌ Lỗi khi lưu file: {e}")
        return False

def main_menu():
    """Menu chính"""
    filename = "11-tests.jpg"
    
    # Kiểm tra file tồn tại
    if not os.path.exists(filename):
        print(f"❌ Không tìm thấy file: {filename}")
        print("Vui lòng đảm bảo file ảnh nằm trong cùng thư mục với script này.")
        return
    
    # Tải EXIF hiện có
    try:
        exif_dict = piexif.load(filename)
    except:
        exif_dict = {"0th":{}, "Exif":{}, "GPS":{}, "1st":{}, "thumbnail":None}
    
    datetime_original = None  # Lưu lại datetime để sync với file system
    
    while True:
        clear_screen()
        print("="*50)
        print("        CHỈNH SỬA EXIF METADATA")
        print("="*50)
        print(f"File: {filename}")
        print("="*50)
        print("\nChọn thao tác:")
        print("1. Thay đổi ngày giờ chụp ảnh (DateTimeOriginal)")
        print("2. Thay đổi vị trí GPS (Location)")
        print("3. Thay đổi thông tin máy ảnh (Make, Model, Lens)")
        print("4. Thay đổi thông số chụp (ISO, F-number, Shutter, Focal Length)")
        print("5. Thay đổi thông tin tác giả (Artist, Copyright, Software)")
        print("6. Đồng bộ ngày giờ file với DateTimeOriginal")
        print("7. Xem thông tin EXIF hiện tại")
        print("8. Lưu tất cả thay đổi")
        print("0. Thoát")
        print("="*50)
        
        choice = input("\nNhập lựa chọn của bạn: ").strip()
        
        if choice == "1":
            result = change_datetime_original(exif_dict)
            if result:
                datetime_original = result
            input("\nNhấn Enter để tiếp tục...")
            
        elif choice == "2":
            change_location(exif_dict)
            input("\nNhấn Enter để tiếp tục...")
            
        elif choice == "3":
            change_camera_info(exif_dict)
            input("\nNhấn Enter để tiếp tục...")
            
        elif choice == "4":
            change_camera_settings(exif_dict)
            input("\nNhấn Enter để tiếp tục...")
            
        elif choice == "5":
            change_author_info(exif_dict)
            input("\nNhấn Enter để tiếp tục...")
            
        elif choice == "6":
            if datetime_original:
                change_file_dates(filename, datetime_original)
            else:
                print("\n⚠️ Vui lòng thiết lập DateTimeOriginal trước (Chọn 1)")
            input("\nNhấn Enter để tiếp tục...")
            
        elif choice == "7":
            view_current_exif(exif_dict)
            
        elif choice == "8":
            if save_changes(filename, exif_dict):
                print("Tất cả thay đổi đã được lưu thành công!")
            input("\nNhấn Enter để tiếp tục...")
            
        elif choice == "0":
            print("\n👋 Cảm ơn bạn đã sử dụng chương trình!")
            break
            
        else:
            print("\n❌ Lựa chọn không hợp lệ!")
            input("\nNhấn Enter để tiếp tục...")

if __name__ == "__main__":
    main_menu()