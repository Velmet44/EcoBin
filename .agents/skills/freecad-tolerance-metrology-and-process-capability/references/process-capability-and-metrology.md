# Process capability and metrology

Capability is conditional on a stable process and a defined population. Record raw data and the approved statistical method; do not treat a high index as a substitute for control charts, engineering review, or representativeness.

For a bilateral characteristic with specification width `USL - LSL`, a common normal-process calculation is:

- `Cp = (USL - LSL) / (6 * sigma_within)`
- `Cpk = min((USL - mean), (mean - LSL)) / (3 * sigma_within)`
- `Pp/Ppk` use overall rather than within-process variation.

These equations are not universally valid. One-sided specifications, non-normal distributions, autocorrelation, tool wear, mixed cavities/build positions, and small samples require an approved method. Capability targets are project/supplier decisions, not universal numbers.

Measurement uncertainty affects acceptance. ISO 14253-1:2017 establishes GPS conformity/nonconformity decision rules that account for uncertainty near specification limits. ISO 14253-2:2011 gives guidance on estimating uncertainty. Record the project’s exact decision rule and guard band rather than claiming that this skill reproduces the standards.

ISO 22514-4:2016 covers process capability/performance measures; ISO/TR 22514-9:2023 addresses capability indices for GPS characteristics. Use controlled copies and the organization’s approved quality procedure.

Primary references:

- https://www.iso.org/standard/70137.html
- https://www.iso.org/standard/65289.html
- https://www.iso.org/standard/69643.html
- https://www.nist.gov/pml/nist-technical-note-1297
