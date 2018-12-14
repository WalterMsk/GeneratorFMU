
//   Important note about DLL memory management when your DLL uses the
//   static version of the RunTime Library:
//
//   If your DLL exports any functions that pass String objects (or structs/
//   classes containing nested Strings) as parameter or function results,
//   you will need to add the library MEMMGR.LIB to both the DLL project and
//   any other projects that use the DLL.  You will also need to use MEMMGR.LIB
//   if any other projects which use the DLL will be performing new or delete
//   operations on any non-TObject-derived classes which are exported from the
//   DLL. Adding MEMMGR.LIB to your project will change the DLL and its calling
//   EXE's to use the BORLNDMM.DLL as their memory manager.  In these cases,
//   the file BORLNDMM.DLL should be deployed along with your DLL.
//
//   To avoid using BORLNDMM.DLL, pass string information using "char *" or
//   ShortString parameters.
//
//   If your DLL uses the dynamic version of the RTL, you do not need to
//   explicitly add MEMMGR.LIB as this will be done implicitly for you

#pragma hdrstop
#pragma argsused

#include <vcl.h>
#include <windows.h>
#include <fstream>
#include <Python.h>
#include <vector>

int WINAPI DllEntryPoint(HINSTANCE hinst, unsigned long reason, void* lpReserved)
{
	return 1;
}

#define FMI_COSIMULATION

// define class name and unique id
#define MODEL_IDENTIFIER PythonModel
#define MODEL_GUID "{8c4e810f-3df3-4a00-8276-176fa3c9f003}"
#define REAL 0
#define INTEGER 1
#define BOOL 2
#define STRING 3

//defines to build tuple function
#define VALUE = 0
#define VR = 1

// define model size
#define NUMBER_OF_STATES 0
#define NUMBER_OF_EVENT_INDICATORS 0

// include fmu header files, typedefs and macros
#include "fmuTemplate.h"

// called by fmiInstantiateModel
// Set values for all variables that define a start value
// Settings used unless changed by fmiSetX before fmiInitialize
void setStartValues(ModelInstance* comp) {
}


void PrintPyOutErr(fmiComponent c, ModelInstance* comp, PyObject *catcher)
{
	//make python print any errors
	PyErr_Print();
	//get the stdout and stderr from our catchOutErr object
	PyObject *output = PyObject_GetAttrString(catcher,"value");
	std::string pyStr = PyString_AsString(output);
	if (!pyStr.empty())
		comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Python:\n%s",pyStr.c_str());
	Py_DECREF(output);
	PyObject* myString = PyString_FromString((char*)"");
	PyObject_SetAttrString(catcher,"value",myString);
	Py_DECREF(myString);
}

PyObject *InitializePythonStdoutErrRedirect(PyObject *pModule)
{
	 std::string stdOutErr =
"import sys\n\
class CatchOutErr:\n\
	def __init__(self):\n\
		self.value = ''\n\
	def write(self, txt):\n\
		self.value += txt\n\
catchOutErr = CatchOutErr()\n\
sys.stdout = catchOutErr\n\
sys.stderr = catchOutErr\n\
"; //this is python code to redirect stdouts/stderr

	//invoke code to redirect
	PyRun_SimpleString(stdOutErr.c_str());
	//get our catchOutErr created above
	PyObject *catcher = PyObject_GetAttrString(pModule,"catchOutErr");
	return catcher;
}

// Tuples:
PyObject* BuildTuple(fmiComponent c, ModelInstance* comp, unsigned type_)
{
	// We create a new Tuple
	unsigned int size = 0;
	if (type_ == REAL)
		size = comp->realValues.size();
	if (type_ == INTEGER)
		size = comp->intValues.size();
	if (type_ == BOOL)
		size = comp->boolValues.size();
	if (type_ == STRING)
		size = comp->strValues.size();

	PyObject* valueTuple = PyTuple_New(size);
	PyObject* vrTuple = PyTuple_New(size);
	if ((valueTuple == 0) || (valueTuple == 0)) {
		// Error
		comp->functions.logger(c, comp->instanceName, fmiError, "log", "Couldn't create a tuple!");
		return 0;
	}
	for (unsigned int i = 0; i < size; i++) {
		PyObject* obj;
		PyObject* vrObj;
		if (type_ == REAL) {
			obj = PyFloat_FromDouble(comp->realValues[i].value);
			vrObj = PyInt_FromLong(comp->realValues[i].vr);
		}
		if (type_ == INTEGER) {
			obj = PyInt_FromLong(comp->intValues[i].value);
			vrObj = PyInt_FromLong(comp->intValues[i].vr);
		}
		if (type_ == BOOL) {
			obj = PyBool_FromLong(comp->boolValues[i].value);
			vrObj = PyInt_FromLong(comp->boolValues[i].vr);
		}
		if (type_ == STRING) {
			obj = PyString_FromString(comp->strValues[i].value);
			vrObj = PyInt_FromLong(comp->strValues[i].vr);
		}

		if (obj == 0) {
			// clean up
			comp->functions.logger(c, comp->instanceName, fmiError, "log",
									 "Couldn't store a new value in the tuple!");
			return 0;
		}
		PyTuple_SetItem(valueTuple, i, obj);
		PyTuple_SetItem(vrTuple, i, vrObj);
	}

	PyObject* newTuple = PyTuple_New(2);
	PyTuple_SetItem(newTuple, 0, valueTuple);
	PyTuple_SetItem(newTuple, 1, vrTuple);
	return newTuple;
}

