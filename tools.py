'''
version: 1.0.0
date: 21/04/2020

#----------------
content: 

self.check_input() #print input infomation
self.input_unit() #convert input list in a string

root_grp(input = '', repalce_np = False) #Create a group over the input		
asign_color(input = '', color = '') #asign color to the input
replace_name(input = '', custom = False, custom_name = 'customName', autoRoot = True, replace_nc = False) #Change names with or without Hierarchy
hide_attr(input = '',t= False, r = False, s = False, v = False, show = False) #Hide attrs in channel box o show them all

#----------------
how to: 
	
import RdM_ScriptTools
from RdM_ScriptTools import tools
reload(RdM_ScriptTools.tools)

tool = tools.tools_class()
tool.FUNC_NAME(argument = '')

#----------------
dependencies:   

json
pymel
maya mel
maya.cmds

#----------------
licence: https://www.eulatemplate.com/live.php?token=ySe25XC0bKARQymXaGQGR8i4gvXMJgVS
author:  Esteban Rodriguez <info@renderdemartes.com>

'''

import maya.mel
from maya import cmds
import pymel.core as pm

import json

#----------------------------------------------------------------------------------------------------------------

#Read name conventions as nc['']
PATH = cmds.internalVar(usd = True) + 'RdM_ScriptTools'
JSON_FILE = (PATH+'/NameConventions.json')
with open(JSON_FILE) as json_file:
	nc = json.load(json_file)

#----------------------------------------------------------------------------------------------------------------
#create base class for selection objects

class Tools_class:
	
	def __init__(self, input = ''):
		
		self.input = input
#----------------------------------------------------------------------------------------------------------------			
	#input can be an argument or a selection
	def check_input(self, func = '', print_input = False):
		if self.input == '':
						
			self.input = cmds.ls(sl = True)
			if (print_input):
				print '{} input is selection: {}'.format(func, self.input)
			
		else:
			if (print_input):
				print '{} input is argument: {}'.format(func, self.input)

#----------------------------------------------------------------------------------------------------------------			
	#If input is a list make it a simple object	
	def input_unit(self):
		
		#if input is nothing ERROR message
		if len(self.input) == 0:
			cmds.error('selection is empty, please check input')
			
		#if input is a string do nothing	
		elif type(self.input) == str:
			self.input = self.input 	
			
		#if input is a list select the first one only
		else:
			self.input = self.input[0]
		
		print '{}'.format(self.input)
	
	
#----------------------------------------------------------------------------------------------------------------			
	#create a group over the 
	def	root_grp(self, input = '', custom = False, custom_name = 'customName', autoRoot = True, replace_nc = False):
		
		#Check input
		if input != '':
			self.input = [input]
			
		else:	
			self.input = input	
		
		self.check_input('root_grp')			
				
		#Group to have something to work after the command
		groups = []
		
		for i in self.input:
			
			if autoRoot == True:           
				group_names = ['Root', 'Auto']
			if custom == True:
				group_names = [customName]          
			if custom and autoRoot:
				group_names = ['Root', 'Auto',customName]
				
			for name in group_names:
				
				cmds.select(i)
				father = cmds.listRelatives(i, p =1)
				
				#Null group as parent in same xform
				group_zero = cmds.group(em=1, n = '{}_{}'.format(i,name) + nc['group'])
				cmds.delete(cmds.parentConstraint(i,group_zero, mo =0))
			  
				cmds.parent(i,group_zero)
				
				#if they have upper nodes, put them inside
				if father :cmds.parent(group_zero, father) 
				cmds.select(group_zero)
				
				#Remove Nameconventions		
				if (replace_nc):
					try:group_zero = self.replace_name(input = '', search = nc['ctrl'], replace = '', hi = False)
					except:pass
					
					try:group_zero = self.replace_name(input = '', search = nc['joint'], replace = '', hi = False)
					except:pass	
				
				#return this groups				
				groups.append(group_zero)     
				
		return groups    

#----------------------------------------------------------------------------------------------------------------		
	#Search and Replace names
	
	def replace_name(self, input = '', search = '', replace = '', hi = True):
			
		if hi ==True:

			pm.mel.searchReplaceNames(search, replace, "hierarchy")
			cmds.select(hi = True)
	
		else:
			pm.mel.searchReplaceNames(search, replace, "selected")
	
	
		return cmds.ls(sl = True)


#----------------------------------------------------------------------------------------------------------------		
	#Asign Color
	
	def asign_color(self, input = '', color = 'white'):
		
		if input != '':
			self.input = [input]
			
		else:	
			self.input = input	
			
		self.check_input('assing_color')		
		
		colors = {  'red':       13,
					'blue':       6,
					'white':     16,
					'purple':     9,
					'green':     14, 
					'lightBlue': 18,
					'yellow':    17,
					'grey':      1 }

		color_num = colors[color]
		
		for obj in self.input:
			cmds.setAttr ('{}.overrideEnabled'.format(obj), 1)
			cmds.setAttr ('{}.overrideColor'.format(obj), color_num)
			
#----------------------------------------------------------------------------------------------------------------					
	def hide_attr(self, input = '',t= False, r = False, s = False, v = False, show = False):

		if input != '':
			self.input = [input]
			
		else:	
			self.input = input

		self.check_input('hide_attr')
		
		#Axis to hide in selection input
		axis_to_hide = ['X','Y','Z']
		
		#hide selected attrs
		for i in self.input:

			if (t):
				for T in self.input:
					for axis in axis_to_hide:
						cmds.setAttr('{}.translate{}'.format(T, axis),lock = True, keyable = False, channelBox = False)
		
			if (r):
				for T in self.input:
					for axis in axis_to_hide:
						cmds.setAttr('{}.rotate{}'.format(R, axis),lock = True, keyable = False, channelBox = False)
		
			if (s):
				for S in self.input:
					for axis in axis_to_hide:
						cmds.setAttr('{}.scale{}'.format(S, axis),lock = True, keyable = False, channelBox = False)
		
				
			if (v):
				for V in self.input:
					cmds.setAttr('{}.visibility'.format(V),lock = True, keyable = False, channelBox = False)        
				
			#show and unlock everything
			if (show):
				sel=pm.ls(long=1, sl=1)
				attrs = ['.tx','.ty','.tz','.rx','.ry','.rz','.sx','.sy','.sz','.v']
				
				for eachObj in sel:
					for attr in attrs:	        
						ud=pm.listAttr(eachObj, ud=1)
						pm.setAttr('{}{}'.format(eachObj, attr), k=True)
						pm.setAttr('{}{}'.format(eachObj,attr), l=False)

#----------------------------------------------------------------------------------------------------------------					

#tool = Tools_class()


		
		
		
		
	