from copyreg import pickle
import pydicom
from Cryptodome.Hash import SHA256
import pickle


def hash_dicom(dataset: pydicom.FileDataset) -> bytes:
    dataset_bytes = pickle.dumps(dataset)
    hash = SHA256.new()
    hash.update(dataset_bytes)
    print(hash.hexdigest())
    return hash.digest()