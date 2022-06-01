import numpy as np
import os
from pathlib import Path


def write_nparr_to_file(image_array, filename):
    f = open(os.path.join(Path(os.getcwd()).parent, 'ds_diffs',filename), mode = 'w')
    x = image_array.reshape(512,512).tolist()
    for row in x:
        f.write(str(row))
        f.write('\n')
    f.close()
