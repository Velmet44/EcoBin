# FMEA and criticality discipline

## Analysis quality

Start from functions, requirements, interfaces and process transformations. Avoid vague rows such as “part fails,” “operator error,” or “bad material.” State observable loss/degradation/unintended function, physical or process mechanism, initiating conditions and consequence chain.

Keep distinct:

- Failure mode: what function is lost, degraded or unintended.
- Effect: what happens locally, at the next level and to the end user/system.
- Cause/mechanism: why the mode occurs.
- Prevention control: reduces likelihood of cause/mechanism.
- Detection control: detects cause/mode before the effect escapes.
- Action: an owned change with verifiable closure.

## Scoring

Store the controlled scale/version and rationale for every rating. RPN is commonly the product of severity, occurrence and detection ratings; recalculate it deterministically when the method uses it. Do not compare RPNs created under different scales.

Classify every mode explicitly as safety-related or not. A safety-related mode must link to the hazard analysis and receive verified action closure at production maturity even when its scoring scale assigns severity below the project’s usual escalation threshold.

Do not:

- Lower severity because inspection was added.
- Lower occurrence without a prevention change or evidence.
- Lower detection without a detection-control change and effectiveness evidence.
- close an action merely because a document was updated.
- accept a safety-significant mode solely because its RPN is below a generic threshold.

Record both baseline and post-action ratings. Preserve action history and ineffective trials.

## DFMEA/PFMEA linkage

Translate design special/critical characteristics into process steps and controls. Translate PFMEA escape risks back to drawing/specification clarity, tolerance feasibility, access, datum strategy, mistake-proofing and design simplification.

Link:

- DFMEA cause → design prevention/verification.
- Product characteristic → PFMEA process step.
- PFMEA cause → process control plan/inspection.
- Escape → downstream effect/hazard/nonconformance.

## FMECA

Use FMECA only with a declared criticality method, data sources, unit population/mission time and dependency assumptions. A numeric criticality value without exposure and source rationale is not decision-grade.

Potentially applicable references include IEC 60812:2018 for FMEA/FMECA methods. Obtain the controlled standard and apply the organization’s approved scale; this file does not reproduce proprietary scoring tables.
