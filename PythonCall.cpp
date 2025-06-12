
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

#pragma comment(lib, "python312")

#define HAVE_ROUND
#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include <windows.h>
#include <fstream>
#include <vector>
#include <string>

#include <iostream>
#include <sstream>
#include <exception>
#include <stdexcept>

std::wstring widen(const std::string &str)
{
    std::wostringstream wstm;
    const std::ctype<wchar_t> &ctfacet =
        std::use_facet<std::ctype<wchar_t> >(wstm.getloc());
    for (size_t i = 0; i < str.size(); ++i)
        wstm << ctfacet.widen(str[i]);
    return wstm.str();
}

std::string narrow(const wchar_t *str) {
	if (str == NULL || wcslen(str) == 0) {
		return "";
	}

	std::ostringstream stm;
	const std::ctype<char> &ctfacet = std::use_facet< std::ctype<char> >(stm.getloc());
	while (*str) {
		stm << ctfacet.narrow(*str++, 0);
	}
	return stm.str();
}

int WINAPI DllEntryPoint(
    HINSTANCE hinst, unsigned long reason, void* lpReserved)
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
void setStartValues(ModelInstance* comp) {}

void PrintPyOutErr(fmiComponent c, ModelInstance* comp, PyObject* catcher)
{
    //make python print any errors
    PyErr_Print();
    //get the stdout and stderr from our catchOutErr object
    PyObject* output =
        PyObject_GetAttrString(catcher, "value"); // New reference
    const char* pyStr = PyUnicode_AsUTF8(output); // not be deallocated.
    if (strlen(pyStr) > 0)
        comp->functions.logger(
            c, comp->instanceName, fmiOK, "log", "Python:\n%s", pyStr);
    Py_DECREF(output); //ok
    PyObject* myString = PyUnicode_FromString((char*)""); //New reference.
    PyObject_SetAttrString(catcher, "value", myString);
    Py_DECREF(myString); //ok
}

PyObject* InitializePythonStdoutErrRedirect(PyObject* pModule)
{
    const char* stdOutErr = "import sys\n\
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
    PyRun_SimpleString(stdOutErr);
    //get our catchOutErr created above
    PyObject* catcher =
        PyObject_GetAttrString(pModule, "catchOutErr"); //New reference.
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

	PyObject* valueTuple = PyTuple_New(size); // New reference. �steals�
	PyObject* vrTuple = PyTuple_New(size); // New reference. �steals�
	if ((valueTuple == 0) || (valueTuple == 0)) {
		// Error
		comp->functions.logger(
			c, comp->instanceName, fmiError, "log", "Couldn't create a tuple!");
		return 0;
	}
	for (unsigned int i = 0; i < size; i++) {
		PyObject* obj;
		PyObject* vrObj;
		if (type_ == REAL) {
            obj = PyFloat_FromDouble(
                comp->realValues[i].value); // New reference. �steals�
            vrObj = PyLong_FromLong(
                comp->realValues[i].vr); //New reference. �steals�
        }
        if (type_ == INTEGER) {
            obj = PyLong_FromLong(
                comp->intValues[i].value); //New reference. �steals�
            vrObj = PyLong_FromLong(
                comp->intValues[i].vr); //New reference. �steals�
        }
        if (type_ == BOOL) {
            obj = PyBool_FromLong(
                comp->boolValues[i].value); //New reference. �steals�
            vrObj = PyLong_FromLong(
                comp->boolValues[i].vr); //New reference. �steals�
        }
        if (type_ == STRING) {
	        try{
				char* strAtual = new char(sizeof(comp->strValues[i].value));
				strcpy(strAtual, comp->strValues[i].value);
				int sizeStr = strlen(strAtual);
				if (sizeStr == 0) {
					comp->functions.logger(c, comp->instanceName, fmiError, "log",
						"String nao deveria ser zero aqui");
                    obj = PyUnicode_FromString((char*)" "); //New reference �steals�
                } else {
					obj = PyUnicode_FromStringAndSize(
						(char*)comp->strValues[i].value, sizeStr);
                }
                vrObj = PyLong_FromLong(
                    comp->strValues[i].vr); //New reference. �steals�
            }
            catch (const std::exception &e)
            {
	            comp->functions.logger(c, comp->instanceName, fmiError, "log", "Erro = %s",comp->strValues[i].value);        
            }
        }
        if (obj == 0) {
            // clean up
            comp->functions.logger(c, comp->instanceName, fmiError, "log",
                "Couldn't store a new value in the tuple!");
            continue;
        }
        PyTuple_SetItem(valueTuple, i, obj); // �steals� a reference to o.
        PyTuple_SetItem(vrTuple, i, vrObj); // �steals� a reference to o.
    }

    PyObject* newTuple = PyTuple_New(2); // New reference.
    PyTuple_SetItem(newTuple, 0, valueTuple); // �steals� a reference to o.
    PyTuple_SetItem(newTuple, 1, vrTuple); // �steals� a reference to o.
    return newTuple;
}

