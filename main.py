import math
import numpy as np


def test(a):
    """Stupid test function"""
    return pow(a, 5) - 4 * pow(a, 4) + 3 * pow(a, 3) - 2 * pow(a, 2) + a - 1


import time
t = time.time()

for i in xrange(20):
    a = np.linspace(0 + i * 100, 100 + i * 100, 200)
    test(a)
    print time.time() - t
    t = time.time()