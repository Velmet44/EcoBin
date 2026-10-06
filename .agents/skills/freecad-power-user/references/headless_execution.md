# FreeCAD Headless Execution & Automation

FreeCAD can be executed completely without an X11/Wayland display or Windows desktop session. This makes it ideal for automated CAD generation, cloud rendering, CLI batch processing, and AI agent integration.

---

## 1. Running Scripts from Command Line

### A. Using `freecadcmd` or `FreeCADCmd`
FreeCAD bundles a console-only binary (`freecadcmd` on Linux/macOS, `FreeCADCmd.exe` on Windows):
```bash
# Windows
FreeCADCmd.exe path\to\script.py

# Linux / Docker
freecadcmd path/to/script.py
```

### B. Passing Arguments to Scripts
To pass arguments to your script:
```bash
freecadcmd myscript.py -- --input model.step --output model.stl --resolution 0.02
```
In Python:
```python
import sys
# FreeCAD places custom script arguments in sys.argv after the '--'
args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
```

---

## 2. Importing FreeCAD into External Python Environments

You can `import FreeCAD` into standard Python scripts by adding FreeCAD's `bin` and `lib` directories to `sys.path`:

```python
import sys

# Linux (adjust path to your FreeCAD install)
# sys.path.append("/usr/lib/freecad/lib")
# sys.path.append("/usr/lib/freecad-python3/lib")

# Windows (example default install location)
FREECADPATH = r"C:\Program Files\FreeCAD 1.0\bin"
if FREECADPATH not in sys.path:
    sys.path.append(FREECADPATH)

import FreeCAD as App
import Part

# Initialize headless document
doc = App.newDocument("HeadlessBuild")
box = Part.makeBox(10, 20, 30)
box.exportStep("output.step")
box.exportStl("output.stl")
App.closeDocument(doc.Name)
print("Successfully generated output files headlessly.")
```

---

## 3. Headless Export Recipes

### Export STEP to STL in Batch:
```python
import FreeCAD as App
import Part
import Mesh

def convert_step_to_stl(step_file, stl_file, deflection=0.01):
    doc = App.newDocument("Convert")
    # Read STEP
    shape = Part.Shape()
    shape.read(step_file)
    
    # Mesh with controlled deflection
    mesh = Mesh.Mesh()
    mesh.addFacets(shape.tessellate(deflection))
    mesh.write(stl_file)
    
    App.closeDocument(doc.Name)

# Usage: convert_step_to_stl("input.step", "output.stl", 0.01)
```

---

## 4. FreeCAD RPC / MCP Server Integration

AI coding agents often interact with FreeCAD via an RPC or MCP (Model Context Protocol) server.
When executing code through RPC:
- Always check if an active document exists before creating one.
- Wrap model generation in `try...except` and print clear status messages.
- Always call `doc.recompute()` after geometric changes.
