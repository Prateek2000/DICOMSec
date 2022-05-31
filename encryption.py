import pydicom
import pickle
import os
import requests
import time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF #hmac based key derivation fn
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization 
from cryptography.hazmat.backends.openssl.ec import _EllipticCurvePublicKey

Encrypted_Dicom_Return = tuple[_EllipticCurvePublicKey, bytes, bytes]

def encrypt_dicom(dataset: pydicom.FileDataset, old_values: dict, ip: str, port: str) -> Encrypted_Dicom_Return:
    #EC DH to generate shared key over insecure medium
    # we are peer, server is server (rpi).
    server_public_key = get_server_public_key(ip, port)
    st = time.time()
    peer_private_key = ec.generate_private_key(
        ec.SECP256K1() # Also known as NIST P-256 elliptic curve
    )
    peer_public_key = peer_private_key.public_key() #To send to server
    shared_key = peer_private_key.exchange(ec.ECDH(), server_public_key)
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length = 16,
        salt = None,
        info = b'handshake data'
    ).derive(shared_key)
    #Use this derived key as AES key
    
    header = b"authenticated, unencrypted data" 
    """
    #not using anything as header for now but possibly metadata of DICOM? 
    need to think if sending it as plaintext is okay
    """
    data = pickle.dumps([dataset,old_values])
    key = derived_key 
    # print("length of derived key =", len(derived_key))
    tag = os.urandom(12)
    cipher = AESGCM(key)    
    ciphertext = cipher.encrypt(tag, data, None) #optionally add header
    """
    tag is for authentication of data+header
    data is plaintext
    header is unencrypted but authenticated during decryption
    """

    encryption_time = time.time()-st
    print("Encryption Time: ", encryption_time)
    fp = open("client_timelogs.txt", mode='a')
    print("Encryption Time: ", encryption_time, file=fp)

    return peer_public_key, ciphertext, tag


def get_server_public_key(ip: str, port: str):
    endpoint = 'http://' + ip + ':' + port + '/generate_keys'
    print("Sending get request to: ", endpoint)
    response = requests.get(endpoint)
    server_public_key = serialization.load_pem_public_key(
        bytes(response.json()['public_key'], encoding='utf-8')
    )
    return server_public_key