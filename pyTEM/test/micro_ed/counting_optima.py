import numpy as np
from scipy.signal import argrelextrema

shifts = np.random.random(12)

local_maxima = argrelextrema(shifts, np.greater)[0]
local_minima = argrelextrema(shifts, np.less)[0]

print(type(local_minima[0]))

print(local_minima)

print(type(local_maxima))
print(type(local_minima))

optima = np.concatenate((local_minima, local_maxima))
print(optima)