// Tuples:
void RecoverFromTuples(fmiComponent c, ModelInstance* comp, PyObject* catcher,
    PyObject* out, unsigned type_)
{
    // We created a new Tuple
    if (!PyTuple_Check(out)) {
        // Error
        comp->functions.logger(
            c, comp->instanceName, fmiError, "log", "Couldn't read the tuple!");
        return;
    }
    PyObject* valueTuple = PyTuple_GetItem(out, 0); // Borrowed reference.
    PyObject* vrTuple = PyTuple_GetItem(out, 1); // Borrowed reference.
    Py_INCREF(valueTuple); /* Prevent valueTuple being deallocated. */
    Py_INCREF(vrTuple); /* Prevent vrTuple being deallocated. */
    Py_ssize_t sizeTuple = PyTuple_Size(valueTuple);
    if (type_ == STRING)
        comp->strValues.reserve(comp->strValues.size() + sizeTuple);
    for (Py_ssize_t i = 0; i < sizeTuple; i++) {
        PyObject* value = PyTuple_GetItem(valueTuple, i); // Borrowed reference.
        PyObject* vr = PyTuple_GetItem(vrTuple, i); // Borrowed reference.
        Py_INCREF(value); /* Prevent being deallocated. */
        Py_INCREF(vr); /* Prevent being deallocated. */
        if (type_ == REAL) {
            ValueDefReal newValue;
            if (value != 0) {
                newValue.value = PyFloat_AsDouble(value);
                comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                    "new output: value = %f!", newValue.value);
            }
            if (vr != 0) {
                newValue.vr = PyLong_AsLong(vr);
                comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                    "new output: vr = %u ", newValue.vr);
            }
            comp->realValues.push_back(newValue);
            comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                "Num of output elem = %d!", comp->realValues.size());
        }
        if (type_ == INTEGER) {
            ValueDefInt newValue;
            if (value != 0) {
                newValue.value = PyLong_AsLong(value);
                comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                    "new output: value = %f!", newValue.value);
            }
            if (vr != 0) {
                newValue.vr = PyLong_AsLong(vr);
                comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                    "new output: vr = %u ", newValue.vr);
            }
            comp->intValues.push_back(newValue);
            comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                "Num of output elem = %d!", comp->intValues.size());
        }
        if (type_ == BOOL) {
            ValueDefBool newValue;
            if (value != 0) {
                newValue.value = PyLong_AsLong(value);
                comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                    "new output: value = %f!", newValue.value);
            }
            if (vr != 0) {
                newValue.vr = PyLong_AsLong(vr);
                comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                    "new output: vr = %u ", newValue.vr);
            }
            comp->boolValues.push_back(newValue);
            comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                "Num of output elem = %d!", comp->boolValues.size());
        }
        if (type_ == STRING) {
            ValueDefString newValue;
            if (value != 0) {
                newValue.value = PyUnicode_AsUTF8(value); // not be deallocated.
                comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                    "new output: value = %s!", newValue.value);
            }
            if (vr != 0) {
                newValue.vr = PyLong_AsLong(vr);
                comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                    "new output: vr = %u ", newValue.vr);
            }
            comp->strValues.push_back(newValue);
            comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                "Num output elem = %d!", comp->strValues.size());
            PrintPyOutErr(c, comp, catcher);
        }
        PrintPyOutErr(c, comp, catcher);
        Py_DECREF(value); //ok
        Py_DECREF(vr); //ok
    }
    Py_DECREF(
        valueTuple); //ok /* No longer interested in valueTuple, it might     */
    /* get deallocated here but we shouldn't care. */
    Py_DECREF(vrTuple); //ok
}