// Tuples:
void RecoverFromTuples(fmiComponent c, ModelInstance* comp, PyObject* out, unsigned type_)
{
	// We create a new Tuple
	if (!PyTuple_Check(out)) {
		// Error
		comp->functions.logger(c, comp->instanceName, fmiError, "log", "Couldn't read the tuple!");
		return;
	}
	PyObject *valueTuple = PyTuple_GetItem(out, 0);
	PyObject *vrTuple = PyTuple_GetItem(out, 1);
	for(Py_ssize_t i = 0; i < PyTuple_Size(valueTuple); i++) {
		if (type_ == REAL) {
			PyObject *value = PyTuple_GetItem(valueTuple, i);
			PyObject *vr = PyTuple_GetItem(vrTuple, i);
			ValueDefReal newValue;
			if (value != 0) {
				newValue.value = PyFloat_AsDouble(value);
				comp->functions.logger(c, comp->instanceName, fmiOK, "log", "new output = %f!",newValue.value);
			}
			if (vr != 0) {
				newValue.vr = PyInt_AsLong(vr);
			}
			comp->realValues.push_back(newValue);
			comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Num output elem = %d!",comp->realValues.size());
		}
		if (type_ == INTEGER) {
			PyObject *value = PyTuple_GetItem(valueTuple, i);
			PyObject *vr = PyTuple_GetItem(vrTuple, i);
			ValueDefInt newValue;
			if (value != 0) {
				newValue.value = PyInt_AsLong(value);
				comp->functions.logger(c, comp->instanceName, fmiOK, "log", "new output = %f!",newValue.value);
			}
			if (vr != 0) {
				newValue.vr = PyInt_AsLong(vr);
			}
			comp->intValues.push_back(newValue);
			comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Num output elem = %d!",comp->intValues.size());
		}
		if (type_ == BOOL) {
			PyObject *value = PyTuple_GetItem(valueTuple, i);
			PyObject *vr = PyTuple_GetItem(vrTuple, i);
			ValueDefBool newValue;
			if (value != 0) {
				newValue.value = PyInt_AsLong(value);
				comp->functions.logger(c, comp->instanceName, fmiOK, "log", "new output = %f!",newValue.value);
			}
			if (vr != 0) {
				newValue.vr = PyInt_AsLong(vr);
			}
			comp->boolValues.push_back(newValue);
			comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Num output elem = %d!",comp->boolValues.size());
		}
		if (type_ == STRING) {
			PyObject *value = PyTuple_GetItem(valueTuple, i);
			PyObject *vr = PyTuple_GetItem(vrTuple, i);
			ValueDefString newValue;
			if (value != 0) {
				newValue.value = PyString_AsString(value);
				comp->functions.logger(c, comp->instanceName, fmiOK, "log", "new output = %f!",newValue.value);
			}
			if (vr != 0) {
				newValue.vr = PyInt_AsLong(vr);
			}
			comp->strValues.push_back(newValue);
			comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Num output elem = %d!",comp->strValues.size());
		}
	}
	Py_DECREF(valueTuple);
	Py_DECREF(vrTuple);
}

