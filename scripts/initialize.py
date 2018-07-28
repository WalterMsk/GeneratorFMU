# -*- coding: utf-8 -*-
'''
Created on 23/07/2018

@author: Walter Mazuroski
'''

realOutSize = 0
intOutSize = 0
boolOutSize = 0
strOutSize = 0

#you can use this function to call inputs by defined value reference(VR)
def findValueWithVR(id, vr):
	for i, item in enumerate(vr):
		if int(item) == int(id): 
			return i
	  
def main():
	#Write here your initializing program
	
	#If there is outputs, you must define then here also
	#outputReal,outputRealVR
	#outputInt,outputIntVR
	#outputBool,outputBoolVR
	#outputStr,outputStrVR
	print 'initialized'
    
	
# defining input variables
def SetReal(value, vr):
	global realArray;
	global realArrayVR;
	realArray = list(value)
	realArrayVR = list(vr)
	
def SetInteger(value, vr):
	global intArray;
	global intArrayVR;
	intArray = list(value)
	intArrayVR = list(vr)	

def SetBoolean(value, vr):
	global boolArray;
	global boolArrayVR;
	boolArray = list(value)
	boolArrayVR = list(vr)	
	
def SetString(value, vr):
	global stringArray;
	global stringArrayVR;
	stringArray = list(value)
	stringArrayVR = list(vr)


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