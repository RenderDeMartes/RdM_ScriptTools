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

NEEDS A UPDATE :)

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

JSON_FILE = (PATH+'/name_conventions.json')
with open(JSON_FILE) as json_file:
	nc = json.load(json_file)
SETUP_FILE = (PATH+'/rig_setup.json')
with open(SETUP_FILE) as setup_file:
	setup = json.load(setup_file)

#----------------------------------------------------------------------------------------------------------------
#create base class for selection objects

class Kinematics_class(tools.Tools_class):
	
	def fk_chain(self, size = 1, color = setup['main_color'], curve_type = setup['fk_ctrl'], scale = True, twist_axis = setup['twist_axis']) :
		'''
		create a FK Chain with selected joints, settings can be change in the setup json file
		'''

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
				fk_controller = self.bounding_cube(input = bone, size = size, name =  '{}{}'.format(bone,nc['ctrl']), axis = twist_axis)
			else:
				fk_controller = self.curve(type = curve_type, custom_name = True, name = '{}{}'.format(bone,nc['ctrl']), size = size)

			if nc['joint'] in str(fk_controller):
				fk_controller = cmds.rename(fk_controller, fk_controller.replace(nc['joint'],''))


			cmds.delete(cmds.parentConstraint(bone, fk_controller)) #put the controller in position

			#create Root Grp
			fk_auto_grp = self.root_grp(replace_nc = False)

			#add connections
			cmds.parentConstraint(fk_controller,bone) #parent Ctrl to Bone
			if scale == True:
				cmds.scaleConstraint(fk_controller,bone) #parent Ctrl to Bone

			#Organize a bit
			self.asign_color(fk_controller, color)
			self.hide_attr(fk_controller, s = 1 - scale, v = True)

			#try to parent it to create chain 
			if len(fk_controllers) > 0:cmds.parent(fk_auto_grp[0], fk_controllers[-1])
			else:pass 

			#Create Controller List
			fk_controllers.append(fk_controller)
		

		return fk_controllers

#----------------------------------------------------------------------------------------------------------------

	def pole_vector(self, bone_one = '', bone_two = '', bone_three = '',back_distance = 1):
		'''
		finds correct position of the pole vector for the ik and create a locator for it
		'''

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
		cmds.xform(loc , ws =1 , t= (finalV.x , finalV.y ,finalV.z*back_distance))
		
		cmds.xform ( loc , ws = 1 , rotation = ((rot.x/math.pi*180.0),
		(rot.y/math.pi*180.0),
		(rot.z/math.pi*180.0)))
		
		return loc

