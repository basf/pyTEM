#
# TemSet.py
# %%
# Test Philipp git sync
# Tested with Python 3.6.7

import numpy as np
import math as ma
import multiprocessing as mp
import scipy.signal as sig
import time
import tifffile

from earlier_versions.TemPackage import TEM


scope = TEM()

# %% TILTING TEMSCRIPT
""" Before getting to the part of the script that runs the tilt series acqusition, 
 we have to define a bunch of functions that are used only in this series. 

 All of the basic microscope interaction functions are pulled out of TemPackage"""


class Tilt():

    # initilazation...
    def __init__(self):
        """ Initialize the class. Comtypes client is the interface through which we can access
        The microscope. Define 'self.tem' as the basic tem scripting and 'self.phd' as the advanced
        tem scripting.

        self.Variable is used to let you use that variable throughout the class.
        If I did not do this, I would have to call
        tem = cc.CreateObject('TEMScripting.Instrument') or
        phd = cc.CreateObject("TEMAdvancedScripting.AdvancedInstrument")
        each time I wanted  to use the TEM scripting. """

        import comtypes.client as cc
        self.tem = cc.CreateObject("TEMScripting.Instrument")  # basic tem scripting
        self.phd = cc.CreateObject("TEMAdvancedScripting.AdvancedInstrument")  # advanced

    def UserInputs(self):
        """ Takes user input on the tilt series properties.
        Lowerbound, upperbound, and del_theta are used to determine # of images,
        exposure time and del_theta are used to determine alpha tilt speed.
        binning and exposure time are fed into the acquisition function. """
        # user input lower alpha bound. TEM scripting uses inputs as radians
        # but it's easier to think in degrees; ma.radians() converts to rad.
        lower_bound = ma.radians(float(input("Input degree start, ex. -20.0    ")))

        # user input upper alpha bound. TEM scripting uses inputs as radians
        # but it's easier to think in degrees; ma.radians() converts to rad.
        upper_bound = ma.radians(float(input("Input degree end, ex. 20.0    ")))

        # Angle interval between images.. TEM scripting uses inputs as radians
        # but it's easier to think in degrees; ma.radians() converts degree to rad.
        del_theta = ma.radians(float(input("Input degree interval between images, ex. 0.3     ")))

        # Exposure time for photos in seconds. Decimal or integer is okay
        exposure = float(input("Input exposure time in seconds.    "))

        # Binning for the desired image resolution.
        binn = input("Input resolution of image. ex. 4k, 2k, 1k, 0.5k    ")

        # return all of the inputs for use in the main function.
        return lower_bound, upper_bound, del_theta, exposure, binn

    def AlphaList(self, lowerbound, upperbound, dtheta):
        """ Makes a list of all of the alpha values that will be used in the tilt acquisition series.
        They are paired for each image; an alpha start and alpha stop value.

        The first pair in the series will be (lowerbound, lowerbound+dtheta)
        Last pair in the series will be (upperbound-dtheta, upperbound)

        Inputs should all be in radians because the input for the TEM is in radians.
        Can take the inputs straight from the output of UserInputs()"""
        # initialize alphalist as below so that it has the correct number of dimensions
        # This is because I'm using np.append on it. This first entry will be dropped.
        alphalist = [(0, 0)]
        alpha1 = lowerbound
        alpha2 = lowerbound + dtheta
        while alpha1 < upperbound + dtheta:
            # for each value of alpha, create a pair of (start, stop) values that
            # will be given to the acquisition function.
            alphalist = np.append(alphalist, [(alpha1, alpha2)], axis=0)
            alpha1 = alpha1 + dtheta  # increment up by the alpha change
            alpha2 = alpha2 + dtheta
            # get rid of the first placeholder number
        alphalist = alphalist[1::]
        return alphalist

    def Housekeeping(self):
        """ Housekeeping function that returns the TEM to a safe state after the acquisition"""
        scope.blank_beam(blank=True)  # blank the beam
        scope.set_stage(a=0.0)  # move alpha back to zero
        scope.set_projection_mode("Imaging")  # return to imaging mode
        # PULL OUT THE APERATURE???
        scope.column_valve(column="Closed")  # close the column valve

    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # below are functions that are used in the Manual Calibration
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

    def _ManualCalibration_Input(self, lowerbound, midposition, upperbound):
        """ Manual calibration of drift correction. This takes three stage positions
        and returns them for use in other functions.

        The user centers the particle of interest each time.
        This is not optimal for large alpha ranges, so accomodations could be made in the future.

        Used as a back up if the cross correlation fails. """

        # Set the alpha position to the lower bound
        print('Setting alpha tilt to lower bound.')
        scope.set_stage(a=lowerbound)
        input('Manually center particle then press Enter to proceed.')  # Have the user center the particle
        lowerpos = scope.get_stage()  # get the current stage position and store it.
        print("Calibration 1 of 3 complete... Wait...")

        print('Setting alpha tilt to midpoint.')
        # go to the midpoint of alpha
        scope.set_stage(a=midposition)
        input('Manually center particle then press Enter to proceed.')
        midpos = scope.get_stage()  # get the current stage position and store it.
        print("Calibration 2 of 3 complete... Wait...")

        print('Setting alpha tilt to upper bound.')
        # go to alpha = upper bound.
        scope.set_stage(a=upperbound)
        input('Manually center particle then press Enter to proceed.')
        upperpos = scope.get_stage()  # get the current stage position and store it.
        print("Calibration 3 of 3 complete.")

        return lowerpos, midpos, upperpos

    def AlphaTiltSpeed(self, dalpha, exposuretime):
        """ Finds the correct alpha tilt speed in ~Thermo Fisher~ speed units.
        Alpha tilt speed is determined in radians per second by the alpha sweep
        per image and the exposure time per image. """
        temspeed = 1.4768 * (dalpha / exposuretime) + 0.0001
        return temspeed

    def _Velocity(self, lowerpos, midpos, upperpos, da):
        """ Internal function called by ManualCalibration.
        Takes the three stage positions and finds dx/da and dy/da for both of the movement halves.
        da is the alpha spacing between images -- from UserInputs
        Stage position inputs need units of meters and be dictionaries from tem.get_stage()
        Time difference is determined by the speed at which alpha is changing. """

        # change in alpha is just the alpha spacing between images,
        # the way the script works, we only have to calculate how much x and y
        # need to move for each of the images -- so dx/da and dy/da

        # from Lowerposition to Midposition.. simple displacement
        dx_da1 = (midpos['x'] - lowerpos['x']) / da  # units of meters per radian
        dy_da1 = (midpos['y'] - lowerpos['y']) / da  # units of meters per radian

        # from Midposition to Upperposition.. simple displacement
        dx_da2 = (upperpos['x'] - midpos['x']) / da  # units of meters per radian
        dy_da2 = (upperpos['y'] - midpos['y']) / da  # units of meters per radian

        return (dx_da1, dy_da1), (dx_da2, dy_da2)

    def CompareAndCorrect(self, position1, position2, pixelsize):
        # Position one and two are (x1,y1) and (x2,y2) lists.
        xsh = position2[0] - position1[0]
        ysh = position2[1] - position1[1]  # simple displacement -- units of pixels
        xsh = xsh * pixelsize  # in micrometers
        ysh = ysh * pixelsize  # in micrometers

        # coordinate transformation into the temscript coordinate plane
        u = 0.8904 * xsh + 0.4636 * ysh  # in micrometers
        v = 0.4636 * xsh - 0.8904 * ysh  # in micrometers
        scope._ImageShift(xsh=u * 10 ** (-6), ysh=v * 10 ** (-6))  # set the image shift
        scope._BeamShift(xsh=u * 10 ** (-6), ysh=-v * 10 ** (-6))  # Set the beam shift
        # positive v axis for beam is negative v axis for image
        # so beam/image shift v coordinate are opposite signs.

    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # below are functions that are used in the Automated Calibration
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

    def CrossCorrelation(self, image1, image2, pixelsize):
        """ Determines the similarity between two images with cross correlation.
        Inputs can be numpy arrays if they are greyscale and uint8
        Or inputs can be cv arrays too. The bigger the input, the longer this takes,
        So use 1k or less for the images -- they're calibration images after all.

        Output is the u-v shift (shift in the TEM plane) between images."""
        # image1 = cv.GaussianBlur(image1, (3,3), 4) #blur image
        # image2 = cv.GaussianBlur(image2, (3,3), 4)

        image1 = image1 - np.mean(image1)  # subtract mean values from the image
        image2 = image2 - np.mean(image2)  # preprocessing that makes the result better.

        # Cross Corrrelate with Self
        fftself = sig.fftconvolve(image1, image1[::-1, ::-1], mode='same')
        # the [::-1, ::-1] mirrors the second image which changes the convolution to correlation

        # Cross Correlate with Other
        fftcomp = sig.fftconvolve(image1, image2[::-1, ::-1], mode='same')

        # find the coordinate of the brightest spots for both correlations
        # argmax returns the position of the brightest spot and then unravel_index will return an (x,y) coordinate
        selfcenter = np.unravel_index(np.argmax(fftself), fftself.shape)
        compcenter = np.unravel_index(np.argmax(fftcomp), fftcomp.shape)

        """ selfcenter is 'most similar point' between image1 & image1 
        compcenter is 'most similar point' between image1 & image2 
        x and y offset of these will be the positional difference between image1 and image2 
        remember that pixel (0,0) is the top left, and we are shifting with respect to 
        center stage, so we have to manipulate the y axis.  """

        pixelsize = float(pixelsize[0])
        xsh = (compcenter[0] - selfcenter[0]) * pixelsize  # xshift
        ysh = (-(compcenter[1] - selfcenter[1])) * pixelsize  # yshift

        # coordinate transformation into the temscript coordinate plane
        u = 0.8904 * xsh + 0.4636 * ysh  # in meters (compcenter in pixels ** pixelsize in meters/pixel )
        v = 0.4636 * xsh - 0.8904 * ysh  # in meters
        return (u, v)

    def _Calib_Image_Array(self, alphavalue):
        """ Internal function used in the automatic calibration.
        Takes a low resolution image and returns it, along with the pixelsize information. """
        # set the stage to the given alpha value
        scope.set_stage(a=alphavalue)
        # take an image with binning of 1k and readout of 1 -> return a 512*512 image.
        ai = scope.acquisition("BM-Ceta", binning='1k', exposuretime=3.0, readout=1)
        pixelsize = scope.metadata(ai, 'dict')['PixelSize']  # Pull the pixel size from the metadata
        calibrationarray = np.asarray(ai.AsSafeArray)  # pull the image array from the pointer and convert to numpy
        return calibrationarray, pixelsize

    # %% Functions that run the main things


