"""EcoBin Stage 2 carousel + chambers (spec 11.4, PR-011/014-018).

Run inside FreeCAD via the FreeCAD MCP execute_code tool:
    exec(open('E:/Project/EcoBin/scripts/cad/stage2_carousel.py').read())

Creates nine NEW documents (one file per part) in 3D-Design/parts/.
Re-running wipes and rebuilds those nine docs only.

Conventions: local coordinates, origin at part center-bottom.
Q1 centered on index-0 (+X); Q2..Q4 are 90 deg rotations (symmetric).
Chambers A..D are identical solids (letter labels added at print release).
Pocket Ø114 x 5 in carrier matches bin flange Ø112 x 5.
Joint M3 holes sit ON quadrant edges so neighbours pair into full holes.
"""

import FreeCAD as App
import Part
import math
from FreeCAD import Vector as V

OUT_DIR = 'E:/Project/EcoBin/3D-Design/parts/'

# ---- mirrored master values ----
ROTOR_R = 140.0    # RotorDia 280 / 2 (rim kept >=3 mm past bin pocket)
R_ST = 80.0        # R_station
CARRIER_T = 12.0   # CarrierThk
MOUTH = 100.0      # MouthDia / ChamberDia
CHAMBER_H = 150.0  # ChamberH
WALL = 3.0         # FDM wall for shared-lab printer
FLANGE_D = 110.0   # bin foot flange (pocket gets +2 drop-in clearance)
FLANGE_T = 5.0
M3 = 3.2           # clearance drill (tap at build where noted)


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
    solid = doc.Objects[0].Shape
    bb = solid.BoundBox
    assert bb.XLength <= 210.0 and bb.YLength <= 210.0 and bb.ZLength <= 240.0, \
        'PRINT ENVELOPE EXCEEDED: ' + filename
    doc.saveAs(OUT_DIR + filename)
    print('%s volume=%.0f mm3 bbox=%.0fx%.0fx%.0f invalid=%s'
          % (filename, solid.Volume, bb.XLength, bb.YLength, bb.ZLength, bad))


def polar(r, deg):
    a = math.radians(deg)
    return (r * math.cos(a), r * math.sin(a))


def build_quadrant(docname, filename, center_deg):
    doc = fresh_doc(docname)
    sec = Part.makeCylinder(ROTOR_R, CARRIER_T, V(0, 0, 0), V(0, 0, 1), 90.0)
    sec = sec.rotate(V(0, 0, 0), V(0, 0, 1), center_deg - 45.0)
    sec = sec.cut(Part.makeCylinder(13.0, CARRIER_T, V(0, 0, 0)))  # hub barrel clearance
    hx, hy = polar(17.0, center_deg)                            # hub flange bolt
    sec = sec.cut(Part.makeCylinder(M3 / 2.0, CARRIER_T, V(hx, hy, 0)))
    px, py = polar(R_ST, center_deg)                               # bin pocket
    sec = sec.cut(Part.makeCylinder(FLANGE_D / 2.0 + 1.0, FLANGE_T,
                                    V(px, py, CARRIER_T - FLANGE_T)))
    for s in (-45.0, 45.0):                                       # joint half-holes
        qx, qy = polar(115.0, center_deg + s)
        sec = sec.cut(Part.makeCylinder(M3 / 2.0, CARRIER_T, V(qx, qy, 0)))
    o = doc.addObject('Part::Feature', 'CarrierQuadrant')
    o.Shape = sec
    finish(doc, filename, color=(0.60, 0.70, 0.85))


def build_chamber(docname, filename):
    doc = fresh_doc(docname)
    outer = Part.makeCylinder(MOUTH / 2.0, CHAMBER_H, V(0, 0, 0))
    inner = Part.makeCylinder(MOUTH / 2.0 - WALL, CHAMBER_H - WALL, V(0, 0, WALL))
    body = outer.cut(inner)
    body = body.fuse(Part.makeCylinder(FLANGE_D / 2.0, FLANGE_T, V(0, 0, 0)))
    o = doc.addObject('Part::Feature', 'ChamberBin')
    o.Shape = body
    finish(doc, filename, color=(0.85, 0.85, 0.85))


def build_clips():
    doc = fresh_doc('PR018_Clips')
    base = Part.makeBox(20.0, 12.0, 4.0, V(0, 0, 0))
    base = base.cut(Part.makeCylinder(M3 / 2.0, 4.0, V(10.0, 6.0, 0.0)))
    upright = Part.makeBox(4.0, 12.0, 14.0, V(0, 0, 4.0))
    o = doc.addObject('Part::Feature', 'RetentionClip')
    o.Shape = base.fuse(upright)
    finish(doc, 'PR-018_Clips.FCStd', color=(1.00, 0.65, 0.25))


build_quadrant('PR011_Carrier_Q1', 'PR-011_Carrier_Q1.FCStd', 0.0)
build_quadrant('PR011_Carrier_Q2', 'PR-011_Carrier_Q2.FCStd', 90.0)
build_quadrant('PR011_Carrier_Q3', 'PR-011_Carrier_Q3.FCStd', 180.0)
build_quadrant('PR011_Carrier_Q4', 'PR-011_Carrier_Q4.FCStd', 270.0)
build_chamber('PR014_Chamber_A', 'PR-014_Chamber_A.FCStd')
build_chamber('PR015_Chamber_B', 'PR-015_Chamber_B.FCStd')
build_chamber('PR016_Chamber_C', 'PR-016_Chamber_C.FCStd')
build_chamber('PR017_Chamber_D', 'PR-017_Chamber_D.FCStd')
build_clips()
print('Stage2 done')
