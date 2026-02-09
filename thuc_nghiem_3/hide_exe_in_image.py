"""
Hide EXE in Image using LSB Steganography
Giấu file EXE vào ảnh bằng kỹ thuật LSB
"""

from PIL import Image
import numpy as np
import os
import sys

class ExeHider:
    def __init__(self):
        self.HEADER_MARKER = "<<EXE_START>>"
        self.FOOTER_MARKER = "<<EXE_END>>"
    
    def file_to_binary(self, file_path):
        """Chuyển file thành chuỗi binary"""
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        
        binary = ''.join(format(byte, '08b') for byte in file_bytes)
        return binary, len(file_bytes)
    
    def create_header(self, file_size):
        """Tạo header chứa metadata"""
        header = f"{self.HEADER_MARKER}{file_size:010d}<<DATA_START>>"
        return ''.join(format(ord(c), '08b') for c in header)
    
    def hide_exe(self, image_path, exe_path, output_path):
        """
        Giấu EXE vào ảnh
        
        Args:
            image_path: Đường dẫn ảnh gốc
            exe_path: Đường dẫn file EXE cần giấu
            output_path: Đường dẫn ảnh output
        """
        print("=" * 60)
        print("HIDING EXE IN IMAGE")
        print("=" * 60)
        
        # 1. Đọc EXE file
        print(f"[1/5] Reading EXE file: {exe_path}")
        exe_binary, exe_size = self.file_to_binary(exe_path)
        print(f"      ✓ EXE size: {exe_size:,} bytes")
        
        # 2. Tạo header
        print(f"[2/5] Creating header...")
        header_binary = self.create_header(exe_size)
        
        # 3. Ghép header + data
        full_binary = header_binary + exe_binary
        print(f"      ✓ Total bits to hide: {len(full_binary):,}")
        
        # 4. Mở ảnh
        print(f"[3/5] Loading image: {image_path}")
        img = Image.open(image_path)
        
        # Convert sang RGB nếu cần
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img_array = np.array(img)
        print(f"      ✓ Image size: {img.size[0]} x {img.size[1]}")
        
        # 5. Kiểm tra capacity
        print(f"[4/5] Checking capacity...")
        total_pixels = img_array.shape[0] * img_array.shape[1]
        max_bits = total_pixels * 3  # 3 channels RGB
        
        if len(full_binary) > max_bits:
            print(f"      ✗ ERROR: EXE too large!")
            print(f"        Need: {len(full_binary):,} bits")
            print(f"        Have: {max_bits:,} bits")
            print(f"\n      Solutions:")
            print(f"        - Use larger image")
            print(f"        - Compress the EXE")
            sys.exit(1)
        
        usage_percent = (len(full_binary) / max_bits) * 100
        print(f"      ✓ Capacity: {len(full_binary):,} / {max_bits:,} bits ({usage_percent:.2f}%)")
        
        # 6. Giấu vào LSB
        print(f"[5/5] Hiding data in LSB...")
        bit_index = 0
        
        for i in range(img_array.shape[0]):
            for j in range(img_array.shape[1]):
                for k in range(3):  # R, G, B
                    if bit_index < len(full_binary):
                        # Thay thế LSB
                        img_array[i, j, k] = (img_array[i, j, k] & 0xFE) | \
                                              int(full_binary[bit_index])
                        bit_index += 1
                    else:
                        break
                if bit_index >= len(full_binary):
                    break
            if bit_index >= len(full_binary):
                break
            
            # Progress bar
            if i % 100 == 0:
                progress = (bit_index / len(full_binary)) * 100
                print(f"      Progress: {progress:.1f}%", end='\r')
        
        print(f"      ✓ Data hidden: 100.0%")
        
        # 7. Lưu ảnh
        result = Image.fromarray(img_array)
        result.save(output_path, 'PNG')
        
        output_size = os.path.getsize(output_path)
        print(f"\n      ✓ Saved: {output_path}")
        print(f"      ✓ Output size: {output_size:,} bytes")
        
        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        
        # Thông tin tổng kết
        print(f"\nOriginal Image : {image_path}")
        print(f"Hidden Payload : {exe_path} ({exe_size:,} bytes)")
        print(f"Output Image   : {output_path} ({output_size:,} bytes)")
        print(f"Capacity Used  : {usage_percent:.2f}%")
        
        return True

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Hide EXE file in image using LSB steganography'
    )
    parser.add_argument('image', help='Path to cover image')
    parser.add_argument('exe', help='Path to EXE file to hide')
    parser.add_argument('-o', '--output', default='stego_image.png',
                        help='Output stego image path (default: stego_image.png)')
    
    args = parser.parse_args()
    
    # Kiểm tra file tồn tại
    if not os.path.exists(args.image):
        print(f"Error: Image not found: {args.image}")
        sys.exit(1)
    
    if not os.path.exists(args.exe):
        print(f"Error: EXE not found: {args.exe}")
        sys.exit(1)
    
    # Giấu EXE
    hider = ExeHider()
    hider.hide_exe(args.image, args.exe, args.output)

if __name__ == '__main__':
    main()