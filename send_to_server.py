import pickle
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends.openssl.ec import _EllipticCurvePublicKey

def send_dicom_to_server(ciphertext:bytes, tag:bytes, peer_public_key: _EllipticCurvePublicKey):
    public_key_bytes = peer_public_key.public_bytes(
        encoding = serialization.Encoding.PEM,
        format = serialization.PublicFormat.SubjectPublicKeyInfo
    )
    print("Public key bytes format  = ", type(public_key_bytes))
    print("CT format  = ", type(ciphertext))
    print("tag format  = ", type(tag))
    response = requests.get('http://localhost:5000/transfer_dicom',
    data = {'ciphertext': ciphertext,
            'tag': tag,
            'peer_public_key': peer_public_key})
    return response