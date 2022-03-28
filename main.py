import pydicom
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from anonymization import anonymise
from hashing import hash_dicom
from encryption import encrypt_dicom
from send_to_server import send_dicom_to_server

if __name__ == "__main__":
    ds = pydicom.dcmread("sample.dcm")
    ds = anonymise(ds)
    hash = hash_dicom(ds)
    image_array = ds.pixel_array
    #function that takes pixel array, and hash as arg and returns watermarked pixel array
    #ds.pixel_array = watermarked_image_array
    peer_public_key, ciphertext, tag = encrypt_dicom(ds)
    #send this ciphertext and tag to server
    response_code = send_dicom_to_server(ciphertext, tag, peer_public_key)
    #print(ds)
    if(response_code == 200):
        print("Done!")
    else:
        print('Failed! HTTP Response Code ', response_code)
