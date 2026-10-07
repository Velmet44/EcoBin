"""EcoBin Stage 4 mounts + upper structure (PR-002/003/020-029).

Run inside FreeCAD via the FreeCAD MCP execute_code tool:
    exec(open('E:/Project/EcoBin/scripts/cad/stage4_upper.py').read())

Creates twelve NEW documents (one file per part) in 3D-Design/parts/.
Re-running wipes and rebuilds those twelve docs only.

Frames: PR-003 gantry, PR-020 bracket, PR-022 ring, PR-023 stalk and
PR-002 panels are built in MASTER-frame coordinates (position-critical).
Small parts (bezels, holder, tray, cover, feet, clips) use local origins.

TBD notes: camera hole pattern, OLED dims, sensor module strap, tray
sandwich order (resolved at Stage 5 assembly), chamber letter labels.
"""

import FreeCAD as App
import Part
import math
from FreeCAD import Vector as V

OUT_DIR = 'E:/Project/EcoBin/3D-Design/parts/'
M3 = 3.2


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


def polar(r, deg):
    a = math.radians(deg)
    return (r * math.cos(a), r * math.sin(a))


def vhole(solid, drill, x, y, z0, z1):
    return solid.cut(Part.makeCylinder(drill / 2.0, z1 - z0, V(x, y, z0)))


def build_gantry():
    # PR-003: 2 posts + bridge fused = one printable gantry (master frame).
    doc = fresh_doc('PR003_Gantry')
    parts = []
    for sa in (14.0, -14.0):
        cx, cy = polar(146.0, sa)
        post = Part.makeCylinder(4.0, 213.0, V(cx, cy, 20.0))
        post = post.cut(Part.makeCylinder(1.25, 15.0, V(cx, cy, 20.0)))  # M3 tap from below
        post = post.cut(Part.makeCylinder(2.1, 12.0, V(cx, cy, 221.0)))  # M3 insert top
        parts.append(post)
    bridge = Part.makeBox(130.0, 90.0, 15.0, V(20.0, -45.0, 233.0))
    bridge = bridge.cut(Part.makeCylinder(55.0, 15.0, V(80.0, 0.0, 233.0)))
    for (hx, hy) in [(141.65, 35.37), (141.65, -35.37),
                     (28.0, 32.0), (28.0, -32.0), (132.0, 32.0), (132.0, -32.0),
                     (131.0, 25.0), (131.0, -25.0), (141.0, 25.0), (141.0, -25.0)]:
        bridge = vhole(bridge, M3, hx, hy, 233.0, 248.0)
    solid = parts[0].fuse(parts[1]).fuse(bridge)
    o = doc.addObject('Part::Feature', 'Gantry')
    o.Shape = solid
    finish(doc, 'PR-003_Gantry.FCStd', color=(0.60, 0.70, 0.85))


def panel_solid():
    wall = Part.makeBox(170.0, 4.0, 60.0, V(-85.0, 143.0, 20.0))
    flange = Part.makeBox(170.0, 8.0, 4.0, V(-85.0, 142.0, 20.0))
    solid = wall.fuse(flange)
    for hx in (-30.0, 30.0):
        solid = vhole(solid, M3, hx, 146.0, 20.0, 24.0)
    return solid


def build_panels():
    # PR-002: 3 skirt panels (open frame; drop station stays open).
    # One file each: ring-arranged panels cannot share a printable file.
    # Panel_3 (front, -Y) gets the OLED window; the bezel seats from inside.
    base = panel_solid()
    for i, ang in enumerate((90.0, 180.0, 270.0)):
        d = fresh_doc('PR002_Panel_%d' % (i + 1))
        shape = base.rotated(V(0, 0, 0), V(0, 0, 1), ang - 90.0)
        if i == 2:
            shape = shape.cut(Part.makeBox(34.0, 10.0, 18.0, V(-17.0, -150.0, 41.0)))
        o = d.addObject('Part::Feature', 'SkirtPanel')
        o.Shape = shape
        finish(d, 'PR-002_Panel_%d.FCStd' % (i + 1))


