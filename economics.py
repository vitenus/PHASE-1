"""Economic calculations for VITENUS V0.1."""

def annual_gross_benefit(savings_material=0.0,savings_waste=0.0,savings_energy=0.0,savings_water=0.0,revenue_additional=0.0,other_savings=0.0):
    return savings_material+savings_waste+savings_energy+savings_water+revenue_additional+other_savings

def net_annual_benefit(gross_benefit, opex_additional=0.0):
    return gross_benefit-opex_additional

def simple_annual_return(net_annual_benefit_value, investment):
    if investment<=0: raise ValueError("Investment must be > 0.")
    return net_annual_benefit_value/investment

def simple_payback_months(investment, net_annual_benefit_value):
    if investment<0: raise ValueError("Investment cannot be negative.")
    if net_annual_benefit_value<=0: return float("inf")
    return investment/(net_annual_benefit_value/12.0)

def project_roi_percent(total_benefits, additional_costs, investment):
    if investment<=0: raise ValueError("Investment must be > 0.")
    return (total_benefits-additional_costs-investment)/investment*100.0

def vitenus_service_roi_percent(incremental_benefits, implementation_costs, consulting_fees):
    denominator=implementation_costs+consulting_fees
    if denominator<=0: raise ValueError("Implementation costs + consulting fees must be > 0.")
    return (incremental_benefits-implementation_costs-consulting_fees)/denominator*100.0

def period_cashflows(benefits, opex, investments):
    b,o,i=list(benefits),list(opex),list(investments)
    if not(len(b)==len(o)==len(i)): raise ValueError("Benefits, OPEX and investments must have equal length.")
    return [bb-oo-ii for bb,oo,ii in zip(b,o,i)]

def projected_payback_periods(benefits, opex, investments):
    cf=period_cashflows(benefits,opex,investments); cumulative=0.0
    for idx,flow in enumerate(cf,start=1):
        previous=cumulative; cumulative+=flow
        if cumulative>=0 and flow>0: return (idx-1)+abs(previous)/flow
    return float("inf")

def realized_roi_percent(total_real_benefit,total_additional_opex,total_investment):
    if total_investment<=0: raise ValueError("Total investment must be > 0.")
    return (total_real_benefit-total_additional_opex-total_investment)/total_investment*100.0

def cumulative_roi_percent(cumulative_net_benefit,initial_investment):
    if initial_investment<=0: raise ValueError("Initial investment must be > 0.")
    return (cumulative_net_benefit-initial_investment)/initial_investment*100.0

def variance_percent(actual,forecast):
    if forecast==0: return 0.0 if actual==0 else float("inf")
    return (actual-forecast)/forecast*100.0
