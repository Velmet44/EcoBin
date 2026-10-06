# Reliability evidence and change control

## Evidence hierarchy

Use the evidence appropriate to the failure mechanism and claim:

- Physics/engineering calculation with controlled inputs and sensitivity.
- Validated simulation correlated to known solutions or tests.
- Supplier qualification/data with exact part, revision and operating envelope.
- Material/process characterization and coupons.
- Subassembly and system qualification.
- Reliability demonstration or accelerated testing with a justified model.
- Production acceptance/screening.
- Field exposure, failures, repairs and censored units.

These sources answer different questions. Do not treat a supplier MTBF value, a single prototype, HALT survival, or a passed acceptance test as proof of field reliability.

## Duty and life

Archive the load/duty/environment spectrum and configuration that feeds every life model. Include transient events, starts/stops, reversals, shock, thermal cycles, dwell, contamination, maintenance and storage/transport where relevant.

Report:

- Failure criterion and mechanism.
- Required life/reliability/confidence.
- Model/source/allowables and validity range.
- Scatter, factors, uncertainty and sensitivity.
- Calculated result and margin.
- Test population, exposure, failures/censoring and statistical method.
- Correlation and limitations.

## Change invalidation

Every released analysis should declare input IDs/hashes and invalidation triggers. On change:

1. Identify affected configurations and serial/effectivity range.
2. Mark dependent evidence pending review.
3. Recalculate/retest or document why the evidence remains applicable.
4. Re-rate FMEA/hazards and check introduced failure modes.
5. Update user/service/inspection information.
6. Obtain approvals before restoring release status.

Use a dependency graph or where-used report when practical. Silent reuse of an old analysis after material, supplier, geometry, process, duty or software change is not acceptable.

## Production learning

Normalize field failures by exposure and configuration. Preserve no-fault-found and censored outcomes. Link nonconformance/corrective-action IDs to the failure mode and confirm whether controls detected the issue at the predicted stage.

Reopen analyses when evidence contradicts assumptions; do not merely append a lesson-learned note.
