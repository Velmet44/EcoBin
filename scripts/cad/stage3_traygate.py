"""EcoBin Stage 3 tray + trapdoor gate (spec 11.4, PR-004..010).

Run inside FreeCAD via the FreeCAD MCP execute_code tool:
    exec(open('E:/Project/EcoBin/scripts/cad/stage3_traygate.py').read())

Creates seven NEW documents (one file per part) in 3D-Design/parts/.
Re-running wipes and rebuilds those seven docs only.

Local coordinates, origin at part center-bottom unless noted.
Load-cell M5 pattern and servo ear slots are placeholders (TBD notes).
"""

import FreeCAD as App
import Part
from FreeCAD import Vector as V

OUT_DIR = 'E:/Project/EcoBin/3D-Design/parts/'

TRAY_OPEN = 80.0   # TrayOpening
FLAP_D = 90.0      # FlapDia
GUIDE_ID = 90.0    # GuideDia
M3 = 3.2
M5 = 5.5


def fresh_doc(name):
    if name in App.listDocuments():
        App.closeDocument(name)
    return App.newDocument(name)


def finish(doc, filename, color=(0.85, 0.85, 0.85)):
    solids = [o.Shape for o in doc.Objects if hasattr(o, 'Shape')]
    bb = solids[0].BoundBox
    for s in solids[1:]:
        bb.add(s.BoundBox)
    assert bb.XLength <= 210.0 and bb.YLength <= 210.0 and bb.ZLength <= 240.0, \
        'PRINT ENVELOPE EXCEEDED: ' + filename
    for o in doc.Objects:
        try:
            o.ViewObject.ShapeColor = color
        except Exception:
            pass
    doc.recompute()
    bad = [o.Name for o in doc.Objects if 'Invalid' in o.State]
    vol = sum(s.Volume for s in solids)
    doc.saveAs(OUT_DIR + filename)
    print('%s volume=%.0f mm3 bbox=%.0fx%.0fx%.0f invalid=%s'
          % (filename, vol, bb.XLength, bb.YLength, bb.ZLength, bad))


def bolt_circle(solid, drill, circle_dia, count, z0, z1):
    import math
    for i in range(count):
        a = math.radians(360.0 * i / count)
        x = circle_dia / 2.0 * math.cos(a)
        y = circle_dia / 2.0 * math.sin(a)
        solid = solid.cut(Part.makeCylinder(drill / 2.0, z1 - z0, V(x, y, z0)))
    return solid


def build_tray():
    doc = fresh_doc('PR005_TrayBody')
    plate = Part.makeBox(140.0, 140.0, 6.0, V(-70.0, -70.0, 0.0))
    plate = plate.cut(Part.makeCylinder(TRAY_OPEN / 2.0, 6.0, V(0, 0, 0)))
    plate = bolt_circle(plate, M3, 120.0, 4, 0.0, 6.0)
    o = doc.addObject('Part::Feature', 'TrayBody')
    o.Shape = plate
    finish(doc, 'PR-005_TrayBody.FCStd')


def build_scale_support():
    doc = fresh_doc('PR006_ScaleSupport')
    # Frame plate: carries tray above, bolts to 5 kg load cell below.
    # Cell M5 pattern placeholder: 2 holes, 60 mm spacing (TBD vs cell drawing).
    plate = Part.makeBox(140.0, 140.0, 8.0, V(-70.0, -70.0, 0.0))
    plate = plate.cut(Part.makeCylinder(TRAY_OPEN / 2.0, 8.0, V(0, 0, 0)))
    plate = bolt_circle(plate, M3, 120.0, 4, 0.0, 8.0)
    for sx in (-30.0, 30.0):
        plate = plate.cut(Part.makeCylinder(M5 / 2.0, 8.0, V(sx, 0.0, 0.0)))
    o = doc.addObject('Part::Feature', 'ScaleSupport')
    o.Shape = plate
    finish(doc, 'PR-006_ScaleSupport.FCStd', color=(0.60, 0.70, 0.85))