//
void UpdateInputVariables(fmiComponent c, ModelInstance* comp, PyObject* myModule)
{
	//set real variables
	PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"SetReal");
	comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Creating tuple for real array...");
	PyObject *args = BuildTuple(c,comp,REAL);
	comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Calling python SetReal");
	PyObject_CallObject(myFunction, args);

	Py_DECREF(args);
	Py_DECREF(myFunction);

	//set int variables
	myFunction = PyObject_GetAttrString(myModule,(char*)"SetInteger");
	comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Creating tuple for integer array...");
	args = BuildTuple(c,comp,INTEGER);
	comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Calling python SetInteger");
	PyObject_CallObject(myFunction, args);

	Py_DECREF(args);
	Py_DECREF(myFunction);

	//set string variables
	myFunction = PyObject_GetAttrString(myModule,(char*)"SetBoolean");
	comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Creating tuple for boolean array...");
	args = BuildTuple(c,comp,BOOL);
	comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Calling python SetBoolean");
	PyObject_CallObject(myFunction, args);

	Py_DECREF(args);
	Py_DECREF(myFunction);

	//set string variables
	myFunction = PyObject_GetAttrString(myModule,(char*)"SetString");
	comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Creating tuple for string array...");
	args = BuildTuple(c,comp,STRING);
	comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Calling python SetString");
	PyObject_CallObject(myFunction, args);

	Py_DECREF(args);
	Py_DECREF(myFunction);
}


//
void UpdateOutputVariables(fmiComponent c, ModelInstance* comp, PyObject* myModule)
{
	//set real variables
	PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"GetReal");
	comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Calling python GetReal");
	PyObject *out = PyObject_CallObject(myFunction, 0);
	RecoverFromTuples(c,comp,out,REAL);

	//Py_DECREF(out);
	Py_DECREF(myFunction);

	//set int variables
	myFunction = PyObject_GetAttrString(myModule,(char*)"GetInteger");
	comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Calling python GetInteger");
	out = PyObject_CallObject(myFunction, 0);
	RecoverFromTuples(c,comp,out,INTEGER);

	Py_DECREF(out);
	Py_DECREF(myFunction);

	//set string variables
	myFunction = PyObject_GetAttrString(myModule,(char*)"GetBoolean");
	comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Calling python GetBoolean");
	out = PyObject_CallObject(myFunction, 0);
	RecoverFromTuples(c,comp,out,BOOL);

	Py_DECREF(out);
	Py_DECREF(myFunction);

	//set string variables
	myFunction = PyObject_GetAttrString(myModule,(char*)"GetString");
	comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Calling python GetString");
	out = PyObject_CallObject(myFunction, 0);
	RecoverFromTuples(c,comp,out,STRING);

	Py_DECREF(out);
	Py_DECREF(myFunction);
}

// called by fmiInitialize() after setting eventInfo to defaults
// Used to set the first time event, if any.
bool initialize(fmiComponent c, ModelInstance* comp, fmiEventInfo* eventInfo)
{
	comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Initializing Python");
	Py_Initialize();
	//prepare to collect python outputs and errors
	PyObject *pModule = PyImport_AddModule("__main__");
	PyObject *catcher = InitializePythonStdoutErrRedirect(pModule);

	try {
		//Set path to source files
		comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Setting path ..\\..\\sources");
		PyObject* myPath = PySys_GetObject("path");
		PyObject* myPathString = PyString_FromString((char*)"..\\..\\sources");
		int res = PyList_Append(myPath, myPathString);

		PyObject* myModuleString = PyString_FromString((char*)"initialize");
		comp->functions.logger(c, comp->instanceName, fmiOK, "log",
										"Importing python initialize module...");
		PyObject* myModule = PyImport_Import(myModuleString);
		PrintPyOutErr(c,comp,catcher);

		if (myModule != 0) {
			//update real, int, bool and string values em python code
			comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Updating Input Variables...");
			UpdateInputVariables(c,comp,myModule);
			PrintPyOutErr(c,comp,catcher);

			//run initialize main
			comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Getting python main() function...");
			PyObject *myFunction = PyObject_GetAttrString(myModule,(char*)"main");
			comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Calling function main()");
			PyObject_CallObject(myFunction, 0);
			comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Terminou de chamar main()");
			PrintPyOutErr(c,comp,catcher);

			comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Updating Output Variables...");
			UpdateOutputVariables(c,comp,myModule);
			PrintPyOutErr(c,comp,catcher);

			// Clean up
			//Py_DECREF(result);
			Py_DECREF(myFunction);
			//Py_DECREF(myModule);
		}
		Py_DECREF(myModuleString);
		//Py_DECREF(myPath);   // não limpar o path, da erro
		Py_DECREF(myPathString);
		//Setting config for time event step
		eventInfo->upcomingTimeEvent   = fmiTrue;
		eventInfo->nextEventTime       = 1 + comp->time;

        //save initialize object as state object
		comp->stateObj = myModule;

	}catch(...)
	{
		comp->functions.logger(c, comp->instanceName, fmiError, "log", "Error in python interface initialization");
		PrintPyOutErr(c, comp,catcher);
		Py_XDECREF(catcher);
		//Py_XDECREF(pModule);
		return false;
	}
	if (catcher == 0) {
		comp->functions.logger(c, comp->instanceName, fmiError, "log", "Ahh??");
	}
	if (pModule == 0) {
		comp->functions.logger(c, comp->instanceName, fmiError, "log", "why??");
	}
	//Py_DECREF(catcher);
	//Py_DECREF(pModule);
	return true;
}
//------------------------------------------------------------------------------

