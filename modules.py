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
version = '3.0.1'

import math

import maya.mel
from maya import cmds
import pymel.core as pm
from maya import OpenMaya

import os
import json

try: 
	import tools
	reload(tools)
	import kinematics
	reload(kinematics)
except:
	import RdM_ScriptTools
	from RdM_ScriptTools import tools
	reload(RdM_ScriptTools.tools)
	from RdM_ScriptTools import kinematics
	reload(RdM_ScriptTools.kinematics)

#----------------


#Read name conventions as nc['']
#PATH = cmds.internalVar(usd = True) + 'RdM_ScriptTools'
PATH = os.path.dirname(__file__)

JSON_FILE = (PATH+'/name_conventions.json')
with open(JSON_FILE) as json_file:
	nc = json.load(json_file)
SETUP_FILE = (PATH+'/rig_setup.json')
with open(SETUP_FILE) as setup_file:
	setup = json.load(setup_file)

#----------------------------------------------------------------------------------------------------------------

class Modules_class(kinematics.Kinematics_class):

	def __init__ (self):
		''

#----------------------------------------------------------------------------------------------------------------

	def create_block(self, attrs = {'name':''}):
		''

#----------------------------------------------------------------------------------------------------------------

	def build_base(self, name='RdM_Tools_V3', size = 1):
		'''
		This will crate the base structure for any kinf of rig with the same base sctructure
		'''

		#main grp
		main_grp = cmds.group(em=True, name = setup['main_grp'])

		#create base Groups
		base_groups = setup['base_groups']
		print (base_groups)

		for grp in base_groups:
			base_grp = cmds.group(em=True, n = base_groups[grp] + nc['group'])
			cmds.parent(base_grp, main_grp)
		
		geo_groups = setup['geo_groups']
		print (geo_groups)		
		for grp in geo_groups:
			geo_grp = cmds.group(em=True, n = geo_groups[grp] + nc['group'])
			cmds.parent(geo_grp, base_groups['geometry']+nc['group'])		
				
		rig_groups = setup['rig_groups']
		print (rig_groups)		
		for grp in rig_groups:
			rig_grp = cmds.group(em=True, n = rig_groups[grp] + nc['group'])
			cmds.parent(rig_grp, base_groups['rig']+nc['group'])	

		
		#create the base controllers

#----------------------------------------------------------------------------------------------------------------

	def arm_leg_module(self):		
		''



		

