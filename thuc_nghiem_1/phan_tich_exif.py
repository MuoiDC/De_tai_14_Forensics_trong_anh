import exifread
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
from datetime import datetime

def phan_tich_exif_voi_exifread(duong_dan_anh):
    """
    Phân tích EXIF sử dụng thư viện exifread
    """
    print("=" * 80)
    print("PHÂN TÍCH EXIF VỚI EXIFREAD")
    print("=" * 80)
    
    try:
        with open(duong_dan_anh, 'rb') as f:
            tags = exifread.process_file(f, details=True)
        
        if not tags:
            print("Không tìm thấy dữ liệu EXIF!")
            return None
        # Hiển thị tất cả các tag
        print(f"\nTổng số tag tìm thấy: {len(tags)}\n")
        
        # Nhóm các tag theo loại
        nhom_tags = {
            'Image': [],
            'EXIF': [],
            'GPS': [],
            'Thumbnail': [],
            'Other': []
        }
        
        for tag, value in tags.items():
            if tag.startswith('Image'):
                nhom_tags['Image'].append((tag, value))
            elif tag.startswith('EXIF'):
                nhom_tags['EXIF'].append((tag, value))
            elif tag.startswith('GPS'):
                nhom_tags['GPS'].append((tag, value))
            elif tag.startswith('Thumbnail'):
                nhom_tags['Thumbnail'].append((tag, value))
            else:
                nhom_tags['Other'].append((tag, value))
        
        # Hiển thị các nhóm
        for nhom, items in nhom_tags.items():
            if items:
                print(f"\n--- {nhom} Tags ---")
                for tag, value in items:
                    print(f"{tag:40s}: {value}")
        
        return tags
    
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file {duong_dan_anh}")
        return None
    except Exception as e:
        print(f"Lỗi khi đọc EXIF: {e}")
        return None

def phan_tich_exif_voi_pil(duong_dan_anh):
    """
    Phân tích EXIF sử dụng thư viện PIL/Pillow
    """
    print("\n" + "=" * 80)
    print("PHÂN TÍCH EXIF VỚI PIL/PILLOW")
    print("=" * 80)
    
    try:
        image = Image.open(duong_dan_anh)
        
        # Lấy EXIF data
        exif_data = image._getexif()
        
        if not exif_data:
            print("Không tìm thấy dữ liệu EXIF!")
            return None
        
        print(f"\nTổng số tag tìm thấy: {len(exif_data)}\n")
        
        # Decode EXIF tags
        exif_decoded = {}
        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)
            
            # Xử lý GPS data riêng
            if tag_name == "GPSInfo":
                gps_data = {}
                for gps_tag_id, gps_value in value.items():
                    gps_tag_name = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_data[gps_tag_name] = gps_value
                exif_decoded[tag_name] = gps_data
            else:
                exif_decoded[tag_name] = value
        
        # Hiển thị EXIF data
        for tag, value in sorted(exif_decoded.items()):
            if tag == "GPSInfo":
                print(f"\n--- GPS Information ---")
                for gps_tag, gps_value in value.items():
                    print(f"  {gps_tag:35s}: {gps_value}")
            else:
                # Cắt ngắn giá trị nếu quá dài
                value_str = str(value)
                if len(value_str) > 100:
                    value_str = value_str[:100] + "..."
                print(f"{tag:40s}: {value_str}")
        
        return exif_decoded
    
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file {duong_dan_anh}")
        return None
    except Exception as e:
        print(f"Lỗi khi đọc EXIF: {e}")
        return None

