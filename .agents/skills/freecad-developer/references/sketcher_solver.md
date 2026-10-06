# FreeCAD Sketcher Solver Internals (PlaneGCS)

The FreeCAD Sketcher workbench relies on **PlaneGCS** (Planar Geometric Constraint Solver), a high-performance C++ numerical solver developed specifically for 2D parametric geometry.

---

## 1. Solver Architecture & Code Location

The solver code lives in:
- `src/Mod/Sketcher/App/planegcs/`
  - `GCS.cpp` / `GCS.h`: The main PlaneGCS solver class.
  - `SubSystem.cpp`: System decomposition and subsystem solving.
  - `Constraints.cpp`: Mathematical formulations of geometric constraints.

---

## 2. Mathematical Formulation

PlaneGCS models the sketch as a non-linear system of equations:

$$\mathbf{F}(\mathbf{x}) = \mathbf{0}$$

Where:
- $\mathbf{x}$ is the parameter vector representing degrees of freedom: coordinates of points $(x_i, y_i)$, radii $r_i$, angles $\theta_i$, and major/minor axes of ellipses.
- $\mathbf{F}(\mathbf{x})$ is the vector of constraint error functions (residuals).

### Example Constraint Residuals:
- **Horizontal Line**: Between point $(x_1, y_1)$ and $(x_2, y_2)$:
  $$f(\mathbf{x}) = y_2 - y_1 = 0$$
- **Distance Between Two Points**: Equal to target $D$:
  $$f(\mathbf{x}) = (x_2 - x_1)^2 + (y_2 - y_1)^2 - D^2 = 0$$
- **Point on Circle**: Radius $R$ centered at $(x_c, y_c)$:
  $$f(\mathbf{x}) = (x_p - x_c)^2 + (y_p - y_c)^2 - R^2 = 0$$

---

## 3. The Solving Algorithm: Levenberg-Marquardt & BFGS

PlaneGCS minimizes the sum of squared residuals:

$$S(\mathbf{x}) = \frac{1}{2} \|\mathbf{F}(\mathbf{x})\|^2$$

1. **DOF Analysis**: PlaneGCS counts free parameters vs independent equations.
   - If `parameters > equations`: **Under-constrained** (degrees of freedom remain).
   - If `parameters == equations`: **Fully constrained** (unique solution sought).
   - If `parameters < equations` or conflicting equations: **Over-constrained / Conflicting**.
2. **Decomposition**: PlaneGCS decomposes large sketches into smaller independent sub-systems (clusters) using graph algorithms, solving each cluster sequentially.
3. **Iteration**:
   - Computes the Jacobian matrix $\mathbf{J} = \frac{\partial \mathbf{F}}{\partial \mathbf{x}}$.
   - Uses damped least-squares (**Levenberg-Marquardt**) or **Dogleg** step to converge towards the root from the user's initial mouse drag position.

---

## 4. Troubleshooting Solver Issues in Development

- **Numerical Precision for Large Values**: When sketches contain coordinates $> 10,000\text{ mm}$, single-precision roundoff or poorly scaled gradients can cause solver convergence failure.
- **Redundant / Red / Conflicting Constraints**: PlaneGCS computes the rank of the Jacobian matrix $\mathbf{J}$. If rows are linearly dependent, rank deficiency identifies the conflicting constraint.
- **Diagnostics**: Enable solver debug logging in FreeCAD by setting `Sketcher.General.SolverDebug = True` in the Parameter Editor.
