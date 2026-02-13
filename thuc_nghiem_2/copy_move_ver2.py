import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import dct
from collections import defaultdict

# =============================
# PARAMETERS
# =============================
BLOCK_SIZE = 8
STEP = 1
QUANT = 15
MIN_SHIFT = 20
MIN_MATCHES = 10
DIST_THRESH = 1e-5

# =============================
# 2D DCT
# =============================
def dct2(block):
    return dct(dct(block.T, norm='ortho').T, norm='ortho')

# =============================
# COPY-MOVE DETECTION
# =============================
def detect_copy_move(image_path):
    # Load images
    img_gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img_color = cv2.imread(image_path)

    if img_gray is None:
        raise ValueError("Cannot load image")

    h, w = img_gray.shape

    features = []
    positions = []

    # 1. Divide into blocks + DCT features
    for y in range(0, h - BLOCK_SIZE + 1, STEP):
        for x in range(0, w - BLOCK_SIZE + 1, STEP):
            block = img_gray[y:y+BLOCK_SIZE, x:x+BLOCK_SIZE]

            dct_block = dct2(block)
            coeffs = dct_block[:4, :4].flatten()
            coeffs_q = np.round(coeffs / QUANT)

            features.append(coeffs_q)
            positions.append((y, x))

    features = np.array(features)

    # 2. Lexicographic sorting
    idx = np.lexsort(features.T)
    features = features[idx]
    positions = [positions[i] for i in idx]

    # 3. Matching + shift clustering
    shift_groups = defaultdict(list)

    for i in range(len(features) - 1):
        if np.linalg.norm(features[i] - features[i+1]) < DIST_THRESH:
            y1, x1 = positions[i]
            y2, x2 = positions[i+1]

            dx = x2 - x1
            dy = y2 - y1

            if np.hypot(dx, dy) > MIN_SHIFT:
                shift_groups[(dx, dy)].append((y1, x1, y2, x2))

    # 4. Create binary mask
    mask = np.zeros((h, w), dtype=np.uint8)

    for pairs in shift_groups.values():
        if len(pairs) >= MIN_MATCHES:
            for y1, x1, y2, x2 in pairs:
                mask[y1:y1+BLOCK_SIZE, x1:x1+BLOCK_SIZE] = 255
                mask[y2:y2+BLOCK_SIZE, x2:x2+BLOCK_SIZE] = 255

    # 5. Morphological refinement
    kernel = np.ones((7, 7), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.medianBlur(mask, 5)

    # 6. Apply mask to color image (OUTPUT LIKE YOUR IMAGE)
    masked_output = cv2.bitwise_and(img_color, img_color, mask=mask)

    return img_color, mask, masked_output

# =============================
# RUN
# =============================
if __name__ == "__main__":
    image_path = "forged1.png"  # đổi tên nếu cần

    original, mask, output = detect_copy_move(image_path)

    plt.figure(figsize=(15, 5))

    plt.subplot(1, 3, 1)
    plt.imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
    plt.title("Original")
    plt.axis("off")

    plt.subplot(1, 3, 2)
    plt.imshow(mask, cmap='gray')
    plt.title("Binary Mask")
    plt.axis("off")

    plt.subplot(1, 3, 3)
    plt.imshow(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))
    plt.title("Copy-Move Region (Black Background)")
    plt.axis("off")

    plt.tight_layout()
    plt.show()
