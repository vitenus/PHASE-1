from scoring import ipc_band, roi_band
from validation import validate_opportunity

def recommend(ipc_value,roi_percent,payback_months,data_confidence,hurdle_rate_percent,regulatory_block=False,safety_block=False,technical_incompatibility=False,critical_risk=False,market_available=True,supplier_available=True):
    gov=validate_opportunity(data_confidence,regulatory_block,safety_block,technical_incompatibility,critical_risk,market_available,supplier_available)
    roi_ok=roi_percent>=hurdle_rate_percent
    payback_ok=payback_months!=float("inf")
    if not gov.recommendable: decision="blocked"
    elif data_confidence<60: decision="pilot_data_insufficient"
    elif not roi_ok: decision="economic_review"
    elif not payback_ok: decision="no_payback_within_model_horizon"
    elif ipc_value<40: decision="low_priority"
    elif ipc_value<60: decision="conditional_priority"
    elif ipc_value<80: decision="high_priority"
    else: decision="immediate_priority"
    return {"decision":decision,"ipc_band":ipc_band(ipc_value),"roi_band":roi_band(roi_percent),"roi_meets_hurdle_rate":roi_ok,"payback_is_finite":payback_ok,"recommendable_under_governance":gov.recommendable,"blockers":gov.blockers,"warnings":gov.warnings}