def build_flap():
    doc = fresh_doc('PR007_Flap')
    disc = Part.makeCylinder(FLAP_D / 2.0, 4.0, V(0, 0, 0))
    # Two hinge lugs at rim (+/-X), Ø3.2 pin bore along Y.
    for sx in (-1.0, 1.0):
        lug = Part.makeBox(12.0, 10.0, 8.0, V(sx * 45.0 - 6.0, -5.0, 0.0))
        pin = Part.makeCylinder(1.6, 12.0, V(sx * 45.0 - 6.0, -6.0, 4.0))
        pin = pin.rotate(V(sx * 45.0 - 6.0, 0.0, 4.0), V(1, 0, 0), 90.0)
        lug = lug.cut(pin)
        disc = disc.fuse(lug)
    o = doc.addObject('Part::Feature', 'TrapdoorFlap')
    o.Shape = disc
    finish(doc, 'PR-007_TrapdoorFlap.FCStd', color=(1.00, 0.75, 0.35))


def build_hinges():
    doc = fresh_doc('PR008_HingeSupports')
    for i, sx in enumerate((-48.0, 48.0)):
        blk = Part.makeBox(16.0, 14.0, 12.0, V(sx - 8.0, -7.0, 0.0))
        pin = Part.makeCylinder(1.6, 16.0, V(sx - 8.0, -7.0, 8.0))
        pin = pin.rotate(V(sx, 0.0, 8.0), V(1, 0, 0), 90.0)
        blk = blk.cut(pin)
        blk = blk.cut(Part.makeCylinder(M3 / 2.0, 12.0, V(sx - 4.0, 0.0, 0.0)))
        blk = blk.cut(Part.makeCylinder(M3 / 2.0, 12.0, V(sx + 4.0, 0.0, 0.0)))
        o = doc.addObject('Part::Feature', 'HingeSupport_%s' % ('L' if i == 0 else 'R'))
        o.Shape = blk
    finish(doc, 'PR-008_HingeSupports.FCStd')


def build_servo_mount():
    doc = fresh_doc('PR009_ServoMount')
    # MG90S envelope ~23 x 12 x 26; flange ears with Ø2.2 holes (slots TBD).
    plate = Part.makeBox(32.0, 28.0, 4.0, V(-16.0, -14.0, 0.0))
    # Base holes kept clear of the ear footprint (|y| < 10).
    for hx in (-12.0, 12.0):
        for hy in (-5.0, 5.0):
            plate = plate.cut(Part.makeCylinder(M3 / 2.0, 4.0, V(hx, hy, 0.0)))
    for sy in (-1.0, 1.0):
        y0 = 10.0 if sy > 0 else -14.0
        ear = Part.makeBox(32.0, 4.0, 22.0, V(-16.0, y0, 4.0))
        ear = ear.cut(Part.makeCylinder(1.1, 4.0, V(-8.0, sy * 12.0, 12.0)))
        ear = ear.cut(Part.makeCylinder(1.1, 4.0, V(8.0, sy * 12.0, 12.0)))
        plate = plate.fuse(ear)
    o = doc.addObject('Part::Feature', 'ServoMount')
    o.Shape = plate
    finish(doc, 'PR-009_ServoMount.FCStd', color=(0.55, 0.75, 1.00))


def build_linkage():
    doc = fresh_doc('PR010_Linkage')
    bar = Part.makeBox(30.0, 8.0, 4.0, V(-15.0, -4.0, 0.0))
    bar = bar.cut(Part.makeCylinder(1.0, 4.0, V(-11.0, 0.0, 0.0)))
    bar = bar.cut(Part.makeCylinder(1.5, 4.0, V(11.0, 0.0, 0.0)))
    o = doc.addObject('Part::Feature', 'LinkageAdapter')
    o.Shape = bar
    finish(doc, 'PR-010_Linkage.FCStd', color=(1.00, 0.65, 0.25))


def build_guide():
    doc = fresh_doc('PR004_DropGuide')
    tube = Part.makeCylinder(55.0, 40.0, V(0, 0, 0))
    tube = tube.cut(Part.makeCylinder(GUIDE_ID / 2.0, 40.0, V(0, 0, 0)))
    flange = Part.makeCylinder(65.0, 5.0, V(0, 0, 0))
    solid = tube.fuse(flange)
    solid = bolt_circle(solid, M3, 118.0, 4, 0.0, 5.0)
    o = doc.addObject('Part::Feature', 'DropGuide')
    o.Shape = solid
    finish(doc, 'PR-004_DropGuide.FCStd')


build_tray()
build_scale_support()
build_flap()
build_hinges()
build_servo_mount()
build_linkage()
build_guide()
print('Stage3 done')
