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
    plt.imshow(image_array, cmap=plt.cm.bone)
    plt.show()
    #function that takes pixel array, and hash as arg and returns watermarked pixel array
    #ds.pixel_array = watermarked_image_array
    #Watermarking complete

    peer_public_key, ciphertext, tag = encrypt_dicom(ds)
    print("Encryption complete! Sending to server...")

    #send this ciphertext and tag to server
    response = send_dicom_to_server(ciphertext, tag, peer_public_key, filename)
    #print(ds)
    if(response.status_code == 200):
        print("Successfully sent file to server!")
    else:
        print('Failed! HTTP', response.status_code)
