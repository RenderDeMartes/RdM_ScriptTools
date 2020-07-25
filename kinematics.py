'''
version: 1.0.0
date: 21/04/2020

#----------------
content: 

fk_chain(size = 1, color = 'lightBlue', curve_type = 'circleX') #works on selection only
pole_vector(bone_one = '', bone_two = '', bone_three = '') create locator in the correct pv pos
ik_chain(start = '', end = '', size = 1, color = 'lightBlue', curve_type = 'cube', pv = True)
joints_middle(start = '', end = '', axis = 'X', amount = 4)
twist(start = '', end = '', axis = 'X', amount = 4, mode = 'down'

#----------------
how to: 
	
import RdM_ScriptTools
from RdM_ScriptTools import kinematics
reload(RdM_ScriptTools.kinematics)

kin = kinematics.Kinematics_class()
kin.FUNC_NAME(argument = '')

#----------------
dependencies:   
	
math
json
pymel
maya mel
maya.cmds
OpenMaya

tools.Tools_Class

#----------------
licence: https://www.eulatemplate.com/live.php?token=ySe25XC0bKARQymXaGQGR8i4gvXMJgVS
author:  Esteban Rodriguez <info@renderdemartes.com>

'''
import math

import maya.mel as mel
from maya import cmds
import pymel.core as pm
from maya import OpenMaya

import os
import json

try: 
	import tools
	reload(tools)

except:
	import RdM_ScriptTools
	from RdM_ScriptTools import tools
	reload(RdM_ScriptTools.tools)

#----------------------------------------------------------------------------------------------------------------

#Read name conventions as nc['']
#PATH = cmds.internalVar(usd = True) + 'RdM_ScriptTools'
PATH = os.path.dirname(__file__)

JSON_FILE = (PATH+'/NameConventions.json')
with open(JSON_FILE) as json_file:
	nc = json.load(json_file)
SETUP_FILE = (PATH+'/rig_setup.json')
with open(SETUP_FILE) as setup_file:
	setup = json.load(setup_file)

#----------------------------------------------------------------------------------------------------------------
#create base class for selection objects

class Kinematics_class(tools.Tools_class):
	
	def fk_chain(self, size = 1, color = 'lightBlue', curve_type = 'bounding_cube') :

		#Check input
		if input != '':
			self.input = [input]
			
		else:   
			self.input = input  
		
		self.check_input('fk_chain')    

		fk_controllers = []

		for bone in cmds.ls(sl =True) :
			
			#Create controller and groups to zero it
			#fk_controller = cmds.circle( n = '{}{}'.format(bone,nc['ctrl']) , nr = (1,0,0), r = size)[0]
			if curve_type == 'bounding_cube':
				fk_controller = self.bounding_cube(input = bone, size = size, name =  '{}{}'.format(bone,nc['ctrl']))
			else:
				fk_controller = self.curve(type = curve_type, custom_name = True, name = '{}{}'.format(bone,nc['ctrl']), size = size)
			
			cmds.delete(cmds.parentConstraint(bone, fk_controller)) #put the controller in position
			cmds.parentConstraint(fk_controller,bone) #parent Ctrl to Bone
					
			fk_auto_grp = self.root_grp(replace_nc = True)
			 
			#Organize a bit
			self.asign_color(fk_controller, color)
			self.hide_attr(fk_controller, s = True, v = True)

			#try to parent it to create chain 
			if len(fk_controllers) > 0:cmds.parent(fk_auto_grp[0], fk_controllers[-1])
			else:pass 

			#Create Controller List
			fk_controllers.append(fk_controller)
		

		return fk_controllers

