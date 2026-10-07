"""Render Stage 5 assembly: standard views + area zooms (spec 11.4 verification).

Run inside FreeCAD via the FreeCAD MCP execute_code tool:
    exec(open('E:/Project/EcoBin/scripts/cad/render_stage5.py').read())
"""

import FreeCAD as App
import FreeCADGui as Gui
from PySide.QtGui import QMdiArea

OUT = 'E:/Project/EcoBin/media/renders/'
doc = App.getDocument('EcoBin_Top')
mdi = Gui.getMainWindow().findChild(QMdiArea)
wins = [w for w in mdi.subWindowList() if w.windowTitle().startswith('EcoBin_Top')]
wins[0].show()
mdi.setActiveSubWindow(wins[0])
v = Gui.getDocument('EcoBin_Top').ActiveView
links = [o.Name for o in doc.Objects if o.TypeId == 'App::Link']
print('links: %d' % len(links))


def show_only(keep):
    for n in links:
        doc.getObject(n).Visibility = (n in keep)


def snap(fn, name, w=1200, h=900):
    fn()
    v.fitAll()
    v.saveImage(OUT + name, w, h)
    print('saved ' + name)


BINS = ['L_BinA', 'L_BinB', 'L_BinC', 'L_BinD']
QUADS = ['L_Q1', 'L_Q2', 'L_Q3', 'L_Q4']
CLIPS = ['L_Clip%d' % i for i in range(1, 9)]
STACK = ['L_Tray', 'L_Support', 'L_Flap', 'L_BossA', 'L_BossB', 'L_Guide',
         'L_Servo', 'L_Linkage']

# Standard views, everything visible.
show_only(set(links))
snap(v.viewIsometric, 'EcoBin_Top_iso.png')
snap(v.viewTop, 'EcoBin_Top_top.png')
snap(v.viewFront, 'EcoBin_Top_front.png')
snap(v.viewRear, 'EcoBin_Top_rear.png')
snap(v.viewLeft, 'EcoBin_Top_left.png')
snap(v.viewRight, 'EcoBin_Top_right.png')
snap(v.viewBottom, 'EcoBin_Top_bottom.png')

# Drop station closeups.
show_only(set(BINS + QUADS + STACK + ['L_Gantry']))
snap(v.viewFront, 'zoom_drop_front.png')
snap(v.viewIsometric, 'zoom_drop_iso.png')

# Center stack (drive end).
show_only(set(['L_Base', 'L_Seat', 'L_Mount', 'L_Hub', 'L_Q1', 'L_Magnet', 'L_Hall']))
snap(v.viewIsometric, 'zoom_stack_iso.png')
snap(v.viewBottom, 'zoom_stack_bottom.png')

# Hall sensor + magnet + clips.
show_only(set(['L_Base', 'L_Q1', 'L_Hall', 'L_Magnet', 'L_BinA'] + CLIPS[:2]))
snap(v.viewIsometric, 'zoom_hall_iso.png')

# Front panel + OLED.
show_only(set(['L_Base', 'L_Panel1', 'L_Panel2', 'L_Panel3', 'L_OLED']))
snap(v.viewRear, 'zoom_panel_rear.png')
snap(v.viewFront, 'zoom_panel_front.png')

# Camera hood + LED ring.
show_only(set(['L_Gantry', 'L_Bracket', 'L_CBezel', 'L_Ring', 'L_Tray', 'L_Support']))
snap(v.viewIsometric, 'zoom_hood_iso.png')
snap(v.viewRight, 'zoom_hood_right.png')

show_only(set(links))
print('RENDER DONE')
