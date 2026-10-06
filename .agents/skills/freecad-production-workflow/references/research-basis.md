# Research basis

Checked 2026-07-24. These links establish the workflow’s baseline; they do not reproduce proprietary standards.

## FreeCAD

- [FreeCAD 1.1.2 release announcement](https://blog.freecad.org/2026/07/23/freecad-1-1-2-released/) — current stable patch release and security/backport recommendation.
- [FreeCAD PartDesign Body](https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/en/PartDesign_Body.html) — single contiguous solid intent, origin elements, body tip, base feature, and attachment behavior.
- [FreeCAD expressions](https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/Expressions.html) — units, spreadsheet aliases, named constraints, and cyclic-dependency limitations.
- [FreeCAD new sketch guidance](https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/PartDesign_NewSketch.html) — sketches are generally safer reference sources than generated faces or edges.
- [FreeCAD Check Geometry](https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/Part_CheckGeometry.html) — B-rep validity and optional BOP checks; detected faults require manual model repair.
- [FreeCAD CAM Workbench](https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/CAM_Workbench.html) — job/tool/post flow, unit behavior, 2.5D limitations, and lack of clamp awareness.
- [FreeCAD CAM postprocessing](https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/CAM_Post.html) — controller dialect translation and postprocessor responsibilities.
- [FreeCAD TechDraw length dimensions](https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/TechDraw_LengthDimension.html) — drawing dimensions remain vulnerable to topology changes and should be applied after model stabilization.
- [FreeCAD Assembly Create Simulation](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Assembly_CreateSimulation.md) — prescribed joint-motion definitions, frame generation, and Animation Player controls.
- [FreeCAD Assembly Create Exploded View](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Assembly_CreateView.md) — native exploded view/move objects and TechDraw use.
- [FreeCAD FEM getting started](https://blog.freecad.org/2025/09/16/getting-started-with-fem/) — current CalculiX/Elmer roles and FreeCAD FEM preparation limits.

## Product definition standards

- [ASME Y14.5-2018 (R2024)](https://www.asme.org/codes-standards/find-codes-standards/y14-5-dimensioning-tolerancing/2018) — current ASME GD&T language and drawing/model interpretation baseline.
- [ASME Y14 standards catalog](https://www.asme.org/codes-standards/y14-standards) — drawing, digital product definition, revision, casting/forging/molding, and related standards.
- [ISO 8015:2011](https://www.iso.org/standard/55979.html) — fundamental GPS concepts, principles, and rules.
- [ISO 1101:2017](https://www.iso.org/standard/66777.html) — geometrical-tolerancing symbol language and interpretation.
- [ISO 22081:2021](https://www.iso.org/standard/72514.html) — general geometrical and size specifications; replaces withdrawn ISO 2768-2.
- [ISO 286-1:2010](https://www.iso.org/standard/45975.html) — linear size tolerance and fits system.
- [ISO 965-1:2026](https://www.iso.org/standard/87889.html) — current ISO metric thread tolerance principles.
- [ISO 21920-1:2021](https://www.iso.org/standard/72196.html) — current surface-texture indication standard; ISO 1302:2002 is withdrawn.
- [ISO 2768-1:1989](https://www.iso.org/standard/7748.html) and its [replacement project](https://www.iso.org/standard/85741.html) — check publication status before each release; a replacement was under publication in July 2026.
- [ISO/ASTM 52910:2018](https://www.iso.org/standard/67289.html) — general additive-manufacturing design requirements and recommendations.
- [ISO/ASTM 52902:2023](https://www.iso.org/standard/79683.html) — AM test artifacts for geometric capability assessment and calibration.
- [ISO/ASTM 52920:2023](https://www.iso.org/standard/76911.html) — industrial AM process/site qualification and quality-assurance principles.
- [ISO/ASTM 52901:2017](https://www.iso.org/standard/67288.html) — purchased AM part definition, feedstock, final property, inspection, and acceptance information.
- [ISO/ASTM 52908:2023](https://www.iso.org/standard/81779.html) — metal PBF post-processing, inspection, testing, and qualification.
- [ISO 14253-1:2017](https://www.iso.org/standard/70137.html) — conformity decisions that account for measurement uncertainty.
- [ISO 22514-4:2016](https://www.iso.org/standard/65289.html) — commonly used process capability and performance measures.

## Dynamics and model credibility

- [FreeCAD 1.1.2 Assembly simulation source](https://github.com/FreeCAD/FreeCAD/blob/1.1.2/src/Mod/Assembly/CommandCreateSimulation.py) — version-specific prescribed motion implementation and supported driver types.
- [MBDyn](https://www.mbdyn.org/) and [official FAQ](https://www.mbdyn.org/Documentation/FAQ.html) — nonlinear multibody/multiphysics, controls, and co-simulation capabilities and documentation boundaries.
- [Project Chrono](https://github.com/projectchrono/chrono) and [official API](https://api.projectchrono.org/) — open-source multibody, contact, FEA, robotics, and co-simulation capabilities.
- [ASME V&V 10-2019 (R2025)](https://www.asme.org/codes-standards/find-codes-standards/standard-for-verification-and-validation-in-computational-solid-mechanics) — verification, validation, and uncertainty-quantification framework for computational solid mechanics.

## Manufacturing evidence

- [Protolabs CNC tolerance guidance](https://www.protolabs.com/resources/design-tips/fine-tuning-tolerances-for-cnc-machined-parts/) — examples of supplier-specific capability, tolerance cost, warpage, and surface-finish effects.
- [Protolabs complex CNC features](https://www.protolabs.com/resources/design-tips/mastering-complex-features-on-machined-parts/) — supplier-specific deep feature, tool access, thread, and internal-radius guidance.
- [Protolabs sheet-metal bend guidance](https://www.protolabs.com/resources/design-tips/the-basics-of-bend-radii-in-sheet-metal/) — application-specific K-factor, bend radius, relief, and feature-proximity considerations.
- [Protolabs molding draft guidance](https://www.protolabs.com/resources/design-tips/improving-part-moldability-with-draft/) — draft, texture, ejection, and supplier-analysis considerations.
- [Protolabs additive tolerance guidance](https://www.protolabs.com/resources/design-tips/3d-printing-tolerances/) — process-, orientation-, material-, and geometry-dependent accuracy.
- [Haas mill part setup](https://www.haascnc.com/service/online-operator-s-manuals/mill-operator-s-manual/mill---part-setup.html) — workholding, tool offsets, work offsets, and machine-specific safety cautions.

Treat all vendor figures as examples for that vendor and offering, not universal limits. Obtain the selected supplier’s current capability statement.
