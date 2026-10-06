---
name: freecad-developer
description: >-
  C++ core development, source architecture, CMake compilation, C++ workbench creation,
  exposing C++ classes to Python (PyCXX/CPython XML templates), Sketcher PlaneGCS solver internals,
  testing (`App::UnitTest`), and packaging (Docker, Conda, AppImage, Windows/macOS) for FreeCAD.
  Use this skill whenever assisting with compiling FreeCAD from source, hacking or modifying
  FreeCAD's C++ codebase, creating native C++ workbenches, writing Python/C++ bindings,
  or troubleshooting low-level solver and build issues.
---

# FreeCAD Developer Skill

This skill guides AI agents in navigating, building, extending, and debugging the core C++ and hybrid Python architecture of FreeCAD.

Based on the official [FreeCAD Documentation: Developers hub](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Developer_hub.md).

---

## FreeCAD Source Architecture Overview

FreeCAD is organized as a layered modular system:

```
FreeCAD Core Source Tree (`src/`):
├── Base/       # Fundamental abstractions: Vectors, Matrices, Units, Exceptions, XML parser, Logging
├── App/        # Core document model: PropertyContainer, Document, DocumentObject, Transactions (No GUI)
├── Gui/        # Presentation layer: Qt Widgets, 3D Coin3D Viewer, Selection, ViewProviders, Commands
└── Mod/        # Domain modules / Workbenches (Part, PartDesign, Sketcher, TechDraw, FEM, BIM, etc.)
    ├── Part/
    │   ├── App/    # Part C++ backend (OCCT integration, Part::TopoShape, BRep algorithms)
    │   └── Gui/    # Part GUI commands, ViewProviders, Qt dialogs
    ├── Sketcher/
    │   ├── App/    # Sketcher C++ backend & PlaneGCS constraint solver
    │   └── Gui/    # Sketcher interactive 2D solver editor & UI tools
    └── ...
```

---

## Key Development Workflows

### 1. Compiling FreeCAD with CMake

Standard build instructions across Linux, macOS, and Windows:

```bash
# 1. Clone repository
git clone --recurse-submodules https://github.com/FreeCAD/FreeCAD.git freecad-source

# 2. Configure build directory
mkdir build && cd build
cmake ../freecad-source \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DFREECAD_USE_QT_FILEDIALOG=ON \
  -DBUILD_ENABLE_CXX20=ON \
  -DPYTHON_EXECUTABLE=$(which python3)

# 3. Compile
cmake --build . --parallel $(nproc)

# 4. Run tests
ctest --output-on-failure
```

### 2. Exposing C++ Classes to Python

FreeCAD uses XML definition templates and code generation scripts to generate C++ boilerplate for Python type wrappers:
- `FeaturePy.xml`: Defines Python class name, docstrings, methods, and attributes.
- FreeCAD build tool runs `GenerateFeaturePy.py` &rarr; produces `FeaturePy.h` and `FeaturePyImp.cpp`.
- Developer implements method logic in `FeaturePyImp.cpp`.

### 3. Adding a New Workbench

Workbenches can be:
1. **Pure Python**: Fast prototyping, dynamic loading via `Init.py` and `InitGui.py`.
2. **Hybrid / C++**: Performance-critical algorithms, OpenCASCADE kernel extensions, native Coin3D nodes.

Every workbench implements:
- `Init.py`: Headless initialization (runs when FreeCAD starts without GUI).
- `InitGui.py`: GUI workbench registration, workbench icon, menus, toolbars, and context menus.

---

## Detailed References

Consult the following comprehensive guides in `references/`:
- [Developer Handbook & Roadmap](./references/developer_handbook_and_roadmap.md): Complete index of all 57 C++ source documentation guides, compilation options, architecture modules, and roadmap.
- [Source Architecture & Modules](./references/source_architecture.md): Deep breakdown of `Base`, `App`, `Gui`, and `Mod` libraries.
- [Compilation Guide](./references/compilation_guide.md): Building on Ubuntu/Debian, Fedora, Arch, Windows (MSVC/Conda), macOS, and Docker.
- [C++ & Python Bindings](./references/cpp_python_bindings.md): How to create XML templates and implement Python wrappers for C++ classes.
- [New Workbench Creation](./references/new_workbench_creation.md): Step-by-step guide to writing pure Python and C++ workbenches.
- [Sketcher Solver Internals](./references/sketcher_solver.md): The PlaneGCS geometric constraint solver architecture and algorithm.
- [Testing & Packaging](./references/testing_and_ci.md): Running `FreeCADTest`, writing unit tests, and packaging (AppImage, Conda, Flatpak).

### Offline Documentation Search Tool
To query internal classes, build flags, solver details, or C++ API symbols across all 2,595+ documentation files:
```bash
python scripts/freecad_doc_query.py "<symbol_or_topic>"
```

## Examples

- [dummy_workbench_template/](./examples/dummy_workbench_template/): Minimal, functional workbench boilerplate ready to drop into `~/.FreeCAD/Mod/` or `src/Mod/`.
