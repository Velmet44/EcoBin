# FreeCAD PySide & GUI Integration

FreeCAD uses **Qt** (via **PySide**) for its graphical interface and **Coin3D** (via **Pivy**) for 3D OpenGL scene graph rendering.

---

## 1. Accessing FreeCAD Main Window and Widgets

```python
from PySide import QtGui, QtCore
# In Qt5/Qt6 environments:
# from PySide2 import QtWidgets, QtCore or PySide6

import FreeCADGui as Gui

# Get main application window
main_win = Gui.getMainWindow()

# Simple Message Box
QtGui.QMessageBox.information(main_win, "Title", "Operation finished successfully!")

# Simple Input Dialog
val, ok = QtGui.QInputDialog.getDouble(main_win, "Set Radius", "Enter radius in mm:", 10.0, 0.1, 1000.0, 2)
if ok:
    print(f"User entered: {val}")
```

---

## 2. Registering a Custom GUI Command

Commands appear in menus, toolbars, and shortcut managers.

```python
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui

class QuickBoxCommand:
    """Command that creates a 20x20x20 box."""
    def GetResources(self):
        return {
            'Pixmap': 'Part_Box', # Built-in icon name or path to .svg/.png
            'MenuText': 'Create Quick Box',
            'ToolTip': 'Creates a standard 20mm test box',
            'Accel': 'Ctrl+Shift+B'
        }

    def Activated(self):
        doc = App.ActiveDocument or App.newDocument()
        import Part
        box = doc.addObject("Part::Box", "QuickBox")
        box.Length = 20
        box.Width = 20
        box.Height = 20
        doc.recompute()
        if App.GuiUp:
            Gui.ActiveDocument.ActiveView.fitAll()

    def IsActive(self):
        # Command enabled if there is an active document
        return App.ActiveDocument is not None

# Register command with the GUI
Gui.addCommand('QuickBox_Cmd', QuickBoxCommand())
```

---

## 3. Creating Custom Task Panels

Task Panels sit in the left sidebar (Combo View / Task tab) and provide an interactive workflow without blocking modal dialogs.

```python
from PySide import QtGui
import FreeCADGui as Gui

class BoxGeneratorTaskPanel:
    def __init__(self):
        self.form = QtGui.QWidget()
        layout = QtGui.QVBoxLayout(self.form)
        
        layout.addWidget(QtGui.QLabel("Box Length:"))
        self.length_spin = QtGui.QDoubleSpinBox()
        self.length_spin.setValue(50.0)
        layout.addWidget(self.length_spin)

    def accept(self):
        # Called when user clicks "OK" in the Task Panel
        length = self.length_spin.value()
        # perform CAD operations...
        Gui.Control.closeDialog()
        return True

    def reject(self):
        # Called when user clicks "Cancel"
        Gui.Control.closeDialog()
        return True

    def getStandardButtons(self):
        # Return standard OK and Cancel buttons
        return int(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)

# To open panel:
# panel = BoxGeneratorTaskPanel()
# Gui.Control.showDialog(panel)
```

---

## 4. 3D Scene Graph Customization (Coin3D / Pivy)

To draw custom temporary overlays, markers, or lines in the 3D viewport:

```python
import pivy.coin as coin
import FreeCADGui as Gui

# Access the active viewer's scene graph
sg = Gui.ActiveDocument.ActiveView.getSceneGraph()

# Create Coin nodes
sep = coin.SoSeparator()
col = coin.SoBaseColor()
col.rgb = (1.0, 0.5, 0.0) # Orange color

coords = coin.SoCoordinate3()
coords.point.setValues(0, 2, [[0, 0, 0], [50, 50, 50]])

line = coin.SoLineSet()
line.numVertices.setValue(2)

sep.addChild(col)
sep.addChild(coords)
sep.addChild(line)

# Add to scene
sg.addChild(sep)

# Remove when done:
# sg.removeChild(sep)
```
