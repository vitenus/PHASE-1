# VITENUS Methodology V0.1 — Scientific rationale

## 1. What is grounded in standards

**ISO 14051:2011** frames Material Flow Cost Accounting around tracing and quantifying material flows/stocks in physical units and evaluating associated costs. Therefore VITENUS stores physical observations separately from monetary benefits and requires units, periods and provenance.

**ISO 14053:2021** provides guidance for phased MFCA implementation. VITENUS therefore treats V0.1 as staged and pilot-oriented.

**ISO 14031:2021** provides guidance for environmental performance evaluation but does not establish universal performance levels. Therefore IA thresholds are explicitly internal normalization hypotheses, not ISO thresholds.

**ISO 50015:2014** provides principles and guidelines for measurement and verification of energy performance. Energy savings should therefore be linked to baseline, measurement period, unit and source.

**ISO 59020:2024** provides a framework for measuring and assessing circularity in a defined economic system, including system boundaries, indicator selection and reproducible processing. VITENUS follows this discipline.

**ISO 59010:2024** addresses transition of value-creation models and value networks from linear to circular configurations. It supports the conceptual treatment of circular value-network opportunities.

## 2. V0.1 hypotheses — not universal constants

- IPC weights 30/20/20/10/10/10;
- REA-to-IE bands;
- environmental improvement-to-IA bands;
- implementation-time thresholds;
- complexity and risk subweights;
- ROI bands;
- Payback screening rules;
- Data Confidence thresholds.

These must be validated empirically. The software stores methodology version so recalibrated results remain reproducible.

## 3. Why a multi-criteria IPC

A circular opportunity can have high financial return but low technical feasibility, high implementation complexity, high risk or weak measured environmental effect. The IPC keeps those dimensions visible. It is a governance model, not a physical law. Therefore raw measurements and all six component indices remain visible and sensitivity analysis is mandatory before methodological changes.

## 4. ROI threshold logic

No universal ROI cutoff is scientifically valid for every industrial project. Required return depends on capital cost, project duration, uncertainty, alternatives and risk. V0.1 therefore separates:

- **calculated ROI**;
- **project hurdle rate** supplied by finance;
- **pilot screening bands**.

Default bands: <0 negative; 0–<10 low positive; 10–<20 positive; 20–<35 high; ≥35 very high. These labels are only screening labels. The decision engine also checks the hurdle rate and governance blockers.

## 5. Environmental data

No single GHG emission factor is hard-coded. Factors vary with geography, year, technology and accounting boundary. Production should use a versioned factor registry containing source, geography, year, unit, scope and factor value.

## 6. Future statistical validation

After a meaningful pilot sample, evaluate inter-rater reliability for expert ratings, sensitivity of IPC to weights, forecast-vs-realized benefit calibration, Payback/ROI calibration, missing-data patterns and uncertainty of measured variables. Sector-specific thresholds should only be introduced after evidence supports them.
