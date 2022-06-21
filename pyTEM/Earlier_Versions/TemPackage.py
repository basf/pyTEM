#
# TEM Pacakge for interacting with the Thermo Fiscer Talos TEM 
# written by Maegan Jennings 
# 15 December 2021

# Tested with Python 3.6.7

#%% Import Other Packages 

import numpy as np 
import math as ma

#%% All of the Functions
""" When writing a new function within the TEM() class, the first argument must be 'self' in order 
for the function to be able to find the self.tem and self.phd definitions. """

class TEM():
    
    def __init__(self): 
        import comtypes.client as cc 
        self.tem = cc.CreateObject("TEMScripting.Instrument") # Make the base TEMScripting
        self.phd = cc.CreateObject("TEMAdvancedScripting.AdvancedInstrument") # Make the Advanced TEMScripting
    
   
    def _GoTo(self, xp = None, yp = None, zp = None, ap = None, bp = None): 
        """ Goes to the specified position. uses keyword arguments. 
        If multiple coordinate changes are made, this should excecute multiple tem.Stage.GoTo commands""" 
        pos = self.tem.Stage.Position # current position
        
        # x-movement without y-movement
        if xp != None and yp == None: 
            pos.X = xp # edit the position pointer's x coordinate. 
            self.tem.Stage.GoTo(pos, 1) # change the x position; 1 -> x-axis
            
        # y-movement without x-movement 
        if xp == None and yp != None: 
            pos.Y = yp # edit the position pointer's y coordinate 
            self.tem.Stage.GoTo(pos, 2) # change the y position; 2 -> y-axis
            
        # x-movement with y-movement     
        if xp != None and yp != None: 
            pos.X = xp
            pos.Y = yp 
            self.tem.Stage.GoTo(pos, 3) # change the x and y position; 3 -> (xy)-axis
            
         # z-movement     
        if zp != None:
            pos.Z = zp # edit the position pointer's z coordinate 
            self.tem.Stage.GoTo(pos, 4) # change the z position; 4 -> z-axis
            
        # alpha-movement  
        if ap != None:
            pos.A = ap # edit the position pointer's alpha coordinate 
            self.tem.Stage.GoTo(pos, 8) # change the alpha position; 8 -> alpha-axis
            
        # beta-movement   
        if bp != None:
            pos.B = bp # edit the position pointer's beta coordinate 
            self.tem.Stage.GoTo(pos, 16) # change the beta position; 16 -> beta-axis
        
        
    def _GoToSpeed(self, xp = None, yp = None, zp = None, ap = None, v = None): 
        """ Goes to the specified position. uses keyword arguments. 
        Essentially the same function as _GoTo with the addition of 'speed'
        However, _GoToWithSpeed will not work for (xy)-axis or b-axis movement
        If multiple coordinate changes are made, this should excecute multiple tem.Stage.GoTo commands""" 
        pos = self.tem.Stage.Position # current position
        speed = v
        # x-movement
        if xp != None: 
            pos.X = xp # edit the position pointer's x coordinate. 
            self.tem.Stage.GoToWithSpeed(pos, 1, speed) # change the x position; 1 -> x-axis
            
        # y-movement 
        if yp != None: 
            pos.Y = yp # edit the position pointer's y coordinate 
            self.tem.Stage.GoToWithSpeed(pos, 2, speed ) # change the y position; 2 -> y-axis
            
         # z-movement     
        if zp != None:
            pos.Z = zp # edit the position pointer's z coordinate 
            self.tem.Stage.GoToWithSpeed(pos, 4, speed) # change the z position; 4 -> z-axis
            
        # alpha-movement  
        if ap != None:
            pos.A = ap # edit the position pointer's alpha coordinate 
            self.tem.Stage.GoToWithSpeed(pos, 8, speed) # change the alpha position; 8 -> alpha-axis 
       
    
    def _MoveTo(self, xp = None, yp = None, zp = None, ap = None, bp = None): 
        """ Goes to the specified position. uses keyword arguments. 
        If multiple coordinate changes are made, this should excecute multiple tem.Stage.GoTo commands
        Units for x y z are meters and alpha beta are radians """ 
        pos = self.TEM.Stage.Position # current position
        
        # x-movement without y-movement
        if xp != None and yp == None: 
            pos.X = xp # edit the position pointer's x coordinate. 
            self.tem.Stage.MoveTo(pos, 1) # change the x position; 1 -> x-axis
            
        # y-movement without x-movement 
        if xp == None and yp != None: 
            pos.Y = yp # edit the position pointer's y coordinate 
            self.tem.Stage.MoveTo(pos, 2) # change the y position; 2 -> y-axis
            
        # x-movement with y-movement     
        if xp != None and yp != None: 
            pos.X = xp
            pos.Y = yp 
            self.tem.Stage.MoveTo(pos, 3) # change the x and y position; 3 -> (xy)-axis
            
         # z-movement     
        if zp != None:
            pos.Z = zp # edit the position pointer's z coordinate 
            self.tem.Stage.MoveTo(pos, 4) # change the z position; 4 -> z-axis
            
        # alpha-movement  
        if ap != None:
            pos.A = ap # edit the position pointer's alpha coordinate 
            self.tem.Stage.MoveTo(pos, 8) # change the alpha position; 8 -> alpha-axis
            
        # beta-movement   
        if bp != None:
            pos.B = bp # edit the position pointer's beta coordinate 
            self.tem.Stage.MoveTo(pos, 16) # change the beta position; 16 -> beta-axis
        
          
    def _BeamShift(self, xsh=None, ysh=None):
        """ Shifts the beam by a specified amount. Inputs are in the TEM's u and v axis
        With units of meters.. """
        # the X or Y component of bms has to be set to a number value
        # So we have to do x only if the only keyword argument is x, etc. 
        
        bms = self.TEM.Illumination.Shift # get the beam shift
        if xsh != None and ysh == None: 
            bms.X = xsh 
            self.TEM.Illumination.Shift = bms # set the beam shift
        elif ysh != None and xsh == None: 
            bms.Y = ysh 
            self.TEM.Illumination.Shift = bms # set the beam shift
        else:
            bms.X = xsh
            bms.Y = ysh
            self.TEM.Illumination.Shift = bms # set the beam shift
                
            
    def _ImageShift(self, xsh=None, ysh=None):
        """ Shifts the beam by a specified amount. Inputs are in the TEM's 
        u and v axis (see the PositionCorrection function for the linear algebra). """
        # the X or Y component of bms has to be set to a number value
        # So we have to do x only if the only keyword argument is x, etc. 
        
        ims = self.TEM.Projection.ImageShift # get the beam shift
        if xsh != None and ysh == None: 
            ims.X = xsh 
            self.TEM.Projection.ImageShift = ims # set the beam shift
        elif ysh != None and xsh == None: 
            ims.Y = ysh 
            self.TEM.Projection.ImageShift = ims # set the beam shift
        else:
            ims.X = xsh
            ims.Y = ysh
            self.TEM.Projection.ImageShift = ims # set the beam shift
            
            
    def _STEM_Mag(self, value): 
        """ Internal.         
        STEM mode input: A decimal value of the magnification -- ex. 25300.0. 
        If the input is not one of the preset values, then the TEM will automatically 
        Set the magnification to the next nearest defined magnification value. """
        # value from the set_magnification() function: 
        self.tem.Illumination.StemMagnification = value
                
    def _TEM_Mag(self, value): 
        """ Internal. SPECIFICALLY FOR TALOS  
        Value must pull in a string.  
        TEM mode input: either magnification ID (integer between 1 and 44) 
        OR an up/down shift from current magnification (+7, -2, +10, etc.)
        If up/down shift exceeds the magnification bounds, magnification will set to the bound. """
        # current magnification 
        magid = self.tem.Projection.MagnificationIndex 
        # pulling int(value) will return a positive number if '+' used and a negative number if '-' used. 
        # simple math equation from there. 
        if ('+' or '-') in value: # if the value is a plusminus shift
            newmag = magid + int(value)
            if newmag > 44: # make sure that we don't set the magnification higher than 44
                newmag = 44
            elif newmag < 1: # or set it lower than one. 
                newmag = 1 
            else:
                newmag = newmag
        elif (1 <= int(value) <= 44 ): # if the value is just a reassignment of the magnification
            newmag = int(value)
        else: 
            print("Error, requested magnification outside of bounds.")
            
        # set the magnification to the new mag value
        self.tem.Projection.MagnificationIndex = newmag 
        
    def _TalosMagnification(self, index):
        # IMAGING MODE ONLY. 
        # NEED A WHOLE OTHER SET FOR DIFFRACTION MODE. ~FOURIER~
        magvalues = [25.0, 34.0, 46.0, 62.0, 84.0, 115.0, 155.0, 210.0, 280.0, 380.0, 
                     510.0, 700.0, 940.0, 1300.0, 1700.0, 2300.0, 2050.0, 2600.0, 3300.0, 
                     4300.0, 5500.0, 7000.0, 8600.0, 11000.0, 14000.0, 17500.0, 22500.0, 
                     28500.0, 36000.0, 46000.0, 58000.0, 74000.0, 94000.0, 120000.0, 
                     150000.0, 190000.0, 245000.0, 310000.0, 390000.0, 500000.0, 630000.0, 
                     650000.0, 820000.0, 1050000.0]
        # index starts counting at 1, python counts with 0 as the first 
        # retrieve the magnification value based on index
        mag = magvalues[index-1]
        return 'Magnification set to ' + str(mag) +'x '
    
                
    def _Vacuum(self):
        """ Checks the Vacuum status and prints the current vacuum status in Pascals."""
        gauges = self.tem.Vacuum.Gauges # creates the pointer with all of the vacuum information
        # Here are the names of the vacuum gauges that we know of 
        gaugenames = ['IGPa (Accelerator)', 'IGPco (column)', 'PIRco (detector)', 'PPm (unknown)', 'IGPf (unknown)']
        # if there is a leak it starts at the column 
        
        dictio = dict() # create a blank dictionary in which to write the pressures. 
        for i in range(len(gauges)):
            dictio.update({gaugenames[i]: gauges[i].Pressure}) # pull the pressures from the pointers 
        # output the dictionary for the get_vacuum and the set_column_valve functions 
        return dictio 
    
    
    def get_VacuumSafety(self):
        """ Checks the vacuum of the TEM to make sure that they are safe.""" 
        # if there is a leak then the pressure in the column vacuum will go up. 
        # safe value for the TEM to operate under is 15 ~~Log~~ units. 
        columnPascal = TEM()._Vacuum()['IGPco (column)'] # get the current vacuum of the column (in Pascals) 
        # Convert from pascals to ~~Log~~ units
        columnLog = 3.5683*ma.log(columnPascal)+53.497
        if 0 < columnLog < 20:
            out = "Safe"
        else: 
            out = "Unsafe"
        return out
    
            
    def get_stage(self):
        """ Gets current stage position and returns as a dictionary list. """ 
        pos = self.tem.Stage.Position # Store the stage position pointer
        # create and return a dictionary of the current stage position. 
        dictio = {'x': pos.X, 'y': pos.Y, 'z': pos.Z, 'a': pos.A, 'b': pos.B}
        return dictio 
    
    
    def set_stage(self, x = None, y = None, z = None, a = None, b = None, type = "GO", speed = 1.0):
        """ Set the stage to a specific position. 
        Input units for x, y, and z are meters, and input units for a and b are radians. 
        type can be "GO" or "MOVE" ... "GO" is default
            "GO" will proceed from current position to input position. 
            "MOVE" will proceed from current position to stage zero to input position. 
        speed can be any decimal value below 1.0 ... 1.0 is default 
            Due to limitations of the TEMScripting interface, the speed keyword is only available for setting the stage to a new alpha position. """ 
        # Input axis is an internal integer parameter for the TEMScripting interface. 
            # x-axis = 1, y-axis = 2, x-y-axis = 3, z-axis = 4, alpha-axis = 8, beta-axis = 16
        if type == "GO":
            if speed != 1.0: # If the speed isn't one, then move at the directed speed
                TEM()._GoToSpeed(xp = x, yp = y, zp = z, ap = a, v = speed)
            else: # else, the speed is 1 (default) 
                TEM()._GoTo(xp = x, yp = y, zp = z, ap = a, bp = b) 
        # if "MOVE" is the type, 
        elif type == "MOVE":
            TEM()._MoveTo(xp = x, yp = y, zp = z, ap = a, bp = b)
        else: 
            pass 
        
                
    def get_beam_shift(self):
        """ Gets current beam shift and returns as an x-y coordinate pair """ 
        pos = self.tem.Illumination.Shift # Store the beam shift pointer
        # This is in the u and v coordinate plane, so switch back to the x y plane. 
        u = pos.X 
        v = pos.Y  # should be in meters 
        x = (0.8904*u + 0.4636*v)
        y = (-0.4636*u + 0.8904*v) # will also output in meters.  
        
        return [x, y]

    
    def set_beam_shift(self, x = 0, y = 0): 
        """ Shifts the beam by a specified amount. 
        Input units for x and y are in METERS. This will be translated into the TEM's 
        'x' and 'y' axis for movement. Here they are called u and v. """ 
        # coordinate transformation into the temscript coordinate plane
        u = (0.8904*x + 0.4636*y) # inputs in meters, output in meters 
        v = (-0.4636*x + 0.8904*y) # inputs in meters, output in meters
        # then apply the beam shift. 
        TEM()._BeamShift(u, v)

        
    def set_imagebeamshift(self, xsh=0, ysh=0):
        """ Shifts the beam by a specified amount. Inputs are in the TEM's 
        u and v axis (see the PositionCorrection function for the linear algebra). """
        # the X or Y component of bms has to be set to a number value
        # So we have to do x only if the only keyword argument is x, etc. 

        # coordinate transformation into the temscript coordinate plane
        u = (0.8904*xsh + 0.4636*ysh) # inputs in meters, output in meters 
        v = (0.4636*xsh - 0.8904*ysh) # inputs in meters, output in meters
        # then apply the beam shift. 

        bs = self.tem.Projection.ImageBeamShift # get the image/beam shift

        bs.X = u
        bs.Y = v
        self.tem.Projection.ImageBeamShift = bs # set the beam shift
        
        
        
    def get_image_shift(self):
        """ Gets current image shift and returns as an x-y coordinate pair """ 
        pos = self.tem.Projection.ImageShift # Store the beam shift pointer
        # This is in the u and v coordinate plane, so switch back to the x y plane. 
        u = pos.X 
        v = pos.Y  # should be in meters 
        x = (0.8904*u + 0.4636*v)
        y = (0.4636*u - 0.8904*v) # will also output in meters.  
        
        return [x, y]
    
  
    def set_image_shift(self, x = 0, y = 0): 
        """ Shifts the image by a specified amount. 
        Input units for x and y are in METERS. This will be translated into the TEM's 
        'x' and 'y' axis for movement. Here they are called u and v. """ 
        
        # coordinate transformation into the temscript coordinate plane
        u = (0.8904*x + 0.4636*y) # inputs in meters, output in meters 
        v = (0.4636*x - 0.8904*y) # inputs in meters, output in meters
        # then apply the beam shift. 
        TEM()._ImageShift(u, v)
      
        
    def get_magnification(self):
        """ Gets the current magnification value and magnification index ID. 
        The magnification index ID is what is used to set the magnification of the 
        microscope. """ 
        mag = self.tem.Projection.Magnification
        magind = self.tem.Projection.MagnificationIndex
        return str(mag)+'x Magnification. Magnification Index ID = ' +str(magind) 
    
            
    
    def set_magnification(self, value): 
        """ Set the magnification. 
        Note: If you are in STEM mode, input must be the desired magnification 
        If you are in TEM mode, the input must be the magnification index.
        
        STEM mode input: A decimal value of the magnification -- ex. 25300.0
        
        TEM mode input: either magnification ID (integer between 1 and 44) 
        OR an up/down shift from current magnification (+7, -2, +10, etc.)
        If up/down shift exceeds the magnification bounds, magnification will set to the bound. """ 
        # get the current mode
        mode = self.tem.InstrumentModeControl.InstrumentMode
        if mode == 1: # mode 1 is the STEM mode
            TEM()._STEM_Mag(value) 
        if mode == 2: # mode 2 is the TEM mode
            TEM()._TEM_Mag(value) 

    
    def get_mode(self): 
        """ Gets the current mode of the microscope. Will be either "STEM" or "TEM" """
        mode = self.tem.InstrumentModeControl.InstrumentMode
        if mode == 1: # mode 1 is the STEM mode
            return "STEM"
        else:  # the only other option is mode is 2, which is TEM mode. 
            return "TEM" 
            
        
    def set_mode(self, mode):
        """ Changes the TEM to be either STEM or 'normal' imaging mode. 
        Input is either 'STEM' for STEM mode or 'TEM' for normal imaging mode. """
        if mode == ("STEM" or "Stem" or "stem"): # if input is 'STEM' 
            self.tem.InstrumentModeControl.InstrumentMode = 1 # set to STEM Mode
        elif mode == ("TEM" or "Tem" or "tem"): # if input is "TEM"
            self.tem.InstrumentModeControl.InstrumentMode = 2 # set to TEM Mode
        else:
            print("Error, unknown mode.")


    def get_vacuum(self):
        """ Checks the Vacuum status and prints the current vacuum status in Pascals."""
        # pull the vacuum status 
        status = TEM()._Vacuum()
        
        print("{:<20} {:<25} ".format('Vacuum','Value (Pa)')) # String formatting to make a table!
        for k, v in status.items(): # for key and value in the dictionary,
            print("{:<20} {:<25}".format(k, v)) # print out the key and value. 
            
            
    def column_valve(self, column = None):
        """ If column = None (default) then this function will OUTPUT the current position of the column value. 
         Using the keyword argument you can column the column valve. 
        Options for column are either "Open" or "Closed" """
        valve = self.tem.Vacuum.ColumnValvesOpen
        
        if column == None and valve == False: # 
            output = "Column Valve is Closed"
        elif column == None and valve == True:
            output = "Column Valve is Open" 
        
        if column != None: # if a value was specified for setting: 
            if column == ("Open" or "open"):
                if TEM().get_VacuumSafety() == 'Safe':  # check to make sure the vacuum is safe
                    self.tem.Vacuum.ColumnValvesOpen = True # open the valve
                    output = "Column Valve Opened" 
                else: # otherwise, do nothing and notify the user
                    output = "ERROR: Cannot Safely open Column Valve. Check the TEM."

            elif column == ("Close" or "close"): 
                self.tem.Vacuum.ColumnValvesOpen = False 
                output = "Column Valve Closed" 
        return output 


    def blank_beam(self, blank = None):
        """ Read/Write. If there are no keyword arguments, then the function will return whether or not the 
        beam is currently banked. blank = True will blank the beam, and blank = False will unblank the beam. """ 
        if blank == True: 
            self.tem.Illumination.BeamBlanked = True # blank the beam
        elif blank == False:
            self.tem.Illumination.BeamBlanked = False # unblank the beam 
        elif blank == None:
            value = self.tem.Illumination.BeamBlanked # get the beam blank status
            if value == False:
                return "Beam is not blanked" # return whether or not the beam is blanked.
            else:
                return "Beam is blanked"
            

    def get_projection_mode(self):
        """ Outputs a string of the current mode, will be either "Diffraction" or "Imaging" """
        mode = self.tem.Projection.Mode 
        if mode == 1:
            return "Imaging"
        else:
            return "Diffraction" 
    
    
    def set_projection_mode(self, mode):
        """ Sets the projection mode as either "Diffraction" or "Imaging" 
        Input options are "Diffraction" ('d') or "Imaging" ('i').
        The only modes available are either "Diffraction" or "Imaging"  """
        if mode == ("Diffraction" or "diffraction" or 'd'): 
            self.tem.Projection.Mode = 2 # numerical input corresponds to diffraction mode
        elif mode == ("Imaging" or "imaging" or "i"):
            self.tem.Projection.Mode = 1 # numerical input corresponds to imaging mode 
        else: 
            pass 
        
    
    def acquisition(self, cameraname, binning = None, exposuretime = None, readout = None): 
        """ Changes the parameters on the indicated camera, and then acquires a single image.
        Returns the image data as the raw pointer. 
        Cameras available are 'BM-Ceta' and 'BM-Falcon' use 'Falcon' carefully.
        Parameters should be entered into the function as keyword arguments.
        Binning is either '4k', '2k', '1k', '0.5k' for those resolution images. 
        Exposure time is in seconds. Please expose responsibly. 
        Readout will chop the image (like an extra binning) options are: 
            0: full size, 1: half size, 2: quarter size""" 
        # because calling the below function resets the camera settings to default, we have to 
        # set the settings and take the images all within the same function. 
        # returning the csa to another function 'disconnects' the camera object

        csa = self.phd.Acquisitions.CameraSingleAcquisition # set camera up as a single acquisition
        cams = csa.SupportedCameras
        csa.Camera = cams[[c.name for c in cams].index(cameraname)] # find the given camera and set it as the camera. 
        
        ct = csa.CameraSettings.Capabilities
        cs = csa.CameraSettings
        
        if readout != None: # if a readout keyword argument was entered 
            cs.ReadoutArea = readout
        
        if binning != None: # if a binning keyword argument was entered
            binninglist = ct.SupportedBinnings 
            if binning == '4k':
                cs.Binning = binninglist[0] # 0th pointer in the binning list creates 4k images
            elif binning == '2k':
                cs.Binning = binninglist[1] # 1st pointer in the binning list creates 2k images
            elif binning == '1k':
                cs.Binning = binninglist[2] # 2nd pointer in the binning list creates 1k images
            elif binning == '0.5k':
                cs.Binning = binninglist[3] # 3rd pointer in the binning list creates 0.5k images
            else: 
                print('Unknown Binning Type. Binning not changed.')
        
        if exposuretime != None:  # if an exposure time keyword argument was entered 
            cs.ExposureTime = exposuretime 
            
        return csa.Acquire()
        

    def to_array(self, ai):
        """ Input must be an acquired image pointer. Function pulls the image data
        out of the input and returns it as a numpy array. """ 
        array = np.asarray(ai.AsSafeArray)
        return array 
    
    
    def metadata(self, ai, keys):
        """ Returns metadata information about 'ai' (the pointer produced by take_data). 
        If the full metadata list is requested, it will return as text. 
        If key word arguments are asked, it will return a dictionary of those metadata values. """ 
        
        # initialize a blank dictionary
        metalist = dict()
        # STARTING COUNTS AT ZERO
        if keys == ('All' or 'all'):
            metalist =  f''' 
                        DetectorName: {ai.Metadata[0].ValueAsString} \n 
                        Binning: {int(ai.Metadata[1].ValueAsString)} \n 
                        ReadoutArea: {np.asarray([[ai.Metadata[3].ValueAsString, ai.Metadata[4].ValueAsString], 
                                       [ai.Metadata[5].ValueAsString, ai.Metadata[6].ValueAsString]])} \n 
                        ExposureMode: {ai.Metadata[7].ValueAsString} \n 
                        ExposureTime: {ai.Metadata[8].ValueAsString} \n 
                        DarkGainCorrectionType: {ai.Metadata[9].ValueAsString} \n 
                        ShuttersType: {ai.Metadata[10].ValueAsString} \n 
                        ShuttersPosition: {ai.Metadata[11].ValueAsString} \n 
                        AcquisitionUnit: {ai.Metadata[12].ValueAsString} \n 
                        BitsPerPixel: {ai.Metadata[13].ValueAsString} \n 
                        Encoding: {ai.Metadata[14].ValueAsString} \n 
                        ImageSize: {(ai.Metadata[15].ValueAsString, ai.Metadata[16].ValueAsString)} \n 
                        Offset: {(ai.Metadata[17].ValueAsString, ai.Metadata[18].ValueAsString)} \n 
                        PixelSize: {(ai.Metadata[19].ValueAsString, ai.Metadata[20].ValueAsString)} 
                        PixelUnit: {(ai.Metadata[21].ValueAsString, ai.Metadata[22].ValueAsString)} \n 
                        TimeStamp: {ai.Metadata[23].ValueAsString} \n 
                        MaxPossiblePixelValue: {ai.Metadata[24].ValueAsString} \n                             
                        SaturationPoint: {ai.Metadata[25].ValueAsString} \n 
                        DigitalGain: {ai.Metadata[26].ValueAsString} \n 
                        CombinedSubFrames: {ai.Metadata[27].ValueAsString} \n 
                        CommercialName: {ai.Metadata[28].ValueAsString} \n 
                        FrameID: {ai.Metadata[29].ValueAsString} \n 
                        TransferOK: {ai.Metadata[30].ValueAsString} \n 
                        PixelValueToCameraCounts: {ai.Metadata[31].ValueAsString} \n  
                        ElectronCounted: {ai.Metadata[32].ValueAsString} \n                             
                        AlignIntegratedImage: {ai.Metadata[33].ValueAsString}
                        '''
                        
        if keys == ('dict' or 'All dict'):
            metalist =  {'DetectorName': ai.Metadata[0].ValueAsString, 
                         'Binning': int(ai.Metadata[1].ValueAsString), 
                         'ReadoutArea': ([[ai.Metadata[3].ValueAsString, ai.Metadata[4].ValueAsString], 
                                       [ai.Metadata[5].ValueAsString, ai.Metadata[6].ValueAsString]]), 
                         'ExposureTime': ai.Metadata[8].ValueAsString, 
                         'DarkGainCorrectionType': ai.Metadata[9].ValueAsString, 
                         'ShuttersType': ai.Metadata[10].ValueAsString, 
                         'ShuttersPosition': ai.Metadata[11].ValueAsString, 
                         'AcquisitionUnit': ai.Metadata[12].ValueAsString, 
                         'BitsPerPixel': ai.Metadata[13].ValueAsString, 
                         'Encoding': ai.Metadata[14].ValueAsString, 
                         'ImageSize': (ai.Metadata[15].ValueAsString, ai.Metadata[16].ValueAsString), 
                         'Offset': (ai.Metadata[17].ValueAsString, ai.Metadata[18].ValueAsString), 
                         'PixelSize': (ai.Metadata[19].ValueAsString, ai.Metadata[20].ValueAsString), 
                         'PixelUnit': (ai.Metadata[21].ValueAsString, ai.Metadata[22].ValueAsString), 
                         'TimeStamp': ai.Metadata[23].ValueAsString,
                         'MaxPossiblePixelValue': ai.Metadata[24].ValueAsString,                             
                         'SaturationPoint': ai.Metadata[25].ValueAsString,
                         'DigitalGain': ai.Metadata[26].ValueAsString,
                         'CombinedSubFrames': ai.Metadata[27].ValueAsString,
                         'CommercialName': ai.Metadata[28].ValueAsString,
                         'FrameID': ai.Metadata[29].ValueAsString,
                         'TransferOK': ai.Metadata[30].ValueAsString,
                         'PixelValueToCameraCounts': ai.Metadata[31].ValueAsString, 
                         'ElectronCounted': ai.Metadata[32].ValueAsString,                           
                         'AlignIntegratedImage': ai.Metadata[33].ValueAsString}
            
               # all of the entries below have the same syntax: first matching keywords; there is some 
               # leniency when grabbing keywords. Then, updating the dictionary to include that keyword and its value. 
               # Some values are floats or integers, so they have been converted to the appropriate data type so 
               # users don't have to. 
               
        for keyword in keys: 
            if keyword == ('DetectorName' or 'detectorname' or 'CameraName' or 'cameraname'):
                metalist.update({'DetectorName': ai.Metadata[1].ValueAsString})
            
            if keyword == ('Binning' or 'binning'):
                # binning height and width are different metadata parameters -- is there 
                # an actual difference between the two? ?????????????????
                metalist.update({'Binning': int(ai.Metadata[2].ValueAsString)})
            
            if keyword == ('ReadoutArea' or 'readoutarea' or 'Readoutarea'):
                # readout area: (top, bottom, left, right) 
                # IS THIS LIKE A COORDINATE PAIR, (TOP, LEFT), (BOTTOM, RIGHT) 
                readout = np.asarray([[int(ai.Metadata[4].ValueAsString), int(ai.Metadata[5].ValueAsString)], 
                           [int(ai.Metadata[6].ValueAsString), int(ai.Metadata[7].ValueAsString)]])
                metalist.update({'ReadoutArea': readout })
            
            if keyword == ('ExposureMode' or "exposuremode" or 'Exposuremode'):
                metalist.update({'ExposureMode': f'{ai.Metadata[8].ValueAsString}'}) 
                
            if keyword == ('ExposureTime' or 'Exposuretime' or 'exposuretime'):
                metalist.update({'ExposureTime': int(ai.Metadata[9].ValueAsString)})
                
            if keyword == ('DarkGainCorrectionType' or 'darkgraincorrection' or 'darkgraincorrectiontype' or 'Darkgraincorrection'):
                metalist.update({'DarkGrainCorrectionType': ai.Metadata[10].ValueAsString})
            
            if keyword == ('ShuttersType' or 'Shutterstype' or 'shutterstype'):
                metalist.update({'ShuttersType': ai.Metadata[11].ValueAsString}) 
                
            if keyword == ('ShuttersPosition' or 'Shuttersposition' or 'shuttersposition'):
                metalist.update({'ShuttersPosition': ai.Metadata[12].ValueAsString}) 
            
            if keyword == ('AcquisitionUnit' or 'Acquisitionunit' or 'acquisitionunit'):
                metalist.update({'AcquisitionUnit': ai.Metadata[13].ValueAsString}) 
                
            if keyword == ('BitsPerPixel' or 'Bitsperpixel' or 'bitsperpixel'):
                metalist.update({'BitsPerPixel': int(ai.Metadata[14].ValueAsString)})
                
            if keyword == ('Encoding' or 'encoding'):
                metalist.update({'Encoding': ai.Metadata[15].ValueAsString}) 
                
            if keyword == ('ImageSize' or 'Imagesize' or 'imagesize'):
                readout = np.asarray([int(ai.Metadata[16].ValueAsString), int(ai.Metadata[17].ValueAsString)])
                metalist.update({'ImageSize': readout})
                
            if keyword == ('Offset' or 'offset'):
                readout = np.asaray([float(ai.Metadata[18].ValueAsString), float(ai.Metadata[19].ValueAsString)])
                metalist.update({'Offset': readout}) 
                
            if keyword == ('PixelSize' or 'Pixelsize' or 'pixelsize'): 
                readout = np.asarray([float(ai.Metadata[20].ValueAsString), float(ai.Metadata[21].ValueAsString)])
                metalist.update({'PixelSize': readout}) 
            
            if keyword == ('PixelUnit' or 'Pixelunit' or 'pixelunit' or 'PixelUnits' or 'Pixelunits' or 'pixelunits'):
                readout = [ai.Metadata[22].ValueAsString, ai.Metadata[23].ValueAsString]
                metalist.update({'PixelUnits': readout}) 
                
            if keyword == ('TimeStamp' or 'Timestamp' or 'timestamp' or 'Time' or 'time'):
                metalist.update({'TimeStamp': int(ai.Metadata[24].ValueAsString)}) 
            
            if keyword == ('MaxPossiblePixelValue' or 'maxpossiblepixelvalue'):
                metalist.update({'MaxPossiblePixelValue': int(ai.Metadata[25].ValueAsString)}) 
                
            if keyword == ('SaturationPoint' or 'Saturationpoint' or 'saturationpoint'):
                metalist.update({'SaturationPoint': int(ai.Metadata[26].ValueAsString)}) 
                
            if keyword == ('DigitalGain' or 'Digitalgain' or 'digitalgain'):
                metalist.update({'DigitalGain': int(ai.Metadata[27].ValueAsString)}) 
                 
            if keyword == ('CombinedSubFrames' or 'CombinedSubframes' or 'Combinedsubframes' or 'combinedsubframes'):
                metalist.update({'CombinedSubFrames': int(ai.Metadata[28].ValueAsString)}) 
                
            if keyword == ('CommercialName' or 'Commercialname' or 'commercialname'):
                metalist.update({'CommercialName': ai.Metadata[29].ValueAsString}) 
                
            if keyword == ('FrameID' or 'frameid' or 'frameID' or 'Frameid'):
                metalist.update({'FrameID': int(ai.Metadata[30].ValueAsString)}) 
                
            if keyword == ('TransferOK' or 'transferOK' or 'transferok' or 'Transfer'):
                metalist.update({'TransferOK': ai.Metadata[31].ValueAsString}) 
                
            if keyword == ( 'PixelValueToCameraCounts' or 'pixelvaluetocameracounts'):
                metalist.update({'PixelValueToCameraCounts': int(ai.Metadata[32].ValueAsString)}) 
                
            if keyword == ( 'ElectronCounted' or 'Electroncounted' or 'electroncounted'):
                metalist.update({'ElectronCounted': ai.Metadata[33].ValueAsString}) 
                
            if keyword == ( 'AlignIntegratedImage' or 'AlignIntegratedimage' or 'Alignintegratedimage' or 'alignintegratedimage'):
                metalist.update({'AlignIntegratedImage': ai.Metadata[34].ValueAsString}) 
            # once we have constructed it, return it. 
            
        return metalist 
            
        
    
# %%
