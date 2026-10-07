"""EcoBin Stage 3 tray + trapdoor gate (spec 11.4, PR-004..010).

Run inside FreeCAD via the FreeCAD MCP execute_code tool:
    exec(open('E:/Project/EcoBin/scripts/cad/stage3_traygate.py').read())

Creates seven NEW documents (one file per part) in 3D-Design/parts/.
Re-running wipes and rebuilds those seven docs only.

Drop-path chain (world Z at station): bridge top 248 / flange 248..253 /
support 253..261 / tray 261..267. Flap origin z=241 (pin line z=247);
pin bosses at z=239 (bore z=247). Support M5 pattern TBD vs cell drawing.
"""

import FreeCAD as App
import Part
import math
from FreeCAD import Vector as V

OUT_DIR = 'E:/Project/EcoBin/3D-Design/parts/'

TRAY_OPEN = 76.0   # TrayOpening
FLAP_D = 86.0      # FlapDia (edge-hinged, swings inside guide bore)
GUIDE_ID = 94.0    # GuideDia
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
    # Cell M5 pattern placeholder (TBD vs cell drawing): kept clear of bore.
    plate = Part.makeBox(140.0, 140.0, 8.0, V(-70.0, -70.0, 0.0))
    plate = plate.cut(Part.makeCylinder(TRAY_OPEN / 2.0, 8.0, V(0, 0, 0)))
    plate = bolt_circle(plate, M3, 120.0, 4, 0.0, 8.0)
    for sx in (-45.0, 45.0):
        plate = plate.cut(Part.makeCylinder(M5 / 2.0, 8.0, V(sx, 0.0, 0.0)))
    # Bridge-grid holes mate the support to the gantry bridge.
    for hx in (-52.0, 52.0):
        for hy in (-32.0, 32.0):
            plate = plate.cut(Part.makeCylinder(M3 / 2.0, 8.0, V(hx, hy, 0.0)))
    # Guide-flange pilots (blind-tap M3 from below at assembly).
    for k in range(4):
        a = math.radians(45.0 + 90.0 * k)
        plate = plate.cut(Part.makeCylinder(2.5 / 2.0, 8.0,
                                            V(59.0 * math.cos(a), 59.0 * math.sin(a), 0.0)))
    o = doc.addObject('Part::Feature', 'ScaleSupport')
    o.Shape = plate
    finish(doc, 'PR-006_ScaleSupport.FCStd', color=(0.60, 0.70, 0.85))


def build_flap():
    # Edge-hinged trapdoor, single centered lug + two pin bosses (PR-008).
    # Shared pin line: local y=-40, z=6 (world y=-40, z=249 at assembly).
    # Origin = flap center when closed.
    doc = fresh_doc('PR007_Flap')
    disc = Part.makeCylinder(FLAP_D / 2.0, 4.0, V(0, 0, 0))
    lug = Part.makeBox(8.0, 14.0, 8.0, V(-4.0, -46.0, 0.0))
    disc = disc.fuse(lug)
    pin = Part.makeCylinder(1.6, 60.0, V(-30.0, -40.0, 6.0))
    pin = pin.rotate(V(0, 0, 6.0), V(0, 1, 0), 90.0)
    disc = disc.cut(pin)
    o = doc.addObject('Part::Feature', 'TrapdoorFlap')
    o.Shape = disc
    finish(doc, 'PR-007_TrapdoorFlap.FCStd', color=(1.00, 0.75, 0.35))


def build_hinges():
    # Pin boss inserts press into the guide-tube wall (one each side).
    # Assembly places two links on the pin line; pin = M3 rod (BOM line TBD).
    doc = fresh_doc('PR008_HingeSupports')
    blk = Part.makeBox(6.0, 6.0, 14.0, V(-3.0, -3.0, 0.0))
    blk = blk.rotate(V(0, 0, 0), V(0, 0, 1), 45.0)
    pin = Part.makeCylinder(1.6, 20.0, V(-10.0, 0.0, 8.0))
    pin = pin.rotate(V(0, 0, 8.0), V(0, 1, 0), 90.0)
    blk = blk.cut(pin)
    o = doc.addObject('Part::Feature', 'PinBoss')
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
    # Flange sits on bridge top; tube hangs below into the bridge mouth.
    # Flange bolts (r59 @45 deg) thread up into the support pilots.
    # Assembly places flange base at bridge-top level.
    doc = fresh_doc('PR004_DropGuide')
    tube = Part.makeCylinder(53.0, 18.0, V(0, 0, -18.0))
    tube = tube.cut(Part.makeCylinder(GUIDE_ID / 2.0, 18.0, V(0, 0, -18.0)))
    flange = Part.makeCylinder(65.0, 5.0, V(0, 0, 0))
    flange = flange.cut(Part.makeCylinder(GUIDE_ID / 2.0, 5.0, V(0, 0, 0)))
    solid = tube.fuse(flange)
    for k in range(4):
        a = math.radians(45.0 + 90.0 * k)
        solid = solid.cut(Part.makeCylinder(M3 / 2.0, 5.0,
                                            V(59.0 * math.cos(a), 59.0 * math.sin(a), 0.0)))
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
