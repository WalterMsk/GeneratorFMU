/* ---------------------------------------------------------------------------*
 * fmuTemplate.h
 * Definitions used in fmiModelFunctions.c and by the includer of this file
 * Copyright QTronic GmbH. All rights reserved.
 * ---------------------------------------------------------------------------*/

#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <vector>

#ifdef __cplusplus
extern "C" {
#endif

#ifdef FMI_COSIMULATION
#include "fmiFunctions.h"
#else
#include "fmiModelFunctions.h"
#endif

// macros used to define variables
#define  r(vr) comp->r[vr]
#define  i(vr) comp->i[vr]
#define  b(vr) comp->b[vr]
#define  s(vr) comp->s[vr]
#define pos(z) comp->isPositive[z]
#define copy(vr, value) setString(comp, vr, value)

fmiStatus setString(fmiComponent comp, fmiValueReference vr, fmiString value);

#define not_modelError (modelInstantiated|modelInitialized|modelTerminated)

typedef enum {
    modelInstantiated = 1<<0,
    modelInitialized  = 1<<1,
    modelTerminated   = 1<<2,
    modelError        = 1<<3
} ModelState;

typedef struct {
    fmiReal value;
    fmiValueReference vr;

} ValueDefReal;

typedef struct {
    fmiInteger value;
    fmiValueReference vr;

} ValueDefInt;

typedef struct {
    fmiBoolean value;
    fmiValueReference vr;

} ValueDefBool;

typedef struct {
    fmiString value;
    fmiValueReference vr;

} ValueDefString;

typedef struct {
    //fmiReal    *r;
    //fmiInteger *i;
    //fmiBoolean *b;
    //fmiString  *s;
    std::vector <ValueDefReal> realValues;
    std::vector <ValueDefInt> intValues;
    std::vector <ValueDefBool> boolValues;
    std::vector <ValueDefString> strValues;
    fmiBoolean *isPositive;
    fmiReal time;
    fmiString instanceName;
    fmiString GUID;
    fmiCallbackFunctions functions;
    fmiBoolean loggingOn;
    ModelState state;
    PyObject* stateObj;
#ifdef FMI_COSIMULATION
    fmiEventInfo eventInfo;
#endif
} ModelInstance;

#ifdef __cplusplus
} // closing brace for extern "C"
#endif
