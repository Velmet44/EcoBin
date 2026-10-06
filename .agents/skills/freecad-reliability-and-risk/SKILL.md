---
name: freecad-reliability-and-risk
description: Perform and maintain production-grade mechanical reliability and risk engineering linked to FreeCAD parts, assemblies, manufacturing processes, and robots. Use whenever work involves functional decomposition, DFMEA, PFMEA, FMECA, hazard analysis, criticality, failure effects, prevention/detection controls, reliability or life targets, duty/load spectra, residual-risk approval, change impact, field failures, corrective action, design review, or a claim that a production CAD design is “safe” or “reliable.”
---

# FreeCAD Reliability and Risk

Runtime compatibility: Codex and Claude Code; Python 3.10+ for deterministic risk-register checks. Applicable standards and regulations must be obtained and interpreted by authorized humans.

Turn functions, interfaces, manufacturing steps, life-cycle states, and credible failures into traceable engineering actions and verified residual-risk decisions. A high-quality CAD model and a low RPN do not prove reliability or safety.

Use this skill alongside:

- `../freecad-production-workflow/SKILL.md` for overall release gates.
- `../freecad-assembly-engineering/SKILL.md` for structure, interfaces, configurations, motion, and acceptance.
- `../freecad-dfm-review/SKILL.md` and the manufacturing-planning skill for process feasibility and controls.
- The robotics mechanism and CAE skills for loads, life, fault states, and verification evidence.

Read:

- `references/fmea-and-criticality.md` for analysis structure and scoring discipline.
- `references/hazard-and-residual-risk.md` for lifecycle hazards and risk reduction.
- `references/reliability-evidence-and-change.md` for quantitative evidence, production feedback, and invalidation.

Copy `assets/reliability-risk-contract.json`, `assets/fmea-register.csv`, and `assets/hazard-register.csv` into the project. Run `scripts/reliability_risk_validate.py`. It checks structure, traceability, scoring arithmetic, closure, and approvals; it does not identify every failure, validate probabilities, establish compliance, or replace expert review. `DRAFT` and `CONDITIONAL` are explicitly non-production verdicts.

## Gate 1 — Freeze scope and authority

Record:

- Product/part number, revision, exact configurations/effectivity, maturity, intended use, reasonably foreseeable misuse, lifecycle stages, environment, duty and operating limits.
- Analysis boundaries, assumptions, exclusions, interfaces, upstream/downstream systems, manufacturing route, maintenance concept, disposal/recovery, and controlling requirements.
- Team roles spanning design, manufacturing, quality, service, controls/electrical/software, suppliers, safety, and operators as applicable.
- Scoring tables, risk-acceptance rules, escalation rules, action authority, review cadence, evidence repository, and approval roles.

Do not invent a universal severity, occurrence, detection, RPN, criticality, SIL, PL, or acceptance threshold. Use the organization’s controlled method and the applicable standard/regulatory system. Record its identifier, edition, and tailoring.

## Gate 2 — Build functional and process structure

Decompose the product and process before listing failures.

For each product function record:

- Function ID, owning item/interface/configuration, input/output, performance and allowable degradation.
- Operating states, duty/load/environment, dependent functions, safe state, and requirement/test links.

For each manufacturing/assembly/service process step record:

- Process-step ID, input condition, transformation, tooling/fixture/program, human interaction, output characteristic, special/critical characteristics, inspection/control, rework and escape path.

Trace functions and process steps to controlled FreeCAD definitions, occurrences, interfaces, drawings, BOM/router operations, software/configuration, and requirements. The analysis becomes stale when identity is only a prose description.

## Gate 3 — Perform DFMEA, PFMEA, and FMECA with clear boundaries

Use the appropriate analysis:

- **DFMEA** — ways a design function or interface can fail under intended use and foreseeable misuse.
- **PFMEA** — ways a manufacturing, assembly, inspection, transport, installation, or service step can create or pass a defect.
- **FMECA** — failure modes plus an explicitly defined criticality method when consequence/probability ranking is required.

For every failure mode capture:

- Unique ID, type, function/process step, item/interface, configuration and lifecycle state.
- Failure mode stated as loss/degradation/unintended function—not merely a cause.
- Local, next-higher-level and end effects, including safety, regulatory, production, service and customer effects.
- Physical/process causes and mechanisms with plausible initiating conditions.
- Existing prevention controls and existing detection controls, kept distinct.
- Severity, occurrence/probability and detection/diagnostic rating with source/rationale.
- Explicit `safety_related` classification. Safety-significant modes require hazard linkage and verified action closure regardless of their numerical severity or RPN.
- Related hazard, requirement, test, nonconformance, field issue and sibling/common-cause mode.
- Recommended action, owner, due date, status, evidence and post-action re-rating.

Do not use RPN alone to prioritize. High-severity consequences, regulatory/safety significance, weak single-point controls, uncertainty, common cause and poor detectability require explicit escalation even when multiplication produces a modest number.

## Gate 4 — Link hazards and failure analysis

Maintain a lifecycle hazard register covering design, production, transport, installation, commissioning, normal operation, setup, cleaning, recovery, maintenance, decommissioning and foreseeable misuse.

For each hazardous situation:

