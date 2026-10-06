# Creating a New FreeCAD Workbench

A Workbench in FreeCAD packages tools, toolbars, menus, and commands into a cohesive functional unit.

---

## Pure Python vs C++ Workbench

- **Pure Python Workbench**: Easiest to write, distribute, and maintain. Can be installed directly via the Addon Manager without compilation.
- **C++ / Hybrid Workbench**: Necessary when integrating custom C++ libraries, writing high-performance algorithms, or extending OpenCASCADE core classes.

---

## Directory Layout of a Python Workbench

Place your workbench folder in:
- **User directory**: `~/.FreeCAD/Mod/MyWorkbench/` (Linux/macOS) or `%APPDATA%\FreeCAD\Mod\MyWorkbench\` (Windows).
- **Core source tree**: `src/Mod/MyWorkbench/`.

```
MyWorkbench/
├── Init.py          # Loaded on FreeCAD startup (Headless & GUI)
├── InitGui.py       # Loaded when FreeCAD starts in GUI mode
├── Resources/
│   └── icons/
│       └── MyWorkbench.svg
└── commands/
    ├── __init__.py
    └── BoxTool.py
```

---

## 1. `Init.py` (Headless Initialization)

Runs when FreeCAD starts (even in command line / headless mode):

```python
# FreeCAD init script of the MyWorkbench module
# Append module path or initialize non-GUI services
import FreeCAD
```

---

## 2. `InitGui.py` (GUI Workbench Registration)

FreeCAD discovers workbenches by scanning for classes derived from `FreeCADGui.Workbench`:

```python
import FreeCAD
import FreeCADGui
import os

class MyCustomWorkbench(FreeCADGui.Workbench):
    """Custom FreeCAD Workbench definition."""
    
    MenuText = "My Workbench"
    ToolTip = "A specialized CAD extension workbench"
    Icon = """
        /* XPM icon or path to SVG/PNG */
    """

    def Initialize(self):
        """Executed when the workbench is activated for the first time."""
        import commands.BoxTool # Import custom commands
        
        # Define Toolbars
        self.appendToolbar("Modeling Tools", ["MyWorkbench_BoxCmd", "MyWorkbench_SphereCmd"])
        
        # Define Menus
        self.appendMenu("My Tools", ["MyWorkbench_BoxCmd", "MyWorkbench_SphereCmd"])

    def Activated(self):
        """Executed when switching into this workbench."""
        FreeCAD.Console.PrintMessage("MyWorkbench activated.\n")

    def Deactivated(self):
        """Executed when switching away from this workbench."""
        pass

    def ContextMenu(self, recipient):
        """Add items to the 3D view right-click context menu."""
        self.appendContextMenu("My Tools", ["MyWorkbench_BoxCmd"])

    def GetClassName(self):
        return "Gui::PythonWorkbench"

# Register the workbench with FreeCAD
FreeCADGui.addWorkbench(MyCustomWorkbench())
```

---

## 3. Registering Commands

In `commands/BoxTool.py`:

```python
import FreeCAD as App
import FreeCADGui as Gui
import Part

class BoxToolCommand:
    def GetResources(self):
        return {
            'Pixmap': 'Part_Box',
            'MenuText': 'Create Parametric Box',
            'ToolTip': 'Creates a custom box in the active document',
            'Accel': 'Ctrl+Shift+X'
        }

    def Activated(self):
        doc = App.ActiveDocument or App.newDocument()
        box = doc.addObject("Part::Box", "CustomBox")
        box.Length = 50
        box.Width = 50
        box.Height = 50
        doc.recompute()

    def IsActive(self):
        return App.ActiveDocument is not None

Gui.addCommand('MyWorkbench_BoxCmd', BoxToolCommand())
```
