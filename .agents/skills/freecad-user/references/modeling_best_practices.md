# FreeCAD Modeling Best Practices & TNP Mitigation

The most common point of friction in FreeCAD is the **Topological Naming Problem (TNP)**. Following structured CAD discipline ensures your models remain resilient, easy to modify, and free from breakages when upstream parameters change.

---

## The Topological Naming Problem Explained

### What Happens?
When you create a shape, OpenCASCADE numbers elements: `Edge1`, `Edge2`, `Face1`, `Face2`, etc.
If you map a new sketch directly onto `Face6`, and later increase a hole count or fillet an earlier edge, `Face6` might become `Face8` or disappear entirely. The downstream sketch loses its attachment or attaches to the wrong face, causing model breakages.

### The Mitigation Hierarchy (From Safest to Least Safe)

1. **Top Tier: Datum Planes and Standard Planes (Best Practice)**
   - Always map sketches to the principal planes (`XY_Plane`, `XZ_Plane`, `YZ_Plane`) or to explicit `PartDesign::Plane` (Datum Planes).
   - Position Datum Planes using dimensional offsets or parametric expressions from the Origin.
   - Example: To make a sketch 20mm above the top face, create a Datum Plane parallel to `XY_Plane` with `Z = 20mm`.

2. **Second Tier: SubShapeBinder**
   - When you need to reference an edge or vertex from another feature, create a `PartDesign SubShapeBinder`.
   - The binder acts as an explicit, traceable proxy rather than an implicit direct face attachment.

3. **Lowest Tier: Direct Face Mapping (Avoid on parametric models)**
   - Selecting a generated face of an extrusion and clicking "Create Sketch".
   - Only acceptable for quick throwaway prototypes or models that will never be parametrically adjusted.

---

## 10 Rules for Bulletproof Parametric Models

1. **One Solid per PartDesign Body**:
   A `PartDesign::Body` is strictly designed to contain a single, contiguous solid. Do not attempt to create two disjoint pieces in one Body. Use the `Assembly` workbench or multiple Bodies.

2. **Always Fully Constrain Sketches**:
   Never leave a sketch with open degrees of freedom (white lines). Ensure every vertex and curve is constrained until the solver reports **Fully constrained** (all green lines).

3. **Keep Sketches Simple**:
   Avoid sketching complex multi-feature outlines in a single sketch. Break geometry into simple additive shapes (Pads) and simple subtractive cuts (Pockets/Holes).

4. **Dress-Up Features at the End**:
   Chamfers, Fillets, Drafts, and Thickness should be applied as the very last operations before export. Modifying features upstream of a fillet is the leading cause of topological errors.

5. **Name and Label Objects Clearly**:
   Rename features descriptively (`BasePlatePad`, `MountingHolesPocket`, `RibReinforcement`) rather than leaving default names (`Pad001`, `Pocket003`).

6. **Use External Geometry Sparingly**:
   In Sketcher, use the "External Geometry" tool (`X`) only when necessary, and preferably reference datum axes, origin planes, or stable primitive features.

7. **Use Symmetric Extrusions When Appropriate**:
   Extruding `Symmetric to plane` around the Origin preserves symmetry and keeps the Origin centered, reducing the need for arbitrary offset planes.

8. **Leverage the Expression Engine**:
   Bind dimensions together using expressions:
   - `<<Pocket>>.Length`
   - `Spreadsheet.WallThickness * 2`
   - `sqrt(Body.Length ^ 2 + Body.Width ^ 2)`

9. **Check Geometry Validity**:
   Use `Part Workbench > Check Geometry` to inspect for self-intersecting wires, null faces, or non-manifold topology if a boolean or fillet fails.

10. **Save Incremental Versions**:
    Use FreeCAD's built-in backup saves (`.FCBak`) or Git VCS for critical design iterations.
