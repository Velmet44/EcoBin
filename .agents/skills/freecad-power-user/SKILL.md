---
name: freecad-power-user
description: >-
  Advanced Python scripting, automation, macro creation, and headless execution for FreeCAD.
  Covers FreeCAD API (`FreeCAD`/`App`, `FreeCADGui`/`Gui`, `Part`, `Draft`, `Sketcher`),
  topological B-Rep scripting (OpenCASCADE shapes, wires, faces, booleans), custom parametric
  scripted objects (`FeaturePython` and ViewProviders with `execute`, `onChanged`, and pickle
  `dumps`/`loads`), PySide/Qt UI dialogs, and running FreeCAD headlessly in scripts or CI/RPC.
  Use this skill whenever generating FreeCAD Python code, writing or debugging macros,
  creating custom parametric plugins, or automating CAD operations.
---

# FreeCAD Power User Skill

This skill equips AI agents to write idiomatic, high-performance, and crash-resilient Python code for FreeCAD.

Based on the official [FreeCAD Documentation: Power users hub](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Power_users_hub.md).

---

## The FreeCAD Python Architecture

FreeCAD has a dual-layer architecture:
1. **`FreeCAD` (aliased as `App`)**: The core application module. Manages documents, geometric data, parametric dependency graph, and properties. Operates without any GUI (usable headlessly).
2. **`FreeCADGui` (aliased as `Gui`)**: The presentation layer. Manages 3D scene representation (Coin3D/Pivy scenegraph), selection, Qt/PySide windows, task panels, and colors.

```python
import FreeCAD as App
import FreeCADGui as Gui # Only import when GUI is present!
import Part
import math
```

> [!IMPORTANT]
> **Headless Safety**:
> Never import `FreeCADGui` or call `Gui.` methods in scripts intended to run headlessly, in background workers, or in automated unit tests. FreeCAD can run with `freecadcmd` or `FreeCAD --console`. Check `App.GuiUp` before calling GUI code:
> ```python
> if App.GuiUp:
>     import FreeCADGui as Gui
>     Gui.ActiveDocument.ActiveView.fitAll()
> ```

---

## Essential Patterns & Idioms

### 1. Document Management & Transactions
Always handle document creation and recomputation properly:

```python
import FreeCAD as App

# Get or create active document
doc = App.ActiveDocument
if not doc:
    doc = App.newDocument("ParametricDesign")

# Wrap modifications in a transaction for clean Undo/Redo
doc.openTransaction("Generate Model")
try:
    # ... create or edit objects ...
    doc.recompute()
    doc.commitTransaction()
except Exception as e:
    doc.abortTransaction()
    raise e
```

### 2. Geometry Creation: Part vs Sketcher

#### Direct B-Rep with the `Part` Module (Fast, Precise, Headless-Friendly):
```python
import FreeCAD as App
import Part

doc = App.ActiveDocument or App.newDocument()

# Create geometric primitives in memory
box = Part.makeBox(100, 50, 20)
cylinder = Part.makeCylinder(10, 30, App.Vector(50, 25, 0), App.Vector(0, 0, 1))

# Boolean Cut
result_shape = box.cut(cylinder)

# Add to document
feature = doc.addObject("Part::Feature", "CutPlate")
feature.Shape = result_shape
doc.recompute()
```

#### Parametric Sketch + PartDesign Body:
```python
import FreeCAD as App
import Sketcher

doc = App.ActiveDocument or App.newDocument()
body = doc.addObject("PartDesign::Body", "Body")
sketch = body.newObject("Sketcher::SketchObject", "Sketch")
sketch.Support = (doc.XY_Plane, [""])
sketch.MapMode = "FlatFace"

# Add geometry (Line segment)
sketch.addGeometry(Part.LineSegment(App.Vector(0, 0, 0), App.Vector(50, 0, 0)), False)
# Add constraints
sketch.addConstraint(Sketcher.Constraint('Coincident', 0, 1, -1, 1)) # Vertex 1 to origin
doc.recompute()
```

### 3. Scripted Objects (`FeaturePython`)
A `FeaturePython` object creates a completely custom parametric object in the tree view that automatically recomputes whenever its properties change.

**Core Rules**:
- Store logic in a python proxy class.
- Implement `execute(self, obj)` to rebuild geometry when properties change.
- Implement `onChanged(self, obj, prop)` to validate property updates.
- Store state in `App::Property*` fields, NOT inside `self` instance attributes unless implementing `__getstate__` / `__setstate__` (`dumps` and `loads`).

---

## Detailed References

Consult the deep-dive manuals in `references/`:
- [Python API Full Catalog](./references/python_api_full_catalog.md): Complete index of all 58 Python API documentation pages, scripting modules (`App`, `Gui`, `Part`, `Draft`, `Mesh`, `Sketcher`, `TechDraw`, `FEM`), and classes.
- [Macro Recipes & Automation Catalog](./references/macros_recipes_catalog.md): Comprehensive catalog of 243 official macros, snippets, recipes, and automation scripts.
- [Python API Quick Reference](./references/python_api_reference.md): Document methods, property types, Vector/Matrix math, units, and transactions.
- [Topological Data Scripting](./references/topological_scripting.md): Deep dive into OpenCASCADE `Part::TopoShape`, vertices, wires, faces, shells, and boolean cuts.
- [Scripted Objects (`FeaturePython`)](./references/scripted_objects.md): Production template with properties, recompute lifecycle, ViewProvider, and serialization.
- [PySide & GUI Integration](./references/pyside_gui_integration.md): Custom commands, toolbars, modal dialogs, task panels, and Coin3D/Pivy scene graph.
- [Headless Execution & Batch Automation](./references/headless_execution.md): Running FreeCAD from CLI, Python virtualenvs, Docker, and MCP servers.

### Offline Documentation Search Tool
To query methods, parameters, and macro examples across all 2,595+ documentation files:
```bash
python scripts/freecad_doc_query.py "<method_or_macro_name>"
```

## Code Examples

Check `examples/` for ready-to-run templates:
- [create_box_and_holes.py](./examples/create_box_and_holes.py): Parametric solid creation with holes.
- [custom_feature_python.py](./examples/custom_feature_python.py): Robust, full-featured scripted object class.
- [custom_macro.FCMacro](./examples/custom_macro.FCMacro): Standard macro with undo transaction and GUI feedback.
