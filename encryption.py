import cv2
import numpy as np
import random

# Step 1: Manual Haar Wavelet Transform (single-level)
def haar_wavelet_transform(image):
    image = cv2.resize(image, (256, 256))
    image = np.float32(image)
    rows, cols = image.shape
    temp = np.zeros_like(image)

    # Horizontal transform
    for i in range(rows):
        for j in range(0, cols, 2):
            avg = (image[i, j] + image[i, j+1]) / 2
            diff = (image[i, j] - image[i, j+1]) / 2
            temp[i, j//2] = avg
            temp[i, j//2 + cols//2] = diff

    # Vertical transform
    result = np.zeros_like(temp)
    for j in range(cols):
        for i in range(0, rows, 2):
            avg = (temp[i, j] + temp[i+1, j]) / 2
            diff = (temp[i, j] - temp[i+1, j]) / 2
            result[i//2, j] = avg
            result[i//2 + rows//2, j] = diff

    ll_component = result[:rows//2, :cols//2]
    ll_uint8 = np.uint8(np.clip(ll_component, 0, 255))
    return ll_uint8

# Step 2: Convert image to binary string
def image_to_binary(img):
    flat = img.flatten()
    return ''.join(format(pixel, '08b') for pixel in flat)

# Step 3: Binary to DNA encoding
def binary_to_dna(binary_data):
    mapping = {'00': 'A', '01': 'G', '10': 'C', '11': 'T'}
    return ''.join(mapping[binary_data[i:i+2]] for i in range(0, len(binary_data), 2))

# Step 4: DNA to binary decoding
def dna_to_binary(dna_seq):
    mapping = {'A': '00', 'G': '01', 'C': '10', 'T': '11'}
    return ''.join(mapping.get(base, '00') for base in dna_seq)

# Step 5: Binary to image
def binary_to_image(binary_data, shape=(128, 128)):
    pixels = [int(binary_data[i:i+8], 2) for i in range(0, len(binary_data), 8)]
    array = np.array(pixels, dtype=np.uint8).reshape(shape)
    return array

# Dummy PSO key optimizer
class PSO:
    def __init__(self):
        self.particles = [self.random_key() for _ in range(10)]

    def random_key(self):
        key = list(range(4))
        random.shuffle(key)
        return key

    def fitness(self, key):
        return -sum(key[i] == i for i in range(4))

    def optimize(self):
        best = self.particles[0]
        for key in self.particles:
            if self.fitness(key) > self.fitness(best):
                best = key
        return best

# DNA Encryption
def dna_encrypt(dna_seq, key_order):
    mapping = ['A', 'G', 'C', 'T']
    return ''.join(mapping[key_order[mapping.index(b)]] if b in mapping else b for b in dna_seq)

# DNA Decryption
def dna_decrypt(encrypted_dna, key_order):
    reverse_key = [0]*4
    for i, v in enumerate(key_order):
        reverse_key[v] = i
    mapping = ['A', 'G', 'C', 'T']
    return ''.join(mapping[reverse_key[mapping.index(b)]] if b in mapping else b for b in encrypted_dna)

# Entry function for image preprocessing
def process_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    transformed = haar_wavelet_transform(image)
    return transformed
