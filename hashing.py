from copyreg import pickle
import pydicom
from hashlib import sha256
import pickle


def hash_dicom(dataset: pydicom.FileDataset) -> bytes:
    dataset_bytes = pickle.dumps(dataset)
    hash = sha256()
    hash.update(dataset_bytes)
    hash.hexdigest()
    return hash.digest()