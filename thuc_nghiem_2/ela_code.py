import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path


class ELAAnalyzer:
    def __init__(self, quality: int):
        self.quality = quality
        self.original_image = None
        self.recompressed_image = None
        self.ela_map = None

    def load_image(self, image_path: str):
        if not os.path.exists(image_path):
            raise FileNotFoundError("❌ Không tìm thấy ảnh")

        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("❌ Không đọc được ảnh")

        self.original_image = image
        return image

    def recompress_jpeg(self, image):
        param = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
        _, buffer = cv2.imencode(".jpg", image, param)
        self.recompressed_image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)

    def compute_ela_color(self):
        # Absolute difference (GIỮ NGUYÊN RGB)
        diff = cv2.absdiff(self.original_image, self.recompressed_image)

        # Scale mạnh để nhìn rõ
        max_val = np.max(diff)
        scale = 255.0 / max_val if max_val != 0 else 1

        ela_color = np.clip(diff * scale, 0, 255).astype(np.uint8)
        self.ela_map = ela_color
        return ela_color

    def save_ela(self, image_path):
        out = Path(image_path).with_name(
            f"{Path(image_path).stem}_ELA_Q{self.quality}.jpg"
        )
        cv2.imwrite(str(out), self.ela_map)
        print(f"✅ Đã lưu ELA: {out}")

    def show(self):
        # OpenCV đọc BGR → chuyển sang RGB để hiển thị đúng màu
        ela_rgb = cv2.cvtColor(self.ela_map, cv2.COLOR_BGR2RGB)
        plt.imshow(ela_rgb)
        plt.title(f"ELA Result (Q={self.quality})")
        plt.axis("off")
        plt.show()


def run_ela():
    image_path = input("📂 Nhập đường dẫn ảnh: ").strip()
    q = input("🎚️ Nhập quality (1–100, mặc định 85): ").strip()

    if q == "":
        q = 85
    else:
        q = int(q)

    if not (1 <= q <= 100):
        print("❌ Quality không hợp lệ")
        return

    ela = ELAAnalyzer(q)

    try:
        img = ela.load_image(image_path)
        ela.recompress_jpeg(img)
        ela.compute_ela_color()   # ← đúng tên hàm
        ela.save_ela(image_path)
        ela.show()
    except Exception as e:
        print(e)


def menu():
    while True:
        print("\n=== ELA IMAGE FORENSICS TOOL ===")
        print("1. Phân tích ảnh (ELA)")
        print("0. Thoát")

        choice = input("👉 Chọn: ").strip()

        if choice == "1":
            run_ela()
        elif choice == "0":
            print("👋 Thoát chương trình")
            break
        else:
            print("❌ Lựa chọn không hợp lệ")


if __name__ == "__main__":
    menu()
