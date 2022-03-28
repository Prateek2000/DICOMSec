import pydicom
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from anonymization import anonymise

if __name__ == "__main__":
    ds = pydicom.dcmread("sample.dcm")
    ds = anonymise(ds)
    print(ds)
