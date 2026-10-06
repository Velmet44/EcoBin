# FreeCAD GUI Init Script for DummyWorkbench
# Executed when FreeCAD starts in GUI mode.

import FreeCAD
import FreeCADGui

class DummyWorkbench(FreeCADGui.Workbench):
    MenuText = "Dummy Workbench"
    ToolTip = "Template workbench showing custom commands and menus"
    Icon = """
        /* XPM */
        static const char *dummy_icon[] = {
        "16 16 2 1",
        "  c None",
        ". c #204A87",
        "                ",
        "  ............  ",
        "  ............  ",
        "  ..        ..  ",
        "  ..  ....  ..  ",
        "  ..  ....  ..  ",
        "  ..        ..  ",
        "  ..  ....  ..  ",
        "  ..  ....  ..  ",
        "  ..        ..  ",
        "  ............  ",
        "  ............  ",
        "                ",
        "                ",
        "                ",
        "                "
        };
    """

    def Initialize(self):
        """Register commands, toolbars, and menus."""
        # Append commands to toolbar
        self.appendToolbar("Dummy Tools", ["Dummy_HelloCmd"])
        # Append to main menu
        self.appendMenu("Dummy Workbench", ["Dummy_HelloCmd"])

    def Activated(self):
        FreeCAD.Console.PrintMessage("DummyWorkbench activated.\n")

    def Deactivated(self):
        pass

    def GetClassName(self):
        return "Gui::PythonWorkbench"


class HelloCommand:
    """Sample command demonstrating FreeCADGui command registration."""
    def GetResources(self):
        return {
            'Pixmap': 'Part_Box',
            'MenuText': 'Hello FreeCAD',
            'ToolTip': 'Prints a greeting to the FreeCAD console',
            'Accel': 'Ctrl+Shift+H'
        }

    def Activated(self):
        FreeCAD.Console.PrintMessage("Hello from DummyWorkbench!\n")

    def IsActive(self):
        return True


# Register command and workbench
FreeCADGui.addCommand('Dummy_HelloCmd', HelloCommand())
FreeCADGui.addWorkbench(DummyWorkbench())
