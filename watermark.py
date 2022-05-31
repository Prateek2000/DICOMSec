import pydicom
import numpy
import math
import random
from matplotlib import pyplot as plt
import time

from hashing import hash_dicom


#Algorithm:

    # find minimum value in pixelarray - Does not work because some images have shades of black instead of a single black colour so there are very few pixels with the same value as the min value
    # choose 256 random pixels without repetition and store their coordinates and value as key:value pairs.
    # Then replace all those 256 pixels with bits of the hash
    # To optimise this store a nibble or byte in each pixel since each pixel can contain values more than just 1 and 0 - Turns out it can store values even upto 10000 (probably even more, 2^16 or 32) and the pixels are rendered relative to the max value. However, we dont want to put values which are huge outliers since that will make it easy to find the pixels containing the hash data. Therefore, we will stick to values below 1024. 1000 seems like a fine upper limit (3 digits of the int conversion of the hash).
    # Pickle the key:value pair dictionary and add it to the GET request to the server
    # Unpickle the dictionary and read all the pixel coordinates given and append them to a string (in case the bits were converted to int then restore them before appending them to the string). This gives us the hash. Replace these with values from the dictionary to restore the pixelarray
    # The max length of 2^m in base n is given

    # max_length=1+⌊m∗logₙ2⌋

    # So in this case, the length of 2^256 in base 10 is

    # =>max_length=1+⌊256∗log102⌋

    # =>max_length=1+⌊77.06367889⌋

    # =>max_length=78

    # Note that the hash length may be less than 78 base 10 digits. In that case we pad the front with zeroes, i.e., the first  78−len(base_10_hash)  digits are zeroes and are filled accordingly in the pixels
#
#


#generate (x,y) | 0<x,y<511
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
        
    watermark_time = time.time()-st
    print("Watermark Time: ", watermark_time)
    fp = open("client_timelogs.txt", mode='a')
    print("Watermark Time: ", watermark_time, file=fp)
    
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

    

    return substituted_image_array.tobytes(), old_values

    
if __name__ == '__main__':
    ds = pydicom.dcmread('sample.dcm')
    image_array = ds.pixel_array
    hash = hash_dicom(ds)
    watermarked_image, old_values = watermark_image(image_array, hash)

    #work in colab notebook
