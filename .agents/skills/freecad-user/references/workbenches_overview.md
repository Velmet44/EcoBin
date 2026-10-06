# FreeCAD Workbenches Reference: The Complete Guide

FreeCAD organizes its toolset into modular environments called **Workbenches**. Each workbench groups tools dedicated to a specific CAD, CAM, CAE, or BIM task. Switching workbenches changes the available toolbars and menus while keeping the active document and 3D scene intact.

---

## Complete Catalog of Built-in Workbenches

### 1. PartDesign Workbench (`PartDesign`)
- **Target**: Feature-based parametric mechanical modeling, precision engineering, 3D printing.
- **Philosophy**: Enforces a single contiguous solid per `PartDesign::Body`. Uses a sequential feature tree where each operation modifies the preceding tip solid.
- **Key Tools**:
  - **Body** & **Sketch**: Container and 2D profile definition.
  - **Additive Features**: `Pad` (linear extrusion), `Revolution` (axial revolve), `AdditiveLoft`, `AdditivePipe` (sweep).
  - **Subtractive Features**: `Pocket` (linear cut), `Hole` (threaded/counterbore/countersink holes), `Groove` (revolved cut), `SubtractiveLoft`, `SubtractivePipe`.
  - **Dress-up Features**: `Fillet`, `Chamfer`, `Draft`, `Thickness`.
  - **Patterns**: `LinearPattern`, `PolarPattern`, `Mirrored`, `MultiTransform`.
  - **Referencing**: `SubShapeBinder` (safely references external geometry from other bodies).

---

### 2. Sketcher Workbench (`Sketcher`)
- **Target**: 2D geometry-constrained profile creation for 3D operations in PartDesign, Part, Arch, and TechDraw.
- **Solver**: Powered by the C++ **PlaneGCS** solver.
- **Geometry Tools**: Point, Line, Arc (center/endpoints, 3 points), Circle, Ellipse, Rectangle, Regular Polygon, B-spline, Polyline, Slot.
- **Geometric Constraints**: Coincident, PointOnObject, Horizontal, Vertical, Parallel, Perpendicular, Tangent, Equal, Symmetric, Block.
- **Dimensional Constraints**: Horizontal Distance, Vertical Distance, Point-to-Point Distance, Radius, Diameter, Angle.
- **Color Coding**:
  - **White**: Under-constrained (degrees of freedom remain).
  - **Green**: Fully constrained (0 degrees of freedom &mdash; best practice!).
  - **Orange / Red**: Over-constrained or conflicting constraints.
  - **Blue**: Construction lines (reference geometry ignored during 3D extrusions).

---

### 3. Part Workbench (`Part`)
- **Target**: CSG (Constructive Solid Geometry) modeling, direct B-Rep shape manipulation, boolean operations, non-manifold repairs.
- **Philosophy**: Independent geometric primitives combined via booleans. Can handle multiple disjoint solids and arbitrary compounds.
- **Key Tools**:
  - **Primitives**: `Box`, `Cylinder`, `Sphere`, `Cone`, `Torus`, `Tube`, `Wedge`, `Helix`, `Spiral`.
  - **Boolean Operations**: `Union / Fuse`, `Difference / Cut`, `Intersection / Common`, `Section`.
  - **Shape Modification**: `Extrude`, `Revolve`, `Mirror`, `Fillet`, `Chamfer`, `Offset 3D`, `Thickness`.
  - **Shape Builder**: Build Vertex &rarr; Edge &rarr; Wire &rarr; Face &rarr; Shell &rarr; Solid &rarr; Compound.
  - **Defeaturing & Analysis**: Check Geometry, Defeaturing, Measure linear/angular.

---

### 4. Assembly Workbench (`Assembly`) *(FreeCAD 1.0+)*
- **Target**: Building and solving mechanical multi-part assemblies with realistic kinematic joints.
- **Key Features**:
  - Official integrated assembly solver replacing older external addons.
  - **Joint Types**:
    - **Fixed Joint**: Locks parts together rigidly.
    - **Revolute Joint**: Permits rotation around one shared axis (hinges, pivots).
    - **Cylindrical Joint**: Permits rotation and axial sliding along an axis.
    - **Slider Joint**: Permits linear sliding along an axis (prismatic).
    - **Ball Joint**: Permits spherical 3-axis rotation around a point.
    - **Distance Joint**: Enforces fixed distance between points, edges, or planes.
    - **Parallel & Perpendicular Joints**: Constrains relative orientation.
    - **Angle Joint**: Fixes angular relationship between features.
  - Grounding mechanism to anchor base parts in space.

---

