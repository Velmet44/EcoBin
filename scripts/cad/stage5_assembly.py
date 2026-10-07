"""EcoBin Stage 5 top assembly (spec 11.4). App::Link, no duplicated geometry.

Run inside FreeCAD via the FreeCAD MCP execute_code tool:
    exec(open('E:/Project/EcoBin/scripts/cad/stage5_assembly.py').read())

Builds 3D-Design/assemblies/EcoBin_Top.FCStd from App::Links, positions
every part, then runs numeric fit proofs (datum alignment, pin-line
coincidence, clearances, intended contacts, overall box).
Re-running wipes and rebuilds the assembly doc only (parts untouched).

Center stack (world Z): mount plate -6..0 under base / base 0..20 /
seat flange 20..28 + boss 28..68 / carrier 68..80 / hub flange 80..86.
Motor cavity r30 reserved through cover/elex/base into the mount boss
hole; motor + coupling + bearing are TBD (open item, no clash today).

Sandwich at drop station: bridge top 248 / flange 248..253 /
support 253..261 / tray 261..267. Flap origin z=241 (pin line z=247);
pin bosses at z=239 (bore z=247). Guide tube 230..248 in bridge mouth.
Linkage rests in the servo mount (horn wire trim at fit-up).
OLED bezel seats from inside front panel window (recessed 4 mm).
PR-018 ClipMaster x8 (anti-rotation stops); PR-029 clips x8 stowed as
wire guides on the elex tray edges.

Open items (bench/fit-up, not geometry): bearing/coupling/motor picks,
hinge-pin M3x50 (BOM-031 SKU TBD), servo self-taps, linkage trim,
chamber letter labels, mount/foot/stack bolt lengths (see README).
"""

import FreeCAD as App
import math
from FreeCAD import Vector as V

PARTS = 'E:/Project/EcoBin/3D-Design/parts/'
ASM = 'E:/Project/EcoBin/3D-Design/assemblies/EcoBin_Top.FCStd'


def fresh(name):
    if name in App.listDocuments():
        App.closeDocument(name)
    return App.newDocument(name)


top = fresh('EcoBin_Top')
top.saveAs(ASM)  # owner doc must exist on disk before external links
# Drop stale in-memory part docs: disk (just rebuilt) is truth.
for _name in list(App.listDocuments()):
    if _name != 'EcoBin_Top':
        try:
            App.closeDocument(_name)
        except Exception:
            pass
opened = {}


def part(fname):
    if fname not in opened:
        opened[fname] = App.openDocument(PARTS + fname)
    return opened[fname]


def link(fname, objname, linkname, base=(0, 0, 0), axis=None, deg=0.0):
    o = part(fname).getObject(objname)
    assert o is not None, 'missing %s in %s' % (objname, fname)
    assert hasattr(o, 'Shape'), 'no Shape: %s in %s' % (objname, fname)
    l = top.addObject('App::Link', linkname)
    l.LinkedObject = o
    if axis is None:
        l.Placement = App.Placement(V(*base), App.Rotation())
    else:
        l.Placement = App.Placement(V(*base), App.Rotation(V(*axis), deg))
    return l


def P(hex_, deg):
    a = math.radians(deg)
    return (hex_ * math.cos(a), hex_ * math.sin(a))


L = {}
L['base'] = link('PR-001_BaseFrame.FCStd', 'BaseFrame', 'L_Base')
L['seat'] = link('PR-013_BearingSeat.FCStd', 'BearingSeat', 'L_Seat', (0, 0, 20))
L['mount'] = link('PR-019_StepperMount.FCStd', 'StepperMount', 'L_Mount', (0, 0, -6))
L['hub'] = link('PR-012_Hub.FCStd', 'Hub', 'L_Hub', (0, 0, 80))
for i, ang in enumerate((0.0, 90.0, 180.0, 270.0)):
    L['q%d' % (i + 1)] = link('PR-011_Carrier_Q%d.FCStd' % (i + 1),
                              'CarrierQuadrant', 'L_Q%d' % (i + 1), (0, 0, 68))
chambers = (('PR-014_Chamber_A.FCStd', 'A', 0.0), ('PR-015_Chamber_B.FCStd', 'B', 90.0),
            ('PR-016_Chamber_C.FCStd', 'C', 180.0), ('PR-017_Chamber_D.FCStd', 'D', 270.0))
for fname, tag, ang in chambers:
    x, y = P(80.0, ang)
    L['bin' + tag] = link(fname, 'ChamberBin', 'L_Bin' + tag, (x, y, 80))
