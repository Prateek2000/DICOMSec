import pickle
from pathlib import Path
from flask import Flask, request, Response
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF #hmac based key derivation fn
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes


app = Flask(__name__)

@app.route('/generate_keys')
def generate_or_load_key():
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
            DO NOT UNCOMMENT THIS IT IS STUPID TO SHOW PRIVATE KEYS DON'T DO IT
            IT IS ONLY FOR DEBUGGING
            print("private key = ", server_private_key.private_bytes(
                encoding = serialization.Encoding.PEM,
                format= serialization.PrivateFormat.PKCS8,
                encryption_algorithm= serialization.NoEncryption()))
            """
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
        return {
            'public_key': server_public_key.public_bytes(
                encoding = serialization.Encoding.PEM, 
                format = serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8')
        }


@app.route('/transfer_dicom')
def receive_dicom_image():
    print("=======Received payload=========")
    data = request.args
    print("type of data=", type(data))
    print("headers=", request.headers)
    print("data=", data)
    rameshbytes = request.args.get('ramesh', type=bytes)
    print("Type of value=", type(data['ramesh']))
    """
    ciphertext = bytes(request.args.get('ciphertext', type=str), encoding='utf-8')
    tag = bytes(request.args.get('tag', type=str), encoding='utf-8')
    peer_public_key_bytes = bytes(request.args.get('peer_public_key', type=str), encoding='utf-8')
    peer_public_key = serialization.load_pem_public_key(peer_public_key_bytes)
    print('peer public key bytes type=',type(peer_public_key_bytes))
    print('ct type=',type(ciphertext))
    print('tag type=',type(tag))
    shared_key = server_private_key.exchange(ec.ECDH(), peer_public_key_bytes)
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length = 16,
        salt = None,
        info = b'handshake data'
    ).derive(shared_key)
    
    key = derived_key
    cipher = AESGCM(key)
    data = cipher.decrypt(tag, ciphertext, None) #add header param if used in encryption
    dataset = pickle.loads(data)
    print("Data type = ", type(dataset))
    """
    return Response('Server received file')



if __name__=='__main__':
    import logging
    logging.basicConfig(filename='error.log', level=logging.DEBUG)
    app.run(host='0.0.0.0', port=5000)