class Run():

    def __init__(self):
        """ Initialize the class again with the normal and advanced
        TEM scripting """
        import comtypes.client as cc
        self.tem = cc.CreateObject("TEMScripting.Instrument")
        self.phd = cc.CreateObject("TEMAdvancedScripting.AdvancedInstrument")

    def AutomatedCalibration(self, alphalist):
        """ Automatic calibration that will pull two calibration images,
        Compare them with cross correlation, and store the calculated stage correction
        into x-correction and y-correction arrays. """

        xcorr = []  # initalize the x correction array
        ycorr = []  # initalize the y correction array

        for i in range(0, len(alphalist), 15):
            # take calibration image at the first alpha pair position -- alpha
            calibration1, pixelsize = Tilt()._Calib_Image_Array(alphalist[i][0])

            # take calibration image at the second alpha pair position -- alpha + d_alpha
            calibration2, pixelsize = Tilt()._Calib_Image_Array(alphalist[i][1])

            # compare the images with cross correlation
            u, v = Tilt().CrossCorrelation(calibration1, calibration2, pixelsize)

            xcorr = np.append(xcorr, u)  # append the x and y correction values
            ycorr = np.append(ycorr, v)  # to the arrays.

        # output the x and y correction arrays -- will be used in the image acquisition.
        return xcorr, ycorr  # , correct

    def ManualCalibration(self, alphalist, dalpha):
        """ Manual calibration that takes three alpha positions (lower bound, upper bound, and midpoint),
        And has the user manually center the particle for each position.
        Those positions are used to determine the x and y correction that should occur
        between each image. Particle **should** stay centered, but this is a backup method and
        not as reliable as the automated calibration.

        Outputs  x-correction and y-correction arrays to be used in image acquistion """
        # find the index of the midpoint alpha position in alpha list
        # and and pull the first entry (the starting alpha value) (second entry is the ending alpha value for that picture's tilt)
        midalpha = alphalist[round(len(alphalist) / 2)][0]

        # input the first, last, and midpoint alpha values into the manual calibration.
        lowerpos, midpos, upperpos = Tilt()._ManualCalibration_Input(alphalist[0][0], midalpha, alphalist[-1][0])

        # take the positions given and find the dx_da and dy_da.
        (dx_da1, dy_da1), (dx_da2, dy_da2) = Tilt()._Velocity(lowerpos, midpos, upperpos, dalpha)

        # the x and y correction will be an array filled with the same value for the starting alpha until
        # the mid alpha and then a different same value for the mid alpha until the ending alpha.

        # array full of the same value for x change from lowerbound alpha to midalpha.
        xcorr1 = np.full(round(len(alphalist) / 2), dx_da1 * dalpha)
        # Array full of the same value for x change from midpos to upperbound alpha.
        xcorr2 = np.full(len(alphalist) - round(len(alphalist) / 2), dx_da2 * dalpha)

        # array full of the same value for y change from lowerbound alpha to midalpha.
        ycorr1 = np.full(round(len(alphalist) / 2), dy_da1 * dalpha)
        # Array full of the same value for y change from midpos to upperbound alpha.
        ycorr2 = np.full(len(alphalist) - round(len(alphalist) / 2), dy_da2 * dalpha)

        # append the lists so they're one long list from lowerbound -> midpoint
        # and midpoint -> upperbound
        xcorr = np.append(xcorr1, xcorr2)
        ycorr = np.append(ycorr1, ycorr2)

        # output the x and y correction arrays -- will be used in the image acquisition.
        return xcorr, ycorr

    def ImageProcess(self, numimages, behemoth, alphalist, tiltspeed, directory):
        """ The function that saves all of the images to TIFF file. Used to be in the main() function
        But it is here now to clean up the main function.

        Goes through all of the entries in the behemoth list, and saves each of them as a tiff
        with the given metadata. The tiffs are saved inside the user-defined directory
        as image_1, image_2, etc. """
        # for all of the images,
        for i in range(numimages):
            # pull the metadata dictionary out of the behemoth. Each image will have a 'metadict'
            metadict = behemoth[i]

            # Pull the image data out of the image array and then delete that dictionary entry
            # so that when the metadata is saved it doesnt include a copy of the data.
            imagearray = np.asarray(metadict['ImageArray'])
            del metadict['ImageArray']

            # Add the alpha starting tilt position and the tilting speed to the image metadata.
            metadict.update({'Alpha (start, stop)': alphalist[i], 'Tilt Speed': tiltspeed})

            # define the image filename to be within the user input directory.
            filename = str(directory) + '\\image_' + str(i) + '.tiff'

            # save the image to a tiff with metadata with tifffile
            tifffile.imwrite(filename, imagearray, metadata=metadict)

    def SaveInfo(self, lb, ub, dtheta, t_exp, binning, directory):
        # access the camera length
        cameralength = self.tem.Projection.CameraLength
        infofile = str(directory) + '\\infofile.txt'
        with open(infofile, 'w') as info:
            info.write('Alpha lower bound:' + str(lb) +
                       '\n Alpha upper bound:' + str(ub) +
                       '\n Degrees between images:' + str(dtheta) +
                       '\n Exposure Time:' + str(t_exp) +
                       '\n Binning:' + str(binning) +
                       '\n Camera Length: ' + str(cameralength) + ' m')


