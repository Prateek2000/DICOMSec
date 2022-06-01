import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends.openssl.ec import _EllipticCurvePublicKey
from base64 import b64encode


def send_dicom_to_server(ciphertext:bytes, tag:bytes, peer_public_key: _EllipticCurvePublicKey, ip: str, port: str):
    public_key_bytes = peer_public_key.public_bytes(
        encoding = serialization.Encoding.PEM,
        format = serialization.PublicFormat.SubjectPublicKeyInfo
    )
    data = {'ciphertext': b64encode(ciphertext).decode('utf-8'),
            'tag': b64encode(tag).decode('utf-8'),
            'peer_public_key_bytes': b64encode(public_key_bytes).decode('utf-8')}

    endpoint = 'http://' + ip + ':' + port + '/transfer_dicom'
    print("Sending get request to: ", endpoint)
    response = requests.get (endpoint, params = data)
    return response