'''
version: 1.0.0
date: 21/04/2020

#----------------
content: 

fk_chain(input = '', size = 1, color = 'white')

#----------------
how to: 
    
import RdM_ScriptTools
from RdM_ScriptTools import kinematics
reload(RdM_ScriptTools.kinematics)

kin = kinematics_class()
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

import maya.mel
from maya import cmds
import pymel.core as pm
from maya import OpenMaya

import json

import RdM_ScriptTools
from RdM_ScriptTools import tools
reload(RdM_ScriptTools.tools)

#----------------------------------------------------------------------------------------------------------------

#Read name conventions as nc['']
PATH = cmds.internalVar(usd = True) + 'RdM_ScriptTools'
JSON_FILE = (PATH+'/NameConventions.json')
with open(JSON_FILE) as json_file:
    nc = json.load(json_file)

#----------------------------------------------------------------------------------------------------------------
#create base class for selection objects

class Kinematics_class(tools.Tools_class):
    
    def fk_chain(self, input = '', size = 1, color = 'white') :

        #Check input
        if input != '':
            self.input = [input]
            
        else:   
            self.input = input  
        
        self.check_input('fk_chain')    
    

        fk_controllers = []

        for bone in self.input :
            
            #Create controller and groups to zero it
            fk_controller = cmds.circle( n = '{}{}'.format(bone,nc['ctrl']) , nr = (1,0,0), r = size)[0]
            
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
        
        loc = cmds.spaceLocator(n = '{}{}'.format(bone_two, nc['locator']))[0]
        cmds.xform(loc , ws =1 , t= (finalV.x , finalV.y ,finalV.z))
        
        cmds.xform ( loc , ws = 1 , rotation = ((rot.x/math.pi*180.0),
        (rot.y/math.pi*180.0),
        (rot.z/math.pi*180.0)))
        
        return loc

#----------------------------------------------------------------------------------------------------------------

    def ik_chain(self):
        ''
        
        

#kin = Kinematics_class()
