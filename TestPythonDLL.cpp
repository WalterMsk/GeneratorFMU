#pragma hdrstop
#pragma argsused

#ifdef _WIN32
#include <tchar.h>
#else
  typedef char _TCHAR;
  #define _tmain main
#endif

#pragma comment(lib, "PythonModel")

#include <stdlib.h>
#include <stdio.h>
#include <locale.h>
#include <string.h>

//#define FMI_COSIMULATION
#include "fmiFunctions.h"
#include <fmilib.h>
//#define HAVE_ROUND
//
#include <windows.h>
#include <fstream>
//#include <Python.h>
//#include "fmuTemplate.h"
#include <shlwapi.h>
#include <direct.h>
#include <iostream>
//#include <fmilib.h>

#define jm_dll_function_ptr FARPROC

//extern "C" __declspec(dllimport) fmiStatus initialize(fmiComponent c, ModelInstance* comp, fmiEventInfo* eventInfo);

typedef fmiComponent (*TYPEGETINST)(fmiString, fmiString,
	fmiString, fmiString, fmiReal, fmiBoolean,
	fmiBoolean, fmiCallbackFunctions, fmiBoolean);

typedef FARPROC (*TYPEGETVERSION)(void);

fmiCallbackFunctions callBackFunctions;
jm_callbacks callbacks;
//
//void importlogger(jm_callbacks* c, fmiString module, int log_level, fmiString message)
//{
//	char *buffer = new char [strlen(message)+strlen(module)+100];
//	sprintf(buffer,"module = %s, log level = %s: %s\n", module, jm_log_level_to_string(log_level), message);
//	logFile << buffer  << std::endl;
//	delete [] buffer;
//}

void importlogger(jm_callbacks* c, jm_string module, jm_log_level_enu_t log_level, jm_string message)
{
        printf("module = %s, log level = %d: %s\n", module, log_level, message);
}

//Configure callback struture, FMUInfo class variable
void ConfigureCallbacks(void)
{
	callbacks.malloc = malloc;
	callbacks.calloc = calloc;
	callbacks.realloc = realloc;
	callbacks.free = free;
	callbacks.logger = importlogger;
	callbacks.log_level = jm_log_level_all;
	callbacks.context = 0;

	callBackFunctions.logger = 0;//fmi1_log_forwarding;
	callBackFunctions.allocateMemory = calloc;
	callBackFunctions.freeMemory = free;
   	callBackFunctions.stepFinished = 0;
}
//------------------------------------------------------------------------------

int _tmain(int argc, _TCHAR* argv[])
{
//	fmiCallbackFunctions *functions  = 0;
	chdir("E:\\Git\\GeneratorFMU\\release\\python312\\win64\\");
	HANDLE dll_handle = LoadLibrary("PythonModel.dll");

	if (!dll_handle) {
		std::cout << "could not load the dynamic library" << std::endl;
		return EXIT_FAILURE;
	}

	// resolve function address here

	jm_dll_function_ptr dll_function_ptrptr;
	char* dll_function_name = new char(100);
	strcpy(dll_function_name,"PythonModel_fmiGetVersion");
	dll_function_ptrptr = (jm_dll_function_ptr)GetProcAddress((HMODULE)dll_handle, dll_function_name);
	if (!dll_function_ptrptr) {
		std::cout <<  GetLastError() << std::endl;
		return EXIT_FAILURE;
	}
	fmiString test = (fmiString)dll_function_ptrptr();

    ConfigureCallbacks();
	strcpy(dll_function_name,"PythonModel_fmiInstantiateSlave");
	TYPEGETINST dll_function_ptrptr2 = (TYPEGETINST)GetProcAddress((HMODULE)dll_handle, dll_function_name);
	fmiString  instanceName = "PythonModel" ;
	fmiString GUID = "{8c4e810f-3df3-4a00-8276-176fa3c9f003}" ;
	fmiString fmuLocation = "" ;
	fmiString mimeType = "";
	fmiReal timeout = 0;
	fmiBoolean visible = true;
	fmiBoolean interactive = true;
//	fmiCallbackFunctions functions;
	fmiBoolean loggingOn = true;

	fmiComponent testInstanciate = (fmiComponent)dll_function_ptrptr2(instanceName, GUID, fmuLocation,
				mimeType, timeout, visible, interactive, callBackFunctions, loggingOn);
	if (!testInstanciate) {
		std::cout <<  GetLastError() << std::endl;
		return EXIT_FAILURE;
	}
	delete dll_function_name;
}
