# FreeCAD Scripted Objects (`FeaturePython`)

A **`FeaturePython`** object is a parametric custom object authored 100% in Python that behaves identically to native C++ features. It appears in the tree view, reacts to property changes in the Property Editor, and serializes seamlessly to `.FCStd`.

---

## Anatomy of a Scripted Object

A scripted object consists of:
1. **Document Object (`App::FeaturePython`)**: The C++ container in the document holding properties.
2. **Proxy Class**: The Python class instance attached to `obj.Proxy` defining custom logic.
3. **ViewProvider (Optional)**: The GUI representation class attached to `vobj.Proxy` controlling icon, colors, and 3D visual display.

---

## Complete Production Pattern

```python
import FreeCAD as App
import Part

class ParametricCylinderPipe:
    """
    Parametric pipe feature with outer radius, wall thickness, and height.
    """
    def __init__(self, obj):
        # 1. Attach Proxy
        obj.Proxy = self
        
        # 2. Add Dynamic Properties
        obj.addProperty("App::PropertyLength", "OuterRadius", "Dimensions", "Outer radius").OuterRadius = 20.0
        obj.addProperty("App::PropertyLength", "Thickness", "Dimensions", "Wall thickness").Thickness = 3.0
        obj.addProperty("App::PropertyLength", "Height", "Dimensions", "Extrusion height").Height = 60.0
        
    def execute(self, obj):
        """
        Called automatically by FreeCAD whenever recompute() runs or properties change.
        Must assign a valid Part.Shape to obj.Shape.
        """
        r_outer = obj.OuterRadius.Value
        t = obj.Thickness.Value
        h = obj.Height.Value
        
        # Validation
        if t >= r_outer or r_outer <= 0 or h <= 0:
            App.Console.PrintError("Invalid dimensions: thickness must be less than outer radius.\n")
            return
            
        r_inner = r_outer - t
        
        # Build outer and inner cylinders
        c_outer = Part.makeCylinder(r_outer, h)
        c_inner = Part.makeCylinder(r_inner, h)
        
        # Assign hollow shape
        obj.Shape = c_outer.cut(c_inner)

    def onChanged(self, obj, prop):
        """
        Called when a property value changes in the GUI or script.
        """
        if prop == "Thickness":
            if obj.Thickness.Value >= obj.OuterRadius.Value:
                App.Console.PrintWarning("Warning: Thickness exceeds or equals outer radius!\n")

    def __getstate__(self):
        """Used by pickle when saving the FCStd file."""
        return None

    def __setstate__(self, state):
        """Used by pickle when loading the FCStd file."""
        return None


class ViewProviderPipe:
    """ViewProvider for 3D visualization and tree icon."""
    def __init__(self, vobj):
        vobj.Proxy = self

    def attach(self, vobj):
        """Setup coin nodes if needed."""
        pass

    def updateData(self, fp, prop):
        pass

    def getDisplayModes(self, vobj):
        return ["Shaded", "Wireframe", "Points"]

    def getDefaultDisplayMode(self):
        return "Shaded"

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


def create_pipe(doc=None, name="ParametricPipe"):
    """Factory function to instantiate the object cleanly."""
    if doc is None:
        doc = App.ActiveDocument or App.newDocument()
        
    obj = doc.addObject("Part::FeaturePython", name)
    ParametricCylinderPipe(obj)
    
    if App.GuiUp:
        ViewProviderPipe(obj.ViewObject)
        
    doc.recompute()
    return obj
```

---

## Critical Rules for Persistence (`__getstate__` / `__setstate__`)

1. **Avoid Storing Dynamic State in `self`**:
   Never store parametric data in `self.radius`. Always create an `App::Property*` on the `obj`. Properties are serialized natively into `Document.xml`.
2. **If You Store Non-Property Data**:
   You must implement `__getstate__` returning a pickleable dictionary, and `__setstate__(self, state)` restoring it.
3. **Never Pickle C++ References**:
   Never store `obj`, `vobj`, or Coin3D C++ nodes in `self`. FreeCAD destroys and recreates C++ pointers across document reload.
