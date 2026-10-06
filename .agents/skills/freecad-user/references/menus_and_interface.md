# FreeCAD Menus & User Interface Reference

FreeCAD features a modular, Qt-based graphical user interface composed of standard menus, workbench-specific menus, dockable panels, and context-sensitive menus.

---

## 1. The Standard Top Menu Bar

The standard menu bar provides global tools accessible across all workbenches:

```
[File]   [Edit]   [View]   [Tools]   [Macro]   [Windows]   [Help]
```

### A. File Menu (`Std_File_Menu`)
Tools related to document lifecycle and file input/output:
- **New** (`Ctrl+N`): Creates a new empty document.
- **Open...** (`Ctrl+O`): Opens existing `.FCStd` documents or imports external files.
- **Open Recent**: Fast access to recently edited documents.
- **Close / Close All** (`Ctrl+W` / `Ctrl+Shift+W`): Closes active or all document tabs.
- **Save / Save As...** (`Ctrl+S` / `Ctrl+Shift+S`): Saves the document.
- **Save a Copy...**: Saves a duplicate without changing the active working file.
- **Revert**: Discards unsaved changes and reverts to the last saved state on disk.
- **Import...** (`Ctrl+I`): Imports external geometry (STEP, IGES, DXF, SVG, STL, OBJ, IFC) into the active document.
- **Export...** (`Ctrl+E`): Exports selected objects to CAD exchange or mesh formats.
- **Merge Project...**: Adds objects from another `.FCStd` file into the active document.
- **Document Information...**: Displays author, license, and creation metadata.
- **Print / Print Preview / Export PDF...**: Printing and 2D vector PDF output.
- **Exit** (`Ctrl+Q`): Closes FreeCAD.

---

### B. Edit Menu (`Std_Edit_Menu`)
Tools for modifying geometry, clipboard actions, and preferences:
- **Undo / Redo** (`Ctrl+Z` / `Ctrl+Y`): Undoes or redoes transactions.
- **Cut / Copy / Paste** (`Ctrl+X` / `Ctrl+C` / `Ctrl+V`): Standard clipboard actions.
- **Duplicate Selection**: Duplicates objects inside the document (switches to `PartDesign DuplicateSelection` if PartDesign is active).
- **Refresh / Recompute** (`F5`): Manually forces a full document recompute.
- **Box Selection / Box Element Selection** (`Shift+B`): Rectangular marquee selection of objects or sub-elements (faces/edges).
- **Select All** (`Ctrl+A`): Selects all objects in the active document.
- **Delete** (`Del`): Deletes selected objects.
- **Send to Python Console**: Injects selected objects as Python variables into the built-in console.
- **Placement...**: Opens the Placement task panel (translation X/Y/Z and rotation angles/axes).
- **Transform**: Interactive 3D triad manipulation gizmo in the 3D viewport.
- **Alignment...**: Aligns two objects using reference points.
- **Toggle Edit Mode**: Activates or exits in-place object edit mode (e.g. entering/exiting a sketch).
- **Preferences...**: Comprehensive application settings (Display, Navigation, Workbenches, Units, Import/Export). *On macOS, located under application menu.*

---

### C. View Menu (`Std_View_Menu`)
Controls 3D camera projections, rendering styles, visibility, panels, and toolbars:
- **Standard Views**:
  - **Axonometric** (`0`), **Isometric**, **Dimetric**, **Trimetric**.
  - **Top** (`1`), **Front** (`2`), **Right** (`3`), **Rear** (`4`), **Bottom** (`5`), **Left** (`6`).
- **Zoom / Fit**:
  - **Fit All** (`V, F` or `Space`): Fits all visible geometry into the viewport.
  - **Fit Selection** (`V, S`): Zooms to selected objects or faces.
  - **Box Zoom** (`Ctrl+B`): Zooms into a user-drawn rectangular window.
- **Projection Mode**: Toggle between **Orthographic** (engineering blueprint perspective) and **Perspective** (realistic camera view).
- **Display Mode**:
  - **As Is**, **Flat Lines** (`V, 1` - shaded with visible boundary edges), **Shaded** (`V, 2`), **Wireframe** (`V, 3`), **Points** (`V, 4`), **Hidden Line** (`V, 5`).
- **Clipping Plane & Persistent Section Cut**: Live cutting planes to inspect internal hollow features.
- **Visibility Submenu**:
  - **Toggle Visibility** (`Space`): Shows or hides the selected object.
  - **Show / Hide All Objects**.
- **Material & Appearance**: Set object diffuse colors, specular reflection, and transparency (0% to 100%).
- **Workbench Submenu**: Dropdown to switch the active workbench.
- **Toolbars Submenu**: Toggle individual toolbars on/off or lock toolbars.
- **Panels Submenu**: Toggle individual interface panels (Tree view, Property view, Tasks, Python console, Report view).
- **Tree View Actions**: SyncView, SyncSelection, Single/Multi-document display mode.

---