#----------------------------------------------------------------------------------------------------------------

	def streatchy_ik(self, ik = '', ik_ctrl= '', top_ctrl = '', pv_ctrl = '', attrs_location = '', name = '', axis = 'Y'):
		
		'''
		create a ik stretchy system for the simple ik chain (only 3 joints allowed)
		'''

		if ik == '':
			ik = cmds.ls(sl=True)
		if name == '':
			name = ik
	
		#get components in the ik
		base_joint = cmds.listConnections (ik)
		effector = base_joint[1]
		end_joint = cmds.listConnections (effector)

		#joints in chain
		ik_joints = cmds.listRelatives (base_joint, ad = True, typ = 'joint')
		ik_joints.append (base_joint[0])  

		#find position of the base and end joints to create the distance tool
		first_pos = cmds.xform(ik_joints[0], q=True, t = True, ws=True)
		end_pos= cmds.xform(ik_joints[-1], q=True, t = True, ws=True) 
		pv_pos= cmds.xform(pv_ctrl, q=True, t = True, ws=True) 

		start_loc = cmds.spaceLocator(n = str(ik_joints[0]) + '_Stretchy' + nc['locator'])
		cmds.xform(start_loc, t = first_pos)
		cmds.setAttr(str(start_loc[0])+'.visibility', 0)
		end_loc = cmds.spaceLocator(n = str(ik_joints[-1])+ '_Stretchy'+ nc['locator'])
		cmds.xform(end_loc, t = end_pos)
		cmds.setAttr(str(end_loc[0])+'.visibility', 0)
		pv_loc = cmds.spaceLocator(n = str(ik_joints[1])+ '_Stretchy'+ nc['locator'])
		cmds.xform(pv_loc, t = pv_pos)
		cmds.setAttr(str(pv_loc[0])+'.visibility', 0)

		cmds.parentConstraint(top_ctrl, start_loc)
		cmds.parentConstraint(ik_ctrl, end_loc)
		cmds.parentConstraint(pv_ctrl, pv_loc)
				
		#distances nodes
		#main distance
		distance = cmds.distanceDimension(sp=first_pos, ep=end_pos)
		distance = cmds.rename(distance, ik_joints[-1] + '_' + ik_joints[0]+ nc['distance']+'_Shape')
		cmds.rename(cmds.listRelatives(distance, p =True), ik_joints[-1] + '_' + ik_joints[0]+ nc['distance'])
		cmds.setAttr('{}.visibility'.format(distance), 0)
		#top PV distance
		top_distance = cmds.distanceDimension(sp=first_pos, ep=pv_pos)
		top_distance = cmds.rename(top_distance, ik_joints[1] + '_' + ik_joints[0]+ nc['distance']+'_Shape')
		cmds.rename(cmds.listRelatives(top_distance, p =True), ik_joints[1] + '_' + ik_joints[0]+ nc['distance'])
		cmds.setAttr('{}.visibility'.format(top_distance), 0)		
		#IK PV distance
		ik_distance = cmds.distanceDimension(sp=end_pos, ep=pv_pos)
		ik_distance = cmds.rename(ik_distance, ik_joints[-1] + '_' + ik_joints[1]+ nc['distance']+'_Shape')
		cmds.rename(cmds.listRelatives(ik_distance, p =True), ik_joints[-1] + '_' + ik_joints[1]+ nc['distance'])	
		cmds.setAttr('{}.visibility'.format(ik_distance), 0)
				
		# stretchy math
		joints_for_distance = cmds.listRelatives (base_joint, ad = True, typ = 'joint')

		total_distance = 0
		
		for joint in joints_for_distance:
			current_distance = cmds.getAttr (joint + str ('.translate'+ axis))   
			total_distance = total_distance + current_distance  
			
			
		if total_distance < 0:
			total_distance = total_distance * -1  
			
		# New Attributes
		
		#Attr mult Stretchy
		print (attrs_location)

		for line in reversed(range(11)):
			try:
				self.line_attr(input = attrs_location, name = 'IK', lines = line)
				break
			except:pass
		
		stretch_Attr = self.new_attr(input= attrs_location, name = 'Stretch_On', min = 0 , max = 1, default = int(setup['stretch_default']))
		
		#IK Stretchy Nodes and Connections from RdM2 
		contidion_node = cmds.shadingNode('condition', asUtility=True, n= end_joint[0]+nc['condition'])
		cmds.setAttr(str(contidion_node)+".operation", 2)
		cmds.setAttr(str(contidion_node)+'.secondTerm', total_distance)

		#Connect To Distance
		md0 = self.connect_md_node(in_x1 = str(distance)+'.distance', in_x2 = total_distance, out_x = str(contidion_node)+'.colorIfTrueR', mode = 'divide', name = '')		
		
		#connect to joints
		md1 = self.connect_md_node(in_x1 = str(contidion_node)+'.outColorR', in_x2 = cmds.getAttr(str(ik_joints[1])+'.scale{}'.format(axis)), out_x = str(ik_joints[1])+'.scale{}'.format(axis), mode = 'mult', name = '{}_NewScale'.format(ik_joints[1]))
		md2 = self.connect_md_node(in_x1 = str(contidion_node)+'.outColorR', in_x2 = cmds.getAttr(str(ik_joints[2])+'.scale{}'.format(axis)), out_x = str(ik_joints[2])+'.scale{}'.format(axis), mode = 'mult', name = '{}_NewScale'.format(ik_joints[2]))
		
		md3 = self.connect_md_node(in_x1 = str(distance)+'.distance', in_x2 = stretch_Attr, out_x = str(contidion_node)+'.firstTerm', mode = 'mult', name = '{}_TotalDistance'.format(name))
		print (md0,md1,md2, md3)

		#normalize stretch
		normalize_loc = cmds.spaceLocator(n = name + '_NormalScale' + nc['locator'])[0]
		normal_md = self.connect_md_node( in_x1 = str(distance)+'.distance', in_x2 = str(normalize_loc) + '.scaleX', out_x = md0 + '.input1X', mode = 'divide', name = '{}_Normalize'.format(distance), force = True)
		cmds.connectAttr(normal_md + '.outputX', md3 + '.input1X', f=True)

		#manual change the sacles mult
		lower_attr = self.new_attr(input= attrs_location, name = 'Lower_Lenght', min = 0 , max = 2, default = 1)
		upper_attr = self.new_attr(input= attrs_location, name = 'Upper_Lenght', min = 0 , max = 2, default = 1)
		cmds.connectAttr(lower_attr, md2 + '.input2X', f=True)
		cmds.connectAttr(upper_attr, md1 + '.input2X', f=True)
		 		
		#elbow/knee lock #a bit hard coded bit it is what it is
		lock_attr = self.new_attr(input= attrs_location, name = 'Pole_Vector_Lock', min = 0 , max = 1, default = 0)

		upper_lock_blend = cmds.shadingNode('blendColors', asUtility=True, n = '{}_Lock{}'.format(ik_joints[1], nc['blend']))
		cmds.connectAttr(lock_attr, '{}.blender'.format(upper_lock_blend))
		cmds.connectAttr('{}.output.outputR'.format(upper_lock_blend), str(ik_joints[2])+'.scale{}'.format(axis), f=True)
		cmds.connectAttr('{}.outputX'.format(md1),'{}.color2.color2R'.format(upper_lock_blend), f=True)

		lower_lock_blend = cmds.shadingNode('blendColors', asUtility=True, n = '{}_Lock{}'.format(ik_joints[2], nc['blend']))
		cmds.connectAttr(lock_attr, '{}.blender'.format(lower_lock_blend))
		cmds.connectAttr('{}.output.outputR'.format(lower_lock_blend), str(ik_joints[1])+'.scale{}'.format(axis) , f=True)
		cmds.connectAttr('{}.outputX'.format(md2),'{}.color2.color2R'.format(lower_lock_blend), f=True)

		#connect lock pole vectors distance to normalize too
		cmds.connectAttr(str(top_distance)+'.distance', normal_md + '.input1Y')
		cmds.connectAttr(str(ik_distance)+'.distance', normal_md + '.input1Z')
		
		self.connect_md_node(in_x1 = normal_md + '.outputY', in_x2 = cmds.getAttr(str(ik_joints[0])+'.translate'+ axis), out_x = lower_lock_blend+ '.color1.color1R', mode = 'divide', name = '{}_DownLock_PV'.format(name))
		self.connect_md_node(in_x1 = normal_md + '.outputZ', in_x2 = cmds.getAttr(str(ik_joints[1])+'.translate'+ axis), out_x = upper_lock_blend + '.color1.color1R', mode = 'divide', name = '{}_UpLock_PV'.format(name))
		
		#volume preservation
		volume_attr = self.new_attr(input= attrs_location, name = 'Volume', min = 0 , max = 1, default = float(setup['volume_preservation']))

		upper_volume_blend = cmds.shadingNode('blendColors', asUtility=True, n = '{}_Volume{}'.format(ik_joints[2], nc['blend']))
		lower_volume_blend = cmds.shadingNode('blendColors', asUtility=True, n = '{}_Volume{}'.format(ik_joints[1], nc['blend']))
		cmds.setAttr('{}.color2.color2R'.format(upper_volume_blend), 1) 
		cmds.setAttr('{}.color2.color2R'.format(lower_volume_blend), 1) 

		cmds.connectAttr(volume_attr, '{}.blender'.format(upper_volume_blend))
		cmds.connectAttr(volume_attr, '{}.blender'.format(lower_volume_blend))

		self.connect_md_node(in_x1 = 1, in_x2 = upper_lock_blend+ '.output.outputR',out_x = upper_volume_blend+ '.color1.color1R', mode = 'divide', name = '{}_DownLock_PV'.format(name))
		self.connect_md_node(in_x1 = 1, in_x2 = lower_lock_blend+ '.output.outputR', out_x = lower_volume_blend+ '.color1.color1R', mode = 'divide', name = '{}_DownLock_PV'.format(name))

		volume_axis = ['X','Y','Z']
		volume_axis.remove(axis)
		#str(ik_joints[2])+'.scale{}'.format(axis)
		for scale_axis in volume_axis:
			cmds.connectAttr('{}.output.outputR'.format(upper_volume_blend), str(ik_joints[2])+'.scale{}'.format(scale_axis))
			cmds.connectAttr('{}.output.outputR'.format(upper_volume_blend), str(ik_joints[1])+'.scale{}'.format(scale_axis))

		#organize
		ik_grp = cmds.group(top_distance, ik_distance, distance,start_loc, end_loc, pv_loc ,normalize_loc , n = '{}_Stretchy{}'.format(ik, nc['group']))
		cmds.setAttr('{}.visibility'.format(ik_grp), 0)

		return (ik_grp, normalize_loc, start_loc, end_loc, pv_loc, distance, top_distance, ik_distance)
		
	#----------------------------------------------------------------------------------------------------------------

	def simple_ik_chain(self, start = '', end = '', size = 1, color = setup['main_color'], ik_curve = setup['ik_ctrl'], pv_curve = setup['pv_ctrl'], pv = True, top_curve = setup['top_ik_ctrl']):
		'''
		create a ik chain for desire joints
		'''

		if start == '':
			start = cmds.ls(sl =True)[0]
		if end == '':
			end = cmds.ls(sl =True)[-1]

		ik_system = []

		#create Ik Chain
		ik_handle = cmds.ikHandle (n = '{}{}'.format(end.replace(nc['joint'], ''), nc['ik_rp']), sj=start, ee= end, sol = 'ikRPsolver')
		cmds.rename(ik_handle[1],'{}{}'.format(end, nc['effector']))
		ik_handle = ik_handle[0]

		#create ik Controller with offset grp and clean attr
		ctrl = self.curve(type = ik_curve, rename = False, custom_name = True, name = '{}{}'.format(end, nc ['ctrl']), size = size)
		ctrl = cmds.rename(ctrl, ctrl.replace(nc['joint'],''))

		ik_system.append(ctrl)
		self.match(ctrl, end)
		IK_grp = self.root_grp(replace_nc = True)
		self.hide_attr(ctrl, s = True, v = True)

		cmds.orientConstraint(ctrl, end ,mo =True)

		#parent ik to controller
		cmds.parentConstraint(ctrl, ik_handle, mo =True)
		cmds.group(ik_handle, n = ik_handle+ nc['group'])

		#create pole vector
		if (pv):

			#create pole vector in correct position
			pv_loc = self.pole_vector(bone_one = start, bone_two = cmds.listRelatives(end, p = True), bone_three = end)
			
			#create controller in position with offset grp
			pv_ctrl = self.curve(type = pv_curve, rename = False, custom_name = True, name = '{}{}{}'.format(end,nc ['pole_vector'], nc ['ctrl']), size = size/2)
			pv_ctrl = cmds.rename(pv_ctrl, pv_ctrl.replace(nc['joint'],''))

			ik_system.append(pv_ctrl)
			self.match(pv_ctrl, pv_loc)
			cmds.delete(pv_loc)
			cmds.poleVectorConstraint(pv_ctrl, ik_handle)
			pv_grp = self.root_grp(replace_nc = True)        

			#clean controller
			self.hide_attr(pv_ctrl, r = True,  s = True, v = True)

		#create top controler
		top_ctrl = self.curve(type = top_curve, rename = False, custom_name = True, name = '{}{}'.format(start.replace(nc['joint'], ''), nc ['ctrl']), size = size)
		self.match(top_ctrl, start)
		top_grp = self.root_grp(replace_nc = True)

		self.hide_attr(top_ctrl,r = True,  s = True, v = True)
		ik_system.append(top_ctrl)

		cmds.parentConstraint(top_ctrl, start)

		#organize and add color

		#create IK Grp
		cmds.select(cl=True)
		ik_main_grp = cmds.group(n = start + nc['ctrl'] + nc ['group'], em =True)
		cmds.parent(pv_grp[0],ik_main_grp)
		cmds.parent(IK_grp[0],ik_main_grp)
		cmds.parent(top_grp[0],ik_main_grp)

		for c in ik_system:
			cmds.select(c)
			self.asign_color(color = color)

		#put the ik in the return list
		ik_system.append(ik_handle)		

		return ik_system

	#----------------------------------------------------------------------------------------------------------------

	def joints_middle(self, start = '', end = '', axis = setup['twist_axis'], amount = 4):
		'''
		create joints in between a joint chain
		'''
		if start == '':
			start = cmds.ls(sl =True)[0]
		if end == '':
			end = cmds.ls(sl =True)[-1]

		#create list for new joints
		middle_joints = []
		
		#create joints in between
		for i in range(amount):
			#duplicate joint and delete children
			middle_joint = cmds.duplicate(start, n = '{}_Twist_{}{}'.format(start,i, nc['joint']), rc = True)[0]
			cmds.delete(cmds.listRelatives(middle_joint, c = True))

			middle_joints.append(middle_joint)

			#if the new joint is not the first parent it to the last one
			if cmds.objExists('{}_Twist_{}{}'.format(start,i - 1, nc['joint'])):
				cmds.parent(middle_joint,'{}_Twist_{}{}'.format(start,i - 1, nc['joint']))
			
			else:
				try:cmds.parent(middle_joint, w=True)
				except:pass

		#Position joints in correct the spot... 
		
		for jnt in middle_joints:
			if jnt != middle_joints[0]:	
				cmds.setAttr('{}.translate{}'.format(jnt, axis), cmds.getAttr('{}.translate{}'.format(end, axis))/ (amount -1 ))

		#cmds.setAttr('{}.translate{}'.format(middle_joints[0], axis), 0)

	
		return middle_joints

