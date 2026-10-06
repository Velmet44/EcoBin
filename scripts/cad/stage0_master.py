"""EcoBin Stage 0 master skeleton generator (spec section 11.4).

Run inside FreeCAD via the FreeCAD MCP execute_code tool:
    exec(open('E:/Project/EcoBin/scripts/cad/stage0_master.py').read())

Regenerates the content of the EcoBin_Master document, which is saved as
3D-Design/parts/00_Master.FCStd. Re-running is idempotent: stale Params
and Skeleton objects are removed first, then rebuilt.

Single source of layout truth: edit PARAMS below, re-run, save.
Locked owner decisions: medium envelope (300 x 350), 60 mm / 150 g item,
separate lift-out bins, shared lab printer (210 x 210 x 240 target).
"""

import FreeCAD as App

DOC_NAME = 'EcoBin_Master'
SAVE_PATH = 'E:/Project/EcoBin/3D-Design/parts/00_Master.FCStd'

PARAMS = [
    ('OverallDia', '300 mm', 'Model footprint diameter (locked: medium size)'),
    ('OverallHeight', '350 mm', 'Model total height (locked)'),
    ('R_station', '80 mm', 'Drop-station radius from carousel axis'),
    ('MouthDia', '100 mm', 'Chamber mouth diameter (60 mm item + clearance)'),
    ('TrayOpening', '80 mm', 'Tray floor opening'),
    ('FlapDia', '90 mm', 'Trapdoor flap clearing diameter'),
    ('GuideDia', '90 mm', 'Drop guide inner diameter'),
    ('ChamberDia', '100 mm', 'Chamber body diameter (separate lift-out bins)'),
    ('ChamberH', '150 mm', 'Chamber body height'),
    ('RotorDia', '260 mm', 'Carrier plate diameter (splits into 4 quadrants)'),
    ('CarrierThk', '12 mm', 'Carrier plate thickness'),
    ('BaseThk', '20 mm', 'Base frame thickness'),
    ('MotorZoneH', '60 mm', 'Bearing + motor stack height'),
    ('DeckThk', '15 mm', 'Fixed deck plate thickness'),
    ('TrayZoneH', '60 mm', 'Tray + guide zone height'),
    ('HoodZoneH', '45 mm', 'Camera hood zone height'),
    ('BedX', '210 mm', 'Shared-lab printer target X'),
    ('BedY', '210 mm', 'Shared-lab printer target Y'),
    ('BedZ', '240 mm', 'Shared-lab printer target Z'),
    ('NumChambers', '4', 'Chamber count'),
    ('IndexAngle', '90 deg', 'Nominal index step'),
]

DERIVED = [
    ('CarrierZ', '=BaseThk + MotorZoneH', 'Rotor plane height (20+60=80)'),
    ('DeckZ0', '=CarrierZ + ChamberH', 'Deck underside / chamber mouth plane (80+150=230)'),
    ('TrayZ0', '=DeckZ0 + DeckThk', 'Deck top / tray floor plane (230+15=245)'),
    ('TopZ', '=TrayZ0 + TrayZoneH + HoodZoneH', 'Model top; must equal OverallHeight (245+60+45=350)'),
]


def build():
    doc = App.getDocument(DOC_NAME)

    # 00_Master holds generated content only: wipe every known object so
    # re-runs never leave stale or auto-renamed (001) duplicates behind.
    for _ in range(3):
        stale = [o for o in doc.Objects
                 if o.Name in ('Params', 'Skeleton')
                 or o.Name.startswith(('REFERENCE_', 'DATUM_'))]
        if not stale:
            break
        for o in stale:
            try:
                doc.removeObject(o.Name)
            except Exception:
                pass

    sheet = doc.addObject('Spreadsheet::Sheet', 'Params')
    sheet.set('A1', 'Parameter')
    sheet.set('B1', 'Value')
    sheet.set('C1', 'Notes')
    row = 2
    for alias, val, note in PARAMS:
        sheet.set('A%d' % row, alias)
        sheet.set('B%d' % row, val)
        sheet.set('C%d' % row, note)
        sheet.setAlias('B%d' % row, alias)
        row += 1
    for alias, formula, note in DERIVED:
        sheet.set('A%d' % row, alias)
        sheet.set('B%d' % row, formula)
        sheet.set('C%d' % row, note)
        sheet.setAlias('B%d' % row, alias)
        row += 1

    grp = doc.addObject('App::DocumentObjectGroup', 'Skeleton')

    def add_solid(type_id, name, exprs=None, values=None, color=None, transparency=0):
        o = doc.addObject(type_id, name)
        for prop, expr in (exprs or {}).items():
            o.setExpression(prop, expr)
        for prop, val in (values or {}).items():
            setattr(o, prop, val)
        grp.addObject(o)
        if color is not None:
            try:
                o.ViewObject.ShapeColor = color
                o.ViewObject.Transparency = transparency
            except Exception:
                pass
        return o

    P = 'Params.'
    grey = (0.70, 0.70, 0.70)
    red = (1.00, 0.20, 0.20)
    blue = (0.20, 0.45, 1.00)
    orange = (1.00, 0.55, 0.10)

    # Reference envelope (visual only, not printable).
    add_solid('Part::Cylinder', 'REFERENCE_Envelope',
              {'Radius': P + 'OverallDia / 2', 'Height': P + 'OverallHeight'},
              color=grey, transparency=85)

    # Carousel Z axis, full model height.
    add_solid('Part::Cylinder', 'DATUM_CarouselAxis',
              {'Height': P + 'TopZ'}, values={'Radius': 1.0},
              color=red)

    # Drop-station vertical axis at (R_station, 0), mouth plane to top.
    add_solid('Part::Cylinder', 'DATUM_DropAxis',
              {'Height': P + 'TopZ - ' + P + 'DeckZ0',
               'Placement.Base.x': P + 'R_station',
               'Placement.Base.z': P + 'DeckZ0'},
              values={'Radius': 1.0}, color=red)

    # Datum planes (squares centred on the axis).
    def datum_plane(name, z_expr):
        half = '-1 * ' + P + 'RotorDia / 2'
        add_solid('Part::Plane', name,
                  {'Length': P + 'RotorDia',
                   'Width': P + 'RotorDia',
                   'Placement.Base.x': half,
                   'Placement.Base.y': half,
                   'Placement.Base.z': z_expr},
                  color=blue, transparency=75)

    datum_plane('DATUM_RotorPlane', P + 'CarrierZ')
    datum_plane('DATUM_DeckPlane', P + 'DeckZ0')
    datum_plane('DATUM_TrayPlane', P + 'TrayZ0')

    # 90-degree index points on the mouth plane (no trig needed).
    def index_point(name, x_expr, y_expr):
        add_solid('Part::Sphere', name,
                  {'Placement.Base.x': x_expr,
                   'Placement.Base.y': y_expr,
                   'Placement.Base.z': P + 'DeckZ0'},
                  values={'Radius': 2.5}, color=orange)

    index_point('DATUM_Index0', P + 'R_station', '0')
    index_point('DATUM_Index1', '0', P + 'R_station')
    index_point('DATUM_Index2', '-1 * ' + P + 'R_station', '0')
    index_point('DATUM_Index3', '0', '-1 * ' + P + 'R_station')

    doc.recompute()
    bad = [o.Name for o in doc.Objects if 'Invalid' in o.State]
    print('Stage0 objects: %d, invalid: %s' % (len(doc.Objects), bad))
    doc.saveAs(SAVE_PATH)
    print('Saved ' + SAVE_PATH)


build()
