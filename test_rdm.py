import RdM_ScriptTools
from RdM_ScriptTools import main_rdm
reload(RdM_ScriptTools.main_rdm)

rdm = main_rdm.RdM()


ikfk = rdm.simple_fk_ik(start = '', mid = '', end = '', size = 2, color = 'red')

