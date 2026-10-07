"""EcoBin Stage 1 frame / bearing / motor-mount parts (spec 11.4, PR-001/012/013/019).

Run inside FreeCAD via the FreeCAD MCP execute_code tool:
    exec(open('E:/Project/EcoBin/scripts/cad/stage1_frame.py').read())

Creates four NEW documents (one file per part) and saves them into
3D-Design/parts/. Re-running wipes and rebuilds those four docs only.

Conventions:
- Each part is modeled in LOCAL coordinates (origin = its mounting
  interface). The Z-stack is resolved later in EcoBin_Top assembly.
- Interface diameters/patterns are real; heights marked TBD follow the
  bearing + coupling picks (both still unpriced in the BOM).
- Placeholder values below mirror 00_Master Params unless marked TBD.
"""

import FreeCAD as App
import Part
from FreeCAD import Vector as V

OUT_DIR = 'E:/Project/EcoBin/3D-Design/parts/'

# ---- mirrored master values (see 00_Master Params) ----
OVERALL_DIA = 300.0
ROTOR_DIA = 280.0  # informational; rotor quadrants are built in stage2
BASE_THK = 20.0
# ---- TBD placeholders (bearing + coupling not yet selected) ----
BRG_SEAT_BORE = 70.0   # TBD: turntable bearing OD (BOM-020 open)
SEAT_H = 40.0          # boss top lands exactly on carrier bottom (20+8+40=68);
                       # TBD bearing occupies the r35 bore below the hub barrel
NEMA_BCD = 31.0        # NEMA-17 standard M3 pattern
NEMA_BODY = 42.0
MOTOR_SHAFT = 5.0      # NEMA-17 standard shaft dia
M3_CLEAR = 3.2
M3_TAP_DRILL = 2.5


def fresh_doc(name):
    if name in App.listDocuments():
        App.closeDocument(name)
    return App.newDocument(name)


def finish(doc, filename, color=(0.85, 0.85, 0.85)):
    for o in doc.Objects:
        try:
            o.ViewObject.ShapeColor = color
        except Exception:
            pass
    doc.recompute()
    bad = [o.Name for o in doc.Objects if 'Invalid' in o.State]
    doc.saveAs(OUT_DIR + filename)
    print('%s -> %s, invalid: %s' % (doc.Name, filename, bad))


def hole_plate(solid, dia, circle_dia, count, z0=0.0, z1=None, drill=M3_CLEAR):
    """Cut `count` vertical holes on a bolt circle. Returns new shape."""
    import math
    h = (z1 if z1 is not None else 1000.0) - z0
    for i in range(count):
        a = math.radians(360.0 * i / count)
        x = circle_dia / 2.0 * math.cos(a)
        y = circle_dia / 2.0 * math.sin(a)
        tool = Part.makeCylinder(drill / 2.0, h, V(x, y, z0))
        solid = solid.cut(tool)
    return solid


def build_base():
    doc = fresh_doc('PR001_BaseFrame')
    disc = Part.makeCylinder(OVERALL_DIA / 2.0, BASE_THK, V(0, 0, 0))
    disc = disc.cut(Part.makeCylinder(30.0, BASE_THK, V(0, 0, 0)))  # hub/wiring clearance
    disc = hole_plate(disc, M3_CLEAR, 280.0, 6, 0.0, BASE_THK)      # spare trim screws
    disc = hole_plate(disc, M3_CLEAR, 120.0, 4, 0.0, BASE_THK)      # bearing-seat bolts
    # Gantry post feet (r146, +/-14 deg, tangent +/-5), skirt panels
    # ((+-30, 146) at 90/180/270), hall stalk (91/109, 0), feet (r120 @45).
    import math as _m
    pts = []
    for sa in (14.0, -14.0):
        a = _m.radians(sa)
        pts.append((146.0 * _m.cos(a), 146.0 * _m.sin(a)))  # gantry post M3 from below
    for ang in (90.0, 180.0, 270.0):
        for lx in (-30.0, 30.0):
            ra = _m.radians(ang - 90.0)  # match panel rotation R(ang-90) in stage4
            x, y = lx, 146.0
            pts.append((x * _m.cos(ra) - y * _m.sin(ra),
                        x * _m.sin(ra) + y * _m.cos(ra)))
    pts += [(92.0, 0.0), (108.0, 0.0)]  # hall stalk base
    pts += [(20.0, 20.0), (20.0, -20.0), (-20.0, 20.0), (-20.0, -20.0)]  # stepper-mount M3
    for k in range(4):
        fa = _m.radians(45.0 + 90.0 * k)
        pts.append((120.0 * _m.cos(fa), 120.0 * _m.sin(fa)))
    for (x, y) in pts:
        disc = disc.cut(Part.makeCylinder(M3_CLEAR / 2.0, BASE_THK, V(x, y, 0.0)))
    o = doc.addObject('Part::Feature', 'BaseFrame')
    o.Shape = disc
    finish(doc, 'PR-001_BaseFrame.FCStd')


