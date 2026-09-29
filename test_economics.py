import math
from economics import *

def test_business_case():
    gross=annual_gross_benefit(100,20,10,5,15)
    assert gross==150 and net_annual_benefit(gross,50)==100

def test_payback():
    assert simple_payback_months(1200,1200)==12
    assert math.isinf(simple_payback_months(1200,0))

def test_roi():
    assert project_roi_percent(150,20,100)==30
    assert round(vitenus_service_roi_percent(200,100,50),6)==round(33.33333333333333,6)

def test_projected_payback():
    assert projected_payback_periods([0,50,100],[0,0,0],[100,0,0])==2.5

def test_realized_roi():
    assert realized_roi_percent(200,20,100)==80
    assert cumulative_roi_percent(200,100)==100
    assert variance_percent(120,100)==20
