import pydicom
from hashlib import sha256
import pickle
import sys
import io
import os
import time

from write_np_to_file import write_nparr_to_file

def verify_hash(dataset: pydicom.FileDataset, old_values: dict) -> str:
    st = time.time()
    watermarked_image_array = dataset.pixel_array
    restored_image_array = watermarked_image_array
    int_old_hash_parts = [] 
    for coord, value in old_values.items():
        (x, y) = coord
        #retrieve the watermarked hash
        int_old_hash_parts.append(str(watermarked_image_array[x, y]).zfill(3))
        #restore old values
        restored_image_array[x, y] = value
    


    # print(f'old hash values = {int_old_hash_parts}')
    #zip magic after this
    old_hash_str = zip(*int_old_hash_parts) #transposes the list and returns 3 tuples containing 26 elements each
    old_hash_str = list(map(''.join, old_hash_str)) #applies the string join operation to the 3 tuples of transposed list and returns 3 strings in a list
    old_hash_str = ''.join(old_hash_str) #joins the 3 strings in the list
    # print(f'old hash int={old_hash_int}')
    old_hash_int = int(old_hash_str)
    # print(f'old hash str = {old_hash_str}, of type {type(old_hash_str)}')
    print(f'old hash int: {old_hash_int}')
    old_hash = old_hash_int.to_bytes(length=32, byteorder='little', signed=False)

    
    ####################################################################
    # Replaces the watermarked pixel data with the restored pixel data #
    ####################################################################
    dataset.PixelData = restored_image_array.tobytes()
    

    #####################################################################################
    ds_diff_folder = os.path.join("D:\\","VIT","Sem8","Capstone","DICOMSec","ds_diffs") #
    fp = open(os.path.join(ds_diff_folder,"restored.txt"), mode="w")                    #
    print(dataset, file=fp)                                                             #
    write_nparr_to_file(dataset.pixel_array, 'after_restoring.txt')                     #                                        #
    fp.close()                                                                          #
    #####################################################################################



    old_stdout = sys.stdout
    new_stdout_metadata = io.StringIO()
    new_stdout_array = io.StringIO()

    sys.stdout = new_stdout_metadata
    print(dataset)
    ds_metadata = new_stdout_metadata.getvalue()

    sys.stdout = new_stdout_array
    print(dataset.pixel_array)
    ds_image_array = new_stdout_array.getvalue()

    sys.stdout = old_stdout

    # print(f'type = {type(ds_metadata)} , metadata = \n{ds_metadata}')
    # print(f'type = {type(ds_image_array)} , metadata = \n{ds_image_array}')

    
    restored_dataset_bytes = pickle.dumps(ds_metadata+ds_image_array)
    hash = sha256()
    hash.update(restored_dataset_bytes)
    print("New hash calculated: ", hash.hexdigest())
    new_hash = hash.digest()

    if (new_hash == old_hash):
        print(f'Hash match')
        hash_verification_time = time.time()-st
        print("Hash verification time: ", hash_verification_time)
        fp = open("server_timelogs.txt", mode='a')
        print("Hash verification time: ", hash_verification_time, file=fp)
        return str(hash.hexdigest())
    else:
        print(f'Hash not match')
        print(f'Old hash = {old_hash}')
        print(f'New hash = {new_hash}')
        hash_verification_time = time.time()-st
        print("Hash verification time: ", hash_verification_time)
        fp = open("server_timelogs.txt", mode='a')
        print("Hash verification time: ", hash_verification_time, file=fp)
        return '0'


    #compare this hash with whatever we used for generating the old hash
