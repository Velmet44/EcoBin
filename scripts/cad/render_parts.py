"""Refresh per-part renders from current on-disk files (Stage 5 media roll-up).

Run inside FreeCAD via the FreeCAD MCP execute_code tool:
    exec(open('E:/Project/EcoBin/scripts/cad/render_parts.py').read())
"""

import os
import FreeCAD as App
import FreeCADGui as Gui
from PySide.QtGui import QMdiArea

PARTS = 'E:/Project/EcoBin/3D-Design/parts/'
OUT = 'E:/Project/EcoBin/media/renders/'
mdi = Gui.getMainWindow().findChild(QMdiArea)

files = sorted(f for f in os.listdir(PARTS) if f.endswith('.FCStd'))
print('parts: %d' % len(files))
for fname in files:
    base = fname[:-len('.FCStd')]
    try:
        d = App.openDocument(PARTS + fname)
    except Exception as e:
        print(fname + ' OPEN-ERR ' + str(e))
        continue
    for w in mdi.subWindowList():
        if d.Name in w.windowTitle() or base in w.windowTitle():
            w.show()
            mdi.setActiveSubWindow(w)
            break
    try:
        v = Gui.getDocument(d.Name).ActiveView
        v.viewIsometric()
        v.fitAll()
        v.saveImage(OUT + base + '.png', 900, 700)
        print('saved ' + base + '.png')
    except Exception as e:
        print(fname + ' SNAP-ERR ' + str(e))
print('PART RENDERS DONE')
