from urllib import response
import pydicom
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

from anonymization import anonymise
from hashing import hash_dicom
from encryption import encrypt_dicom
from send_to_server import send_dicom_to_server
from watermark import watermark_image

if __name__ == "__main__":
    filename = "sample.dcm"
    ds = pydicom.dcmread(filename)
    print("Read DICOM file...")
    print("Dicom file on the client=",ds)


    ds = anonymise(ds)
    print("Anonymized DICOM file...")

    hash = hash_dicom(ds)
    print("Hash generated= ", hash)

    image_array = ds.pixel_array
    
    
    #function that takes pixel array, and hash as arg and returns watermarked pixel array, and dict containing old values
    ds.PixelData, old_values = watermark_image(image_array, hash)
    #Watermarking complete

    peer_public_key, ciphertext, tag = encrypt_dicom(ds, old_values)
    print("Encryption complete! Sending to server...")

    #send this ciphertext and tag to server
    response = send_dicom_to_server(ciphertext, tag, peer_public_key, filename)
    #print(ds)
    if(response.status_code == 200):
        print("Successfully sent file to server!")
    else:
        print('Failed! HTTP', response.status_code)
