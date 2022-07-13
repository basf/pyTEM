import pathlib

import numpy as np


def get_stock_mrc_extended_header() -> np.ndarray:
    """
    Read in and return a "stock" extended header. This extended header will allow MRC files to be returned to
    :return:
    """
    header_file = pathlib.Path(__file__).parent.resolve() / "stock_mrc_extended_header.npy"
    print(header_file)
    extended_header = np.load(str(header_file))
    return extended_header


if __name__ == "__main__":
    ext_header = get_stock_mrc_extended_header()
    print(ext_header)
    print(len(ext_header))
    print(type(ext_header))
    print(type(ext_header[0]))
    print(ext_header.tobytes())
