from PIL import Image
import numpy as np
import os
import sys

with open("payload.exe", 'rb') as f:
    file_bytes = f.read()
    print(file_bytes[0:100])
binary_data = ''.join(format(byte, '08b') for byte in file_bytes)
print(binary_data[0:100])


header = f"<<EXE_START>>{len(file_bytes):010d}<<DATA_START>>"
binary_header = ''.join(format(ord(c), '08b') for c in header)

print(header)
full_binary = binary_header + binary_data
img = Image.open('land.jpg')
img = img.convert('RGB')
img_array = np.array(img)
print(img_array)
print(img_array.shape[0])
print(img_array.shape[1])
bit_index = 0
for i in range(img_array.shape[0]):
    for j in range(img_array.shape[1]):
        print(img_array[i, j])
        
    
for i in range(img_array.shape[0]):
    for j in range(img_array.shape[1]):
        for k in range(3):  # R, G, B
            if bit_index < len(full_binary):
                # Thay thế LSB
                print(img_array[i, j, k])
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