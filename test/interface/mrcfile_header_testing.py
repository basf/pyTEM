"""
The standard is described here: https://www.ccpem.ac.uk/mrc_format/mrc2014.php.
Details of the MRC file format used by IMOD can be found here: https://bio3d.colorado.edu/imod/doc/mrc_format.txt
Check here for dtypes: https://github.com/ccpem/mrcfile/blob/23ca116b57a72cbef02f39c88c315cad471ad503/mrcfile/dtypes.py
"""


# Let's see if it is something hyperspy can load
import pathlib
import numpy as np
import mrcfile
# np.set_printoptions(threshold=np.inf)

out_dir = pathlib.Path(__file__).parent.resolve().parent.resolve().parent.resolve() / "test" \
                / "interface" / "test_images"
in_file_ = out_dir / "size_testing.mrc"
# in_file_ = out_dir / "Valid_tilt_series.mrc"

# mrc_file = mrcfile.validate(in_file_)
# print(mrc_file)

print("Loading data from " + str(in_file_))
with mrcfile.open(in_file_, permissive=True) as mrc:
    images = mrc.data
    print(dir(mrc))
    header = mrc.header
    extended_header = mrc.extended_header

    print("\nHeader: ")
    print(header)
    mrc.print_header()
    print(type(header))

    print("\nExtended Header: ")
    print(extended_header)
    print(len(extended_header))
    print(type(extended_header))

    tp = np.dtype("S" + str(mrc.header.nsymbt))
    recovered = np.frombuffer(extended_header, dtype=tp)[0]

    print("\nNumber of Columns (Number of pixels along x): " + str(header.nx))
    print("Number of Rows (Number of pixels along y): " + str(header.ny))
    print("Number of Sections (number of images): " + str(header.nz))
    print("Map: " + str(header.map))
    print("Map testing: " + str(header.getfield(np.dtype('S4'), offset=208)))
    print("Number of bytes in the header: " + str(header.nsymbt))

    # Type of extended header, includes 'SERI' for SerialEM, 'FEI1' for FEI, 'AGAR' for Agard
    print("Type of the extended header: " + str(header.getfield(np.dtype('S4'), offset=104)))

    print("RMS deviation of densities from mean: " + str(header.getfield(np.dtype('f4'), offset=216)))

    np.save(str(out_dir / "stock_mrc_extended_header"), extended_header)


# in_file_2 = out_dir / "size_testing.mrc"
# print("Loading extended header into " + str(in_file_2))
# with mrcfile.open(in_file_2, permissive=True, mode='r+') as mrc:
#     mrc.set_extended_header(extended_header)
#     print("New extended header size: " + str(mrc.header.nsymbt))

# print(images)
# print(type(images))
# print(np.shape(images))
#
# first_image = images[0]
# print(np.shape(first_image))
# print(type(first_image[0][0]))  # Element type