#----------------------------------------------------------------------------------------------------------------

	def pole_vector(self, bone_one = '', bone_two = '', bone_three = ''):

		#Thanks to >>> https://vimeo.com/66015036
		if bone_one == '':
				sel = cmds.ls(sl = 1)
				bone_one = sel[0]
				bone_two = sel[1]
				bone_three = sel[2]
		
		else:
			cmds.select(bone_one, bone_two, bone_three)
			sel = cmds.ls(sl = 1)

		start = cmds.xform(sel[0] ,q= 1 ,ws = 1,t =1 )
		mid = cmds.xform(sel[1] ,q= 1 ,ws = 1,t =1 )
		end = cmds.xform(sel[2] ,q= 1 ,ws = 1,t =1 )
		
		startV = OpenMaya.MVector(start[0] ,start[1],start[2])
		midV = OpenMaya.MVector(mid[0] ,mid[1],mid[2])
		endV = OpenMaya.MVector(end[0] ,end[1],end[2])
		
		startEnd = endV - startV
		startMid = midV - startV
		
		dotP = startMid * startEnd
		proj = float(dotP) / float(startEnd.length())
		startEndN = startEnd.normal()
		projV = startEndN * proj
		
		arrowV = startMid - projV
		arrowV*= 0.5
		finalV = arrowV + midV
		
		cross1 = startEnd ^ startMid
		cross1.normalize()
		
		cross2 = cross1 ^ arrowV
		cross2.normalize()
		arrowV.normalize()
		
		matrixV = [arrowV.x , arrowV.y , arrowV.z , 0 ,
		cross1.x ,cross1.y , cross1.z , 0 ,
		cross2.x , cross2.y , cross2.z , 0,
		0,0,0,1]
		
		matrixM = OpenMaya.MMatrix()
		
		OpenMaya.MScriptUtil.createMatrixFromList(matrixV , matrixM)
		
		matrixFn = OpenMaya.MTransformationMatrix(matrixM)
		
		rot = matrixFn.eulerRotation()
		
		loc = cmds.spaceLocator(n = '{}{}'.format(bone_two[0], nc['locator']))[0]
		cmds.xform(loc , ws =1 , t= (finalV.x , finalV.y ,finalV.z))
		
		cmds.xform ( loc , ws = 1 , rotation = ((rot.x/math.pi*180.0),
		(rot.y/math.pi*180.0),
		(rot.z/math.pi*180.0)))
		
		return loc

#----------------------------------------------------------------------------------------------------------------

	def simple_ik_chain(self, start = '', end = '', size = 1, color = 'lightBlue', ik_curve = 'cube', pv_curve = 'sphere', pv = True):
 
		if start == '':
			start = cmds.ls(sl =True)[0]
		if end == '':
			end = cmds.ls(sl =True)[-1]

		ik_system = []

		#create Ik Chain
		ik_handle = cmds.ikHandle (n = '{}{}'.format(end, nc['ik_rp']), sj=start, ee= end, sol = 'ikRPsolver')[0]

		#create ik Controller with offset grp and clean attr
		ctrl = self.curve(type = ik_curve, rename = False, custom_name = True, name = '{}{}'.format(end, nc ['ctrl']), size = size)
		ik_system.append(ctrl)
		self.match(ctrl, end)
		IK_grp = self.root_grp(replace_nc = True)
		self.hide_attr(ctrl, s = True, v = True)

		cmds.orientConstraint(ctrl, end ,mo =True)

		#parent ik to controller
		cmds.parent(ik_handle, ctrl)


		#create pole vector
		if (pv):

			#create pole vector in correct position
			pv_loc = self.pole_vector(bone_one = start, bone_two = cmds.listRelatives(end, p = True), bone_three = end)
			
			#create controller in position with offset grp
			pv_ctrl = self.curve(type = pv_curve, rename = False, custom_name = True, name = '{}_PV{}'.format(end, nc ['ctrl']), size = size/2)
			ik_system.append(pv_ctrl)
			self.match(pv_ctrl, pv_loc)
			cmds.delete(pv_loc)
			cmds.poleVectorConstraint(pv_ctrl, ik_handle)
			pv_grp = self.root_grp(replace_nc = True)        

			#clean controller
			self.hide_attr(pv_ctrl, r = True,  s = True, v = True)


		#organize
		for c in ik_system:
			cmds.select(c)
			self.asign_color(color = color)

		#put the ik in the return list
		ik_system.append(ik_handle)

		#put PV under Ik Offset Grp
		cmds.parent(pv_grp[0],IK_grp[0])

		return ik_system

