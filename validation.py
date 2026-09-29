from dataclasses import dataclass

@dataclass
class GovernanceResult:
    recommendable: bool
    blockers: list[str]
    warnings: list[str]

def validate_opportunity(data_confidence, regulatory_block=False, safety_block=False, technical_incompatibility=False, critical_risk=False, market_available=True, supplier_available=True):
    blockers=[]; warnings=[]
    if regulatory_block: blockers.append("regulatory_constraint")
    if safety_block: blockers.append("safety_constraint")
    if technical_incompatibility: blockers.append("technical_incompatibility")
    if critical_risk: blockers.append("critical_risk")
    if not market_available: blockers.append("no_market")
    if not supplier_available: blockers.append("no_supplier")
    if data_confidence<60: warnings.append("low_data_confidence")
    return GovernanceResult(len(blockers)==0,blockers,warnings)
