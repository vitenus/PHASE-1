from vitenus.scoring import *

def test_rea_boundaries():
    assert [rea_score(x) for x in [0,2,5,10,20,35,50,75,100,150]] == [1,2,3,4,5,6,7,8,9,10]

def test_index_extremes():
    assert technical_feasibility_index({k:10 for k in FT_WEIGHTS})==100
    assert implementation_complexity_index({k:1 for k in CI_WEIGHTS})==100
    assert risk_index({k:1 for k in GR_WEIGHTS})==100

def test_ipc():
    assert ipc({k:100 for k in WEIGHTS_IPC})==100
    assert ipc_band(39)=="low_priority"
    assert ipc_band(40)=="conditional_priority"
    assert ipc_band(60)=="high_priority"
    assert ipc_band(80)=="immediate_priority"

def test_ia_redistributes_missing_weights():
    value,scores=environmental_index({"virgin_material_avoided":20,"waste_avoided_recovered":30,"energy_avoided":None,"water_avoided":None,"emissions_avoided":15})
    assert 0<=value<=100 and "energy_avoided" not in scores
