# -*- coding: utf-8 -*-
'''
Created on 23/07/2018

@author: Walter Mazuroski
'''

realOutSize = 0
intOutSize = 0
boolOutSize = 0
strOutSize = 0

def main():

	print 'event updated!'
    
# defining input variables
def SetReal(value, vr):
	global realArray;
	global realArrayVR;
	realArray = list(value)
	realArrayVR = list(vr)
	if len(realArray) > 0:
		print 'adicionado var1 = ', realArray[0], 'value ref = ', vr[0]
	if len(realArray) > 1:
		print '\nadicionado var2 = ', realArray[1], 'value ref = ', vr[1]
	
def SetInteger(value, vr):
	global intArray;
	global intArrayVR;
	intArray = list(value)
	intArrayVR = list(vr)	
	if len(intArray) > 0:
		print 'adicionado var1 = ', intArray[0]
	if len(intArray) > 1:
		print '\nadicionado var2 = ', intArray[1]

def SetBoolean(value, vr):
	global boolArray;
	global boolArrayVR;
	boolArray = list(value)
	boolArrayVR = list(vr)	
	if len(boolArray) > 0:
		print 'adicionado var1 = ', boolArray[0]
	if len(boolArray) > 1:
		print '\nadicionado var2 = ', boolArray[1]
	
def SetString(value, vr):
	global stringArray;
	global stringArrayVR;
	stringArray = list(value)
	stringArrayVR = list(vr)
	if len(stringArray) > 0:
		print 'adicionado var1 = ', stringArray[0]
	if len(stringArray) > 1:
		print '\nadicionado var2 = ', stringArray[1]		


# defining output variables
def GetReal():
	if realOutSize > 0:
		return (outputReal,outputRealVR)
	else:
		return 0
	
def GetInteger():
	if intOutSize > 0:
		return (outputInt,outputIntVR)
	else:
		return 0
		
def GetBoolean():
	if boolOutSize > 0:
		return (outputBool,outputBoolVR)
	else:
		return 0
		
def GetString():
	if strOutSize > 0:
		return (outputStr,outputStrVR)
	else:
		return 0