- Hazard, sequence of events, exposed persons/assets, operating/fault state, initiating causes and potential harm.
- Initial risk using the controlled method and source rationale.
- Risk-reduction measures in priority order: inherently safer design, safeguards/protective measures, then information for use.
- Implementing requirement/design/process/control IDs and verification evidence.
- Residual risk, new hazards introduced by the measure, remaining uncertainty, disclosure and authorized acceptance.

Cross-link failure modes that can initiate, defeat detection of, or worsen the hazard. A hazard analysis and FMEA are complementary; neither substitutes for the other.

For machinery, evaluate ISO 12100 principles and applicable type-B/type-C standards. For industrial robots/applications evaluate the current ISO 10218 scope; other robot categories require their own applicable framework. This skill does not determine conformity or certification.

## Gate 5 — Establish life and reliability evidence

Translate claims such as “ten-year life,” “one million cycles,” or “99.9% reliable” into:

- Mission profile and load/duty/environment spectra by configuration and population.
- Failure mechanisms, physics-of-failure models, material/process allowables, supplier data, uncertainty, degradation/wear limits, and maintenance assumptions.
- Structural/thermal/fatigue/wear/corrosion/lubrication/electrical/software analyses where relevant.
- Reliability allocation and dependent/common-cause assumptions.
- Test strategy: sample size, units, cycles/time, stresses, censoring, confidence, acceleration model, pass/fail criteria, teardown and anomaly disposition.
- Correlation among analysis, qualification, production acceptance, field data and updated predictions.

Do not claim a statistical confidence or failure rate from an unsupported sample. Do not mix demonstration testing, growth testing, screening, HALT, qualification and production acceptance as if they prove the same thing.

## Gate 6 — Control actions and verification

An action is closed only when the design/process/control changed, its controlled artifact is identified, verification passed, and the FMEA/hazard ratings were re-evaluated.

Action discipline:

- Assign one accountable owner and due date.
- Prefer eliminating the cause or reducing severity/exposure before adding inspection.
- Link geometry changes to exact FreeCAD object/feature/datum/revision; link process changes to router/work instruction/program/fixture/control-plan revision.
- Verify supplier and software/control actions against the released configuration.
- Keep containment separate from permanent corrective action.
- Record ineffective actions and reopened risks; never erase the audit trail.

Production-candidate high-severity, safety-linked, or acceptance-rule-triggering modes cannot remain open without a time-bounded, configuration-specific deviation approved by the proper authority.

## Gate 7 — Close residual risk

Before release, reconcile:

- Every function/process step has been analyzed or explicitly excluded with approval.
- Each critical/special characteristic appears in product definition, process control, inspection and acceptance.
- Every safety-significant failure mode links to a hazard or has a documented rationale.
- Each risk-reduction measure has a verified implementation and has not introduced an uncontrolled hazard.
- Required life evidence meets the declared mission profile and configuration.
- Open actions, deviations and residual risks have explicit effectivity, expiration, controls and authority.
- User/service information, maintenance, inspection, proof-test and replacement intervals match the accepted assumptions.

Residual risk is a human decision by a named authorized role. The analyst or script must not auto-approve it.

## Gate 8 — Invalidate on change and learn from production

Create change triggers for:

- Geometry, material, finish, heat treatment, supplier, standard part, tolerance/GD&T, interface, mass/inertia or load path.
- Firmware/control law, speed/acceleration, payload/tool, operating envelope, environment, duty cycle or life.
- Manufacturing route, machine, fixture, tooling, program, inspection, rework, packaging, installation or maintenance.
- Nonconformance, test anomaly, field failure, complaint, repair, supplier notice, obsolescence or regulation/standard update.

For each change, perform where-used and configuration/effectivity analysis. Mark affected calculations, tests, FMEA rows, hazards, controls, maintenance instructions, spares, and approvals invalid until reviewed. Preserve old released baselines.

Feed production/field evidence back into causes, occurrence estimates, detection effectiveness, life models and actions. Absence of reported failures is not automatically evidence of high reliability; account for exposure and reporting quality.

## Gate 9 — Release the risk package

Release:

- Scope, team, method/scales, functions/process structure and interface map.
- Baseline and post-action DFMEA/PFMEA/FMECA registers.
- Hazard analysis, risk-reduction trace, residual-risk register and information-for-use links.
- Life/reliability calculations and source spectra, qualification/acceptance reports, anomalies and correlation.
- Action/deviation register, design/process/control revisions, change-impact status and production/field feedback.
- Human approvals naming person, role, date, scope, configuration/effectivity and decision.

Verdicts:

- `PASS — risk package production candidate`: required actions and evidence close; residual risks have authorized, configuration-specific decisions.
- `DRAFT`: concept or prototype records are internally consistent but are not production candidates.
- `CONDITIONAL`: exact open items, controls, expiration/effectivity, assumptions and invalidated claims are stated.
- `FAIL`: unlinked functions/hazards, unsupported ratings/life claims, overdue/ineffective actions, unverified controls, unaccepted residual risk, or change invalidation remains.
- `RELEASED`: only after authorized approval and configuration release.

Never claim zero risk, guaranteed life, certification, regulatory conformity, or physical acceptance from the register or validator.