//
void UpdateInputVariables(
    fmiComponent c, ModelInstance* comp, PyObject* myModule)
{
    //set real variables
    PyObject* myFunction =
        PyObject_GetAttrString(myModule, (char*)"SetReal"); //New reference.
    comp->functions.logger(c, comp->instanceName, fmiOK, "log",
        "Creating tuple for real array...");
    PyObject* args = BuildTuple(c, comp, REAL);
    comp->functions.logger(
        c, comp->instanceName, fmiOK, "log", "Calling python SetReal");
    PyObject* out = PyObject_CallObject(myFunction, args); //New reference.

    Py_DECREF(out); //ok
    Py_DECREF(args); //ok
    Py_DECREF(myFunction); //ok

    //set int variables
    myFunction =
        PyObject_GetAttrString(myModule, (char*)"SetInteger"); //New reference.
    comp->functions.logger(c, comp->instanceName, fmiOK, "log",
        "Creating tuple for integer array...");
    args = BuildTuple(c, comp, INTEGER);
    comp->functions.logger(
        c, comp->instanceName, fmiOK, "log", "Calling python SetInteger");
    out = PyObject_CallObject(myFunction, args); //New reference.

    Py_DECREF(out); //ok
    Py_DECREF(args); //ok
    Py_DECREF(myFunction); //ok

    //set boolean variables
    myFunction =
        PyObject_GetAttrString(myModule, (char*)"SetBoolean"); //New reference.
    comp->functions.logger(c, comp->instanceName, fmiOK, "log",
        "Creating tuple for boolean array...");
    args = BuildTuple(c, comp, BOOL);
    comp->functions.logger(
        c, comp->instanceName, fmiOK, "log", "Calling python SetBoolean");
    out = PyObject_CallObject(myFunction, args); //New reference.

    Py_DECREF(out); //ok
    Py_DECREF(args); //ok
    Py_DECREF(myFunction); //ok

    //set string variables
    myFunction =
        PyObject_GetAttrString(myModule, (char*)"SetString"); //New reference.
    comp->functions.logger(c, comp->instanceName, fmiOK, "log",
        "Creating tuple for string array...");
    args = BuildTuple(c, comp, STRING);
    comp->functions.logger(
        c, comp->instanceName, fmiOK, "log", "Calling python SetString");
    out = PyObject_CallObject(myFunction, args); //New reference.

    Py_DECREF(out); //ok
    Py_DECREF(args); //ok
    Py_DECREF(myFunction); //ok

    //clear input variables alredy sent to python
    comp->realValues.clear();
    comp->intValues.clear();
    comp->boolValues.clear();
    comp->strValues.clear();
}

