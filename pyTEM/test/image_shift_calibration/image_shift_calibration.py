# Use come test images to either validate the existing shift matrix or obtain the correct one

import pathlib

import matplotlib  # import matplotlib for the GUI backend HyperSpy needs

from pyTEM.test.hyperspy_test import convert_images

matplotlib.rcParams["backend"] = "Agg"

import hyperspy.api as hs


def image_shift_calibration_2():
    """
    Code used when investigating the results of the second image calibration test.
    """
    print("Running image_shift_calibration_2()...")

    in_dir = pathlib.Path(__file__).parent.resolve()
    print(in_dir)

    # convert_images(in_file=in_dir / "Calibration_Data" / "Image 0, 0, x=0, y=0 (reference image).emd",
    #                out_file_type='tif')
    #
    """ Compute Shifts """
    print("\nReading in the template... ")
    template = in_dir / "Calibration_Data" / "2" / "Image 0, 0, x=0, y=0 (reference image).emd"
    template = hs.load(template)

    print("\nReading in image 1... ")
    image1 = in_dir / "Calibration_Data" / "2" / "Image 1, x=-0.2, y=0.2.emd"
    convert_images(in_file=image1, out_file_type='tif')
    image1 = hs.load(image1)

    print("\nReading in image 2... ")
    image2 = in_dir / "Calibration_Data" / "2" / "Image 2, x=0, y=0.2.emd"
    convert_images(in_file=image2, out_file_type='tif')
    image2 = hs.load(image2)

    print("\nReading in image 3... ")
    image3 = in_dir / "Calibration_Data" / "2" / "Image 3, x=0.2, y=0.2.emd"
    convert_images(in_file=image3, out_file_type='tif')
    image3 = hs.load(image3)

    print("\nReading in image 4... ")
    image4 = in_dir / "Calibration_Data" / "2" / "Image 4, x=-0.2, y=0.emd"
    convert_images(in_file=image4, out_file_type='tif')
    image4 = hs.load(image4)

    print("\nReading in image 5... ")
    image5 = in_dir / "Calibration_Data" / "2" / "Image 5, x=0.2, y=0.emd"
    convert_images(in_file=image5, out_file_type='tif')
    image5 = hs.load(image5)

    print("\nReading in image 6... ")
    image6 = in_dir / "Calibration_Data" / "2" / "Image 6, x=-0.2, y=-0.2.emd"
    convert_images(in_file=image6, out_file_type='tif')
    image6 = hs.load(image6)

    print("\nReading in image 7... ")
    image7 = in_dir / "Calibration_Data" / "2" / "Image 7, x=0, y=-0.2.emd"
    convert_images(in_file=image7, out_file_type='tif')
    image7 = hs.load(image7)

    print("\nReading in image 8... ")
    image8 = in_dir / "Calibration_Data" / "2" / "Image 8, x=0.2, y=-0.2.emd"
    convert_images(in_file=image8, out_file_type='tif')
    image8 = hs.load(image8)

    print("\nCreating the image stack... ")
    stack = hs.stack(signal_list=[template, image1, image2, image3, image4, image5, image6, image7, image8])

    print("\nComputing the image shifts... ")
    shifts = stack.estimate_shift2D()

    for i, image in enumerate(stack):
        print("Shift for image" + str(i) + ": " + str(shifts[i]))

    # print("\nAligning the images with the template... ")
    # stack.align2D(shifts=shifts)
    #
    # print("\nSaving the aligned images to file... ")
    # out_file = in_dir / "Calibration_Data" / "2" / "Aligned_Stack" / "aligned_image-"
    #
    # for i, image in enumerate(stack):
    #     this_images_out_file = str(out_file) + str(i) + ".png"
    #     print("\nSaving image #" + str(i) + " as " + this_images_out_file + "...")
    #     image.save(filename=this_images_out_file, overwrite=True, extension='png')

    """ Look at individual image shifts"""
    # # The image taken with no beam shift applied
    # template = in_dir / "Calibration_Data" / "2" / "Image 0, 0, x=0, y=0 (reference image).emd"
    #
    # # And the image-shifted image, of which we want to compute the magnitude/direction of shift.
    # image = in_dir / "Calibration_Data" / "2" / "Image 0, 0, x=0, y=0 (reference image).emd"
    # # image = in_dir / "Calibration_Data" / "2" / "Image 1, x=-0.2, y=0.2.emd"
    # # image = in_dir / "Calibration_Data" / "2" / "Image 2, x=0, y=0.2.emd"
    # # image = in_dir / "Calibration_Data" / "2" / "Image 3, x=0.2, y=0.2.emd"
    # # image = in_dir / "Calibration_Data" / "2" / "Image 4, x=-0.2, y=0.emd"
    # # image = in_dir / "Calibration_Data" / "2" / "Image 5, x=0.2, y=0.emd"
    # # image = in_dir / "Calibration_Data" / "2" / "Image 6, x=-0.2, y=-0.2.emd"
    # # image = in_dir / "Calibration_Data" / "2" / "Image 7, x=0, y=-0.2.emd"
    #
    # compute_microscope_shift(template=template, image=image)

    """ Look at meta-data """
    # emd_file = in_dir / "Calibration_Data" / "2" / "Image 0, 0, x=0, y=0 (reference image).emd"
    # emd_image = hs.load(emd_file)
    # print(vars(emd_image))