### 5. TechDraw Workbench (`TechDraw`)
- **Target**: Producing 2D technical drawings, dimensioned engineering blueprints, and vector PDF exports.
- **Key Features**:
  - Standard drawing sheet templates (A4, A3, A2, ANSI, ISO) with title blocks.
  - **View Projection**: Primary Orthographic Views, Projection Groups (First Angle / Third Angle), Section Views, Detail Views.
  - **Dimensioning**: Horizontal, Vertical, Length, Radius, Diameter, Angle, Chamfer dimensions.
  - **Annotations**: Centerlines, Hole center marks, Surface finish symbols, Welding symbols, Leader lines, Rich text balloons.
  - **Export**: Scalable Vector Graphics (`.svg`), AutoCAD (`.dxf`), and `.pdf`.

---

### 6. BIM Workbench (`BIM` / `Arch`)
- **Target**: Architectural design, Building Information Modeling (BIM), floor plans, structural models, IFC open-standard exchange.
- **Components**:
  - **Architectural Elements**: Walls, Structures (Columns, Beams), Windows, Doors, Roofs, Slabs, Stairs, Curtain Walls.
  - **Site & Organization**: Sites, Buildings, Building Stories (Floors).
  - **IFC Classification**: IFC property sets, material definitions, export/import via IfcOpenShell.

---

### 7. CAM Workbench (`CAM` &mdash; formerly *Path*)
- **Target**: Computer-Aided Manufacturing, CNC toolpath planning, and G-Code generation.
- **Workflow**:
  - **Job Setup**: Define machine coordinate systems (WCS), stock bounding dimensions, and tool library.
  - **Operations**: Contour/Profile, Pocketing, Adaptive Clearing, Drilling, Engraving, Surface 3D, Helix, Thread Milling.
  - **Simulation**: 3D toolpath verification and collision checking.
  - **Post-Processors**: Generates optimized G-Code for GRBL, LinuxCNC, Mach3/4, Fanuc, Haas, Marlin, Centroid.

---

### 8. FEM Workbench (`FEM` &mdash; *Finite Element Method*)
- **Target**: Engineering physics simulation, mechanical stress analysis, thermal distribution, modal natural frequencies.
- **Solvers Supported**: CalculiX (default), Elmer, Z88, OpenFOAM (via external module).
- **Workflow**:
  1. Assign materials (mechanical properties: Young's Modulus, Poisson's Ratio, Density).
  2. Define boundary conditions (Fixed constraints, Force/Load, Pressure, Thermal flux).
  3. Mesh geometry using Netgen or Gmsh (tetrahedral 1st and 2nd order elements).
  4. Run solver headlessly.
  5. Post-process results (Von Mises stress, displacement field, factor of safety, temperature gradients).

---

### 9. Material Workbench (`Material`) *(FreeCAD 1.0+)*
- **Target**: Centralized material definition and assignment across all workbenches (PartDesign, FEM, TechDraw, BIM).
- **Capabilities**:
  - Pre-defined material libraries (Metals, Plastics, Woods, Concrete).
  - Physical properties database: density, thermal conductivity, electrical resistivity, yield strength.
  - Visual properties: appearance rendering color, specular highlights, textures.

---

### 10. Mesh Workbench (`Mesh`)
- **Target**: Working with triangulated polygon meshes (STL, OBJ, 3MF, PLY), mesh repair, and 3D printing preparation.
- **Key Tools**:
  - **Import & Export**: High-speed mesh reading and writing.
  - **Mesh Analysis**: Check for non-manifold edges, self-intersections, holes, flipped surface normals.
  - **Mesh Repair**: Fill holes, harmonize normals, remove duplicated faces.
  - **Mesh Conversion**: Create mesh from Part shape (Standard, Mefisto, Netgen) and convert mesh to Part shape.
  - **Boolean Operations on Meshes**: Union, Difference, Intersection directly on triangulated meshes.

---

### 11. Draft Workbench (`Draft`)
- **Target**: 2D architectural and mechanical drafting, rapid 2D/3D wireframe modeling, SVG/DXF conversion.
- **Features**:
  - Drawing primitives: Line, Wire, Arc, Circle, Ellipse, Rectangle, Polygon, BSpline, Text, Dimension.
  - Snapping system: Endpoints, Midpoints, Centers, Orthogonal, Grid, Intersections.
  - Modification tools: Move, Rotate, Scale, Offset, Trim/Extend, Clone, Array (Orthogonal, Polar, Circular, Path).
  - Interoperability bridge: Converts 2D AutoCAD DXF/DWG drawings into FreeCAD sketches and faces.

---

### 12. Spreadsheet Workbench (`Spreadsheet`)
- **Target**: Global parameter management, dimension tables, and formulaic design automation.
- **Features**:
  - Define variables with names, values, units (mm, in, deg), and cell aliases.
  - Two-way binding with FreeCAD's Expression Engine (`=Spreadsheet.WallThickness`).
  - Allows driving entire parametric assemblies from a single master dimension sheet.

---

### 13. OpenSCAD Workbench (`OpenSCAD`)
- **Target**: Interoperability with OpenSCAD script files (`.scad`) and CSG feature tree repair.
- **Capabilities**:
  - Import `.scad` code directly into FreeCAD shapes.
  - Execute OpenSCAD code headlessly via installed OpenSCAD binary.
  - Repair and expand constructive solid geometry trees.

