import numpy as np
import pydicom
from matplotlib import pyplot as plt
from pathlib import Path

p = Path(__file__).parents[1]



ds = pydicom.dcmread(str(p)+'/sample.dcm')
image_array = ds.pixel_array
np.save('image_output', image_array)
image_array = np.load('image_output.npy')
f = open('nparray.txt', mode = 'w')
x = image_array.reshape(512,512).tolist()
max = 0
for row in x:
    for value in row:
        if value>max:
            max = value
print("max=", max)
for row in x:
    f.write(str(row))
    f.write('\n')
f.close()
plt.imshow(image_array, cmap=plt.cm.bone)
plt.show()