# %%


# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# below are functions that are used in the multiprocessing
# These need to be defined "at the top level" ie. not within a class
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


def acq_image(cameraname, t_exp, imtype, queue):
    """ Function that will acquire the image and the image metadata. The output to the queue
    cannot be a pointer, so I do some data processing within this function.

    To use the queue within this function, we have to take the queue as an argument.

    I pull the image array out of the pointer, and add it to the metadata dictionary
    and send the metadata dictionary to the 'queue' which allows us to access the image
    data in the multiprocessing function -- TakingOneImage() """
    # take the image
    ai = scope.acquisition(cameraname, binning=imtype, exposuretime=t_exp)

    # pull the image metadata as a dictionary
    meta = scope.metadata(ai, 'dict')

    # pull the image data as a numpy array
    imarray = np.asarray(ai.AsSafeArray)

    # add the image data to the metadata dictionary
    meta.update({'ImageArray': imarray})

    # send the metadata to the queue.
    # ((basically the same action as 'return' except instead of returning the value to the
    # terminal, the value is 'returned' to the function that created the queue. ))
    queue.put(meta)


def acq_blankn_tilt(t_exp, alphastop, v):
    """ Blank - and - tilt
    This function will make sure the beam is blanked during the time that the camera is blind,
    unblank the beam after (t_exp+0.55) seconds and then start the alpha tilt.
    The alpha tilt uses a specific speed v so that the time needed to go from alpha start to alpha stop
    is the expsure time.
    After the alpha tilt has finished (after t_exp), the beam is blanked again to protect the sample. """

    # Make sure the beam is blanked.
    scope.blank_beam(blank=True)

    # the camera is blind for the exposure time plus 0.55
    time.sleep(t_exp + 0.55)

    # unblank the beam and tilt the alpha
    scope.blank_beam(blank=False)
    scope.set_stage(a=alphastop, speed=v)

    # reblank the beam to protect the sample
    scope.blank_beam(blank=True)


