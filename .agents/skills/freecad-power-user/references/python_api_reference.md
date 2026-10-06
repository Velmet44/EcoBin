# FreeCAD Python API Reference

This reference covers the most frequently used functions, classes, and properties across `FreeCAD` (`App`) and `FreeCADGui` (`Gui`).

---

## 1. Document Management (`FreeCAD` / `App`)

```python
import FreeCAD as App

# Documents
doc = App.newDocument("DocName")         # Create new document
doc = App.activeDocument()               # Get active document (or App.ActiveDocument)
doc = App.getDocument("DocName")         # Get by name
App.closeDocument("DocName")             # Close document
App.setActiveDocument("DocName")         # Set active

# Serialization
doc.saveAs("/path/to/file.FCStd")
doc.save()
doc = App.openDocument("/path/to/file.FCStd")

# Recompute & Transactions
doc.recompute()                          # Recompute full document dependency graph
doc.openTransaction("Operation Name")    # Begin undoable transaction
doc.commitTransaction()                  # Commit undoable transaction
doc.abortTransaction()                   # Discard on error
```

---

## 2. Vectors, Placements, and Rotations

FreeCAD uses internal coordinates in **millimeters** and angles in **degrees**.

```python
# Vectors
v1 = App.Vector(10, 20, 30)
v2 = App.Vector(0, 0, 1)
v3 = v1 + v2
length = v1.Length
unit_v = v1.normalize()
dot = v1.dot(v2)
cross = v1.cross(v2)

# Rotations
# Axis, Angle (in degrees)
rot = App.Rotation(App.Vector(0, 0, 1), 45)
# Euler angles: Yaw, Pitch, Roll
rot_euler = App.Rotation(45, 0, 0)

# Placement: Combines Base Position (Vector) and Rotation (Rotation)
placement = App.Placement(App.Vector(10, 0, 0), rot)
# Transforming objects
obj.Placement = placement
# Moving relatively
obj.Placement.Base += App.Vector(5, 0, 0)
```

---

## 3. Dynamic Property System

Every FreeCAD object holds typed dynamic properties. When creating custom objects or modifying features, use standard property types:

| Property Type | Python Value | Description |
| :--- | :--- | :--- |
| `App::PropertyLength` | `float` | Length with unit handling (mm, in). |
| `App::PropertyDistance`| `float` | Distance measurement. |
| `App::PropertyAngle` | `float` | Angle with unit handling (deg, rad). |
| `App::PropertyFloat` | `float` | Unitless floating-point value. |
| `App::PropertyInteger`| `int` | Integer value. |
| `App::PropertyBool` | `bool` | True/False flag. |
| `App::PropertyString` | `str` | Text string. |
| `App::PropertyVector` | `App.Vector` | 3D coordinate vector. |
| `App::PropertyPlacement`| `App.Placement`| Position and orientation. |
| `App::PropertyLink` | `doc.Object` | Reference to another object in document. |
| `App::PropertyLinkList`| `[doc.Obj1, ...]`| List of references. |
| `Part::PropertyPartShape`| `Part.Shape` | Topological B-Rep shape. |

### Adding Properties to Objects:
```python
obj.addProperty("App::PropertyLength", "BoxLength", "Dimensions", "The length of the box")
obj.BoxLength = 50.0
```

---

## 4. FreeCAD Units System

FreeCAD supports explicit units with automatic conversion:

```python
from FreeCAD import Units

u1 = Units.Quantity("10 mm")
u2 = Units.Quantity("2 in")
u3 = u1 + u2
print(u3.getValueAs("mm")) # Converts inches to mm accurately
print(u3.UserString)       # Formatted according to user preferences
```

---

## 5. Selection and GUI Interaction (`FreeCADGui`)

```python
import FreeCADGui as Gui

# Selection
selection = Gui.Selection.getSelection() # List of selected objects
sub_elements = Gui.Selection.getSelectionEx() # Selected with sub-elements (faces, edges)

# Camera & View
view = Gui.ActiveDocument.ActiveView
view.fitAll()
view.viewAxometric()
view.viewTop()
view.viewFront()

# Visual Properties (on ViewObject)
view_obj = obj.ViewObject
view_obj.ShapeColor = (1.0, 0.0, 0.0)    # RGB (0.0 - 1.0)
view_obj.Transparency = 50               # 0 to 100%
view_obj.Visibility = True
```