---

### 14. Surface Workbench (`Surface`)
- **Target**: Advanced NURBS and B-Spline freeform surface modeling, patching, and surfacing.
- **Key Tools**:
  - **Filling**: Creates a smooth surface bounded by a closed boundary of edges (with optional support surfaces for tangency).
  - **Sewing**: Stitches multiple individual surface patches into a continuous shell.
  - **Curve on Surface**: Projects 3D curves onto complex curved faces.
  - **Geom Plate**: Generates surfaces satisfying point and curve constraints.

---

### 15. Points Workbench (`Points`)
- **Target**: Point cloud data handling, LiDAR scanning, and 3D optical scanner data processing.
- **Capabilities**:
  - Import point cloud formats (`.asc`, `.pcd`, `.ply`).
  - Point cloud inspection, coordinate extraction, and subsampling.
  - Point cloud bounding box and triangulation into meshes.

---

### 16. Reverse Engineering Workbench (`Reverse Engineering`)
- **Target**: Converting 3D scanned meshes and point clouds into parametric CAD surfaces and solids.
- **Capabilities**:
  - Fitting analytical shapes (planes, cylinders, spheres) to selected mesh facets.
  - B-Spline surface fitting over digitized topology.
  - Cross-section extraction from meshes for sketch recreation.

---

### 17. Inspection Workbench (`Inspection`)
- **Target**: Visual and geometric examination of shapes and verification against nominal CAD geometry.
- **Capabilities**:
  - Visual distance inspection between two shapes or between a CAD model and a scanned mesh.
  - Colormap deviation display showing manufacturing tolerances (out-of-spec zones in red/blue).

---

### 18. Robot Workbench (`Robot`)
- **Target**: Simulating 6-axis industrial articulated robot arms and trajectory kinematics.
- **Features**:
  - Robot models: Standard 6-axis industrial robots (Kuka, etc.).
  - Trajectory creation, waypoint definition, reachability check, and kinematics simulation.

---

### 19. Test Framework Workbench (`Testing`)
- **Target**: Internal automated unit testing, regression testing, and developer QA diagnostics.
- **Capabilities**:
  - Runs built-in test suites (`TestPartApp`, `TestSketcherApp`, `TestFemApp`).
  - Accessible headlessly via `freecadcmd -t 0`.

---

### 20. Standard Tools (`Std_Base`)
- **Target**: Universal system functions present across all workbenches.
- **Capabilities**:
  - Document management (New, Open, Save, Import, Export).
  - Global Edit tools (Undo/Redo, Placement, Transform triad).
  - View management (Fit All, Standard Views, Camera Projections, Clipping Planes).
  - Tools & Macros (Addon Manager, Parameter Editor, Macro recorder, Units calculator).

---

## Obsolete Workbenches Reference

These workbenches were included in older FreeCAD versions but have been replaced:
- **`Start Workbench`** (deprecated in 1.0): Replaced by the modern Start page.
- **`Web Workbench`** (removed in 1.0): Provided an internal web browser.
- **`Drawing Workbench`** (replaced in 0.21): Predecessor of **TechDraw**.
- **`Raytracing Workbench`** (replaced in 0.21): Replaced by the external **Render Workbench**.
- **`Image Workbench`** (integrated in 0.21): Functionality merged into `Std_Import` and `Std_ViewLoadImage`.

---

## Major External Workbenches (Addon Manager)

FreeCAD has a thriving ecosystem of community workbenches installable with one click via **Tools &rarr; Addon Manager**:

| Workbench | Function & Purpose |
| :--- | :--- |
| **`SheetMetal`** | Essential for sheet metal fabrication: bending, flanges, corner reliefs, and automatic 2D flat pattern unfolding with K-factor calculations. |
| **`Fasteners`** | One-click insertion of parametric ISO/DIN/ANSI bolts, screws, nuts, threaded rods, and washers with automated thread rendering. |
| **`Curves`** | Advanced NURBS curve and surface tools: Gordon surfaces, blend curves, isoparametric curves, sketch on surface. |
| **`FCGear`** | Parametric generation of mechanical gears: Involute, Bevel, Crown, Worm, Helical, Lantern, and Cycloid gears. |
| **`CfdOF`** | Computational Fluid Dynamics (CFD) frontend for OpenFOAM: airflow, pipe hydraulics, aerodynamics. |
| **`Render`** | Photorealistic rendering using external engines: Cycles (Blender), LuxCoreRender, Appleseed, POV-Ray. |
| **`Reinforcement`** | Automated concrete rebar placement (stirrups, straight bars, bent bars) inside BIM structural elements. |
| **`ExplodedAssembly`**| Creates exploded views of mechanical assemblies and generates disassembly motion animations. |
| **`Lattice2`** | Advanced arrays and complex parametric repetitions of bodies and shapes. |
| **`Defeaturing`** | Removes holes, chamfers, and fillets from imported dumb STEP models for simplified simulation or CAM. |
