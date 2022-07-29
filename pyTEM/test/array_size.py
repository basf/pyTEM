import numpy as np


def optional_args_func(*args):
    print("args: " + str(args))
    print(len(args))
    print(type(args))


my_arr = np.random.random((3, 1024, 1024))

print(np.shape(my_arr))

print(np.shape(my_arr)[0])

for i in range(np.shape(my_arr)[0]):
    print()
    print(i)
    print(np.shape(my_arr[i]))

print("\n\n-- Testing optional arguments --")
optional_args_func()
optional_args_func(1)
optional_args_func(1, 5, "g")


