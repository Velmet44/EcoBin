# FreeCAD File Formats & Interoperability Guide

FreeCAD can import, export, and convert a wide range of CAD, mesh, vector, and exchange formats.

---

## Native Format

- **`.FCStd`**: The native FreeCAD document format.
  - Internally, an `.FCStd` file is a standard ZIP archive containing:
    - `Document.xml`: Metadata, property definitions, and scene hierarchy.
    - Shape data (`.brep` files): OpenCASCADE Boundary Representation files for each geometric object.
    - `GuiDocument.xml`: Camera position, visual colors, transparency, and display styles.
    - Embedded assets: Images, spreadsheets, or scripts.

---

## 3D CAD Exchange Formats

| Format | Extension | Type | FreeCAD Capability | Best Used For |
| :--- | :--- | :--- | :--- | :--- |
| **STEP** | `.step`, `.stp` | Exact B-Rep Solid | Import & Export | Standard exchange with SolidWorks, Inventor, Fusion 360, CNC CAM tools. Preserves true curves and planes. |
| **IGES** | `.iges`, `.igs` | Surface / Wireframe | Import & Export | Legacy surface exchange. Prefer STEP over IGES for solid models. |
| **BREP** | `.brep`, `.brp` | Native OpenCASCADE | Import & Export | Exact geometric debugging without XML overhead. |
| **IFC** | `.ifc` | BIM Architecture | Import & Export | Architectural workflows, Revit / ArchiCAD exchange. |
| **DXF** | `.dxf` | 2D / 3D Vector | Import & Export | Laser cutting, CNC 2D profiles, AutoCAD exchange. |
| **SVG** | `.svg` | 2D Vector | Export (TechDraw/Draft) | Technical drawing vector output, documentation, laser cutting. |

---

## Mesh Formats (3D Printing / Rendering)

| Format | Extension | Type | FreeCAD Capability | Best Used For |
| :--- | :--- | :--- | :--- | :--- |
| **STL** | `.stl` | Triangulated Mesh | Import & Export | 3D printing slicers (OrcaSlicer, PrusaSlicer, Cura). Loses parametric curves. |
| **OBJ** | `.obj` | Polygonal Mesh | Import & Export | Visualization, Blender, game engines, rendering. |
| **3MF** | `.3mf` | Modern 3D Print Mesh | Import & Export | Multi-material 3D printing, slicer project data. |
| **PLY** | `.ply` | Point Cloud / Polygon | Import & Export | 3D scanners, LiDAR, photogrammetry point clouds. |

---

## Best Practices for Exporting to 3D Printing (STL / 3MF)

1. Select the **Body** (or Tip feature), not individual sketches or sub-features.
2. For high-detail circles and cylinders:
   - Go to **Edit &rarr; Preferences &rarr; Import-Export &rarr; Mesh Formats**.
   - Set **Maximum deviation** to `0.01 mm` or `0.02 mm` for smooth circular curves without visible facet edges.
3. Use **File &rarr; Export** and choose `STL Mesh (*.stl *.ast)`.
4. Alternatively, use the **Mesh Workbench** &rarr; `Meshes > Create Mesh from Shape` (Standard / Mefisto / Netgen) for full manual control over mesh density before export.

---

## Best Practices for Importing External Files

### Converting Imported STEP files into Parametric Solids:
1. Import the `.step` file (`File > Import`).
2. The imported geometry appears as a non-parametric `Part::Feature`.
3. To add features using **PartDesign**:
   - Create a new `PartDesign Body`.
   - Drag the imported Part feature into the Body, or select it and click **Create Body** &rarr; FreeCAD will offer to create a **BaseFeature**.
   - You can now add sketches, pockets, holes, and pads directly onto the imported geometry.

### Converting Imported STL Meshes to CAD Solids:
1. Switch to **Part Workbench**.
2. Select the mesh object &rarr; **Part &rarr; Create shape from mesh** (set tolerance, e.g. `0.1`).
3. Select the created shape &rarr; **Part &rarr; Convert to solid**.
4. Select the solid &rarr; **Part &rarr; Refine shape** (merges coplanar triangles into planar faces).
