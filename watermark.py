import pydicom
import numpy
import math
import random
from matplotlib import pyplot as plt
import time

from hashing import hash_dicom


def generate_random_2tuples(dimension: int, count: int) -> tuple:
  raw_sample = random.sample(range(dimension**2), count) #generates "count" (256) tuples containing random values in range "dimension"^2 (512*512)
  decoded_sample = [divmod(x, dimension) for x in raw_sample] #decodes the 256 numbers into quotient and remainder when divided by 512 (generates unique pairs for each unique number)
  return tuple(decoded_sample)


def watermark_image(image_array: numpy.ndarray , hash: bytes) -> tuple[bytes, dict]:
    st = time.time()

    substituted_image_array = image_array
    array_dimension = 512
    required_hash_length = 78

    if substituted_image_array.size != array_dimension ** 2:
        print("Error: Unexpected Scenario: Image is not of dimension 512*512.")
    
    hash_int = int.from_bytes(hash, byteorder='little', signed=False)
    print("Integerified bytes of hash: ", hash_int )
    #split hash_int to 3 digit pieces (reasoning above) and place them in random pixels on the image
    #get 78/3 random pixels = 26 
    number_of_pixels_to_substitute = math.ceil(required_hash_length/3)
    tuple_of_pixels_to_substitute = generate_random_2tuples(array_dimension, number_of_pixels_to_substitute)
    # print(tuple_of_pixels_to_substitute)
    
    #convert hash to string and pad front
    hash_string = str(hash_int).zfill(required_hash_length)
    # print(hash_string)

    #store the address and value of the random pixels in a dictionary and recover it on receiver side
    old_values = {}
    cursor = 0
    for i in tuple_of_pixels_to_substitute:
        old_values[i] = substituted_image_array[i[0], i[1]]
        # print(f"cursor value={cursor}")
        if (cursor >=26):
            print("cursor exceeds 26, check if all the values are being stored properly")
        #print(f'Changing value at position {i[0]}, {i[1]} to {hash_string[cursor::26]}')
        substituted_image_array[i[0], i[1]] = int(hash_string[cursor::26]) # take every 26th digit from position cursor and make a string of length 3 (this should reduce the chance of finding parts of the hash and reconstructing it)
        #print(f'New value at position {i[0]}, {i[1]} is {substituted_image_array[i[0], i[1]]}')
        cursor = cursor + 1
    
    
    fig = plt.figure()
    #old
    fig.add_subplot(1,2,1)
    plt.imshow(image_array, cmap = plt.cm.bone)
    plt.axis('off')
    plt.title('Old')
    #new

    fig.add_subplot(1, 2, 2)
    plt.imshow(substituted_image_array, cmap = plt.cm.bone)
    plt.axis('off')
    plt.title('Watermarked')
    plt.show()
    
    #print("Dict containing old values")
    #print(f'{old_values} of length {len(old_values)}')

    print("Watermark Time: ", time.time()-st)

    return substituted_image_array.tobytes(), old_values

    
if __name__ == '__main__':
    ds = pydicom.dcmread('sample.dcm')
    image_array = ds.pixel_array
    hash = hash_dicom(ds)
    watermarked_image, old_values = watermark_image(image_array, hash)

    #work in colab notebook
