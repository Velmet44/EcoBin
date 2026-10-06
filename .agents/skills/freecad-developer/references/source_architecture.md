# FreeCAD Source Code Architecture & Modules

FreeCAD is designed around strict separation of concerns, modular plugin architecture, and dual-layer C++/Python execution.

---

## 1. Directory Structure (`FreeCAD/src/`)

```
src/
├── Base/       # Fundamental system abstractions
├── App/        # Headless application core
├── Gui/        # Presentation layer (Qt + Coin3D)
├── Main/       # Executable entry points (FreeCAD, FreeCADCmd)
├── Mod/        # Core workbenches and domain modules
│   ├── Part/
│   ├── PartDesign/
│   ├── Sketcher/
│   ├── TechDraw/
│   ├── FEM/
│   ├── CAM/
│   ├── Assembly/
│   └── ...
└── 3rdParty/   # Bundled third-party libraries (salomesmesh, etc.)
```

---

## 2. Core Libraries Breakdown

### A. `Base` Module (`FreeCADBase`)
- **Purpose**: Low-level foundational classes with zero dependencies on CAD geometry or GUI.
- **Key Components**:
  - `Base::Vector3D`, `Base::Matrix4D`, `Base::Rotation`, `Base::Placement`: 3D linear algebra.
  - `Base::Quantity`, `Base::Unit`: Physical dimensions and dimensional analysis.
  - `Base::BaseClass`: Root class of FreeCAD's dynamic runtime type system (RTTI). Provides `getClassTypeId()`, `isDerivedFrom()`.
  - `Base::Exception`: Standard exception hierarchy.
  - `Base::Console`: Logging and message output (`Message`, `Warning`, `Error`, `Log`).
  - `Base::Persistence`: XML and binary serialization interfaces.

### B. `App` Module (`FreeCADApp`)
- **Purpose**: Headless document and data model. Runs without GUI or OpenGL context.
- **Key Components**:
  - `App::Application`: Global singleton managing documents, parameter database, and module loading.
  - `App::Document`: Represents an open `.FCStd` project. Holds objects, dependency graph, and undo/redo stacks.
  - `App::DocumentObject`: Base class for all parametric features (`Part::Feature`, `Sketcher::SketchObject`, etc.).
  - `App::PropertyContainer`: Class providing dynamic, inspectable, typed properties.
  - `App::Property`: Typed attributes (`PropertyLength`, `PropertyString`, `PropertyLink`, `PropertyPlacement`).
  - `App::Transaction`: Atomic undo/redo transaction logging.

### C. `Gui` Module (`FreeCADGui`)
- **Purpose**: User interface, window management, and 3D visualization.
- **Key Components**:
  - `Gui::Application`: Manages GUI documents, active workbench, and main Qt window.
  - `Gui::ViewProvider`: The visual counterpart to `App::DocumentObject`. Responsible for Coin3D scene graph nodes, color, visibility, and 3D selection.
  - `Gui::View3DInventor`: The 3D viewport widget embedding Coin3D SoQt viewer.
  - `Gui::Command`: Base class for interactive user commands registered to toolbars and menus.
  - `Gui::Selection`: Centralized selection manager handling 3D entity picking and observers.

---

## 3. The Property System & Dependency Graph

### Recomputation Pipeline:
1. User modifies property `Pad.Length`.
2. `Pad` is marked **touched** (dirty).
3. FreeCAD traces the Directed Acyclic Graph (DAG) to find all downstream dependent features (e.g. `Pocket`, `Fillet`).
4. `doc->recompute()` calls `execute()` on each dirty feature in topological sort order.
5. In GUI mode, `ViewProvider::updateData()` updates Coin3D representations.
