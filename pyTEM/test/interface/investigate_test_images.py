"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import pathlib
import hyperspy.api as hs

in_dir = pathlib.Path(__file__).parent.resolve() / "test_images"

# Here is an example file where the pixel size registers in imageJ
in_file = in_dir / "Tiltseies_SAD40_-20-20deg_0.5degps_1.1m.tif"
print("Reading in " + str(in_file))
ref_image = hs.load(in_file)

print(ref_image)
# print(dir(ref_image))
print(ref_image.metadata)
# print(ref_image.original_metadata)

original_metadata = ref_image.original_metadata
print(original_metadata)
print(type(original_metadata))
print(original_metadata['ResolutionUnit'])

# And here is an image saved with my save_as_tif() method
in_file = in_dir / "test_image_2.tif"
print("\nReading in " + str(in_file))
image = hs.load(in_file)

print(image)
# print(dir(ref_image))
print(image.metadata)
print(image.original_metadata)

print(image.original_metadata.ImageDescription)  # Metadata dictionary is saved here.
