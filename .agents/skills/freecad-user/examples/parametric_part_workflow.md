# Example Workflow: Designing a Parametric Enclosure

This end-to-end example illustrates the canonical, TNP-safe modeling workflow in FreeCAD PartDesign.

---

## Objective
Design a rectangular electronics enclosure with:
- Outer dimensions: 100mm x 60mm x 30mm
- Wall thickness: 3mm
- Mounting bosses with M3 screw clearance holes in the 4 corners
- 4mm exterior corner rounding

---

## Step-by-Step Procedure

### 1. Parameter Setup in Spreadsheet
1. Open FreeCAD and switch to **Spreadsheet Workbench**.
2. Click **Create Spreadsheet** (`Spreadsheet`).
3. Set up cells:
   - `B1`: `100 mm` &rarr; Alias: `box_length`
   - `B2`: `60 mm` &rarr; Alias: `box_width`
   - `B3`: `30 mm` &rarr; Alias: `box_height`
   - `B4`: `3 mm` &rarr; Alias: `wall_thick`
   - `B5`: `4 mm` &rarr; Alias: `corner_rad`
   - `B6`: `6 mm` &rarr; Alias: `boss_dia`
   - `B7`: `3.2 mm` &rarr; Alias: `hole_dia`

### 2. Base Solid (Main Body)
1. Switch to **PartDesign Workbench**.
2. Click **Create Body** (`PartDesign_Body`).
3. Click **Create Sketch** on the `XY_Plane` (Base Plane).
4. Draw a rectangle centered on the Origin:
   - Add horizontal and vertical symmetry constraints to the origin axes.
   - Constrain horizontal length: `=Spreadsheet.box_length`
   - Constrain vertical width: `=Spreadsheet.box_width`
5. Close Sketch (`Sketch_Base`).
6. Click **Pad**:
   - Type: Length
   - Length: `=Spreadsheet.box_height`
   - Click OK (`Pad_Base`).

### 3. Hollow Out Interior (Pocket from Datum Plane)
1. Select the `XY_Plane` of the Body (NOT the top face of Pad_Base to prevent TNP).
2. Click **Create a sub-object datum plane** (`PartDesign_Plane`):
   - Attachment mode: Flat Face / Parallel.
   - Z offset: `=Spreadsheet.box_height`
3. Click **Create Sketch** attached to the newly created `DatumPlane`.
4. Draw a centered rectangle:
   - Horizontal length: `=Spreadsheet.box_length - (Spreadsheet.wall_thick * 2)`
   - Vertical width: `=Spreadsheet.box_width - (Spreadsheet.wall_thick * 2)`
5. Close sketch.
6. Click **Pocket**:
   - Reversed: Direction pointing down into the body.
   - Length: `=Spreadsheet.box_height - Spreadsheet.wall_thick`
   - Click OK. The enclosure is now hollowed out with a solid 3mm floor.

### 4. Corner Mounting Bosses
1. Create another Sketch on the interior floor (`XY_Plane` with Z offset `=Spreadsheet.wall_thick` or directly on `XY_Plane`).
2. Draw 4 circles at each corner.
3. Constrain diameters to `=Spreadsheet.boss_dia`.
4. Constrain distances from edges to `=Spreadsheet.wall_thick + (Spreadsheet.boss_dia / 2)`.
5. Click **Pad** &rarr; Up to face or Length `=Spreadsheet.box_height - Spreadsheet.wall_thick`.
6. Add M3 screw holes through the bosses using the **Hole** feature or a subtractive pocket sketch with diameter `=Spreadsheet.hole_dia`.

### 5. Final Dress-Up
1. Select the 4 vertical external corner edges.
2. Click **Fillet** &rarr; Radius: `=Spreadsheet.corner_rad`.
3. Save the document (`Enclosure.FCStd`).
4. Select the Body &rarr; File &rarr; Export &rarr; `Enclosure.step` or `Enclosure.stl`.
