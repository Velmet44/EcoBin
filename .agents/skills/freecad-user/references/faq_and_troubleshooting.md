# FreeCAD FAQ & Troubleshooting Guide

Synthesized from the official FreeCAD documentation (`Frequently_asked_questions.md`) and community workarounds (`Workarounds.md`).

---

## Frequently Asked Questions

### 1. General & Navigation
- **How is FreeCAD licensed?** FreeCAD is completely open source under LGPL-2.1+, meaning it is free for personal, educational, and commercial use without any subscription or license fees.
- **Can I change the 3D mouse navigation to match SolidWorks / Inventor / Blender?** Yes. Go to **Edit > Preferences > Display > Navigation > 3D Navigation** and select your preferred mode.
- **Where are configuration files and settings stored?** 
  - Windows: `%APPDATA%\FreeCAD\`
  - Linux: `~/.config/FreeCAD/` and `~/.local/share/FreeCAD/`
  - macOS: `~/Library/Preferences/FreeCAD/` and `~/Library/Application Support/FreeCAD/`

---

### 2. Modeling & PartDesign
- **Why does FreeCAD complain about 'multiple solids' in PartDesign?** A `PartDesign::Body` represents a single contiguous solid. If a cut or pocket cuts completely through a feature such that it divides the piece into two disconnected parts, FreeCAD flags an error. To create multi-part assemblies, use multiple Bodies within `App::Part` or the **Assembly Workbench**.
- **Why did my sketch break after editing an earlier feature?** This is the **Topological Naming Problem (TNP)**. FreeCAD's underlying geometry engine renumbers faces when upstream geometry changes. Always map sketches to Datum Planes or standard planes (`XY`, `XZ`, `YZ`), not directly to model faces.
- **How do I rollback to an earlier feature in the history?** Right-click any feature in the Tree view and select **Set tip**. The model will temporarily roll back to that exact state.

---

### 3. Performance & Large Models
- **FreeCAD feels sluggish with complex sketches:**
  - Avoid putting hundreds of elements in one sketch. Break complex outlines into multiple simpler additive and subtractive sketches.
  - Disable solver auto-recompute while adding many constraints, then re-enable.
- **Slow 3D viewport rendering on complex parts:**
  - Go to **Edit > Preferences > Display > 3D View > Rendering** and adjust the deflection setting from fine to medium (e.g. `0.05` instead of `0.01`).

---

## Known CAD Workarounds & Solutions

| Problem | Symptoms | Canonical Workaround |
| :--- | :--- | :--- |
| **Coplanar Boolean Failures** | Booleans (Cut or Fuse) fail with 'Null shape' or non-manifold error when faces are perfectly flush. | Add a tiny offset (e.g. `0.01 mm` or `0.1 mm`) to cutting cylinders or tool bodies so faces overlap clearly rather than aligning exactly coplanar. |
| **Fillet / Chamfer Failure** | Fillet tool refuses to build a radius at sharp complex corner junctions. | Apply fillets in order: largest radii first, followed by smaller radii. For complex junctions, use the **Curves Workbench** or sketch a custom subtraction profile. |
| **Exporting Smooth Circles for 3D Printing** | Sliced STL models show faceted polygon sides instead of smooth circles. | Go to **Edit > Preferences > Import-Export > Mesh Formats** and set **Maximum deviation** to `0.01 mm`. |
| **Imported STEP Has No Parametric History** | Imported STEP shows as a static `Part::Feature`. | Create a `PartDesign::Body` and drag the STEP into it to make it a **BaseFeature**. You can now add sketches and pockets on top of it. |
| **Sketch Solver Reports Over-Constrained (Orange/Red)** | Conflicting or redundant dimensional constraints preventing recomputation. | Click on the red constraint indicator in the Tasks panel to highlight and delete the redundant constraint. |