def build_camera_bracket():
    # PR-020: foot + vertical + top + 2 gussets, fused (master frame).
    # Foot keeps inside the base silhouette (corner r149.7 < 150).
    doc = fresh_doc('PR020_CameraBracket')
    foot = Part.makeBox(22.0, 66.0, 4.0, V(124.0, -33.0, 248.0))
    for (hx, hy) in [(131.0, 25.0), (131.0, -25.0), (141.0, 25.0), (141.0, -25.0)]:
        foot = vhole(foot, M3, hx, hy, 248.0, 252.0)
    vert = Part.makeBox(4.0, 60.0, 92.0, V(138.0, -30.0, 252.0))
    top = Part.makeBox(97.0, 60.0, 4.0, V(45.0, -30.0, 340.0))
    top = top.cut(Part.makeCylinder(10.0, 4.0, V(80.0, 0.0, 340.0)))
    for (hx, hy) in [(64.0, 11.0), (64.0, -11.0), (96.0, 11.0), (96.0, -11.0)]:
        top = vhole(top, 2.2, hx, hy, 340.0, 344.0)  # camera pattern TBD
    tri = Part.Face(Part.Wire(Part.makePolygon(
        [V(138.0, 252.0, 0), V(138.0, 340.0, 0), V(100.0, 252.0, 0)], True)))
    g1 = tri.extrude(V(0, 0, 4.0))
    g1 = g1.rotate(V(0, 0, 0), V(1, 0, 0), 90.0).translate(V(0, 28.0, 0))
    g2 = tri.extrude(V(0, 0, 4.0))
    g2 = g2.rotate(V(0, 0, 0), V(1, 0, 0), 90.0).translate(V(0, -24.0, 0))
    o = doc.addObject('Part::Feature', 'CameraBracket')
    o.Shape = foot.fuse(vert).fuse(top).fuse(g1).fuse(g2)
    finish(doc, 'PR-020_CameraBracket.FCStd', color=(0.55, 0.75, 1.00))


def build_camera_bezel():
    doc = fresh_doc('PR021_CameraBezel')
    solid = Part.makeBox(40.0, 40.0, 3.0, V(-20.0, -20.0, 0.0))
    solid = solid.cut(Part.makeCylinder(7.0, 3.0, V(0, 0, 0)))
    for hx in (-16.0, 16.0):
        for hy in (-16.0, 16.0):
            solid = vhole(solid, 2.2, hx, hy, 0.0, 3.0)
    o = doc.addObject('Part::Feature', 'CameraBezel')
    o.Shape = solid
    finish(doc, 'PR-021_CameraBezel.FCStd')


def build_led_ring():
    # PR-022: LED annulus on the drop axis + 2 arms to the bracket (master frame).
    # Ring outer r50 stops 8 mm short of the bracket vertical (x138); only the
    # arms touch it. Bore r40 still passes the 60 mm item.
    doc = fresh_doc('PR022_LEDRing')
    ring = Part.makeCylinder(50.0, 6.0, V(80.0, 0.0, 300.0))
    ring = ring.cut(Part.makeCylinder(40.0, 6.0, V(80.0, 0.0, 300.0)))
    for k in range(6):
        lx, ly = polar(45.0, 60.0 * k)
        ring = ring.cut(Part.makeCylinder(2.6, 6.0, V(80.0 + lx, ly, 300.0)))
    for sy in (6.0, -14.0):
        arm = Part.makeBox(12.0, 8.0, 4.0, V(126.0, sy, 298.0))
        ring = ring.fuse(arm)
    o = doc.addObject('Part::Feature', 'LEDRing')
    o.Shape = ring
    finish(doc, 'PR-022_LEDRing.FCStd', color=(1.00, 0.85, 0.40))


def build_hall_bracket():
    # Base-mounted stalk at (100,0); sensor head faces UP at the
    # under-carrier magnet (module face 4 mm below magnet face).
    # Master-frame coordinates; base slots allow radial adjustment.
    doc = fresh_doc('PR023_HallBracket')
    base = Part.makeBox(30.0, 20.0, 4.0, V(85.0, -10.0, 20.0))
    for cx in (92.0, 108.0):  # slots contain the base studs, +/-5 radial play
        slot = Part.makeBox(10.0, 3.2, 4.0, V(cx - 5.0, -1.6, 20.0))
        slot = slot.fuse(Part.makeCylinder(1.6, 4.0, V(cx - 5.0, 0.0, 20.0)))
        slot = slot.fuse(Part.makeCylinder(1.6, 4.0, V(cx + 5.0, 0.0, 20.0)))
        base = base.cut(slot)
    stalk = Part.makeBox(10.0, 10.0, 28.0, V(95.0, -5.0, 24.0))
    head = Part.makeBox(24.0, 16.0, 4.0, V(88.0, -8.0, 52.0))
    head = vhole(head, 2.5, 94.0, 0.0, 52.0, 56.0)
    head = vhole(head, 2.5, 106.0, 0.0, 52.0, 56.0)
    o = doc.addObject('Part::Feature', 'HallBracket')
    o.Shape = base.fuse(stalk).fuse(head)
    finish(doc, 'PR-023_HallBracket.FCStd', color=(0.60, 0.85, 0.60))