def image_shift_calibration_3():
    """
    Code used when investigating the results of the second image calibration test.
    """
    print("Running image_shift_calibration_3()...")

    in_dir = pathlib.Path(__file__).parent.resolve()
    print(in_dir)

    """ Look at meta-data """
    # emd_file = in_dir / "Calibration_Data" / "3" / "Image 0, x=0, y=0 (reference image).emd"
    # emd_image = hs.load(emd_file)
    # print(vars(emd_image))

    # emd_file = in_dir / "Calibration_Data" / "3" / "Image 2, x=0, y=2.emd"
    # emd_image = hs.load(emd_file)
    # print(vars(emd_image))

    """ Compute Shifts """
    print("\nReading in the template... ")
    template = in_dir / "Calibration_Data" / "3" / "Image 0, x=0, y=0 (reference image).emd"
    convert_images(in_file=template, out_file_type='tif')
    template = hs.load(template)

    print("\nReading in image 2... ")
    image1 = in_dir / "Calibration_Data" / "3" / "Image 2, x=0, y=2.emd"
    convert_images(in_file=image1, out_file_type='tif')
    image1 = hs.load(image1)

    print("\nReading in image 4... ")
    image2 = in_dir / "Calibration_Data" / "3" / "Image 4, x=-2, y=0.emd"
    convert_images(in_file=image2, out_file_type='tif')
    image2 = hs.load(image2)

    print("\nReading in image 5... ")
    image5 = in_dir / "Calibration_Data" / "3" / "Image 5, x=2, y=0.emd"
    convert_images(in_file=image5, out_file_type='tif')
    image5 = hs.load(image5)

    print("\nReading in image 7... ")
    image7 = in_dir / "Calibration_Data" / "3" / "Image 7, x=0, y=-2.emd"
    convert_images(in_file=image7, out_file_type='tif')
    image7 = hs.load(image7)

    print("\nCreating the image stack... ")
    stack = hs.stack(signal_list=[template, image1, image2, image5, image7])

    print("\nComputing the image shifts... ")
    shifts = stack.estimate_shift2D()

    print("shifts: " + str(type(shifts)))
    print("shifts[0]: " + str(type(shifts[0])))
    print("shifts[0][0]: " + str(shifts[0][0]))

    for i, image in enumerate(stack):
        print("Shift for image" + str(i) + ": " + str(shifts[i]))

    # print("\nAligning the images with the template... ")
    # stack.align2D(shifts=shifts)
    #
    # print("\nSaving the aligned images to file... ")
    # out_file = in_dir / "Calibration_Data" / "3" / "Aligned_Stack" / "aligned_image-"
    #
    # for i, image in enumerate(stack):
    #     this_images_out_file = str(out_file) + str(i) + ".png"
    #     print("\nSaving image #" + str(i) + " as " + this_images_out_file + "...")
    #     image.save(filename=this_images_out_file, overwrite=True, extension='png')

    """ Look at individual image shifts"""
    # # The image taken with no beam shift applied
    # template = in_dir / "Calibration_Data" / "3" / "Image 0, x=0, y=0 (reference image).emd"
    # convert_images(in_file=template, out_file_type='png')
    #
    # # And the image-shifted image, of which we want to compute the magnitude/direction of shift.
    # # image = in_dir / "Calibration_Data" / "3" / "Image 0, 0, x=0, y=0 (reference image).emd"
    #
    # image = in_dir / "Calibration_Data" / "3" / "Image 2, x=0, y=2.emd"
    #
    # # image = in_dir / "Calibration_Data" / "3" / "Image 4, x=-2, y=0.emd"
    # # image = in_dir / "Calibration_Data" / "3" / "Image 5, x=2, y=0.emd"
    #
    # # image = in_dir / "Calibration_Data" / "3" / "Image 7, x=0, y=-2.emd"
    #
    # compute_microscope_shift(template=template, image=image)


if __name__ == "__main__":
    """ Compute Image shifts """

    # image_shift_calibration_2()
    image_shift_calibration_3()