def build_seat():
    doc = fresh_doc('PR013_BearingSeat')
    flange = Part.makeCylinder(70.0, 8.0, V(0, 0, 0))
    boss = Part.makeCylinder(50.0, SEAT_H, V(0, 0, 8.0))
    solid = flange.fuse(boss)
    solid = solid.cut(Part.makeCylinder(BRG_SEAT_BORE / 2.0, SEAT_H + 8.0, V(0, 0, 0)))
    solid = hole_plate(solid, M3_CLEAR, 120.0, 4, 0.0, 8.0)  # matches base pattern
    o = doc.addObject('Part::Feature', 'BearingSeat')
    o.Shape = solid
    finish(doc, 'PR-013_BearingSeat.FCStd')


def build_stepper_mount():
    doc = fresh_doc('PR019_StepperMount')
    plate = Part.makeBox(50.0, 50.0, 6.0, V(-25.0, -25.0, 0.0))
    plate = plate.cut(Part.makeCylinder(12.0, 6.0, V(0, 0, 0)))  # motor boss clearance
    for hx in (-20.0, 20.0):                                    # frame attachment
        for hy in (-20.0, 20.0):
            plate = plate.cut(Part.makeCylinder(M3_CLEAR / 2.0, 6.0, V(hx, hy, 0.0)))
    # NEMA-17 M3 pattern on 31 mm BCD: holes at (±15.5, ±15.5).
    import math
    half = NEMA_BCD / 2.0  # 31 mm square pattern -> +/-15.5 mm
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            tool = Part.makeCylinder(M3_CLEAR / 2.0, 6.0, V(sx * half, sy * half, 0.0))
            plate = plate.cut(tool)
    o = doc.addObject('Part::Feature', 'StepperMount')
    o.Shape = plate
    finish(doc, 'PR-019_StepperMount.FCStd',
           color=(0.55, 0.75, 1.00))


def build_hub():
    doc = fresh_doc('PR012_Hub')
    flange = Part.makeCylinder(20.0, 6.0, V(0, 0, 0))
    barrel = Part.makeCylinder(12.5, 20.0, V(0, 0, -20.0))
    solid = flange.fuse(barrel)
    solid = solid.cut(Part.makeCylinder(MOTOR_SHAFT / 2.0, 26.0, V(0, 0, -20.0)))
    solid = hole_plate(solid, M3_CLEAR, 34.0, 4, 0.0, 6.0)  # carrier bolts (match Q r17)
    # Radial set-screw hole (drill; tap M3 at build): along +X at barrel mid.
    tool = Part.makeCylinder(M3_TAP_DRILL / 2.0, 25.0, V(0, 0, -10.0))
    tool = tool.rotate(V(0, 0, -10.0), V(0, 1, 0), 90.0)
    solid = solid.cut(tool)
    o = doc.addObject('Part::Feature', 'Hub')
    o.Shape = solid
    finish(doc, 'PR-012_Hub.FCStd', color=(1.00, 0.75, 0.35))


build_base()
build_seat()
build_stepper_mount()
build_hub()
print('Stage1 done')