//
void UpdateOutputVariables(
    fmiComponent c, ModelInstance* comp, PyObject* myModule, PyObject* catcher)
{
    //set real variables
    PyObject* myFunction =
        PyObject_GetAttrString(myModule, (char*)"GetReal"); //New reference.
    comp->functions.logger(
        c, comp->instanceName, fmiOK, "log", "Calling python GetReal");
    PyObject* out = PyObject_CallObject(myFunction, 0); //New reference.
    RecoverFromTuples(c, comp, catcher, out, REAL);

    Py_DECREF(out); //ok
    Py_DECREF(myFunction); //ok

    //set int variables
    myFunction =
        PyObject_GetAttrString(myModule, (char*)"GetInteger"); //New reference.
    comp->functions.logger(
        c, comp->instanceName, fmiOK, "log", "Calling python GetInteger");
    out = PyObject_CallObject(myFunction, 0); //New reference.
    RecoverFromTuples(c, comp, catcher, out, INTEGER);

    Py_DECREF(out); //ok
    Py_DECREF(myFunction); //ok

    //set string variables
    myFunction =
        PyObject_GetAttrString(myModule, (char*)"GetBoolean"); //New reference.
    comp->functions.logger(
        c, comp->instanceName, fmiOK, "log", "Calling python GetBoolean");
    out = PyObject_CallObject(myFunction, 0); //New reference.
    RecoverFromTuples(c, comp, catcher, out, BOOL);

    Py_DECREF(out); //ok
    Py_DECREF(myFunction); //ok

    //set string variables
    myFunction =
        PyObject_GetAttrString(myModule, (char*)"GetString"); //New reference.
    comp->functions.logger(
        c, comp->instanceName, fmiOK, "log", "Calling python GetString");
    out = PyObject_CallObject(myFunction, 0); //New reference.
    RecoverFromTuples(c, comp, catcher, out, STRING);

    Py_DECREF(out); //ok
    Py_DECREF(myFunction); //ok
}

// called by fmiInitialize() after setting eventInfo to defaults
// Used to set the first time event, if any.
fmiStatus __declspec(dllexport)
    initialize(fmiComponent c, ModelInstance* comp, fmiEventInfo* eventInfo)
{
    comp->functions.logger(c, comp->instanceName, fmiOK, "log", "Initializing Python");
    //Program name
    Py_SetProgramName(L"PythonModel");

    //Set Python Home
    if (comp->strValues.size() > 0)
		if (strcmp(comp->strValues[0].value, "") != 0)
		{ // first string is always the python path
			std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>> converter;
			std::wstring wide = converter.from_bytes(comp->strValues[0].value);
			const wchar_t* pythonPath = wide.c_str();
			comp->functions.logger(c, comp->instanceName, fmiOK, "log", "pythonhome = %ls",pythonPath);
            if (pythonPath != NULL) {
				Py_SetPythonHome(pythonPath);
            }
        }

    try {
        //Print info header
		std::string headerString =
            "\n#### Program and system information ####\n";
        headerString =
            headerString + "\nProgram Name: %s\nPrefix: %s\nExec Prefix: %s\n" +
            "Program Full Path: %s\nPath: %s\nVersion: %s\nPlatform: %s\nCompiler: %s\n" +
            "Build Info: %s\nPython Home: %s\n";

		comp->functions.logger(c, comp->instanceName, fmiOK, "log",headerString.c_str(),
			narrow(Py_GetProgramName()).c_str(),narrow(Py_GetPrefix()).c_str(),
			narrow(Py_GetExecPrefix()).c_str(),narrow(Py_GetProgramFullPath()).c_str(),
			narrow(Py_GetPath()).c_str(),Py_GetVersion(),Py_GetPlatform(),Py_GetCompiler(),
			Py_GetBuildInfo(),narrow(Py_GetPythonHome()).c_str());
	} catch (const std::runtime_error &e)
	{
		comp->functions.logger(c, comp->instanceName, fmiError, "log", e.what() );
    }

	//Check if python path is ok, there is a bug in the Py_Initialize and it will
    //close everthing if using a invalid python path
    wchar_t* pythonPathTmp = Py_GetPythonHome();
	comp->functions.logger(c, comp->instanceName, fmiOK, "log", "PythonHome =%s\n",narrow(pythonPathTmp).c_str());

    std::wstring pythonPath =pythonPathTmp;
    if (pythonPath.empty() == true)
        pythonPath = Py_GetPrefix();
    ifstream file(std::string(
		std::string(narrow(pythonPath.c_str()).c_str()) + std::string("\\Python.exe"))
                      .c_str());
    if (!file) {
        comp->functions.logger(c, comp->instanceName, fmiError, "log",
			"It is not possible to locate Python.exe!");
        return fmiError;
    }
    //initialize python interface
    Py_Initialize();

    if (Py_IsInitialized()) {
        //prepare to collect python outputs and errors
        PyObject* pModule =
            PyImport_AddModule("__main__"); //Borrowed reference.
        Py_INCREF(pModule);
        PyObject* catcher =
            InitializePythonStdoutErrRedirect(pModule); //New reference.

        try {
            //Set path to source files
            comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                "Setting path ..\\..\\sources");
            PyObject* myPath = PySys_GetObject("path"); //Borrowed reference.
            Py_INCREF(myPath);
            PyObject* myPathString =
                PyUnicode_FromString((char*)"..\\..\\sources"); //New reference.
            PyList_Append(myPath, myPathString);

            //Run initialize module
            PyObject* myModuleString =
                PyUnicode_FromString((char*)"initialize"); //New reference.
            comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                "Importing python initialize module...");
            PyObject* myModule =
                PyImport_Import(myModuleString); //New reference.
            PrintPyOutErr(c, comp, catcher);

            if (myModule != 0) {
                //update real, int, bool and string values em python code
                comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                    "Updating Input Variables...");
                UpdateInputVariables(c, comp, myModule);
                PrintPyOutErr(c, comp, catcher);

                //run initialize main
				comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                    "Getting python main() function...");
                PyObject* myFunction = PyObject_GetAttrString(
                    myModule, (char*)"main"); //New reference.
				comp->functions.logger(c, comp->instanceName, fmiOK, "log",
					"Calling function main()");
				PyObject* out =
					PyObject_CallObject(myFunction, 0); //New reference.
				PrintPyOutErr(c, comp, catcher);

                comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                    "Updating Output Variables...");
                UpdateOutputVariables(c, comp, myModule, catcher);
                PrintPyOutErr(c, comp, catcher);

                // Clean up
                Py_DECREF(out); //ok
                Py_DECREF(myFunction); //ok
                //Py_DECREF(myModule);  //outro vai ter que fazer isso
            }
            Py_DECREF(myModuleString); //ok
            Py_DECREF(myPath); // n�o limpar o path, da erro
            Py_DECREF(myPathString); //ok
            //Setting config for time event step
            eventInfo->upcomingTimeEvent = fmiTrue;
            eventInfo->nextEventTime = 1 + comp->time;

            //save initialize object as state object
            comp->stateObj = myModule;

        } catch (std::exception &e) {
            comp->functions.logger(
                c, comp->instanceName, fmiError, "log", e.what());
            comp->functions.logger(c, comp->instanceName, fmiError, "log",
                "Error in python interface initialization");
            PrintPyOutErr(c, comp, catcher);
            Py_XDECREF(catcher);
            //Py_XDECREF(pModule);
            return fmiError;
        }
        if (catcher == 0) {
            comp->functions.logger(
                c, comp->instanceName, fmiError, "log", "Ahh??");
        }
        if (pModule == 0) {
            comp->functions.logger(
                c, comp->instanceName, fmiError, "log", "why??");
        }
        Py_XDECREF(catcher); //ok
        Py_DECREF(pModule); //ok
    }
    return fmiOK;
}
//------------------------------------------------------------------------------

