import cv2
import numpy as np
import matplotlib.pyplot as plt

BLOCK_SIZE = 8
STEP = 1

def detect_copy_move_basic(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    h, w = img.shape

    blocks = []
    positions = []

    # 1. Chia block
    for y in range(0, h - BLOCK_SIZE + 1, STEP):
        for x in range(0, w - BLOCK_SIZE + 1, STEP):
            block = img[y:y+BLOCK_SIZE, x:x+BLOCK_SIZE]
            blocks.append(block.flatten())
            positions.append((y, x))

    blocks = np.array(blocks) ## Chuyển mảng blocks thành dạng np.array[N,64] -> N là số blocks, 64 pixel

    # 2. Lexicographic sort
    idx = np.lexsort(blocks.T) ## So sánh các block theo thứ tự pixel
    blocks = blocks[idx] ## Sắp xếp lại các blocks idx 
    positions = [positions[i] for i in idx] ## sắp xếp danh sách vị trí không gian của các block

    # 3. So khớp
    mask = np.zeros_like(img)
    for i in range(len(blocks) - 1):
        if np.array_equal(blocks[i], blocks[i+1]):
            y1, x1 = positions[i]
            y2, x2 = positions[i+1]
            mask[y1:y1+BLOCK_SIZE, x1:x1+BLOCK_SIZE] = 255
            mask[y2:y2+BLOCK_SIZE, x2:x2+BLOCK_SIZE] = 255

    return img, mask

# Run
original, mask = detect_copy_move_basic("forged1.png")

plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
plt.imshow(original, cmap='gray')
plt.title("Original")
plt.axis("off")

plt.subplot(1,2,2)
plt.imshow(mask, cmap='gray')
plt.title("Copy-Move (Basic)")
plt.axis("off")
plt.show()


