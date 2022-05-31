import pydicom
import os
import argparse

from anonymization import anonymise
from hashing import hash_dicom
from encryption import encrypt_dicom
from send_to_server import send_dicom_to_server
from watermark import watermark_image
from server_address import SERVER_IP, SERVER_PORT

from write_np_to_file import write_nparr_to_file

def driver(filename, anonymization, server, port, sha2, timing):
    print(f'server={server}, port={port}')
    # st = time.time()
    ds_diff_folder = os.path.join("D:\\","VIT","Sem8","Capstone","DICOMSec","ds_diffs")
    ds = pydicom.dcmread(filename)
    print("Read DICOM file...")

    #####################################################################
    write_nparr_to_file(ds.pixel_array, 'after_reading.txt')            #
    fp1 = open(os.path.join(ds_diff_folder,"initial.txt"), mode="w")    #
    print(ds, file=fp1)                                                 #
    fp1.close()                                                         #        
    #####################################################################

    if anonymization == True:
        ds = anonymise(ds)
        # print("Anonymized DICOM file...")
        # print(ds)

    #####################################################################
    write_nparr_to_file(ds.pixel_array, 'after_anonymization.txt')      #
    fp1 = open(os.path.join(ds_diff_folder,"anonymized.txt"), mode="w") #
    print(ds, file=fp1)                                                 #
    fp1.close()                                                         #
    #####################################################################

    hash = hash_dicom(ds, sha2)
    print("Hash in bytes: ", hash)
    
    #####################################################################
    fp2 = open(os.path.join(ds_diff_folder,"hashed.txt"), mode="w")     #
    print(ds, file=fp2)                                                 #
    write_nparr_to_file(ds.pixel_array, 'after_hashing.txt')            #
    fp2.close()                                                         #
    #####################################################################


    image_array = ds.pixel_array
    
    #function that takes pixel array, and hash as arg and returns watermarked pixel array, and dict containing old values
    ds.PixelData, old_values = watermark_image(image_array, hash, timing)
    #Watermarking complete

    #####################################################################
    write_nparr_to_file(ds.pixel_array, 'after_watermarking.txt')       #
    fp3 = open(os.path.join(ds_diff_folder,"watermarked.txt"), mode="w")#
    print(ds, file=fp3)                                                 #
    fp3.close()                                                         #
    #####################################################################
    
    peer_public_key, ciphertext, tag = encrypt_dicom(ds, old_values, server, port)
    print("Encryption complete! Sending to server...")

    #send this ciphertext and tag to server
    response = send_dicom_to_server(ciphertext, tag, peer_public_key, server, port)
    #print(ds)
    if(response.status_code == 200):
        print("Successfully sent file to server!")
    else:
        print('Failed! HTTP', response.status_code)
    
    # Not timing main program because it depends on 
    # print('Main program execution completed in ', time.time()-st)


if __name__ == "__main__":
    # Argparse parser for arguments
    #what all do we want: multiple files, anonymization toggle, server IP address,port
    parser = argparse.ArgumentParser(description='Transfer DICOM files securely')
    
    parser.add_argument('--anonymize', '-a', 
    action='store_true', 
    help='Enable Anonymization')
    
    parser.add_argument('--ip', '-i', type=str,
    help='Server IP Address, default=localhost')

    parser.add_argument('--port', '-p', type=str,
    help='Server Port, default=5000')

    parser.add_argument('--sha2', '-s', 
    action='store_true',
    help="Force use of SHA2_256 as hashing algorithm")

    parser.add_argument('--timing', 
    action='store_true',
    help="Disable display of plots for timing the modules")
    
    parser.add_argument('filename',
     nargs='+',
     help='Enter the name of file/files separated by space')


    args = parser.parse_args()

    filenames = args.filename

    if args.ip:
        print(f'Server IP: {args.ip}')
        server_ip = args.ip
    else:
        print('Server IP: localhost')
        server_ip = SERVER_IP


    if args.port:
        print(f'Port: {args.port}')
        server_port = args.port
    else:
        print('Port: 5000')
        server_port = SERVER_PORT

    if args.sha2:
        print("Please make sure to change server config to use SHA2 instead")
    
    for x in filenames:
        driver(filename = x, anonymization = args.anonymize, server = server_ip, port = server_port, sha2 = args.sha2, timing = args.timing)