//
fmiReal getEventIndicator(ModelInstance* comp, int z)
{
	return 1;
}

// Used to set the next time event, if any.
void eventUpdate(fmiComponent c, ModelInstance* comp, fmiEventInfo* eventInfo)
{
	//prepare to collect python outputs and errors
	PyObject *pModule = PyImport_AddModule("__main__");
	PyObject *catcher = InitializePythonStdoutErrRedirect(pModule);

	try {
		PyObject* myModuleString = PyString_FromString((char*)"eventUpdate");

		comp->functions.logger(c,comp->instanceName, fmiOK, "log", "Importing EventUpdate python module...");
		PyObject* myModule = PyImport_Import(myModuleString);
		PrintPyOutErr(c,comp,catcher);

		comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Updating Input Variables...");
		//update real, int, bool and string values em python code
		UpdateInputVariables(c,comp, myModule);
		PrintPyOutErr(c,comp,catcher);

		comp->functions.logger(c,comp->instanceName, fmiOK, "log", "Getting python main() function...");
		PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"main");

		comp->functions.logger(c,comp->instanceName, fmiOK, "log", "Calling function main()");
		//buid tuple with args
		PyObject* stateTuple = PyTuple_New(1);
		PyTuple_SetItem(stateTuple, 0, comp->stateObj);
		//call eventUpdate.main(state)
		PyObject_CallObject(myFunction, stateTuple);
		PrintPyOutErr(c,comp,catcher);

		comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Updating Output Variables...");
		UpdateOutputVariables(c,comp,myModule);
		PrintPyOutErr(c,comp,catcher);

		// Clean up
		Py_DECREF(myFunction);
		//Py_DECREF(myModule);
		Py_DECREF(myModuleString);
		//Py_DECREF(catcher);
		//Py_DECREF(pModule);
	}
	catch(...)
	{
		comp->functions.logger(c, comp->instanceName, fmiError, "log", "Error in python eventUpdate");
		PrintPyOutErr(c, comp,catcher);
		eventInfo->terminateSimulation = fmiTrue;
		Py_XDECREF(catcher);
		//Py_XDECREF(pModule);
		return;
	}

	//Setting config for time event step
	eventInfo->upcomingTimeEvent   = fmiTrue;
	eventInfo->nextEventTime       = 1 + comp->time;
	eventInfo->iterationConverged  = fmiTrue;
	eventInfo->terminateSimulation = fmiFalse;
	return;
 }

//
bool Finalize(fmiComponent c, ModelInstance* comp)
{
	//prepare to collect python outputs and errors
	PyObject *pModule = PyImport_AddModule("__main__");
	PyObject *catcher = InitializePythonStdoutErrRedirect(pModule);

	try {
		comp->functions.logger(c,comp->instanceName, fmiOK, "log", "Finalizing Python");
		PyObject* myModuleString = PyString_FromString((char*)"finalize");
		comp->functions.logger(c,comp->instanceName, fmiOK, "log",
										"Importing finalize python module...");
		PyObject* myModule = PyImport_Import(myModuleString);
		PrintPyOutErr(c,comp,catcher);

		if (myModule != 0) {
			//run finalize main
			comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Getting python main() function...");
			PyObject *myFunction = PyObject_GetAttrString(myModule,(char*)"main");
			PrintPyOutErr(c,comp,catcher);

			comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Calling function main()");
			PyObject_CallObject(myFunction, 0);
			PrintPyOutErr(c,comp,catcher);

			// Clean up
			//Py_DECREF(result);
			//Py_DECREF(myModule);
			Py_DECREF(myFunction);
		}
		Py_DECREF(myModuleString);
		//Py_DECREF(catcher);
		//Py_DECREF(pModule);
		Py_DECREF(comp->stateObj); // free the initialized python state
		comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Finalizing embedded python interface");
	    //Py_Finalize();

	}catch(...)
	{
		comp->functions.logger(c, comp->instanceName, fmiError, "log", "Error in python finalization interface ");
		PrintPyOutErr(c,comp,catcher);
		Py_XDECREF(catcher);
		//Py_XDECREF(pModule);
	    //Py_Finalize();
		return false;
	}
	return true;
}
//------------------------------------------------------------------------------

// include code that implements the FMI based on the above definitions
#include "fmuTemplate.c"

