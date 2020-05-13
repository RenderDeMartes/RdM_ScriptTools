'''
version: 1.0.0
date: 21/04/2020

#----------------
content: 

#----------------
how to: 


#----------------
dependencies:   

maya.cmds
pymel
				
#----------------
licence: https://tldrlegal.com/
author:  Esteban Rodriguez <info@renderdemartes.com>

'''

import json
from maya import cmds

import RdM_ScriptTools
from RdM_ScriptTools import tools
reload(RdM_ScriptTools.tools)
tool = tools.Tools_class()


#Read name conventions as nc['']
PATH = cmds.internalVar(usd = True) + 'RdM_ScriptTools'
JSON_FILE = (PATH+'/NameConventions.json')
with open(JSON_FILE) as json_file:
    nc = json.load(json_file)

#Read curves info
PATH = cmds.internalVar(usd = True) + 'RdM_ScriptTools'
JSON_FILE2 = (PATH+'/curves.json')
with open(JSON_FILE2) as json_file2:
    curve_data = json.load(json_file2)

class Curve_class:
    
    def __init__(name = '', curve_type = ''):
        ''
