# FreeCAD scripting patterns

## Runtime

Run headless scripts with the FreeCAD command-line executable, not a system Python that cannot import FreeCAD:

```text
FreeCADCmd path/to/build_part.py --pass --input part-input.json --output part.FCStd
```

FreeCAD command-line option handling varies by build; inspect `FreeCADCmd --help`. The `--pass` delimiter passes following arguments to a script.

Import modules explicitly:

```python
import FreeCAD as App
import Part
import Sketcher
```

Avoid `FreeCADGui` in headless scripts.

## Document lifecycle

```python
doc = App.newDocument("PartNumber")
try:
    # create objects
    doc.recompute()
    # assert results
    doc.saveAs(output_path)
finally:
    App.closeDocument(doc.Name)
```

Use `App.openDocument(path)` for audits. Close without saving when performing parameter sweeps.

## Quantities

Use `App.Units.Quantity("12 mm")` or a unit-bearing string for properties that accept quantities. Do not assume the displayed unit schema changes FreeCAD’s internal base units.

Spreadsheet aliases are good expression identifiers:

```python
sheet.set("B2", "12 mm")
sheet.setAlias("B2", "plate_thickness")
pad.setExpression("Length", "Parameters.plate_thickness")
```

Use descriptive aliases; short identifiers can collide with unit symbols.

## Recompute and status

After each logical group:

```python
doc.recompute()
bad = []
for obj in doc.Objects:
    state = [str(item) for item in getattr(obj, "State", [])]
    if any(item in {"Invalid", "Error"} for item in state):
        bad.append((obj.Name, state))
if bad:
    raise RuntimeError(f"Object errors after recompute: {bad}")
```

For sketches:

```python
status = sketch.solve()
if status != 0 or not sketch.FullyConstrained:
    raise RuntimeError(
        f"{sketch.Name}: solver={status}, dof={sketch.getLastDoF()}"
    )
```

For the release target:

```python
shape = body.Shape
if shape.isNull() or not shape.isValid():
    raise RuntimeError("Final shape is null or invalid")
if len(shape.Solids) != 1 or shape.Volume <= 0:
    raise RuntimeError("Expected one positive-volume solid")
```

Run the GUI Part Check Geometry command with BOP check as an additional release check; `Shape.isValid()` is not a full substitute.

## Names and metadata

Internal object names are stable identifiers in scripts and expressions; labels are user-facing and can be duplicated. Use a deterministic internal name plus a readable label. Store part number, revision, material, process, units, and requirement source as document or object properties.

## Transaction and error policy

- Validate the input schema and cross-parameter inequalities before creating geometry.
- Raise on the first invalid logical phase with object/feature context.
- Never catch `Exception` merely to continue and save a partial file.
- Never save over an approved release.
- Emit an adjacent JSON build report before promotion.

Use `scripts/freecad_build_contract.py` for shared checks, but keep the part generator self-contained enough to archive with the release.
