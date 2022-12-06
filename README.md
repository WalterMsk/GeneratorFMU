# GeneratorFMU
Small aplication to generate FMU with python code integration

The purpose of this tool is to help create FMUs (Functional Mockup Units) for using python codes in computer simulation tools that implement the FMI (Fuctional Mockup Interface) standard.

For simple convenience the tool has an FMU generator which basically collects the simulation python files and other files and encapsulates them in a .fmu file.

The most important in this .fmu file is the PythonModel.fmu library that makes the interface between the python code and the C standard, which is used for implementing the FMI standard.

# What's in the package?
- The solution consists of an FMU generating application;
- 3 configuration files in python (initialize.py, eventUpdate.py, finalize.py);
- A model description template in XML, necessary for FMU configuration.

# Install and configure

## How to configure?
To configure it will be necessary to fill in the .py files and the .xml descriptor. The .py files will be called in the different stages of the simulation and filling each of them will be explained below.

### .py files
The first file is the model initialization file provided in python code. This file will be executed at simulation startup, just once. The purpose is to initialize any necessary variables and/or establish any initial settings. Figures 1 and 2 show the initialization template for the model, the other templates are very similar with just a few specific differences.
 
Figure 1 – Initialization file template

 
Figure 2 - Initialization file template (continued)

### Definition of the number of output variables
It is necessary to define in all template files how many output variables (outputs) will be returned by the model, separated by variable type. For example, if the program is going to return two outputs of real type and one of integer type, these values must be inserted in the respective configurations, as shown in Figure 3.
 
Figure 3 – Configure the number of outputs by type

### Definition of the main function (main)
In the main function, the code that will be executed for initialization must be inserted, here another code present in another python file can also be called if desired. Some important points for filling this role are:
Use the appropriate functions to get inputs and set outputs
Following the standards of the FMI standard, the variables are divided by type and here they are separated by arrays. Therefore, to obtain the real variables, for example, the specific input of the real type must be used:

var = realArray[findValueWithVR(0,realArrayVR)];

In this example, the var variable will receive the real value referring to an input with a reference value (VR) equal to 0. The findValueWithVR function is an auxiliary function of optional use that aims to retrieve the value of a given array from an informed VR .

To use the model outputs, it is necessary to declare the output arrays, as shown in the template:

#If there is outputs, you must define then here also
global outputReal
global outputRealVR

Both the inputs and outputs of the template must be arrays, so the values must be defined inside parentheses separated by commas. For example:

outputReal = (var,)
outputRealVR = (1000,)

outputInt = (varInt,varInt2)
outputIntVR = (2000,2001)

At the end of initialization, all variables created in this file will be stored and can be used later in eventUpdate.py through the state parameter, as shown in Figure 4. This variable can only be accessed from the eventUpdate.py file.

 
Figure 4 – Use of the state variable

### Functions for handling inputs and outputs
The final part of the templates has the functions that will be used to get and write the input and output arrays. Functions of type Set and Get for each type of variable following the model defined in the FMI standard. This part of the templates should not be changed.