#----------------------------------------------------------------------------------------------------------------

	def twist(self, start = '', end = '', axis = setup['twist_axis'], amount = 4, mode = 'down'):
		'''
		OLD
		old way of creating twist for limbs, i use this one on RdM Tools v2, recommend to use the advance one
		'''

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
		return_joints = twist_joints
		twist_joints.remove(twist_joints[0])
		
		for twist_joint in twist_joints:
			cmds.connectAttr('{}.output.outputX'.format(mult_node), '{}.rotate{}'.format(twist_joint, axis))
		
		return return_joints

#----------------------------------------------------------------------------------------------------------------

	def twist_rotate_info(self, start = '', end = '', axis = setup['twist_axis'], driver = False):
		'''
		create a system to correctly read the twist information for the desire joint, 
		it can be used from top to buttom or buttom to top
		'''

		if start == '':
			start = cmds.ls(sl =True)[0]
		if end == '':
			end = cmds.ls(sl =True)[-1]

		cmds.select(cl=True)
		print ('Twist axis is: '+ axis)

		#try to remove nameconventions
		try:
			name = start.replace(nc['joint'], '')
			name = start.replace(nc['joint_bind'], '')

		except: name = start

		#twist setup
		twist_root = cmds.joint(n=name + '_NoTwist{}'.format(nc['joint']), p =(0,0,0))
		twist_tip = cmds.joint(n=name + '_NoTwist_Tip{}'.format(nc['joint']), p = (1,0,0))
		
		twist_grp = cmds.group(twist_root, n= name + '_NoTwist{}'.format(nc['group']))
		cmds.xform(twist_grp, rp = (0,0,0), sp = (0,0,0))

		#locator reader
		loc = cmds.spaceLocator(n= name + '_Twist{}'.format(nc['locator']))[0]
		cmds.parent(loc, twist_root)

		#position in chain
		cmds.delete(cmds.parentConstraint(start, twist_grp, mo=False))
		cmds.delete(cmds.parentConstraint(end, twist_tip, mo=False))

		if driver:
			cmds.parentConstraint(driver, twist_grp, mo=True)

		#create IK for the locator to follor orientation
		ik_data = cmds.ikHandle(sj=twist_root, ee=twist_tip, sol='ikRPsolver')

		ik = cmds.rename(ik_data[0], name + '_NoTwist_IkHndl')
		cmds.rename(ik_data[1], name + "_" + nc['effector'])

		cmds.setAttr('{}.poleVectorX'.format(ik), 0)
		cmds.setAttr('{}.poleVectorY'.format(ik), 0)
		cmds.setAttr('{}.poleVectorZ'.format(ik), 0)
		cmds.pointConstraint(end, ik, mo=False)

		cmds.orientConstraint(start, loc, mo=True)[0]
		
		#cmds.setAttr(twist_root + '.ro', 3)
		# Offset Grps.
		offset_grp = self.root_grp(twist_root, replace_nc=True)[0]
		print (offset_grp)

		cmds.parent(loc, offset_grp)

		cmds.makeIdentity(twist_root, a=True, t=True, r=True, s=True)
		cmds.parent(loc, twist_root)
		
		return {'ik': ik, 'twist_grp': twist_grp, 'locator': loc, 'joint': twist_root, 'offset': offset_grp}		

