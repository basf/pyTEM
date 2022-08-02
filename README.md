# Disclaimer

```pyTEM``` was developed for use on the BASF SE TEM Laboratory's Talos F200i transmission electron microscope.
 The authors provide no guarantee that the software will function as intended, either in part or in whole, on any 
 other microscope installation.

```pyTEM``` is available under the MIT license [here](/LICENSE).

# About

```pyTEM``` is a *high-level* scripting interface enabling the *user-friendly* control of, and automated data acquisition
 on, Thermo Fisher Scientific and FEI microscopes from a pure Python environment. Bolted directly on top of a COM 
 interface, ```pyTEM``` is a Python wrapper for, and extension of, the prerequisite Thermo Fisher Scientific / FEI scripting 
 interface.

While it may depend on your microscope installation, ```pyTEM``` will likely need to be run on a microscope control 
 computer with the prerequisite Thermo Fisher Scientific / FEI scripting interface installed and properly configured. For 
 detailed information regarding your microscope's scripting capabilities, please refer to the documentation 
 accompanying your microscope or contact to your microscope supplier.

In addition to the main scripting interface, pyTEM ships with various scripts. Besides being usful in-and-of-themselves, 
 these scripts demonstrate how to interface with and control the microscopes using ```pyTEM```. A list of available scripts
 can be found [below](#scripts).

# Interface

```pyTEM``` is a microscope scripting interface. This means that you can issue commands to, and recieve data from, compatible 
 microscopes using ```pyTEM``` functions. This is not a complete interface in that it does not provide access to all of the microscope's 
 functionality. However, it provides access to all fundamental microscope functions as well as some more advanced functions which 
 were required for the development of one or more [```pyTEM``` scripts](#scripts).

```pyTEM``` aims to be more *user-friendly* than the underlying Fisher Scientific / FEI scripting interface. To this end: 
- ```pyTEM``` functions return only built-in data types or instances of useful, simple classes.
- ```pyTEM``` accepts input and returns results in *user-friendly* units. For example, stage position is set in microns/degrees, and tilt sped in degrees-per-second.
- ```pyTEM``` provides many additional functions not directly available through the underlying interface. For example, tilt-while-acquiring and save-to-file functionality.
 - ```pyTEM``` is open source and liscenced such that users can make any changes or modifications required to
  suit their own installation.

Finally, ```pyTEM``` is a good starting place for those interested in learning how to control their microscope from a pure 
 Python environment.
 

  ```pyTEM``` provides the following [controls](#controls)
  
### Controls
 
### Acquisition Controls

Beam blanker optimized, allow aquire-while-tilting functionality. Return Acquisition 

#### Acquisition Controls Example

```
from pyTEM.Interface import Interface
my_microscope = Interface()

# TODO
```

### Magnification Controls

Set and get magnification

#### Magnification Controls Example

```
from pyTEM.Interface import Interface
my_microscope = Interface()

# Get the current magnification.
magnification = my_microscope.get_magnification()

# TODO


```

### Image and Beam Shift Controls


#### Image and Beam Shift Controls Example

```
from pyTEM.Interface import Interface
my_microscope = Interface()

# Print out the current image shift.
u = my_microscope.get_image_shift()
print("Current image shift along the x-axis: " + str(u[0]))
print("Current image shift along the y-axis: " + str(u[1]))

# Shift the image 2 microns to the right, and 3 microns up
my_microscope.set_image_shift(x=u[0] + 2, y=u[1] + 3)
```

### Mode Controls


#### Mode Controls Example

```
from pyTEM.Interface import Interface
my_microscope = Interface()

# TODO
```


### Screen Controls

Insert and retract the FluCam screen.

#### Screen Controls Example

```
from pyTEM.Interface import Interface
my_microscope = Interface()

# TODO
```

### Beam Blanker Controls

Blank and un-blank the electron beam.

#### Beam Blanker Controls Example

```
from pyTEM.Interface import Interface
my_microscope = Interface()

# TODO
```

### Stage Controls



#### Stage Controls Example

```
from pyTEM.Interface import Interface
my_microscope = Interface()

# TODO
```

### Vacuum Controls



#### Vacuum Controls Example

```
from pyTEM.Interface import Interface
my_microscope = Interface()

# TODO
```


# Scripts

```pyTEM``` scripts are stand-alone sequences of ```pyTEM``` instructions that perform usful acquisition series, initialize or 
 return the microscope to some pre-defined state, or achieve some other common task. ```pyTEM``` scripts are distributed with, 
 and automatically installed alongside, ```pyTEM``` itself. Please see [installation](#installation) for more.

```pyTEM``` scipts are run from the command line. For example,
```
micro_ed --verbose
```
To view script usage, use the ```help``` option,
```
micro_ed --help
```

Often, ```pyTEM``` scripts utalize custom ```Tkinter``` user-interfaces to simplify and streamline IO.

Since all ```pyTEM``` scripts utalize ```pyTEM``` itself, they all require that the prerequisite Thermo Fisher Scientific / FEI scripting 
 interface is properly installed and configured.
 


### micro_ed
```micro_ed``` is BASF's micro-crystal electron diffraction (MicroED) automated imaging script. MicroED allows for fast,
 high resolution 3D structure determination of small chemical compounds and biological macromolecules. More on MicroED 
 [here](https://en.wikipedia.org/wiki/Microcrystal_electron_diffraction).

```micro_ed``` achieves automated image alignment by computing the image deviation during a preparatory tilt 
 sequence and then applying a compensatory image shift during the main acquisition sequence. This automated image alignment 
 is optional. 
 
View script usage with
```
micro_ed --help
```

### align_images

```align_images``` 

User IO is handled ```Tkinter``` windows


View script usage with
```
align_images --help
```

### bulk_carbon_analysis


View script usage with
```
bulk_carbon_analysis --help
```

##### Quick-start Example

```
from pyTEM.MicroED import MicroED

MicroED().run(verbose=True)
```

# Authorship

```pyTEM``` is developed and maintained by the TEM microscopy laboratory at BASF SE in Ludwigshafen, Germany. The 
 initial development was performed by RISE (Research Internships in Science and Engineering) Interns from North America. 
 More on the RISE program here: https://www.daad.de/rise/en/.

### *[Meagan Jennings](https://github.com/MaeJennings) (Sept - Dec 2021)*

#### Hometown: 
Baltimore, Maryland, USA

#### Contributions:

- Figured out how to interface with and control the microscope from a pure Python environment.
- developed ```TEMPackage```, the predecessor to ```pyTEM```'s ```Interface``` module. View the project as it existed at the time of Meagan's final commit [here](https://github.com/mrl280/pyTEM/tree/a91f30e11cc648c47cd2d977442754d2cda1e31c).
- Developed ```microED_Tilt_Series```, the predecessor to ```pyTEM```'s ```MicroED``` module. View on GitLab [here](https://gitlab.roqs.basf.net/raa-os-apps/xem/microed-tem-python-script).
- Wrote the original TEM Scripting Guide, which can be found in [docs](/docs).

### *[Michael Luciuk](https://github.com/mrl280) (May - Aug 2022)*

#### Hometown: 
Saskatoon, Saskatchewan, Canada

#### Contributions:

- Refactored the original ```TEMPackage``` and ```microED_Tilt_Series``` into the ```Interface``` and ```MicroED```
 ```pyTEM``` modules we know and love today.

You can view the ```pyTEM``` project as it existed at the time of Michael's final commit [here](https://github.com/mrl280/pyTEM). # TODO: Update after Michael leaves
  
# Installation

Because ```pyTEM``` is often required on microscope control machines which lack internet connectivity, pyTEM is not 
 listed on the Python Package Index (PyPI), nor anywhere else. Rather, we provide a wheel file in [dist](/dist) and 
 [offline install instructions](#offline-install-instructions).

### Offline install instructions
##### On a system with internet access:
1. Download [requirements.txt](./requirements.txt)
2. Download the required dependencies with pip ```pip download -d ./pytem_dependencies -r requirements.txt```
3. Download the ```pyTEM``` wheel file from [dist](/dist).

Transfer ```requirements.txt```, the entire ```pytem_dependencies``` folder you just created, and the ```pyTEM``` wheel file to the offline machine.

##### On the offline system:
1. Install the required dependencies with pip: 
 ```pip install --no-index --find-links ./pytem_dependencies -r requirements.txt```
2. Install ```pyTEM``` itself with pip. Example: ```pip install pyTEM-0.1.0-py3-none-any.whl```


### If you need to build your own custom ```pyTEM``` wheel:
1. Install wheel with ```pip install wheel```, 
2. Download the whole ```pyTEM``` project directory,
3. Navigate to the pyTEM folder, 
4. Run ```setup.py``` with the ```bdist_wheel``` setuptools command. 
 Example: ```python setup.py bdist_wheel```

# Contribution & Contact Info

```pyTEM``` is developed and maintained by the TEM Microscopy Laboratory at BASF SE in Ludwigshafen, Germany. If you 
 have any questions about the ```pyTEM``` project or would like to contribute or colaborate, please contact Philipp Müller at
 [philipp.mueller@basf.com](mailto:philipp.mueller@basf.com).

Issues should be reported [here](https://github.com/mrl280/pyTEM/issues)
