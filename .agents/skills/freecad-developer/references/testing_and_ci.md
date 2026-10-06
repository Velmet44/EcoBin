# FreeCAD Testing & Packaging Guide

FreeCAD includes both C++ and Python automated test frameworks.

---

## 1. Running Unit Tests

### A. Via Command Line (Headless):
```bash
# Run all built-in test suites
freecadcmd -t 0

# Run a specific test suite (e.g. Part or Sketcher)
freecadcmd -t TestPartApp
freecadcmd -t TestSketcherApp
```

### B. Inside Python or Test Scripts:
```python
import FreeCAD
import FreeCADTest

# Run all test suites
FreeCADTest.runAll()
```

### C. Writing a Custom Python Unit Test:
Place tests inside `src/Mod/<Workbench>/Test<Workbench>App.py`:

```python
import unittest
import FreeCAD as App
import Part

class TestMyFeature(unittest.TestCase):
    def setUp(self):
        self.doc = App.newDocument("TestDoc")

    def tearDown(self):
        App.closeDocument(self.doc.Name)

    def test_box_volume(self):
        box = self.doc.addObject("Part::Box", "Box")
        box.Length = 10
        box.Width = 20
        box.Height = 30
        self.doc.recompute()
        
        self.assertAlmostEqual(box.Shape.Volume, 6000.0, places=3)

if __name__ == "__main__":
    unittest.main()
```

---

## 2. Packaging Distributions

FreeCAD is distributed across multiple formats:

### Linux:
- **AppImage**: Bundles all dependencies (OCCT, Qt, Python) in a single portable executable. Built via `conda-pack` or Docker recipes in `FreeCAD/FreeCAD-Bundle`.
- **Flatpak**: Available on Flathub (`org.freecadweb.FreeCAD`).
- **Debian / Ubuntu PPA**: Deb packaging recipes in `debian/` directory.

### Windows:
- **NSIS Installer**: Standard `.exe` installer bundling Conda environment and FreeCAD binaries.
- **7z Portable Archive**: Zero-install standalone zip archive.

### macOS:
- **DMG**: Signed universal/arm64 `.dmg` bundle embedding Python and Qt frameworks.