#----------------------------------------------------------------------------------------------------------------

	def advance_twist(self, start = '', end = '', axis = setup['twist_axis'], amount = 4, mode = 'up', driver = ''):
		'''
		create twist system for the chain, 
		this one can only be used by selecting from top to buttom joints but you can change the mode to up or down for desire effect
		'''

		if start == '':
			start = cmds.ls(sl =True)[0]
		if end == '':
			end = cmds.ls(sl =True)[-1]


		if mode == 'up':
			twist_reader = self.twist_rotate_info(start=start, end=end)
		elif mode == 'down':
			twist_reader = self.twist_rotate_info(start=end, end=start)

		twist_locator = twist_reader['locator']
		
		#Create twist grps
		#create jnts in the middle
		twist_joints = self.joints_middle(start = start, end = end, axis = axis, amount = amount)
		cmds.parentConstraint(start, twist_joints[0], mo=True)
		#connect twist locator to joints using ik spline twist attr
		crv = self.curve_between(start=start, end=end)
		ik_spline = self.create_ik_spline_twist(start=twist_joints[0], end=twist_joints[-1], curve=crv)

		cmds.connectAttr('{}.rotate{}'.format(twist_locator,axis),'{}.twist'.format(ik_spline['ikHandle'])) 
		
		print (twist_reader)
		twist_grp = cmds.group(twist_joints[0],crv, ik_spline['ikHandle'],twist_locator, twist_reader['ik'], twist_reader['twist_grp'] , n = '{}_{}_Twist{}'.format(start,end,nc['group']))
		return {'twist_grp':twist_grp, 'joints':twist_joints, 'curve':crv}

