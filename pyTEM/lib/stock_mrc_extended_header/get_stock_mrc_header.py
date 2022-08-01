"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import os
import numpy as np
BASEDIR = os.path.dirname(os.path.abspath(__file__))


def get_stock_mrc_extended_header() -> np.ndarray:
    """
    Read in and return a "stock" extended header. This extended header will allow MRC files to be returned to
    :return:
    """
    extended_header_path = os.path.join(BASEDIR, "stock_mrc_extended_header.npy")
    extended_header = np.load(str(extended_header_path))
    return extended_header


if __name__ == "__main__":
    ext_header = get_stock_mrc_extended_header()
    print(ext_header)
    print(len(ext_header))
    print(type(ext_header))
    print(type(ext_header[0]))
    print(ext_header.tobytes())
