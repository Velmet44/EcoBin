# FreeCAD Migration Guide: Transitioning from Other CAD Suites

If you are coming from Autodesk Fusion 360, SolidWorks, OnShape, or Revit, this guide maps familiar concepts, shortcuts, and navigation patterns to FreeCAD.

---

## Terminology Mapping

| Commercial CAD Concept | FreeCAD Equivalent | Notes |
| :--- | :--- | :--- |
| **Component / Part** | `PartDesign::Body` or `App::Part` | A `Body` is a single continuous solid; `App::Part` is an assembly container. |
| **Extrude (Boss)** | `PartDesign Pad` / `Part Extrude` | Pad requires a closed sketch in a Body. |
| **Extrude (Cut)** | `PartDesign Pocket` / `Part Cut` | Pocket removes material from the active solid. |
| **Revolve** | `PartDesign Revolution` | Revolves around a sketch line, datum axis, or standard axis. |
| **Sweep / Loft** | `AdditivePipe` / `AdditiveLoft` | Sweep along a path or between multiple profiles. |
| **Mates / Joints** | `Assembly Joints` (v1.0) | Fixed, Revolute, Slider, Cylindrical, Ball joints. |
| **Drawing Sheet** | `TechDraw Page` | Uses SVG templates with dimensioning tools. |
| **Feature Tree / Timeline** | Tree View (Combo View) | FreeCAD uses a hierarchical DAG (Directed Acyclic Graph) tree. |
| **Parameters Table** | `Spreadsheet Workbench` | Use aliases in cells and bind via expressions (`Spreadsheet.param`). |

---

## Mouse Navigation Modes

Commercial CAD users often feel disoriented by mouse navigation. You can set FreeCAD navigation to match your favorite software in:
**Edit &rarr; Preferences &rarr; Display &rarr; Navigation &rarr; 3D Navigation**:

- **Blender**: Middle-click rotate, Shift+Middle-click pan, Wheel zoom.
- **CAD (Default)**: Left-click select, Middle-click pan, Left+Right or Middle+Left rotate.
- **OpenCASCADE**: Left-drag rotate, Right-drag pan, Ctrl+Left zoom.
- **Revit**: Middle-drag pan, Shift+Middle-drag rotate.
- **Inventor**: F4 rotate, F2 pan, F3 zoom (or standard Autodesk conventions).
- **Tinkercad**: Right-drag rotate, Middle-drag pan.
- **Touchpad**: Two-finger drag pan, Alt+drag rotate.

---

## Common Pitfalls for New Migrators

### 1. "My body split into two pieces and threw an error!"
In Fusion 360 or OnShape, an extrude can create disjoint bodies automatically. In FreeCAD, a `PartDesign Body` **MUST be a single connected solid**. If a cut divides a body into two disconnected islands, FreeCAD marks it invalid.
- *Solution*: Model separate components in separate `Bodies`, then group them using `Assembly` or `App::Part`.

### 2. "I edited a sketch and everything downstream turned red!"
You encountered the Topological Naming Problem.
- *Solution*: Avoid mapping sketches directly to model faces. Use Datum Planes or principal planes (`XY`, `XZ`, `YZ`).

### 3. "Where is the Timeline like in Fusion 360?"
FreeCAD does not use an animated horizontal bottom timeline. Instead, the **Tree View** represents the feature history vertically.
- Every feature consumes its predecessor (e.g., `Pad` consumes `Sketch`, `Pocket` consumes `Pad`).
- To rollback or work at an earlier point, right-click any feature in the tree and choose **Set Tip**. The model rolls back to that state.

### 4. "How do I do sheet metal?"
Install the popular external workbench **SheetMetal** via the **Tools &rarr; Addon Manager**. It provides bends, flanges, unfold flat patterns, and K-factor calculations.