def build_magnet_holder():
    # Hangs below Q1 carrier at (100,0); origin = carrier-bottom contact.
    # Magnet face 4 mm above the sensor module face. Screws M3x8 max
    # (tips stop 5 mm below pocket floor and bin flange).
    doc = fresh_doc('PR024_MagnetHolder')
    disc = Part.makeCylinder(16.0, 3.0, V(0, 0, -3.0))
    cup = Part.makeCylinder(7.0, 4.0, V(0, 0, -6.0))
    cup = cup.cut(Part.makeCylinder(2.6, 3.0, V(0, 0, -6.0)))
    solid = disc.fuse(cup)
    for hx in (-12.0, 12.0):
        solid = vhole(solid, M3, hx, 0.0, -3.0, 0.0)
    solid = solid.translate(V(100.0, 0.0, 0.0))
    o = doc.addObject('Part::Feature', 'MagnetHolder')
    o.Shape = solid
    finish(doc, 'PR-024_MagnetHolder.FCStd', color=(1.00, 0.65, 0.25))


def build_oled_bezel():
    # PR-025: 1.3 in OLED frame; window + hole pattern TBD vs exact display.
    doc = fresh_doc('PR025_OLEDBezel')
    solid = Part.makeBox(48.0, 44.0, 5.0, V(-24.0, -22.0, 0.0))
    solid = solid.cut(Part.makeBox(32.0, 18.0, 5.0, V(-16.0, -9.0, 0.0)))
    for hx in (-20.0, 20.0):
        for hy in (-18.0, 18.0):
            solid = vhole(solid, 2.2, hx, hy, 0.0, 5.0)
    o = doc.addObject('Part::Feature', 'OLEDBezel')
    o.Shape = solid
    finish(doc, 'PR-025_OLEDBezel.FCStd')


def build_elex_tray():
    # PR-026: under-base electronics tray (local origin, assembly at z=-20).
    # Center bore reserves the stepper-motor cavity (motor TBD, mount at z-6).
    doc = fresh_doc('PR026_ElexTray')
    tray = Part.makeBox(200.0, 160.0, 4.0, V(-100.0, -80.0, 0.0))
    tray = tray.cut(Part.makeCylinder(30.0, 4.0, V(0, 0, 0)))
    for hx in (-85.0, 85.0):
        for hy in (-65.0, 65.0):
            tray = vhole(tray, M3, hx, hy, 0.0, 4.0)
            tray = tray.fuse(Part.makeCylinder(5.0, 16.0, V(hx, hy, 4.0)))
    o = doc.addObject('Part::Feature', 'ElexTray')
    o.Shape = tray
    finish(doc, 'PR-026_ElexTray.FCStd', color=(0.60, 0.70, 0.85))


def build_bottom_cover():
    # PR-027: 4 quarter-discs (halves still span 280), one file each.
    # Center bore continues the motor cavity; per-quarter bolt hits a foot.
    for i, rot in enumerate((0.0, 90.0, 180.0, 270.0)):
        d = fresh_doc('PR027_CoverQ_%d' % (i + 1))
        q = Part.makeCylinder(140.0, 3.0, V(0, 0, 0), V(0, 0, 1), 90.0)
        q = q.cut(Part.makeCylinder(30.0, 3.0, V(0, 0, 0)))
        q = q.rotate(V(0, 0, 0), V(0, 0, 1), rot)
        hx, hy = polar(120.0, 45.0 + rot)
        q = vhole(q, M3, hx, hy, 0.0, 3.0)
        o = d.addObject('Part::Feature', 'CoverQuarter')
        o.Shape = q
        finish(d, 'PR-027_CoverQ_%d.FCStd' % (i + 1))


def build_feet():
    # PR-028: 4 feet in place (print together or separately).
    doc = fresh_doc('PR028_Feet')
    for i, ang in enumerate((45.0, 135.0, 225.0, 315.0)):
        hx, hy = polar(120.0, ang)
        foot = Part.makeCylinder(15.0, 25.0, V(hx, hy, -25.0))
        foot = foot.cut(Part.makeCylinder(M3 / 2.0, 25.0, V(hx, hy, -25.0)))
        o = doc.addObject('Part::Feature', 'Foot_%d' % (i + 1))
        o.Shape = foot
    finish(doc, 'PR-028_Feet.FCStd')


def build_clips():
    # PR-029: 8 cable clips in a printable row.
    doc = fresh_doc('PR029_Clips')
    for i in range(8):
        x0 = i * 20.0
        clip = Part.makeBox(16.0, 12.0, 9.0, V(x0, 0.0, 0.0))
        bore = Part.makeCylinder(3.25, 16.0, V(x0, 8.0, 4.5))
        bore = bore.rotate(V(x0, 0.0, 4.5), V(0, 1, 0), 90.0)
        clip = clip.cut(bore)
        clip = vhole(clip, M3, x0 + 8.0, 2.5, 0.0, 9.0)
        o = doc.addObject('Part::Feature', 'Clip_%d' % (i + 1))
        o.Shape = clip
    finish(doc, 'PR-029_Clips.FCStd', color=(1.00, 0.65, 0.25))


build_gantry()
build_panels()
build_camera_bracket()
build_camera_bezel()
build_led_ring()
build_hall_bracket()
build_magnet_holder()
build_oled_bezel()
build_elex_tray()
build_bottom_cover()
build_feet()
build_clips()
print('Stage4 done')
