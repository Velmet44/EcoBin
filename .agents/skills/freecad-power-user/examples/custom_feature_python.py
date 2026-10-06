#!/usr/bin/env python3
"""
Production Template for a FreeCAD FeaturePython Scripted Object.
Features:
- Full typed dynamic properties
- Automatic recompute logic
- Property change validation
- Proper pickle serialization support (__getstate__ / __setstate__)
- Dedicated ViewProvider for GUI styling and 3D display
"""

import FreeCAD as App
import Part

class ParametricSteppedShaft:
    """
    Parametric Two-Step Shaft Feature.
    Rebuilds geometry automatically on property change.
    """
    def __init__(self, obj):
        obj.Proxy = self
        self.init_properties(obj)

    def init_properties(self, obj):
        # Section 1 Dimensions
        if not hasattr(obj, "Radius1"):
            obj.addProperty("App::PropertyLength", "Radius1", "Section1", "Radius of lower section").Radius1 = 15.0
        if not hasattr(obj, "Length1"):
            obj.addProperty("App::PropertyLength", "Length1", "Section1", "Length of lower section").Length1 = 40.0

        # Section 2 Dimensions
        if not hasattr(obj, "Radius2"):
            obj.addProperty("App::PropertyLength", "Radius2", "Section2", "Radius of upper section").Radius2 = 10.0
        if not hasattr(obj, "Length2"):
            obj.addProperty("App::PropertyLength", "Length2", "Section2", "Length of upper section").Length2 = 30.0

        # Central Bore
        if not hasattr(obj, "BoreRadius"):
            obj.addProperty("App::PropertyLength", "BoreRadius", "Bore", "Inner through-hole radius").BoreRadius = 5.0

    def execute(self, obj):
        """Recompute geometric shape."""
        r1 = obj.Radius1.Value
        l1 = obj.Length1.Value
        r2 = obj.Radius2.Value
        l2 = obj.Length2.Value
        bore = obj.BoreRadius.Value

        # Validate
        if r1 <= 0 or l1 <= 0 or r2 <= 0 or l2 <= 0:
            App.Console.PrintError("Shaft dimensions must be strictly positive.\n")
            return

        if bore >= min(r1, r2):
            App.Console.PrintError("Bore radius cannot exceed or match the outer radii.\n")
            return

        # Build outer stepped solid
        sec1 = Part.makeCylinder(r1, l1, App.Vector(0, 0, 0), App.Vector(0, 0, 1))
        sec2 = Part.makeCylinder(r2, l2, App.Vector(0, 0, l1), App.Vector(0, 0, 1))
        outer_shaft = sec1.fuse(sec2)

        # Bore cutout
        total_len = l1 + l2 + 4.0
        inner_bore = Part.makeCylinder(bore, total_len, App.Vector(0, 0, -2.0), App.Vector(0, 0, 1))

        # Assign shape
        obj.Shape = outer_shaft.cut(inner_bore)

    def onChanged(self, obj, prop):
        """React to live property modifications."""
        if prop in ("Radius1", "Radius2", "BoreRadius"):
            if hasattr(obj, "BoreRadius") and hasattr(obj, "Radius1") and hasattr(obj, "Radius2"):
                if obj.BoreRadius.Value >= min(obj.Radius1.Value, obj.Radius2.Value):
                    App.Console.PrintWarning(f"Warning: Bore ({obj.BoreRadius.Value}) is too large for outer radius!\n")

    def __getstate__(self):
        """Serialize for .FCStd saving (return pickleable data)."""
        return None

    def __setstate__(self, state):
        """Restore on .FCStd loading."""
        return None


class ViewProviderSteppedShaft:
    """Handles 3D visualization and display modes."""
    def __init__(self, vobj):
        vobj.Proxy = self

    def attach(self, vobj):
        pass

    def updateData(self, fp, prop):
        pass

    def getDisplayModes(self, vobj):
        return ["Shaded", "Wireframe"]

    def getDefaultDisplayMode(self):
        return "Shaded"

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


def create_stepped_shaft(name="SteppedShaft", doc=None):
    """Factory helper to instantiate a FeaturePython stepped shaft."""
    if doc is None:
        doc = App.ActiveDocument or App.newDocument("ShaftDemo")

    doc.openTransaction("Add Stepped Shaft")
    try:
        obj = doc.addObject("Part::FeaturePython", name)
        ParametricSteppedShaft(obj)

        if App.GuiUp:
            ViewProviderSteppedShaft(obj.ViewObject)
            obj.ViewObject.ShapeColor = (0.6, 0.7, 0.9)

        doc.recompute()
        doc.commitTransaction()
        return obj
    except Exception as e:
        doc.abortTransaction()
        raise e

if __name__ == "__main__":
    create_stepped_shaft()
