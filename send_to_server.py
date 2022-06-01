import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends.openssl.ec import _EllipticCurvePublicKey
from base64 import b64encode
from io import BytesIO


def send_dicom_to_server(ciphertext:bytes, tag:bytes, peer_public_key: _EllipticCurvePublicKey, ip: str, port: str):
    public_key_bytes = peer_public_key.public_bytes(
        encoding = serialization.Encoding.PEM,
        format = serialization.PublicFormat.SubjectPublicKeyInfo
    )
    files = {'ciphertext': BytesIO(ciphertext)}
    data = {'tag': b64encode(tag).decode('utf-8'),
            'peer_public_key_bytes': b64encode(public_key_bytes).decode('utf-8')}

    endpoint = 'http://' + ip + ':' + port + '/transfer_dicom'
    print("Sending ciphertext over POST request to server")
    response = requests.post(endpoint, params = data, files=files)
    return response