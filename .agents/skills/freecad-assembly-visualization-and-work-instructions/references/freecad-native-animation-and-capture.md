# FreeCAD native animation and capture

FreeCAD 1.1 introduced Assembly `Create Simulation`. It creates Motion objects with a Joint, angular/linear MotionType and `Formula=f(time)`, then generates frames for the Animation Player. Record time start/end, output step, global solver error tolerance and FPS.

In FreeCAD 1.1.2 source, selectable drivers are Revolute, Slider and Cylindrical joints; cylindrical joints can use angular or linear motion. Treat this as version-sensitive.

The motion definition contains no force/torque, mass/inertia, friction, contact, actuator or controller model. Therefore it is prescribed kinematics. The global solver tolerance is not a physics or collision-accuracy control.

Use `Tools > Save image` or `View3DInventorPy.saveImage` with a fixed camera/resolution for controlled stills. Capture simulation frames in a GUI session and validate the workflow for the pinned build; `FreeCADCmd`/offline rendering may not reproduce Assembly GUI state.

Primary references:

- https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Assembly_CreateSimulation.md
- https://github.com/FreeCAD/FreeCAD/blob/1.1.2/src/Mod/Assembly/CommandCreateSimulation.py
- https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Std_ViewScreenShot.md
- https://freecad.github.io/API/d4/d5a/group__OFFLINERENDERINGUTILS.html
