import pickle
import pydicom
from pathlib import Path
from flask import Flask, request, Response
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF #hmac based key derivation fn
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
import matplotlib.pyplot as plt
from base64 import b64decode
import os
import time

from verify_hash import verify_hash
from write_np_to_file import write_nparr_to_file


app = Flask(__name__)

@app.route('/generate_keys', methods=['GET'])
def generate_or_load_key():
    st = time.time()
    global server_private_key 
    private_key_file = Path("keys/server_private_key.pem")
    if private_key_file.is_file():
        with open('keys/server_private_key.pem', 'rb') as key_file:
            server_private_key = serialization.load_pem_private_key(
                key_file.read(),
                password = b'badpassword'
            )
            server_public_key = server_private_key.public_key()
            """
            DO NOT UNCOMMENT THIS 
            IT IS STUPID TO SHOW PRIVATE KEYS 
            DON'T DO IT
            IT IS ONLY FOR DEBUGGING
            print("private key = ", server_private_key.private_bytes(
                encoding = serialization.Encoding.PEM,
                format= serialization.PrivateFormat.PKCS8,
                encryption_algorithm= serialization.NoEncryption()))
            """
            key_load_time = time.time()-st
            print("Key load time: ", key_load_time)
            fp = open("server_timelogs.txt", mode='a')
            print("Key load time: ", key_load_time, file=fp)
            return {
            'public_key': server_public_key.public_bytes(
                encoding = serialization.Encoding.PEM, 
                format = serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8')
            }
        
    else:
        server_private_key = ec.generate_private_key(
            ec.SECP256K1() # Also known as NIST P-256 elliptic curve
        )
        f = open('keys/server_private_key.pem', mode='wb')
        f.write(server_private_key.private_bytes(
            encoding = serialization.Encoding.PEM,
            format = serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(b'badpassword')
        ))
        f.close()
        server_public_key = server_private_key.public_key() 
        """
        DO NOT UNCOMMENT THIS IT IS STUPID TO SHOW PRIVATE KEYS DON'T DO IT
        IT IS ONLY FOR DEBUGGING
        print("private key = ", server_private_key.private_bytes(
                encoding = serialization.Encoding.PEM,
                format = serialization.PrivateFormat.PKCS8,
                encryption_algorithm = serialization.NoEncryption()))
        """
        key_generate_time = time.time()-st
        print("Key generate time: ", key_generate_time)
        fp = open("server_timelogs.txt", mode='a')
        print("Key generate time: ", key_generate_time, file=fp)
        return {
            'public_key': server_public_key.public_bytes(
                encoding = serialization.Encoding.PEM, 
                format = serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8')
        }


@app.route('/transfer_dicom',  methods=['POST'])
def receive_dicom_image():
    print("=======Received dataset=========")
    ciphertext = (request.files['ciphertext']).read()
    tag = b64decode(bytes(request.values.get('tag'), encoding='utf-8'))
    peer_public_key_bytes = b64decode(bytes(request.args.get('peer_public_key_bytes'), encoding='utf-8'))
    
    peer_public_key = serialization.load_pem_public_key(peer_public_key_bytes)
    shared_key = server_private_key.exchange(ec.ECDH(), peer_public_key)
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length = 16,
        salt = None,
        info = b'handshake data'
    ).derive(shared_key)
    
    key = derived_key
    cipher = AESGCM(key)
    data = cipher.decrypt(tag, ciphertext, None) #add header param if used in encryption
    decoded_data = pickle.loads(data)
    dataset: pydicom.FileDataset = decoded_data[0]
    old_values = decoded_data[1]


    #####################################################################################
    ds_diff_folder = os.path.join(Path(os.getcwd()).parent, 'ds_diffs')      #
    fp = open(os.path.join(ds_diff_folder,"received.txt"), mode="w")                    #
    print(dataset, file=fp)
    write_nparr_to_file(dataset.pixel_array, 'after_receiving.txt')                                                              #
    fp.close()                                                                          #
    #####################################################################################

    """
    image_array = dataset.pixel_array
    plt.imshow(image_array, cmap=plt.cm.bone)
    plt.show()
    """
    hash_success = verify_hash(dataset, old_values)
    if(hash_success != '0'):
        # dataset.save_as('received_files/'+filename, write_like_original=False)
        #maybe add feature to save multiple files with new numbers for each, or get filename from client
        dataset.save_as('received_files/'+hash_success, write_like_original=True) #should be in if statement  
        print("File saved")  
        return(Response('OK'))
    else:
        return(Response('Hash did not match'))


if __name__=='__main__':
    import logging
    logging.basicConfig(filename='error.log', level=logging.DEBUG)
    app.run(debug=True, host='0.0.0.0', port=5000)