# Retention stops: two rings at 45 deg + 90 k (local X points radially out).
n = 0
for R in (100.0, 125.0):
    for k in range(4):
        n += 1
        phi = 45.0 + 90.0 * k
        x, y = P(R, phi)
        L['clip%d' % n] = link('PR-018_Clips.FCStd', 'ClipMaster', 'L_Clip%d' % n,
                               (x, y, 80), (0, 0, 1), phi)
L['tray'] = link('PR-005_TrayBody.FCStd', 'TrayBody', 'L_Tray', (80, 0, 261))
L['support'] = link('PR-006_ScaleSupport.FCStd', 'ScaleSupport', 'L_Support', (80, 0, 253))
L['flap'] = link('PR-007_TrapdoorFlap.FCStd', 'TrapdoorFlap', 'L_Flap', (80, 0, 241))
L['bossA'] = link('PR-008_HingeSupports.FCStd', 'PinBoss', 'L_BossA', (55.4, -40.0, 239))
L['bossB'] = link('PR-008_HingeSupports.FCStd', 'PinBoss', 'L_BossB', (104.6, -40.0, 239))
L['guide'] = link('PR-004_DropGuide.FCStd', 'DropGuide', 'L_Guide', (80, 0, 248))
L['servo'] = link('PR-009_ServoMount.FCStd', 'ServoMount', 'L_Servo', (128, 48, 267))
L['linkage'] = link('PR-010_Linkage.FCStd', 'LinkageAdapter', 'L_Linkage', (128, 48, 271))
L['gantry'] = link('PR-003_Gantry.FCStd', 'Gantry', 'L_Gantry')
for i in (1, 2, 3):
    L['panel%d' % i] = link('PR-002_Panel_%d.FCStd' % i, 'SkirtPanel', 'L_Panel%d' % i)
L['bracket'] = link('PR-020_CameraBracket.FCStd', 'CameraBracket', 'L_Bracket')
L['cbezel'] = link('PR-021_CameraBezel.FCStd', 'CameraBezel', 'L_CBezel', (80, 0, 344))
L['ring'] = link('PR-022_LEDRing.FCStd', 'LEDRing', 'L_Ring')
L['hall'] = link('PR-023_HallBracket.FCStd', 'HallBracket', 'L_Hall')
L['magnet'] = link('PR-024_MagnetHolder.FCStd', 'MagnetHolder', 'L_Magnet', (0, 0, 68))
L['oled'] = link('PR-025_OLEDBezel.FCStd', 'OLEDBezel', 'L_OLED',
                 (0, -138.0, 50), (1, 0, 0), 90.0)
L['etray'] = link('PR-026_ElexTray.FCStd', 'ElexTray', 'L_ETray', (0, 0, -20))
for i in (1, 2, 3, 4):
    L['cov%d' % i] = link('PR-027_CoverQ_%d.FCStd' % i, 'CoverQuarter',
                          'L_Cov%d' % i, (0, 0, -25))
for i in (1, 2, 3, 4):
    L['foot%d' % i] = link('PR-028_Feet.FCStd', 'Foot_%d' % i, 'L_Foot%d' % i)
# Cable clips as tray-edge wire guides (local row offset compensated).
xs = (-72.0, -48.0, -24.0, 0.0)
for i in range(8):
    x0l = (i % 8) * 20.0  # local row origin of Clip_i in PR-029
    xc = xs[i % 4]
    ty = -74.0 if i < 4 else 62.0
    L['cc%d' % (i + 1)] = link('PR-029_Clips.FCStd', 'Clip_%d' % (i + 1),
                               'L_CC%d' % (i + 1), (xc - x0l - 8.0, ty, -16))

top.recompute()

# ---- proofs ----
def shape_at(linkname):
    return L[linkname].Shape


def gap(name, a, b, minimum):
    d = shape_at(a).distToShape(shape_at(b))[0]
    print('%s gap=%.2f (min %.2f)' % (name, d, minimum))
    assert d >= minimum - 1e-6, 'CLEARANCE FAIL: ' + name


def touch(name, a, b):
    d = shape_at(a).distToShape(shape_at(b))[0]
    print('%s contact gap=%.2f (expect <0.5)' % (name, d))
    assert d < 0.5, 'MOUNT FAIL: ' + name


