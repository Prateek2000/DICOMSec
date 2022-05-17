import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends.openssl.ec import _EllipticCurvePublicKey
from base64 import b64encode

def send_dicom_to_server(ciphertext:bytes, tag:bytes, peer_public_key: _EllipticCurvePublicKey, filename: str):
    public_key_bytes = peer_public_key.public_bytes(
        encoding = serialization.Encoding.PEM,
        format = serialization.PublicFormat.SubjectPublicKeyInfo
    )
    data = {'ciphertext': b64encode(ciphertext).decode('utf-8'),
            'tag': b64encode(tag).decode('utf-8'),
            'peer_public_key_bytes': b64encode(public_key_bytes).decode('utf-8'),
            'filename': filename}

    response = requests.get ('http://localhost:5000/transfer_dicom',
    params = data
    )
    return response