def lay_thong_tin_chi_tiet(duong_dan_anh):
    """
    Lấy thông tin chi tiết quan trọng từ EXIF
    """
    print("\n" + "=" * 80)
    print("THÔNG TIN CHI TIẾT QUAN TRỌNG")
    print("=" * 80)
    
    try:
        with open(duong_dan_anh, 'rb') as f:
            tags = exifread.process_file(f)
        
        # Các thông tin quan trọng
        thong_tin = {
            'Camera': tags.get('Image Model'),
            'Nhà sản xuất': tags.get('Image Make'),
            'Ngày chụp': tags.get('EXIF DateTimeOriginal'),
            'Kích thước ảnh': f"{tags.get('EXIF ExifImageWidth')} x {tags.get('EXIF ExifImageLength')}",
            'Độ phân giải': f"{tags.get('Image XResolution')} x {tags.get('Image YResolution')}",
            'ISO': tags.get('EXIF ISOSpeedRatings'),
            'Khẩu độ': tags.get('EXIF FNumber'),
            'Tốc độ màn trập': tags.get('EXIF ExposureTime'),
            'Tiêu cự': tags.get('EXIF FocalLength'),
            'Flash': tags.get('EXIF Flash'),
            'Chương trình chụp': tags.get('EXIF ExposureProgram'),
            'Cân bằng trắng': tags.get('EXIF WhiteBalance'),
            'Phần mềm': tags.get('Image Software'),
        }
        
        print("\nThông tin camera và cài đặt:")
        print("-" * 80)
        for key, value in thong_tin.items():
            if value:
                print(f"{key:25s}: {value}")
        
        # GPS nếu có
        if 'GPS GPSLatitude' in tags:
            print("\nThông tin GPS:")
            print("-" * 80)
            print(f"Vĩ độ: {tags.get('GPS GPSLatitude')}")
            print(f"Kinh độ: {tags.get('GPS GPSLongitude')}")
            print(f"Độ cao: {tags.get('GPS GPSAltitude')}")
        
        return thong_tin
    
    except Exception as e:
        print(f"Lỗi: {e}")
        return None

def so_sanh_ket_qua(duong_dan_anh):
    """
    So sánh kết quả giữa exifread và PIL
    """
    print("\n" + "=" * 80)
    print("SO SÁNH KẾT QUẢ GIỮA EXIFREAD VÀ PIL")
    print("=" * 80)
    
    # Phân tích với exifread
    with open(duong_dan_anh, 'rb') as f:
        tags_exifread = exifread.process_file(f)
    
    # Phân tích với PIL
    image = Image.open(duong_dan_anh)
    exif_pil = image._getexif()
    
    print(f"\nSố lượng tag tìm thấy:")
    print(f"  - ExifRead: {len(tags_exifread)}")
    print(f"  - PIL/Pillow: {len(exif_pil) if exif_pil else 0}")
    
    print("\nNhận xét:")
    print("  - ExifRead thường tìm thấy nhiều tag hơn và chi tiết hơn")
    print("  - PIL/Pillow nhanh hơn nhưng ít chi tiết hơn")
    print("  - ExifRead tốt hơn cho phân tích forensic")
    print("  - PIL/Pillow tốt hơn cho xử lý ảnh cơ bản")

# ===========================
# CHƯƠNG TRÌNH CHÍNH
# ===========================

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║   PHÂN TÍCH METADATA VÀ EXIF - PHẦN 1                      ║
    ║   Phân tích EXIF của ảnh với exifread và PIL               ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    # Đường dẫn ảnh cần phân tích
    duong_dan_anh = input("Nhập đường dẫn file ảnh cần phân tích: ").strip()
    
    if not os.path.exists(duong_dan_anh):
        print(f"Lỗi: File {duong_dan_anh} không tồn tại!")
        print("\nHướng dẫn:")
        print("1. Upload ảnh vào thư mục hiện tại")
        print("2. Nhập tên file (ví dụ: image.jpg)")
        print("3. Hoặc nhập đường dẫn đầy đủ")
    else:
        # Phân tích với exifread
        tags_exifread = phan_tich_exif_voi_exifread(duong_dan_anh)
        
        # Phân tích với PIL
        exif_pil = phan_tich_exif_voi_pil(duong_dan_anh)
        
        # Lấy thông tin chi tiết
        lay_thong_tin_chi_tiet(duong_dan_anh)
        
        # So sánh kết quả
        if tags_exifread and exif_pil:
            so_sanh_ket_qua(duong_dan_anh)
        
        print("\n" + "=" * 80)
        print("HOÀN THÀNH PHÂN TÍCH!")
        print("=" * 80)