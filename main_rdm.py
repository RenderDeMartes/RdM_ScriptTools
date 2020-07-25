'''
version: 1.0.0
date: 21/04/2020


#----------------
how to: 
	
import RdM_ScriptTools
from RdM_ScriptTools import main_rdm
reload(RdM_ScriptTools.main_rdm)

rdm = main_rdm.RdM()
rdm.FUNC(ARGUMENTS)

#----------------
dependencies:   
	
math
json
pymel
maya mel
maya.cmds
OpenMaya

tools.Tools_Class
kinematics.Kinematics_class


#----------------
licence: https://www.eulatemplate.com/live.php?token=ySe25XC0bKARQymXaGQGR8i4gvXMJgVS
author:  Esteban Rodriguez <info@renderdemartes.com>

'''
import math

import maya.mel
from maya import cmds
import pymel.core as pm
from maya import OpenMaya

import os
import json

try: 
	import kinematics
	reload(kinematics)

except:
	import RdM_ScriptTools
	from RdM_ScriptTools import kinematics
	reload(RdM_ScriptTools.kinematics)



#----------------

class RdM(kinematics.Kinematics_class):

	def __init__ (self):
		''
