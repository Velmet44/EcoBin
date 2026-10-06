# FreeCAD Topological Data Scripting (`Part` Module)

FreeCAD's 3D geometric modeling kernel is powered by **OpenCASCADE Technology (OCCT)**. The Python `Part` module provides high-speed access to Boundary Representation (B-Rep) topological shapes.

---

## B-Rep Topological Hierarchy

In OpenCASCADE, shapes are organized strictly from lowest dimension to highest:

```
Vertex      (0D - Point in 3D space)
  ↓
Edge        (1D - Curve bounded by 2 vertices)
  ↓
Wire        (1D - Sequence of connected edges)
  ↓
Face        (2D - Surface bounded by one outer wire and optional hole wires)
  ↓
Shell       (2D - Collection of connected faces)
  ↓
Solid       (3D - Volume enclosed by closed shell(s))
  ↓
CompSolid   (3D - Composite solids joined along shared faces)
  ↓
Compound    (ND - Arbitrary collection of any shapes)
```

Every shape in FreeCAD is an instance of `Part.Shape` (or a subtype like `Part.Solid`, `Part.Face`, `Part.Edge`, `Part.Wire`).

---

## 1. Creating Primitives

```python
import Part
import FreeCAD as App

# Box: length(X), width(Y), height(Z)
box = Part.makeBox(100, 50, 20)

# Cylinder: radius, height, position, axis vector
cyl = Part.makeCylinder(15, 60, App.Vector(50, 25, 0), App.Vector(0, 0, 1))

# Sphere: radius
sphere = Part.makeSphere(25)

# Cone: radius1, radius2, height
cone = Part.makeCone(20, 10, 40)

# Torus: radius1 (major), radius2 (minor)
torus = Part.makeTorus(40, 10)

# Helix: pitch, height, radius
helix = Part.makeHelix(5, 30, 10)
```

---

## 2. Boolean Operations

```python
# Cut (Difference: shape1 minus shape2)
cut_shape = box.cut(cyl)

# Fuse (Union: combines shape1 and shape2 into single solid)
fuse_shape = box.fuse(sphere)

# Common (Intersection: overlapping volume)
common_shape = box.common(sphere)

# Multi-shape boolean
fused_all = Part.fuse([shape1, shape2, shape3])
```

---

## 3. Constructing Custom Geometry from Scratch

### Constructing Wires and Faces:
```python
import Part
import FreeCAD as App

# 1. Create Points
p1 = App.Vector(0, 0, 0)
p2 = App.Vector(100, 0, 0)
p3 = App.Vector(100, 50, 0)
p4 = App.Vector(0, 50, 0)

# 2. Create Edges
e1 = Part.makeLine(p1, p2)
e2 = Part.makeLine(p2, p3)
e3 = Part.makeLine(p3, p4)
e4 = Part.makeLine(p4, p1)

# 3. Assemble into a closed Wire
wire = Part.Wire([e1, e2, e3, e4])

# 4. Make a planar Face bounded by the wire
face = Part.Face(wire)

# 5. Extrude Face into a Solid (direction vector)
solid = face.extrude(App.Vector(0, 0, 30))

# 6. Check Validity
if solid.isValid():
    print(f"Solid Volume: {solid.Volume} mm^3")
```

---

## 4. Inspecting and Traversing Shapes

A `Part.Shape` provides properties to access its sub-elements:

```python
shape = obj.Shape

# Counts
print(f"Vertices: {len(shape.Vertexes)}")
print(f"Edges:    {len(shape.Edges)}")
print(f"Wires:    {len(shape.Wires)}")
print(f"Faces:    {len(shape.Faces)}")
print(f"Solids:   {len(shape.Solids)}")

# Geometric properties
print(f"Volume:       {shape.Volume}")
print(f"Area:         {shape.Area}")
print(f"CenterOfMass: {shape.CenterOfMass}")
print(f"BoundBox:     {shape.BoundBox}") # XMin, XMax, YMin, YMax, ZMin, ZMax

# Finding specific faces (e.g. highest planar face in Z)
top_faces = []
for face in shape.Faces:
    if face.Surface.TypeId == 'Part::GeomPlane':
        normal = face.normalAt(0, 0)
        if normal.isEqual(App.Vector(0, 0, 1), 1e-4):
            top_faces.append(face)
```

---

## 5. Shape Fillets and Chamfers

```python
# Fillet edges
# shape.makeFillet(radius, list_of_edges)
edges_to_fillet = [shape.Edges[0], shape.Edges[2]]
filleted = shape.makeFillet(2.5, edges_to_fillet)

# Chamfer edges
# shape.makeChamfer(distance, list_of_edges)
chamfered = shape.makeChamfer(1.5, [shape.Edges[1]])
```