#----------------------------------------------------------------------------------------------------------------

	def joints_middle(self, start = '', end = '', axis = 'X', amount = 4):

		if start == '':
			start = cmds.ls(sl =True)[0]
		if end == '':
			end = cmds.ls(sl =True)[-1]


		#create list for new joints
		twist_joints = []
		
		#create joints in between
		for i in range(amount):
			#duplicate joint and delete children
			twist_joint = cmds.duplicate(start, n = '{}_Twist_{}{}'.format(start,i, nc['joint']), rc = True)[0]
			cmds.delete(cmds.listRelatives(twist_joint, c = True))

			twist_joints.append(twist_joint)

			#if the new joint is not the first parent it to the last one
			if cmds.objExists('{}_Twist_{}{}'.format(start,i - 1, nc['joint'])):
				cmds.parent(twist_joint,'{}_Twist_{}{}'.format(start,i - 1, nc['joint']))
			
			else:
				cmds.parent(twist_joint, start)

	   #Position joints in correct the spot... 
		for jnt in twist_joints:
			cmds.setAttr('{}.translate{}'.format(jnt, axis), cmds.getAttr('{}.translate{}'.format(end, axis))/ (amount -1 ))

		cmds.setAttr('{}.translate{}'.format(twist_joints[0], axis), 0)

		return twist_joints

#----------------------------------------------------------------------------------------------------------------

	def twist(self, start = '', end = '', axis = 'X', amount = 4, mode = 'down'):

		if start == '':
			start = cmds.ls(sl =True)[0]
		if end == '':
			end = cmds.ls(sl =True)[-1]

		twist_joints = self.joints_middle(start = start, end = end, axis = axis, amount = amount)
		
		#parent to upnode in hierarchy if possible
		try:cmds.parent(twist_joints[0], cmds.listRelatives(start, p = True))
		except:cmds.parent(twist_joints[0],w = True)

		#Ik Handle and pole vector set up
		ik_handle = cmds.ikHandle (n='{}_Twist{}'.format(start, nc['ik_rp']), sj=twist_joints[0], ee= twist_joints[1], sol = 'ikRPsolver')
		
		cmds.parent(ik_handle[0], start)
		
		cmds.setAttr('{}.poleVectorX'.format(ik_handle[0]), 0)
		cmds.setAttr('{}.poleVectorY'.format(ik_handle[0]), 0)
		cmds.setAttr('{}.poleVectorZ'.format(ik_handle[0]), 0)
		cmds.setAttr('{}.snapEnable'.format(ik_handle[0]), 0)
			   
		#Locator Setup
		aim_loc = cmds.spaceLocator(n ='{}_Twist{}'.format(start, nc ['locator']))
		
		#put the locator in correct pos
		if mode == 'up':

			cmds.xform(aim_loc, m = cmds.xform(twist_joints[0], q=1, m=1))
			cmds.parent(aim_loc,twist_joints[0])
			cmds.xform(aim_loc, t = (0,0,0), ra =(0,0,0))
			cmds.rotate( 0,0,0,aim_loc)
			cmds.orientConstraint(start, aim_loc, mo = True)

		elif mode == 'down':
			cmds.delete(cmds.parentConstraint(twist_joints[-1], aim_loc, mo =0))
			cmds.parent(aim_loc, twist_joints[0])
			cmds.xform(aim_loc, ra =(0,0,0))
			cmds.orientConstraint(end, aim_loc, mo = True)

		#connect twist to joints
		mult_node = cmds.shadingNode('multiplyDivide', asUtility=1, n  = '{}_Twist_Divide'.format(start))
		cmds.setAttr(str(mult_node)+'.operation', 2)
		cmds.setAttr(str(mult_node)+'.input2X', amount - 1 )
		cmds.connectAttr('{}.rotate{}'.format(aim_loc[0],axis), '{}.input1.input1X'.format(mult_node))

		#fix tranlation issue
		cmds.pointConstraint(start, twist_joints[0], mo = True)

		#connect joints to rotate
		return_joint = twist_joints
		twist_joints.remove(twist_joints[0])
		
		for twist_joint in twist_joints:
			cmds.connectAttr('{}.output.outputX'.format(mult_node), '{}.rotate{}'.format(twist_joint, axis))
		
		return return_joint

