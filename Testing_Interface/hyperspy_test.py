# Just some simple testing to get started with HyperSpy
# HyperSpy is an open source Python library which provides tools to facilitate the interactive data analysis

import os
import pathlib

import matplotlib  # import matplotlib for the GUI backend HyperSpy needs
matplotlib.rcParams["backend"] = "Agg"

import hyperspy.api as hs


def turn_off_hyperspy_warnings():
    """
    By default, HyperSpy warns the user if one of the GUI packages is not installed. Turn these warnings off.
    :return: None
    """
    hs.preferences.GUIs.warn_if_guis_are_missing = False
    hs.preferences.save()


def convert_images(in_file, out_file_type='tif', index_by_tilt_angle=False):
    """
    Read in image(s) from one file format - convert and save them to another

    Often this will be used to convert images from the Thermo Fisher (formerly FEI) .emi/.ser files provided by the
     microscope to a standard image format (likely TIFF to maintain 32-bit quality).

    :param in_file: str or Path object:
        Path to the file to read in, including the file extension. Must be one of HyperSpy's supported file formats.
    :param out_file_type: str (optional; default is 'tif') :
        The extension of the out file(s). The image will be converted and saved to this file type. Again, must be one of
         HyperSpy's supported file formats.
    :param index_by_tilt_angle: bool (optional; default is False):
        Index output files by alpha tilt angle. If False, output files sequentially (1, 2, ...).
        # TODO: All images in a series may be labelled with the same tilt angle.

    :return: None; images are converted to the out_file_type and saved in out_dir.
    """

    image_stack = hs.load(in_file)  # TODO: Investigate lazy loading for large data sets
    print("Reading " + str(image_stack) + " from in_file: " + str(in_file))

    out_file, _ = os.path.splitext(in_file)
    nav_dimension = image_stack.axes_manager.navigation_dimension

    if nav_dimension == 0:
        # There is only one image
        if index_by_tilt_angle:
            this_images_out_file = out_file + "_" \
                                   + str(image_stack.metadata.Acquisition_instrument.TEM.Stage.tilt_alpha) \
                                   + "." + out_file_type
        else:
            this_images_out_file = out_file + "." + out_file_type
        print("\nSaving image as " + this_images_out_file + "...")
        image_stack.save(filename=this_images_out_file, overwrite=True, extension=out_file_type)

    elif nav_dimension == 1:
        # We have a stack of images, loop through it
        for i, image in enumerate(image_stack):
            if index_by_tilt_angle:
                index = image.metadata.Acquisition_instrument.TEM.Stage.tilt_alpha
            else:
                index = i
            this_images_out_file = out_file + "_" + str(index) + "." + out_file_type
            print("\nSaving image #" + str(i) + " as " + this_images_out_file + "...")
            image.save(filename=this_images_out_file, overwrite=True, extension=out_file_type)

    else:
        raise Exception("Error: navigation dimension not recognized.")


def compute_microscope_shift(template, image):
    """
    Compute the microscope shift required to align the provided image with the provided template.

    :param template: str or Path object:
        Path to template, including the file extension. The template is the image wherein the particle is already
         centered.

    :param image: str or Path object:
        Path to the image, the microscope will be adjusted so that this image is centered.

    :return: idk yet
    """

    out_file_image, _ = os.path.splitext(image)  # Where to save the shifted image

    print("\nLoading template... ")
    template = hs.load(template)
    print("Template: " + str(template))

    print("\nLoading image... ")
    image = hs.load(image)
    print("Image: " + str(image))

    # Stack the template and image
    print("\nStacking the template and the image... ")
    stack = hs.stack(signal_list=[template, image])
    print(stack)

    # Print the shift
    print("\nEstimating the shift... ")
    shifts = stack.estimate_shift2D()
    print("Shifts: " + str(shifts))

    # TODO: Convert this image shift into a microscope shift (image deflector shift and possibly beam deflector shift)

    # Align the image to the template
    print("\nShifting the image to align with the template... ")
    stack.align2D(shifts=shifts)
    shifted_image = stack.inav[1]
    print(shifted_image)

    print("\nSaving the original image as a png... ")
    image.save(filename=out_file_image + '.png', overwrite=True, extension='png')

    print("\nSaving the shifted image as a png... ")
    # Save the shifted image to file so we can
    out_file_image = out_file_image + '_shifted.png'
    shifted_image.save(filename=out_file_image, overwrite=True, extension='png')


def deck_alignment():
    """
    Test aligning a whole series of images.
    Not sure yet if this is a good idea... but I suspect there will be more mechanical error with this approach but
     less drift error.

    :return: None
    """
    in_dir = pathlib.Path(__file__).parent.resolve()
    in_file = in_dir / "data" / "uED_tilt_series_example1.emi"
    out_file = in_dir / "data" / "Aligned Stack" / "uED_tilt_series_example1-"
    print(out_file)

    image_stack = hs.load(in_file)
    sub_stack = image_stack.inav[0:45]  # All the other images are just black
    print(sub_stack)

    shifts = sub_stack.estimate_shift2D()

    for i, image in enumerate(sub_stack):
        print("Shift for image" + str(i) + ": " + str(shifts[i]))

    # Align the image to the template
    sub_stack.align2D(shifts=shifts)

    for i, image in enumerate(sub_stack):
        this_images_out_file = str(out_file) + str(i) + ".png"
        print("\nSaving image #" + str(i) + " as " + this_images_out_file + "...")
        image.save(filename=this_images_out_file, overwrite=True, extension='png')


if __name__ == "__main__":


    """ Test convert_images() """
    # in_dir = pathlib.Path(__file__).parent.resolve()
    #
    # # Note that the EMI file contains the meta-data while the SER file contains the pictures.
    # # Either can be provided to the HyperSpy reader, but both need to be in the same directory.
    # # Only images 0 -> 45. The rest are blank.
    # in_file = in_dir / "data" / "uED_tilt_series_example1.emi"
    #
    # # This file is too big to be read in by HyperSpy
    # # in_file = in_dir / "data" / "uED_tilt_series_example2.emi"
    #
    # # Try a single image
    # # in_file = in_dir / "data" / "uED_tilt_series_example1_1.tif"
    #
    # # convert_images(in_file, out_file_type='tif', index_by_tilt_angle=True)
    # convert_images(in_file, out_file_type='png', index_by_tilt_angle=False)


    """ Investigate file meta-data """
    # in_file = in_dir / "data" / "uED_tilt_series_example1_1.tif"
    # image = hs.load(in_file)
    # print(image)
    # print(dir(image))
    # print(image.metadata)
    # print(image.metadata.Acquisition_instrument.TEM.Stage.tilt_alpha)


    """ Test compute_microscope_shift() """
    # in_dir = pathlib.Path(__file__).parent.resolve()
    # template = in_dir / "data" / "uED_tilt_series_example1_0.tif"
    #
    # image = in_dir / "data" / "uED_tilt_series_example1_5.tif"
    #
    # compute_microscope_shift(template=template, image=image)


    """ Test deck_alignment() """
    deck_alignment()
