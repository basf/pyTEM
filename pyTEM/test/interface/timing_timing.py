"""
Check to see how long the time.time() command takes.

Result: somewhere on the order of e-7 seconds.
"""

import time

iterations = 10000000
start_time = time.time()
for i in range(iterations):
    dummy = time.time()

end_time = time.time()

print((end_time - start_time) / iterations)
