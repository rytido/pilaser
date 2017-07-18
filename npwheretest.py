from time import sleep, time
import numpy as np

a = np.random.random((640,480))
t0 = time()
for i in range(300):
    #(a>.95).sum()
    #np.argwhere(a>.95)
    #np.count_nonzero(a>.95)
    np.transpose(np.unravel_index(np.where((a>.95).ravel())[0], a.shape))
    #np.where(a>.95)
    #np.any(a>.95)
print(time() - t0)
