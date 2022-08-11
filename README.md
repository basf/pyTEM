# Disclaimer

```pyTEM``` was developed for use on the BASF SE TEM Laboratory's Talos F200i transmission electron microscope.
 The authors provide no guarantee that the software will function as intended, either in part or in whole, on any 
 other microscope installation.

```pyTEM``` is available under the MIT license [here](/LICENSE).

# About

```pyTEM``` is a *high-level* scripting interface enabling the *user-friendly* control of, and automated data 
 acquisition on, Thermo Fisher Scientific and FEI microscopes from a pure Python environment. Bolted directly on top 
 of a COM interface, ```pyTEM``` is a Python wrapper for, and extension of, the prerequisite Thermo Fisher Scientific 
 / FEI scripting and advanced scripting interfaces.

While it may depend on your microscope installation, ```pyTEM``` will likely need to be run on a microscope control 
 computer with the prerequisite Thermo Fisher Scientific / FEI scripting and advanced scripting interfaces installed 
 and properly configured. For detailed information regarding your microscope's scripting capabilities, please refer to 
 the documentation accompanying your microscope or contact to your microscope supplier.

In addition to the main scripting interface, pyTEM ships with various [scripts](#scripts). Besides being useful 
 in-and-of-themselves, these scripts demonstrate how to interface with and control the microscopes using ```pyTEM```. 
 A list of available scripts can be found [below](#scripts). These scripts are included as part of pyTEM for the sake 
 of consolidating the TEM Laboratory's scripting efforts.

# Contribution & Contact Info

```pyTEM``` is developed and maintained by the TEM Microscopy Laboratory at BASF SE in Ludwigshafen, Germany. If you 
 have any questions about the ```pyTEM``` project or would like to contribute or collaborate, please contact Philipp 
 Müller at [philipp.mueller@basf.com](mailto:philipp.mueller@basf.com).

Issues should be reported to the issues board [here](https://github.com/basf/pyTEM/issues).

# Interface

```pyTEM``` is a microscope scripting interface. This means that you can issue commands to, and receive microscope data 
 from, compatible microscopes by calling ```pyTEM``` functions. This is not a complete interface in that it does not 
 provide access to all the microscope's functionality. However, it provides access to all fundamental microscope 
 functions as well as some more advanced functions which were required for the development of one or more 
 [```pyTEM``` scripts](#scripts).

```pyTEM``` aims to be more *user-friendly* than the underlying Fisher Scientific / FEI scripting and advanced 
 scripting interfaces. To this end: 
- ```pyTEM``` functions return only built-in data types or instances of useful, simple classes (no pointers).
- ```pyTEM``` accepts input and returns results in *user-friendly* units. For example, stage position is set in 
 microns/degrees, and tilt speed in degrees-per-second.
- ```pyTEM``` provides many additional functions not directly available through the underlying interface. For example, 
 tilt-while-acquiring, metadata evaluation, and save-to-file functionality.
- ```pyTEM``` is open source and licensed such that users can make any changes or modifications required to
  suit their own installation.

Finally, ```pyTEM``` is a good starting place for those interested in learning how to control their microscope from a 
 pure Python environment.

```pyTEM``` [controls](#controls) are divided across Python 
 [mixins](https://www.pythontutorial.net/python-oop/python-mixin/). This simplified 
 [class-diagram](/docs/pyTEM%20Class%20Diagram%20-%20Simple.jpg) 
 was built to help articulate ```pyTEM```'s architecture. Notice that some mixins include other mixins, and a pyTEM 
 ```Interface``` includes all mixins along with some [interface-level controls](#interface-level-controls).
 
### Controls

#### Acquisition Controls

Microscope acquisition controls including ```acquisition()``` and ```acquisition_series()``` functions. By means of 
 multitasking, both functions offer beam-blanker optimization and acquire-while-tilting functionality.

These functions return ```pyTEM``` ```Acquistion``` and ```AcquisitionSeries``` objects, respectively. Both the 
 ```Acquistion``` and ```AcquisitionSeries``` classes provide helpful methods for further image and metadata 
 manipulation as well as save-to-file functionality. 

#### Acquisition Controls Example

```
from pyTEM.Interface import Interface
from pathlib import Path


my_microscope = Interface()

# Get a list of available cameras.
available_cameras = my_microscope.get_available_cameras()

if len(available_cameras) > 0:
    # Let's see what each camera can do...
    for camera in available_cameras:
        my_microscope.print_camera_capabilities(camera_name=camera)

    # Perform a single blanker-optimized acquisition using the first available camera.
    acq = my_microscope.acquisition(camera_name=available_cameras[0], exposure_time=1, 
                                    sampling='4k', blanker_optimization=True)

    # Downsample the acquisition (bilinear decimation by a factor of 2).
    acq.downsample()
    
    # Display a pop-up with the results of our acquisition.
    acq.show_image()

    # Save the acquisition to file.
    downloads_path = str(Path.home() / "Downloads")
    acq.save_to_file(out_file=downloads_path + "/test_acq.tif")

else:
    print("No available cameras!")
```

#### Magnification Controls

When in *imaging* mode, get and set both TEM and STEM magnification. When in *diffraction* mode, get and set 
 camera-length.

#### Magnification Controls Example

```
from pyTEM.Interface import Interface
my_microscope = Interface()

# Make sure we are in TEM imaging mode.
my_microscope.set_mode(new_mode="TEM")
my_microscope.set_projection_mode(new_projection_mode="imaging")

# Print out the current magnification.
current_magnification = my_microscope.get_magnification()
print("Current magnification: " + str(current_magnification) + "x Zoom")

# Print a list of available magnifications.
my_microscope.print_available_magnifications()

# TEM magnification is set by index, let's increase the magnification by three notches.
current_magnification_index = my_microscope.get_magnification_index()
my_microscope.set_tem_magnification(new_magnification_index=current_magnification_index + 3)

# And decrease it back down by one notch.
my_microscope.shift_tem_magnification(magnification_shift=-1)
```

#### Image and Beam Shift Controls

Get and set both image and beam shift.

#### Image and Beam Shift Controls Example

```
from pyTEM.Interface import Interface
my_microscope = Interface()

# Print out the current image shift.
u = my_microscope.get_image_shift()
print("Current image shift in the x-direction: " + str(u[0]))
print("Current image shift in the y-direction: " + str(u[1]))

# Print out the current beam shift.
v = my_microscope.get_beam_shift()
print("\nCurrent beam shift in the x-direction: " + str(v[0]))
print("Current beam shift in the y-direction: " + str(v[1]))

# Shift the image 2 microns to the right, and 3 microns up.
my_microscope.set_image_shift(x=u[0] + 2, y=u[1] + 3)

# Move the beam shift to (-10 um, 5 um).
my_microscope.set_beam_shift(x=-10, y=5)

# Print out the new image shift.
u = my_microscope.get_image_shift()
print("\nNew image shift in the x-direction: " + str(u[0]))
print("New image shift in the y-direction: " + str(u[1]))

# Print out the new beam shift.
v = my_microscope.get_beam_shift()
print("\nNew beam shift in the x-direction: " + str(v[0]))
print("New beam shift in the y-direction: " + str(v[1]))

# Zero both image and beam shift.
my_microscope.zero_shifts()
```

#### Mode Controls

Microscope mode controls, including getters and setters for instrument, illumination, and projection mode.

#### Mode Controls Example

```
from pyTEM.Interface import Interface
my_microscope = Interface()

# Make sure we are in TEM imaging mode.
my_microscope.set_mode(new_mode="TEM")
my_microscope.set_projection_mode(new_projection_mode="imaging")

# Print out the current projection submode.
my_microscope.print_projection_submode()

# Print out the current illumination mode.
print("\nCurrent illumination mode: " + my_microscope.get_illumination_mode())
if my_microscope.get_illumination_mode() == "microprobe":
    print("This mode provides nearly parallel illumination at the cost of a larger probe size.")
else:
    print("Use this mode to get a small convergent electron beam.")
    
# Switch to STEM mode.
my_microscope.set_mode(new_mode="STEM")
```

#### Screen Controls

Insert and retract the FluCam screen.

#### Screen Controls Example

```
from pyTEM.Interface import Interface
my_microscope = Interface()

# Make sure the FluCam screen is inserted.
if my_microscope.get_screen_position() == "retracted":
    my_microscope.insert_screen()
```

#### Beam Blanker Controls

Blank and un-blank the electron beam.

#### Beam Blanker Controls Example

```
from pyTEM.Interface import Interface
my_microscope = Interface()

if my_microscope.beam_is_blank():
    print("The beam is blanked... un-blanking beam...")
    my_microscope.unblank_beam()
else:
    print("The beam is un-blanked... blanking beam...")
    my_microscope.blank_beam()
```

#### Stage Controls

Microscope stage controls, including those to get and set the stage position, monitor the stage status, and inspect 
 the current specimen-holder's capabilities.

#### Stage Controls Example

```
from pyTEM.Interface import Interface
my_microscope = Interface()

# Print out the stage's current status.
my_microscope.print_stage_status()

# Reset the microscope stage to the home position.
if not my_microscope.stage_is_home():
    my_microscope.reset_stage_position()
    
# Update the stage position along the x, y, and alpha-tilt axes. Move at half speed.
my_microscope.set_stage_position(x=5, y=10, alpha=-45, speed=0.5)
 
# Print out the current stage position.
my_microscope.print_stage_position()
```

#### Vacuum Controls

Vacuum system controls, including those to read gauge pressures, monitor the vacuum in the column, and control the 
 column valve.

#### Vacuum Controls Example

```
from pyTEM.Interface import Interface
my_microscope = Interface()

# Print out the current status of the vacuum system.
my_microscope.print_vacuum_status()

# Print out vacuum info in a table-like format.
my_microscope.print_vacuum_info()

# Check if the column is under vacuum.
if my_microscope.column_under_vacuum():
    print("The column is currently under vacuum; it is safe to open the column valve.")
else:
    print("Column vacuum is insufficient to open the column valve.")
    
# Make sure the column valve is closed.
if my_microscope.get_column_valve_position() == "open":
    my_microscope.close_column_valve()
```

#### Interface-Level Controls

Additionally, some ```pyTEM``` functions are defined within the ```Interface``` class itself (rather than included from 
 one of the other mixins). Often, these functions utilize functions from the included mixins.

#### Interface-Level Controls Example

```
from pyTEM.Interface import Interface
my_microscope = Interface()

# Normalize all lenses.
my_microscope.normalize()

# Prepare for holder removal.
my_microscope.prepare_for_holder_removal()

# Return the microscope to a safe state.
my_microscope.make_safe()
```

### Limited Interfaces

As we have seen, a ```pyTEM``` interface can be established by creating an instance of the ```pyTEM.Interface``` class. 
 However, one can also create interfaces that support a limited subset of ```pyTEM``` functions. For example, we can 
 create a ```pyTEM``` interface with only stage controls: 
```
from pyTEM.lib.mixins.StageMixin import StageInterface
stage_interface = StageInterface()
```

Using ```stage_interface```, we can perform the same series of stage commands performed [above](#stage-controls):
```
# Print out the stage's current status.
stage_interface.print_stage_status()

# Reset the microscope stage to the home position.
if stage_interface.stage_is_home():
    pass
else:
    stage_interface.reset_stage_position()

# Update the x, y, and alpha stage positions. Move at half speed.
stage_interface.set_stage_position(x=5, y=10, alpha=-45, speed=0.5)

# Print out the current stage position.
stage_interface.print_stage_position()
```

This technique can be useful when speed is an issue, or when it's best-practice to restrict unnecessary control. 
 Custom interfaces can be created by including only the required mixins. For example, if you need stage and 
 beam-blanker controls but nothing else, you may want to use an instance of the following limited interface:
```
import comtypes.client as cc

from pyTEM.lib.mixins.StageMixin import StageMixin
from pyTEM.lib.mixins.BeamBlankerMixin import BeamBlankerMixin


class StageBeamBlankerInterface(StageMixin, BeamBlankerMixin):
    """
    A microscope interface with only stage and beam blanker controls.
    """

    def __init__(self):
        try:
            self._tem = cc.CreateObject("TEMScripting.Instrument")
        except OSError as e:
            print("Unable to connect to the microscope.")
            raise e
```

### Automated Image Alignment with ```Hyperspy```

Several ```pyTEM``` functions and scripts use ```Hyperspy```'s ```estimate_shift2D()``` function to estimate the pixel 
 offset between images. This function uses a phase correlation algorithm based on the following paper:
<pre>
Schaffer B, Grogger W, Kothleitner G. Automated spatial drift correction for EFTEM image series. Ultramicroscopy. 
    2004 Dec;102(1):27-36. doi: 10.1016/j.ultramic.2004.08.003. PMID: 15556698.
</pre>

# Scripts

```pyTEM``` scripts are sequences of commands that perform useful data acquisitions, initialize 
 or return the microscope to some pre-defined state, or achieve some other common task. They, often heavily, rely on 
 the ```pyTEM``` ```Interface``` or other ```pyTEM``` library functions. ```pyTEM``` scripts are distributed with, 
 and automatically installed alongside, ```pyTEM``` itself.

```pyTEM``` scripts are run from the command line. For example:
```
micro_ed --verbose
```

To view script usage, use the ```--help``` option:
```
micro_ed --help
```

Often, ```pyTEM``` scripts utilize custom ```Tkinter``` UIs to simplify and streamline IO.

Since all ```pyTEM``` scripts utilize ```pyTEM``` itself, running ```pyTEM``` scripts requires all of ```pyTEM``` 
 along with its prerequisites and dependencies.

### micro_ed
```micro_ed``` is BASF's micro-crystal electron diffraction (MicroED) automated imaging script. MicroED allows for the 
 fast, high-resolution 3D structure determination of small chemical compounds and biological macromolecules. More on 
 MicroED [here](https://en.wikipedia.org/wiki/Microcrystal_electron_diffraction).

```micro_ed``` achieves automated image alignment by computing the image deviation during a preparatory tilt 
 sequence and then applying a compensatory image shift during the main acquisition sequence. This automated image 
 alignment functionality is optional. ```micro_ed``` only collects the data, it does not analyse it.
 
```micro_ed``` results can be saved as a single multi-image stack file or as multiple single-image files. Since 
 performing a MicroED acquisition sequence requires some actions that aren't easily automated (such as selecting 
 suitable particles and setting the eucentric height), a series of ```Tkinter``` message boxes guide the user through 
 those steps requiring manual interaction.

### align_images

```align_images``` allows the user to load some images from file (possibly from a single multi-image stack file or 
 possibly from multiple single-image files), align the images, and then save the results back to file as a single 
 multi-image stack.

Colour images are converted to 8bit unsigned greyscale prior to alignment.

### bulk_carbon_analysis

Given 16 natural light-micrographs of a bulk carbon sample sandwiched between polarizers of varying cross, produce both 
 anisotropy and orientation maps.

Colour images are converted to 8bit unsigned greyscale prior to analysis.

This script uses the technique explained in the following paper:
<pre>
Gillard, Adrien & Couégnat, Guillaume & Caty, O. & Allemand, Alexandre & P, Weisbecker & Vignoles, Gerard. (2015). 
    A quantitative, space-resolved method for optical anisotropy estimation in bulk carbons. Carbon. 91. 423-435. 
    10.1016/j.carbon.2015.05.005.
</pre>

### controller

Allows users to control their microscope with an Xbox controller. This is especially helpful for microscope operators working 
 off-site.
  
# Installation

Because ```pyTEM``` is often required on microscope control machines which lack internet connectivity, pyTEM is not 
 listed on the Python Package Index, nor anywhere else. Rather, we provide a wheel file in [/dist](/dist) and the 
 following [offline install instructions](#offline-install-instructions).

### Offline Install Instructions
##### Part 1. On a system with internet access:
1. Download [requirements.txt](./requirements.txt).
2. Download the required dependencies with pip ```pip download -d ./pytem_dependencies -r requirements.txt```.
3. Download the ```pyTEM``` wheel from [/dist](/dist).

Transfer ```requirements.txt```, the entire ```pytem_dependencies``` folder you just created, and the ```pyTEM``` 
 wheel to the offline machine (any directory is fine; most opt for current user's Downloads directory).

##### Part 2. On the offline system:
1. Ensure both [pip](https://pypi.org/project/pip/) and [wheel](https://pypi.org/project/wheel/) are already installed.
2. Install the required dependencies with pip: 
 ```pip install --no-index --find-links ./pytem_dependencies -r requirements.txt```
3. Install ```pyTEM``` itself with pip. Example: ```pip install pyTEM-0.1.0-py3-none-any.whl```

If you run into any problems installing the required dependencies, check that you are using the same version of pip and 
 wheel on both the online and offline systems.

### In case you need to build your own custom ```pyTEM``` wheel
1. Install wheel with ```pip install wheel```.
2. Download the whole ```pyTEM``` project directory.
3. Navigate to the pyTEM folder.
4. Run ```setup.py``` with the ```bdist_wheel``` setuptools command. 
 Example: ```python setup.py bdist_wheel```

# Authorship

```pyTEM``` is developed and maintained by the TEM microscopy laboratory at BASF SE in Ludwigshafen, Germany. The 
 initial development was performed by RISE (Research Internships in Science and Engineering) Interns from North America. 
 More on the RISE program [here](https://www.daad.de/rise/en/).

### *[Meagan Jennings](https://github.com/MaeJennings) (Sept - Dec 2021)*

#### Hometown: 
Baltimore, Maryland, USA

#### Contributions:

- Figured out how to interface with and control the microscope from a pure Python environment.
- developed ```TEMPackage```, the predecessor to ```pyTEM```. View the project as it existed at the time of Meagan's 
 final commit [here](https://github.com/basf/pyTEM/tree/a91f30e11cc648c47cd2d977442754d2cda1e31c).
- Developed ```microED_Tilt_Series```, the predecessor to ```pyTEM```'s ```micro_ed``` script. View the project on 
 GitLab [here](https://gitlab.roqs.basf.net/raa-os-apps/xem/microed-tem-python-script).
- Wrote the original TEM Scripting Guide, which can be found in [/docs](/docs).

### *[Michael Luciuk](https://github.com/mrl280) (May - Aug 2022)*

#### Hometown: 
Saskatoon, Saskatchewan, Canada

#### Contributions:

- Refactored the original ```TEMPackage``` module into the ```pyTEM``` library that we know and love today.
- Refactored the original ```microED_Tilt_Series``` script into the [```micro_ed```](#micro_ed) script that we know and love today.
- Updated and improved both ```pyTEM``` and ```micro_ed```.
- Developed the [```align_images```](#align_images) script and did some initial work on the [```bulk_carbon_analysis```](#bulk_carbon_analysis) script.

You can view the ```pyTEM``` project as it existed at the time of Michael's final commit 
 [here](https://github.com/basf/pyTEM/tree/c0c19a4c8bc481adb15af3e491dd494d15b46ee7).
