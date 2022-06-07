import pathlib
import sys

from HelperMixIn1 import HelperMixIn1
from HelperMixIn2 import HelperMixIn2

# package_directory = pathlib.Path().resolve().parent.resolve()
# sys.path.append(str(package_directory))


class BigClass(HelperMixIn1, HelperMixIn2):
    """

    """

    def __init__(self):
        self._attribute1 = 5
        self._attribute2 = 6


if __name__ == "__main__":
    """
    """

    my_big_class = BigClass()
    # print(my_big_class.__attribute1)
    print(my_big_class.add_attributes())
    print(my_big_class.complicated_expression())