//
fmiReal getEventIndicator(ModelInstance* comp, int z)
{
    return 1;
}

// Used to set the next time event, if any.
fmiStatus eventUpdate(
    fmiComponent c, ModelInstance* comp, fmiEventInfo* eventInfo)
{
    if (Py_IsInitialized()) {
        //prepare to collect python outputs and errors
        PyObject* pModule =
            PyImport_AddModule("__main__"); //Borrowed reference.
        Py_INCREF(pModule);
        PyObject* catcher =
            InitializePythonStdoutErrRedirect(pModule); //New reference.

        try {
            PyObject* myModuleString =
                PyUnicode_FromString((char*)"eventUpdate");

            comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                "Importing EventUpdate python module...");
            PyObject* myModule =
                PyImport_Import(myModuleString); //New reference.
            PrintPyOutErr(c, comp, catcher);

            comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                "Updating Input Variables...");
            //update real, int, bool and string values em python code
            UpdateInputVariables(c, comp, myModule);
            PrintPyOutErr(c, comp, catcher);

            comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                "Getting python main() function...");
            PyObject* myFunction = PyObject_GetAttrString(
                myModule, (char*)"main"); //New reference.

            comp->functions.logger(
                c, comp->instanceName, fmiOK, "log", "Calling function main()");
            //buid tuple with args
            PyObject* stateTuple = PyTuple_New(1); // New reference.
            PyTuple_SetItem(
                stateTuple, 0, comp->stateObj); // �steals� a reference to o.
            //call eventUpdate.main(state)
            PyObject* out =
                PyObject_CallObject(myFunction, stateTuple); //New reference.
            PrintPyOutErr(c, comp, catcher);

            comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                "Updating Output Variables...");
            UpdateOutputVariables(c, comp, myModule, catcher);
            PrintPyOutErr(c, comp, catcher);

            // Clean up
            Py_DECREF(out); //ok
            Py_DECREF(myFunction); //ok
            Py_DECREF(myModule); //ok
            Py_DECREF(myModuleString); //ok
        } catch (...) {
            comp->functions.logger(c, comp->instanceName, fmiError, "log",
                "Error in python eventUpdate");
            PrintPyOutErr(c, comp, catcher);
            eventInfo->terminateSimulation = fmiTrue;
            Py_XDECREF(catcher);
            Py_XDECREF(pModule);
            return fmiError;
        }
        Py_XDECREF(catcher); //ok
        Py_XDECREF(pModule);
    }
    //Setting config for time event step
    eventInfo->upcomingTimeEvent = fmiTrue;
    eventInfo->nextEventTime = 1 + comp->time;
    eventInfo->iterationConverged = fmiTrue;
    eventInfo->terminateSimulation = fmiFalse;
    return fmiOK;
}

