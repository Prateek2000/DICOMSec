import pydicom
from hashlib import sha3_256, sha256
import pickle
import io
import sys
import time


def hash_dicom(dataset: pydicom.FileDataset, sha2: bool) -> bytes:
    st = time.time()
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

    #print(f'type = {type(ds_metadata)} , metadata = \n{ds_metadata}')
    #print(f'type = {type(ds_image_array)} , metadata = \n{ds_image_array}')

    dataset_bytes = pickle.dumps(ds_metadata+ds_image_array)
    if(sha2 == True):
        hash = sha256()
    else:
        hash = sha3_256()
    hash.update(dataset_bytes)
    print(f'Hash generated: {hash.hexdigest()}')

    hashing_time = time.time()-st
    print("Hashing Time: ", hashing_time)
    fp = open("client_timelogs.txt", mode='a')
    print("Hashing Time: ", hashing_time, file=fp)

    return hash.digest()

if __name__ == '__main__':
    hash = hash_dicom(pydicom.dcmread('D:\VIT\Sem8\Capstone\DICOMSec\sample.dcm'))