#----------------------------------------------------------------------------------------------------------------

	def simple_fk_ik(self, start = '', mid = '', end = '', size = 1, color = setup['main_color'], mode = setup['ik_fk_method'], twist_axis = setup['twist_axis']):
		'''
		create a ik fk chain with a switch for 3 joints
		'''

		return_groups = []

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

		fk_system = self.fk_chain(size = size, color = color, curve_type = 'bounding_cube', scale = False)
		print ('FK = {}'.format(fk_system))
		#add fk group to retunr groups
		return_groups.append(cmds.listRelatives(fk_system[0], p =True)[0])

		#Create IK System
		print ('creating ik Chain for : {}'.format(start)),
		ik_system = self.simple_ik_chain(start = ik_joints[0], end = ik_joints[-1], size = size, color = color, pv = True)
		print ('IK = {}'.format(ik_system))

		#add ik group to return groups
		return_groups.append(cmds.listRelatives(ik_system[0], p =True)[0])
		return_groups.append(cmds.listRelatives(ik_system[2], p =True)[0])
		return_groups.append(cmds.listRelatives(return_groups[1], p =True)[0])
		print (return_groups)
		print ('__________')

		#add swtich attr in all controllers
		ik_fk_controllers = fk_system + ik_system
		for ctrl in ik_fk_controllers :
			cmds.select(ctrl)
			if cmds.objectType(ctrl) ==  'transform':
				switch_attr = self.shape_with_attr(input = '', obj_name = '{}_Switch'.format(start), attr_name = 'Switch_IK_FK')


		#create switch ik fk
		print (switch_attr)

		for num, jnt in enumerate(main_joints):
			if mode == 'blend':
				self.switch_blend_colors(this = fk_joints[num], that = ik_joints[num], main = jnt, attr = switch_attr)
			else: 
				self.switch_constraints(this = fk_joints[num], that = ik_joints[num], main = jnt, attr = switch_attr)

		#connect visibility
		#FK Ctrl Grp					
		cmds.connectAttr(switch_attr, '{}.visibility'.format(return_groups[0]))

		#IK
		reverse_node = cmds.shadingNode('reverse', asUtility = True)
		cmds.connectAttr(switch_attr, '{}.input.inputX'.format(reverse_node))
		cmds.connectAttr('{}.output.outputX'.format(reverse_node), '{}.visibility'.format(return_groups[3]))

		#create rotate order and line
		for main in main_joints:
			self.connect_rotate_order(input = main, object = '{}_Switch_Loc'.format(start))
	
		#create ik stretchy system
		ik_stretch = self.streatchy_ik(ik = ik_system[3], ik_ctrl= ik_system[0], top_ctrl = ik_system[2], pv_ctrl = ik_system[1], attrs_location = '{}_Switch_Loc'.format(start), name = '', axis = twist_axis)
		ik_system.append(ik_stretch)

		print (main_joints, ik_joints, fk_joints, fk_system, ik_system, return_groups)
		return main_joints, ik_joints, fk_joints, fk_system, ik_system, return_groups

#----------------------------------------------------------------------------------------------------------------

	def twist_fk_ik(self, start = '', mid = '', end = '', size = 1, color = setup['main_color'], mode = setup['ik_fk_method'], twist_axis = setup['twist_axis']):
		
		'''
		create a ik fk chain with a switch for 3 joints, includes the twist information so is a full limb module
		'''

		#create basic ik fk system
		ik_fk = self.simple_fk_ik(start = start, mid = mid, end = end, size = size, color = color, mode = mode, twist_axis = twist_axis)

		#add the twists
		main_joints = ik_fk[0]

		upper_twist = self.advance_twist(main_joints[0],main_joints[1],mode = 'up', axis = twist_axis)
		lower_twist = self.advance_twist(main_joints[1],main_joints[2],mode = 'down', axis = twist_axis)
		print upper_twist

		#skin cluster a curva y parent constraint a No twist Offset Grp
		

		return ik_fk