def acq_stage(xpos, ypos, alphastart):
    """ Really simple function that just moves the stage position to the correct x, y, and alpha
    values in preparation for the image acquisition. The moved x,y position is the stage drift correction.
    And the alpha is the starting tilt value. """
    scope.set_stage(x=xpos, y=ypos)  # move x and y
    scope.set_stage(a=alphastart)  # move alpha


def TakingOneImage(cameraname, t_exp, imtype, xpos, ypos, alphastart, alphastop, speed):
    """ This is the function that does the multiprocessing.
    It will take an image using 'cameraname'
    The exposure time will be 't_exp'
    The binning type is given with 'imtype'
    The drift corrected stage position is (xpos, ypos)
    The alpha start and alpha stop values are used for tilting alpha while imaging
    And speed is the speed at which alpha will be tilting.

    This uses multiprocessing queue, which you have to create before you do any of the multiprocessing
    commands, and then you have to take your information from the queue BEFORE closing any processes
    that are using the queue. Otherwise the code will spend eternity searching for the queue
    when it doesn't exist anymore."""

    # change stage position to the correct position before multiprocessing.
    # cpos = scope.get_stage()
    # acq_stage(cpos['x'] + xpos, cpos['y'] + ypos, alphastart)
    scope.set_stage(a=alphastart)

    scope.set_image_shift(xpos, ypos)
    scope.set_beam_shift(xpos, -ypos)  # y axis for beam shift flipped

    """ Define the queue BEFORE starting multiprocessing"""
    qq = mp.Queue()

    """ Define multiprocessing target 'acq_blankn_tilt' -- this is the blanking and tilting function. 
    Instead of calling acq_blankn_tilt(t_exp, alphastop, v) as you would with normal python, instead within 
    the multiprocessing Process command, you enter the function name as the target, and the arguments of the 
    function as args (see below) 
        target = acq_blankn_tilt, args = (t_exp, alphastop, v)

    If you have a function that has only one argument, you have to enter it as a list still. So it would be:
        args = (argument1, ) """
    blank = mp.Process(target=acq_blankn_tilt, args=(t_exp, alphastop, speed))
    # start blanking multiprocess
    blank.start()

    # Define the multiprocessing target for image acquisition using the same syntax as above
    image = mp.Process(target=acq_image, args=(cameraname, t_exp, imtype, qq))
    # start the image acquisition multiprocess
    image.start()

    # join the beam blanker multiprocess (will end the subprocess when it is finished.)
    blank.join()

    # Access the image metadata dictionary from the queue
    ima = qq.get()

    # join the imaging multiprocess (will end the subprocess when it is finished)
    image.join()
    return ima


# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# Main Function -- what actually runs the code.
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


def main():
    # make sure we are in imaging mode
    scope.set_projection_mode("Imaging")

    # Take User Inputs.
    lb, ub, dtheta, exp, binn = Tilt().UserInputs()

    # ask the user to input the directory in which the files should be saved
    directory = input('Input directory in which to save files ex. c:\\FEI\\microED     ')

    # verify that the stage is centered on the particle of interest when alpha is tilted to lower bound.
    print('Tilting to lower bound alpha.')
    scope.set_stage(a=lb)
    input('Is the particle of interest centered? If not, center it and then press enter.    ')
    # store the positition to restore the stage to the original position after calibration.
    ogpos = scope.get_stage()  # store the position

    currentmag = scope.get_magnification()  # get current magnification.

    # make the list of alpha values to be used.
    alphalist = Tilt().AlphaList(lb, ub, dtheta)

    # number of images is the total alpha tilt divided by the alpha each image covers
    # abs takes the absolute value for when ub < lb
    numimages = round((abs(ub - lb)) / dtheta)

    # alpha movement speed is determined by the exposure time and alpha each image covers.
    # find tilt speed in TEM speed units
    tiltspeed = Tilt().AlphaTiltSpeed(dtheta, exp)

    input('Remove screen, and then hit enter.   ')

    # Do The Calibration for the Series Acquisition
    # xs and ys are the arrays for the stage position for each image.
    xs, ys = Run().AutomatedCalibration(alphalist)
    # correct = False
    # if correct == False:
    #    xs, ys = Run().ManualCalibration(alphalist, dtheta)

    input('Insert aperature, remove screen, and then hit enter.   ')
    # Make sure we're in diffraction mode for the acquisition.
    scope.set_projection_mode("Diffraction")
    Run().SaveInfo(lb, ub, dtheta, exp, binn, directory)

    # Move stage to beginning position
    scope.set_stage(x=ogpos['x'], y=ogpos['y'], z=ogpos['z'])
    scope.set_stage(a=ogpos['a'])
    input('  hit enter.   ')
    behemoth = []  # initialize behemoth as a blank array

    # RUN THE MULTIPROCESSING
    for i in range(numimages):
        imagedict = TakingOneImage('BM-Ceta', exp, binn, xs[i], ys[i], alphalist[i][0], alphalist[i][1], tiltspeed)
        # possible memmory issue...
        imagearray = np.asarray(imagedict['ImageArray'])

        # Add the alpha starting tilt position and the tilting speed to the image metadata. Need  to convert the alpha start and stop positions to list.
        del imagedict['ImageArray']

        imagedict.update({'Alpha (start, stop)': alphalist[i].tolist(), 'Tilt Speed': tiltspeed})

        # define the image filename to be within the user input directory.
        filename = str(directory) + '\\image_' + str(i) + '.tiff'

        # yikes = list(imagedict.items())

        # save the image to a tiff with metadata with tifffile
        tifffile.imwrite(filename, imagearray, metadata=imagedict)
        # tifffile.imwrite(filename, imagearray, extratags = yikes)

    # return the microscope to a safe state.
    Tilt().Housekeeping()

    # PROCESS AND SAVE THE IMAGES.

    print("Image Acquisition Completed")


if __name__ == '__main__':
    main()  # RUN THE WHOLE THING.
