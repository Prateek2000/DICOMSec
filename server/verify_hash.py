import pydicom
from hashlib import sha256
import pickle

def verify_hash(dataset: pydicom.FileDataset, old_values: dict) -> bool:
    watermarked_image_array = dataset.pixel_array
    restored_image_array = watermarked_image_array
    int_old_hash_parts = [] 
    for coord, value in old_values.items():
        (x, y) = coord
        #retrieve the watermarked hash
        int_old_hash_parts.append(str(watermarked_image_array[x, y]).zfill(3))
        #restore old values
        restored_image_array[x, y] = value
    
    print(f'old hash values = {int_old_hash_parts}')
    #zip magic after this
    old_hash_str = zip(*int_old_hash_parts) #transposes the list and returns 3 tuples containing 26 elements each
    old_hash_str = list(map(''.join, old_hash_str)) #applies the string join operation to the 3 tuples of transposed list and returns 3 strings in a list
    old_hash_str = ''.join(old_hash_str) #joins the 3 strings in the list
    # print(f'old hash int={old_hash_int}')
    old_hash_int = int(old_hash_str)
    print(f'old hash str = {old_hash_str}, of type {type(old_hash_str)}')
    print(f'old hash int = {old_hash_int}, of type {type(old_hash_int)}')
    old_hash = old_hash_int.to_bytes(length=32, byteorder='little', signed=False)


    ####################################################################
    # Replaces the watermarked pixel data with the restored pixel data #
    ####################################################################
    dataset.PixelData = restored_image_array.tobytes()

    
    restored_dataset_bytes = pickle.dumps(dataset)
    hash = sha256()
    hash.update(restored_dataset_bytes)
    hash.hexdigest()
    new_hash = hash.digest()

    if (new_hash == old_hash):
        return True
    else:
        print(f'Old hash = {old_hash}')
        print(f'New hash = {new_hash}')
        return False


    #compare this hash with whatever we used for generating the old hash