//
fmiStatus Finalize(fmiComponent c, ModelInstance* comp)
{
    if (Py_IsInitialized()) {
        //prepare to collect python outputs and errors
        PyObject* pModule =
            PyImport_AddModule("__main__"); //Borrowed reference.
        Py_INCREF(pModule);
        PyObject* catcher =
            InitializePythonStdoutErrRedirect(pModule); //New reference.

        try {
            comp->functions.logger(
                c, comp->instanceName, fmiOK, "log", "Finalizing Python");
            PyObject* myModuleString = PyUnicode_FromString((char*)"finalize");
            comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                "Importing finalize python module...");
            PyObject* myModule =
                PyImport_Import(myModuleString); //New reference.
            PrintPyOutErr(c, comp, catcher);

            if (myModule != 0) {
                //run finalize main
                comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                    "Getting python main() function...");
                PyObject* myFunction = PyObject_GetAttrString(
                    myModule, (char*)"main"); //New reference.
                PrintPyOutErr(c, comp, catcher);

                comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                    "Calling function main()");
                //buid tuple with args
                PyObject* stateTuple = PyTuple_New(1); // New reference.
                PyTuple_SetItem(stateTuple, 0,
                    comp->stateObj); // �steals� a reference to o.
                //call finalize.main(state)
                PyObject* out = PyObject_CallObject(
                    myFunction, stateTuple); //New reference.
                PrintPyOutErr(c, comp, catcher);

                // Clean up
                Py_DECREF(out); //ok
                Py_DECREF(myFunction); //ok
            }
            Py_DECREF(myModuleString); //ok
            Py_DECREF(myModule); //ok
            Py_DECREF(comp->stateObj); // free the initialized python state   ok
            comp->functions.logger(c, comp->instanceName, fmiOK, "log",
                "Finalizing embedded python interface");
            //Py_Finalize();

        } catch (...) {
            comp->functions.logger(c, comp->instanceName, fmiError, "log",
                "Error in python finalization interface ");
            PrintPyOutErr(c, comp, catcher);
            Py_XDECREF(catcher);
            Py_XDECREF(pModule);
            //Py_Finalize();
            return fmiError;
        }
        Py_XDECREF(catcher); //ok
        Py_XDECREF(pModule); //ok
    }
    return fmiOK;
}
//------------------------------------------------------------------------------

// include code that implements the FMI based on the above definitions
#include "fmuTemplate.c"

