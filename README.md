# Disclaimer

TODO. Also make a pop-up box with the disclaimer

# About

The ```tem-scripting-package``` provides a Python wrapper for the scripting interface of Thermo Fisher Scientific and FEI microscopes. The ```tem-scripting-package``` provides a single microscope interface, bolted directly ontop of a COM interface.

This is not a complete interface; it does not provide access to all the functionality of the original scripting interface. However, it provides access to most of the basic microscope functions as well as those required by other related projects. Additionally, this provides several examples for beginners wanting to interface with and control the microscope via scripting from a Python environment.

This package was developed for and tested on the FEI Talos F200i, and may not be compatible (at least not completely) with other Thermo Fisher Scientific and FEI microscopes. For detailed information about TEM scripting, please see the documentation accompanying your microscope.


# Authorship

The ```tem-scripting-package``` was developed by RISE (Research Internships in Science and Engineering) Interns. More on the RISE program here: https://www.daad.de/rise/en/.

### *Meagan Jennings (Sept - Dec 2019)*

#### Hometown: 
TODO

#### Contributions:

- Figured out how to interface with and control the microscope from a pure Python environment.
- developed the original ```TEMPackage```. TODO: Link to file
- Developed the original ```microED_Tilt_Series```. TODO: Link to file
- Wrote the original *TEM Scripting Guide*. TODO: Link to file


### *Michael Luciuk (May - Aug 2022)*

#### Hometown: 
Saskatoon, Saskatchewan, Canada

#### Contributions:

- Refactored the original ```TEMPackage``` and ```microED_Tilt_Series``` into their current state.


# Installation

TODO


# Contribution

TODO


# Quick-start Example

```
from Interface.Interface import Interface
my_tem = Interface()

# Get the current magnification
magnification = my_tem.get_magnification()

# Shift the image 2 microns to the right, and 3 microns up
u = my_tem.get_image_shift()
my_tem.set_image_shift(x=u[0] + 2, y=u[1] + 3)
```

# Related projects

#### Micro Electron Diffraction: 
The ```tem-scripting-package``` was developed to support the TEM micro-ED package, ```tem-ued-package```. To streamline the concurrent development of both packages, they currently both reside here, in this repository. 

More on microcrystal electron diffraction here: https://en.wikipedia.org/wiki/Microcrystal_electron_diffraction.
