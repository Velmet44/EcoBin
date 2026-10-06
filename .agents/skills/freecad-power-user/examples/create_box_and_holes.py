#!/usr/bin/env python3
"""
Example: Parametric Plate with Mounting Holes
Demonstrates robust Part module geometric construction and boolean operations.
Works in both GUI and headless (console) mode.
"""

import FreeCAD as App
import Part
import math

def create_mounting_plate(length=120.0, width=80.0, thickness=10.0, hole_radius=4.0, margin=12.0):
    # Get or create active document
    doc = App.ActiveDocument or App.newDocument("MountingPlateDoc")
    doc.openTransaction("Create Mounting Plate")

    try:
        # 1. Base Plate
        base_box = Part.makeBox(length, width, thickness)

        # 2. Fillet the 4 vertical corners
        # Find vertical edges (parallel to Z axis)
        vertical_edges = []
        z_dir = App.Vector(0, 0, 1)
        for edge in base_box.Edges:
            if hasattr(edge.Curve, 'Direction'):
                if abs(edge.Curve.Direction.dot(z_dir)) > 0.999:
                    vertical_edges.append(edge)

        filleted_base = base_box.makeFillet(margin * 0.8, vertical_edges)

        # 3. Create 4 corner holes
        holes = []
        hole_centers = [
            (margin, margin),
            (length - margin, margin),
            (length - margin, width - margin),
            (margin, width - margin)
        ]

        for cx, cy in hole_centers:
            hole_cyl = Part.makeCylinder(
                hole_radius,
                thickness + 4.0, # Slight overlap to prevent coplanar non-manifold faces
                App.Vector(cx, cy, -2.0),
                App.Vector(0, 0, 1)
            )
            holes.append(hole_cyl)

        # Fuse all holes together first for boolean efficiency
        fused_holes = Part.fuse(holes) if len(holes) > 1 else holes[0]

        # 4. Cut holes from filleted base plate
        final_plate = filleted_base.cut(fused_holes)

        # 5. Add to document
        plate_obj = doc.addObject("Part::Feature", "ParametricMountingPlate")
        plate_obj.Shape = final_plate

        # Set color to metallic steel if GUI is available
        if App.GuiUp:
            plate_obj.ViewObject.ShapeColor = (0.75, 0.78, 0.82)

        doc.recompute()
        doc.commitTransaction()
        App.Console.PrintMessage(f"Plate created successfully. Final Volume: {final_plate.Volume:.2f} mm^3\n")
        return plate_obj

    except Exception as e:
        doc.abortTransaction()
        App.Console.PrintError(f"Failed to create mounting plate: {e}\n")
        raise e

if __name__ == "__main__":
    create_mounting_plate()