#----------------------------------------------------------------------------------------------------------------

	def simple_fk_ik(self, start = '', mid = '', end = '', size = 1, color = 'lightBlue', mode = setup['ik_fk_method']):
		
		if start == '':
			start = cmds.ls(sl=True)[0]
			mid = cmds.ls(sl=True)[1]
			end = cmds.ls(sl=True)[2]

		print ('joints are: {} {} {}'.format(start,mid,end))

		#put name conventions to main chain
		if nc['joint'] in str(start):
			pass
		else: 
			start = cmds.rename(start, '{}{}'.format(start,nc['joint']))

		if nc['joint'] in str(mid):
			pass
		else: 
			mid = cmds.rename(mid, '{}{}'.format(mid,nc['joint']))

		if nc['joint'] in str(end):
			pass
		else: 
			end = cmds.rename(end, '{}{}'.format(end,nc['joint']))

		#mange errors if names exists
		if cmds.objExists(start):
			#cmds.error('we already have a system with theese names sorry')
			''
		main_joints = [start,mid,end]

		#duplicate chains to have the 3 of them
		cmds.select(start)
		ik_joints = self.duplicate_change_names( input = '', hi = True, search=nc['joint'], replace =nc['ik'])
		cmds.select(start)
		fk_joints = self.duplicate_change_names( input = start, hi = True, search=nc['joint'], replace =nc['fk'])

		
		#create FK System
		cmds.select(cl =True)

		for jnt in fk_joints:
			cmds.select(jnt, add = True)

		fk_system = self.fk_chain(size = size, color = color, curve_type = 'bounding_cube')
		print ('FK = {}'.format(fk_system))

		#Create IK System

		print ('creating ik Chain for : {}'.format(start)),
		ik_system = self.simple_ik_chain(start = ik_joints[0], end = ik_joints[-1], size = size, color = color, pv = True)
		print ('IK = {}'.format(ik_system))

		print '__________'


		#add swtich attr in all controllers
		ik_fk_controllers = fk_system + ik_system
		for ctrl in ik_fk_controllers :
			cmds.select(ctrl)
			if cmds.objectType(ctrl) ==  'transform':
				switch_attr = self.shape_with_attr(input = '', obj_name = '{}_Switch'.format(start), attr_name = 'Switch_IK_FK')


		#create rotate order and line
		for main in main_joints:
			self.connect_rotate_order(input = main, object = '{}_Switch_Loc'.format(start))

		self.line_attr(input = '{}_Switch_Loc'.format(start), name = 'IK_FK', lines = 10)

		#reorder attrs
		cmds.deleteAttr('{}_Switch_Loc'.format(start), at = 'Switch_IK_FK')
		mel.eval("Undo;")


		#create switch ik fk
		print switch_attr

		for num, jnt in enumerate(main_joints):
			if mode == 'blend':
				self.switch_blend_colors(this = fk_joints[num], that = ik_joints[num], main = jnt, attr = switch_attr)
			else: 
				self.switch_constraints(this = fk_joints[num], that = ik_joints[num], main = jnt, attr = switch_attr)


		return main_joints, ik_joints, fk_joints, fk_system, ik_system