import RdM_ScriptTools
from RdM_ScriptTools import main_rdm
reload(RdM_ScriptTools.main_rdm)

rdm = main_rdm.RdM()
#help(rdm)
#from see import see
#see(rdm)

#rdm.streatchy_ik(ik_ctrl = 'joint3_Ik_Ctrl',top_ctrl = 'joint1_Ik_Ctrl', attrs_location= 'joint3_Fk_Ctrl|joint1_Jnt_Switch_Loc')
#rdm.connect_md_node(in_x1='joint1_Jnt.translateX',in_x2=5,out_x = 'joint2_Jnt.visibility', mode = 'divide')

#ikfk = rdm.twist_fk_ik(start = '', mid = '', end = '', size = 5, color = 'red')

#rdm.twist_rotate_info()
#rdm.advance_twist(mode = 'down')

rdm.connect_with_line()

rdm.curve(type = 'root')