### D. Tools Menu (`Std_Tools_Menu`)
System inspection, add-on management, and debugging utilities:
- **Edit Parameters...**: Direct low-level registry editor for FreeCAD configuration keys.
- **Save Picture...**: High-resolution screenshot capture with transparent background option.
- **Load Image...**: Opens image files in an independent 2D viewer.
- **Scene Inspector...**: Coin3D OpenGL scene graph inspector.
- **Dependency Graph...**: Graphical node diagram showing parent-child parametric dependencies (requires Graphviz).
- **Export to Web...**: Generates a standalone HTML/WebGL interactive page of the model.
- **Project Utility...**: Diagnostic tool to inspect, unpack, and repair damaged `.FCStd` archives.
- **Measure** (FreeCAD 1.0+): Unified interactive measurement tool (distance, angle, radius).
- **Addon Manager**: Installs community workbenches, macros, color themes, and preferences packs.
- **Customize...**: Customizes keyboard shortcuts, user toolbars, macros, and spaceball settings.

---

### E. Macro Menu (`Std_Macro_Menu`)
Automation and Python macro execution:
- **Macros...**: Dialog listing installed macros with options to Run, Edit, Create, or Delete.
- **Record Macro...**: Records user GUI actions into an executable Python script (`.FCMacro`).
- **Stop Recording**: Finishes recording the active macro.
- **Recent Macros**: Quick access to execute recently run macros.

---

### F. Windows Menu (`Std_Windows_Menu`)
Window arrangement in the main view area:
- **Tile**: Tiles all open document viewports side by side.
- **Cascade**: Stacks viewports with visible titlebars.
- **Next / Previous** (`Ctrl+Tab` / `Ctrl+Shift+Tab`): Cycles through active document tabs.

---

### G. Help Menu (`Std_Help_Menu`)
Help resources, documentation, and version information:
- **FreeCAD Help** (`F1`): Launches built-in offline/online documentation browser.
- **What's This?** (`Shift+F1`): Context-sensitive tool description.
- **Online Documentation / FreeCAD Website / User Forum**: Direct links to official web resources.
- **About FreeCAD**: Version string, Git hash, build date, library versions (OCC, Qt, Python). Essential when reporting bugs or requesting support.

---

## 2. Workbench-Specific Menus

When a workbench is selected, FreeCAD dynamically inserts workbench-specific menus between `Edit` and `Tools`:

| Workbench | Inserted Menus | Key Operations Available |
| :--- | :--- | :--- |
| **PartDesign** | `Part Design` | Create Body, Create Sketch, Pad, Pocket, Revolution, Hole, Fillet, Chamfer, Patterns, SubShapeBinder. |
| **Sketcher** | `Sketch`, `Sketcher Geometries`, `Sketcher Constraints` | Geometries (Line, Arc, Circle, Rectangle, B-spline), Constraints (Coincident, Tangent, Distance, Angle, Equal). |
| **Part** | `Part`, `Measure` | Primitives (Box, Cylinder, Sphere), Booleans (Cut, Fuse, Common), Extrude, Revolve, Shape Builder, Cross-sections. |
| **Assembly** | `Assembly` | Insert Component, Create Joint (Fixed, Revolute, Slider, Ball, Cylindrical, Angle), Solve. |
| **TechDraw** | `TechDraw` | New Page from Template, Insert View, Projection Group, Section View, Dimensions, Centerlines, Annotations. |
| **BIM / Arch** | `BIM`, `Architecture` | Wall, Structure, Window, Door, Roof, Slab, Axis System, IFC classification. |
| **CAM** | `CAM` | New Job, Tool Library, Profiling, Pocketing, Drilling, Post-process (generate G-code). |

---

## 3. Core Interface Panels & Workspaces

The FreeCAD interface comprises several dockable panels:

```
┌───────────────────────────────────────────────────────────┐
│ Top Menus & Toolbars                                      │
├───────────────┬───────────────────────────────────────────┤
│ Combo View:   │ 3D View Area                              │
│ - Tree View   │                                           │
│ - Tasks Panel │                                           │
│               │                                           │
│ Property View:│                                           │
│ - Data Tab    │                                           │
│ - View Tab    │                                           │
├───────────────┴───────────────────────────────────────────┤
│ Report View / Python Console                              │
└───────────────────────────────────────────────────────────┘
```

1. **Tree View** (Model Tree):
   - Hierarchical representation of the document DAG.
   - Shows active Body (bold), features, sketches, and groups.
2. **Property View**:
   - **Data Tab**: Parametric properties (Length, Width, Height, Placement, Expressions).
   - **View Tab**: Display properties (Color, Line Width, Transparency, Point Size).
3. **Tasks Panel**:
   - Appears dynamically when executing operations (Pad dialog, Pocket dialog, Revolve axis picker, Fillet radius).
4. **3D View Area**:
   - High-performance OpenGL viewport showing models with navigation cube in the corner.
5. **Report View**:
   - Displays status logs, solver errors, syntax warnings, and operation summaries.
6. **Python Console**:
   - Live Python REPL interacting with `FreeCAD` and `FreeCADGui`.

---

## 4. Context Menus (Right-Click)

### In the Tree View:
- **Set Tip** (PartDesign): Marks the selected feature as the active state for further additions.
- **Mark to Recompute**: Flags object as dirty for forced recalculation.
- **Appearance...**: Opens color and transparency dialog.
- **Toggle Visibility** (`Space`): Shows/hides item.
- **Delete** (`Del`): Removes object.
- **Rename** (`F2`): Edits user-facing `Label`.

### In the 3D View:
- **Navigation Mode**: Fast switcher between CAD, Blender, Touchpad, Inventor modes.
- **Fit All**: Centers model.
- **Draw Style**: Switches flat lines / shaded / wireframe.
