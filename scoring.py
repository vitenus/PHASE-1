"""Deterministic scoring engine for VITENUS methodology V0.1.

Design rule:
- Raw measurements stay in physical/economic units.
- Primary expert ratings are 1..10.
- Final indices are 0..100.
- Thresholds in this module are pilot governance assumptions, not ISO thresholds.
"""

from typing import Optional

WEIGHTS_IPC = {"IE": .30, "FT": .20, "IA": .20, "CI": .10, "TN": .10, "GR": .10}
FT_WEIGHTS = {
    "process_compatibility": .25, "technology_maturity": .20,
    "equipment_availability": .15, "modification_complexity": .15,
    "third_party_dependency": .10, "pilot_validation_need": .15,
}
CI_WEIGHTS = {k: 1/7 for k in ["departments","process_changes","suppliers","partners","capex_complexity","production_downtime","organizational_change"]}
GR_WEIGHTS = {k: 1/7 for k in ["technical","financial","operational","regulatory","market","supplier","quality"]}

ROI_BANDS = (
    (-float("inf"), 0.0, "negative"), (0.0, 10.0, "low_positive"),
    (10.0, 20.0, "positive"), (20.0, 35.0, "high"),
    (35.0, float("inf"), "very_high"),
)
TN_THRESHOLDS = [(1,10),(2,9),(3,8),(4,7),(6,6),(9,5),(12,4),(18,3),(24,2),(float("inf"),1)]


def _check_1_10(value: float, name: str) -> None:
    if not 1 <= value <= 10:
        raise ValueError(f"{name} must be between 1 and 10.")


def weighted_score(scores: dict[str,float], weights: dict[str,float]) -> float:
    if set(scores) != set(weights):
        raise ValueError(f"Score/weight keys mismatch. missing={set(weights)-set(scores)}, extra={set(scores)-set(weights)}")
    if abs(sum(weights.values()) - 1.0) > 1e-9:
        raise ValueError("Weights must sum to 1.")
    for k,v in scores.items(): _check_1_10(v,k)
    return sum(scores[k]*weights[k] for k in weights)


def rea_score(rea_percent: float) -> int:
    # V0.1 pilot bands; not a universal financial standard.
    if rea_percent <= 0: return 1
    for upper, score in [(2,2),(5,3),(10,4),(20,5),(35,6),(50,7),(75,8),(100,9),(float("inf"),10)]:
        if rea_percent <= upper: return score
    return 10


def economic_index(rea_percent: float) -> float:
    return rea_score(rea_percent) * 10.0


def technical_feasibility_index(scores: dict[str,float]) -> float:
    return weighted_score(scores, FT_WEIGHTS) * 10.0


def impact_score_from_improvement(improvement_percent: float) -> int:
    # Normalization only. Raw physical impact remains mandatory for auditability.
    return rea_score(improvement_percent)


def environmental_index(improvements: dict[str,Optional[float]], weights: Optional[dict[str,float]]=None) -> tuple[float,dict[str,float]]:
    weights = weights or {
        "virgin_material_avoided": .30, "waste_avoided_recovered": .25,
        "energy_avoided": .15, "water_avoided": .10, "emissions_avoided": .20,
    }
    applicable = {k:v for k,v in improvements.items() if v is not None}
    if not applicable: raise ValueError("At least one quantified environmental category is required.")
    total = sum(weights[k] for k in applicable)
    redistributed = {k:weights[k]/total for k in applicable}
    scores = {k:impact_score_from_improvement(v) for k,v in applicable.items()}
    return weighted_score(scores, redistributed)*10.0, scores


def implementation_complexity_index(scores: dict[str,float]) -> float:
    # Input: 1=low complexity, 10=high complexity. Output is inverted to 0..100.
    return 10.0*(11.0-weighted_score(scores, CI_WEIGHTS))


def time_index(months: float) -> float:
    if months < 0: raise ValueError("Implementation time cannot be negative.")
    for upper,score in TN_THRESHOLDS:
        if months <= upper: return score*10.0
    return 10.0


def risk_index(scores: dict[str,float]) -> float:
    # Input: 1=minimal risk, 10=very high risk. Output is inverted to 0..100.
    return 10.0*(11.0-weighted_score(scores, GR_WEIGHTS))


def ipc(indices: dict[str,float], weights: Optional[dict[str,float]]=None) -> float:
    weights = weights or WEIGHTS_IPC
    if set(indices) != set(weights): raise ValueError("IPC requires IE, FT, IA, CI, TN and GR.")
    for k,v in indices.items():
        if not 0 <= v <= 100: raise ValueError(f"{k} must be between 0 and 100.")
    if abs(sum(weights.values())-1.0)>1e-9: raise ValueError("IPC weights must sum to 1.")
    return sum(indices[k]*weights[k] for k in weights)


def ipc_band(value: float) -> str:
    if 0 <= value <= 39: return "low_priority"
    if value <= 59: return "conditional_priority"
    if value <= 79: return "high_priority"
    if value <= 100: return "immediate_priority"
    raise ValueError("IPC must be between 0 and 100.")


def roi_band(roi_percent: float) -> str:
    for low,high,label in ROI_BANDS:
        if low <= roi_percent < high: return label
    return "very_high"


def data_confidence_score(quality_scores: dict[str,float], weights: dict[str,float]) -> float:
    """Governance score: quality 1..5 -> 0..100; not a statistical CI."""
    if not quality_scores: raise ValueError("At least one data-quality score is required.")
    scaled = {k:v*2 for k,v in quality_scores.items()}
    raw = weighted_score(scaled, weights)
    return (raw-1.0)/9.0*100.0
