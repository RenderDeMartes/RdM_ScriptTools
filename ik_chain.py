'''
content: create Ik chain based on selection and scale/color input

version: 1.0.0

date: 21/04/2020

how to: select desire IK joints and execute:
        simpleIK (scale = 1, color = 'red')

dependencies: 	maya.cmds
				json
				nameConventions.json
				hideAttr
				rootGrp
				replaceName

licence: https://tldrlegal.com/
author:  Esteban Rodriguez <info@renderdemartes.com>

'''

from maya import cmds
import json

import RdM_ScriptTools
from RdM_ScriptTools.rootGrp import rootGrp
reload(RdM_ScriptTools.rootGrp)
from RdM_ScriptTools.replaceName import replaceName
reload(RdM_ScriptTools.replaceName)
from RdM_ScriptTools.curveColor import curveColor
reload(RdM_ScriptTools.curveColor)
from RdM_ScriptTools.hideAttr import hideAttr
reload(RdM_ScriptTools.hideAttr)

#Read name conventions as nc['']
PATH = cmds.internalVar(usd = True) + 'RdM_ScriptTools'
JSON_FILE = open(PATH+'/NameConventions.json', 'r')
nc = json.load(JSON_FILE)
JSON_FILE.close()

#Define func
def simpleIk (size = 1, color = 'white'):
    
	joints_sel = cmds.ls(sl = True)
	
	#variables to have outputs after the loops
	ik_controllers = []
	
	#Create Ik system	
	Ik_handle = cmds.ikHandle (n='{}_IKrp'.format(joints_sel[-1]), sj = joints_sel[0], ee= joints_sel[-1], sol = 'ikRPsolver')
    
    #Pole Vector
    
    
    
    