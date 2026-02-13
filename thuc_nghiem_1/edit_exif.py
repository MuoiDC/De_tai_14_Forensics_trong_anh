import piexif

filename = "11-tests.jpg"

# 1. Tải EXIF hiện có
try:
    exif_dict = piexif.load(filename)
except:
    # Tạo mới nếu chưa có
    exif_dict = {"0th":{}, "Exif":{}, "GPS":{}, "1st":{}, "thumbnail":None}

# --- THAY ĐỔI MAKE VÀ MODEL (Nằm trong nhóm "0th") ---
# Lưu ý: Các chuỗi ký tự phải chuyển sang dạng bytes (thêm b phía trước)
exif_dict["0th"][piexif.ImageIFD.Make] = b"Canon"
exif_dict["0th"][piexif.ImageIFD.Model] = b"Canon EOS R5"

# --- THAY ĐỔI SUBIFD (Nhóm "Exif") ---
# Đây là nơi chứa các thông số chụp (ISO, Khẩu, Tốc, Ngày giờ gốc...)
# Ví dụ: Thay đổi ngày giờ chụp ảnh (DateTimeOriginal)
# Định dạng bắt buộc: "YYYY:MM:DD HH:MM:SS"
exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = b"2026:12:25 08:30:00"
exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = b"2026:12:25 08:30:00"

# Ví dụ khác: Thay đổi ISO (ISOSpeedRatings) - Giá trị là số nguyên
exif_dict["Exif"][piexif.ExifIFD.ISOSpeedRatings] = 100

# --- THAY ĐỔI GPS IFD (Nhóm "GPS") ---
# GPS phức tạp hơn vì nó yêu cầu định dạng số hữu tỉ (Rational): (tử số, mẫu số)
# Ví dụ set tọa độ cho Tháp Rùa, Hà Nội: 21.028511, 105.852180

def change_to_rational(number):
    """Hàm phụ trợ để đổi số thập phân sang dạng phân số cho GPS"""
    f = float(number)
    return (int(f * 1000000), 1000000)

# 1. Ghi vĩ độ (Latitude)
exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = b"N" # N là Bắc, S là Nam
# Cần 3 giá trị: Độ, Phút, Giây. Để đơn giản ta quy đổi hết ra độ.
# Dạng piexif yêu cầu là list gồm 3 tuple: [(độ,1), (phút,1), (giây,1)]
# Cách đơn giản nhất là set thẳng độ vào phần đầu tiên, phút giây để 0
lat_rational = change_to_rational(21.028511)
exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] = [lat_rational, (0, 1), (0, 1)]

# 2. Ghi kinh độ (Longitude)
exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = b"E" # E là Đông, W là Tây
lng_rational = change_to_rational(105.852180)
exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] = [lng_rational, (0, 1), (0, 1)]

# --- LƯU LẠI VÀO FILE ---
exif_bytes = piexif.dump(exif_dict)
piexif.insert(exif_bytes, filename)
print("Đã cập nhật Make, Model, SubIFD và GPS thành công!")