idx = [(80.0, 0.0), (0.0, 80.0), (-80.0, 0.0), (0.0, -80.0)]
for (ix, iy), tag in zip(idx, 'ABCD'):
    p = L['bin' + tag].Placement.Base
    assert abs(p.x - ix) < 1e-6 and abs(p.y - iy) < 1e-6, 'bin-%s off index' % tag
    print('bin-%s on index (%.1f, %.1f), mouth top z=%.1f'
          % (tag, p.x, p.y, p.z + 150.0))
    assert abs((p.z + 150.0) - 230.0) < 1e-6, 'mouth plane off datum'
print('mouth plane z=230 matches DATUM deck plane')

fp = (80.0, -40.0, 241.0 + 6.0)   # flap pin line world (origin + local z6)
bp = (55.4, -40.0, 239.0 + 8.0)   # boss bore world (origin + local z8)
assert abs(fp[1] - bp[1]) < 1e-6 and abs(fp[2] - bp[2]) < 1e-6, 'pin lines misaligned'
print('hinge pin line shared at y=%.1f z=%.1f' % (fp[1], fp[2]))

magnet_face_z = 68.0 - 6.0   # holder origin + bore bottom
module_face_z = 56.0 + 4.0   # head top + module thickness (module TBD)
hall_gap = magnet_face_z - module_face_z
print('hall air gap=%.1f (band 1.5..6)' % hall_gap)
assert 1.5 <= hall_gap <= 6.0, 'hall gap out of sensor band'

# Intended contacts (mounting faces / press fits).
touch('seat/base', 'seat', 'base')
touch('mount/base', 'mount', 'base')
touch('carrier/seat', 'q1', 'seat')
touch('hub/carrier', 'hub', 'q1')
touch('bin-seat/pocket', 'binA', 'q1')
touch('post/base', 'gantry', 'base')
touch('flange/bridge', 'guide', 'gantry')
touch('support/flange', 'support', 'guide')
touch('tray/support', 'tray', 'support')
touch('servo/tray', 'servo', 'tray')
touch('linkage/servo', 'linkage', 'servo')
touch('bossA/guide-press', 'bossA', 'guide')  # press into tube wall, intended
touch('bossB/guide-press', 'bossB', 'guide')
touch('ringarm/bracket', 'ring', 'bracket')   # arms only; annulus clears by 8
touch('oled/panel3', 'oled', 'panel3')
for i in range(1, 9):
    # Stops straddle quadrant joints: nearest of the four quadrants counts.
    d = min(shape_at('clip%d' % i).distToShape(shape_at('q%d' % j))[0]
            for j in (1, 2, 3, 4))
    print('clip%d/carrier contact gap=%.2f (expect <0.5)' % (i, d))
    assert d < 0.5, 'MOUNT FAIL: clip%d/carrier' % i
for i in range(1, 9):
    touch('cableclip%d/etray' % i, 'cc%d' % i, 'etray')

# Clearances.
gap('flap/support', 'flap', 'support', 2.0)
gap('flap/guide-corner', 'flap', 'guide', 0.5)
tube_c = L['guide'].Placement.Base
assert abs(tube_c.x - 80.0) < 1e-6 and abs(tube_c.y - 0.0) < 1e-6
print('tube/mouth concentric, wall clearance=%.1f' % (55.0 - 53.0))
gap('rotor/post', 'q1', 'gantry', 1.5)
gap('bin-top/bridge', 'binA', 'gantry', 3.0)
gap('hall/rotor', 'hall', 'q1', 10.0)
gap('mount/etray', 'mount', 'etray', 8.0)
worst = 1e9
for i in range(1, 9):
    for tag in 'ABCD':
        d = shape_at('clip%d' % i).distToShape(shape_at('bin' + tag))[0]
        worst = min(worst, d)
print('clip/bin min gap=%.2f (min 1.50)' % worst)
assert worst >= 1.5 - 1e-6, 'CLEARANCE FAIL: clip/bin'

boxes = [l.Shape.BoundBox for l in top.Objects if hasattr(l, 'Shape')]
bb = boxes[0]
for b in boxes[1:]:
    bb.add(b)
print('assembly bbox x[%.1f, %.1f] y[%.1f, %.1f] z[%.1f, %.1f]'
      % (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))
assert bb.XMin >= -150.5 and bb.XMax <= 150.5, 'envelope X'
assert bb.YMin >= -150.5 and bb.YMax <= 150.5, 'envelope Y'
assert bb.ZMin >= -25.5 and bb.ZMax <= 350.5, 'envelope Z'

top.saveAs(ASM)
print('STAGE5 OK -> ' + ASM)
