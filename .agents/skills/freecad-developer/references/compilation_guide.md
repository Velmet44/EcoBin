# Compiling FreeCAD from Source

This guide provides tested build configurations for compiling FreeCAD across different operating systems.

---

## Prerequisites & Dependencies

FreeCAD depends on:
- **C++20 compliant compiler**: GCC &ge; 11, Clang &ge; 14, or MSVC &ge; 2019 (v142).
- **CMake**: &ge; 3.16.
- **Python**: 3.8 - 3.12.
- **Qt**: Qt 5.15+ or Qt 6.4+.
- **OpenCASCADE (OCCT)**: 7.5+.
- **Coin3D & SoQt**: 3D scene graph and Qt binding.
- **Boost**: Filesystem, System, Program_options, Regex.
- **Eigen3**: Linear algebra.
- **Xerces-C**: XML processing.

---

## 1. Linux (Ubuntu / Debian)

```bash
# 1. Install dependencies
sudo apt-get update
sudo apt-get install -y \
  build-essential cmake git ninja-build \
  libboost-all-dev libxerces-c-dev libeigen3-dev \
  libocct-data-exchange-dev libocct-foundation-dev libocct-modeling-algorithms-dev \
  libocct-modeling-data-dev libocct-ocaf-dev libocct-visualization-dev \
  libcoin-dev libsoqt5-20-dev \
  qtbase5-dev libqt5svg5-dev libqt5xmlpatterns5-dev \
  python3-dev python3-pyside2.qtcore python3-pyside2.qtgui python3-pyside2.qtwidgets \
  python3-matplotlib python3-numpy

# 2. Clone FreeCAD
git clone --recurse-submodules https://github.com/FreeCAD/FreeCAD.git freecad-source

# 3. Configure with Ninja
mkdir build && cd build
cmake -G Ninja ../freecad-source \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DBUILD_ENABLE_CXX20=ON \
  -DFREECAD_USE_EXTERNAL_PIVY=ON

# 4. Build
ninja

# 5. Launch
./bin/FreeCAD
```

---

## 2. Windows (Conda-based Build - Recommended)

The easiest and most reliable way to compile FreeCAD on Windows without configuring hundreds of MSVC dependencies manually is using **Conda**:

```powershell
# 1. Install Miniforge or Mambaforge
# 2. Create build environment from FreeCAD repository recipe:
conda create -n freecad-build -c conda-forge \
  git cmake ninja compiler-rt cxx-compiler \
  boost-cpp occt coin3d soqt pyside2 python=3.10 \
  xerces-c eigen vtk yaml-cpp

# 3. Activate environment
conda activate freecad-build

# 4. Clone and Build
git clone --recurse-submodules https://github.com/FreeCAD/FreeCAD.git freecad-source
mkdir build
cd build
cmake -G Ninja ../freecad-source `
  -DCMAKE_BUILD_TYPE=Release `
  -DCMAKE_PREFIX_PATH=$env:CONDA_PREFIX
ninja
```

---

## 3. Docker Container Build

For clean, isolated builds and CI:

```bash
docker run -it --rm -v $(pwd):/workspace ubuntu:22.04
# In container:
apt-get update && apt-get install -y git build-essential cmake ninja-build ...
```
Or use the official FreeCAD Docker images from Docker Hub (`freecad/ci-ubuntu`, `freecad/ci-conda`).

---

## 4. Key CMake Options Reference

| CMake Variable | Default | Description |
| :--- | :--- | :--- |
| `CMAKE_BUILD_TYPE` | `Release` | `Debug`, `Release`, `RelWithDebInfo`. |
| `BUILD_GUI` | `ON` | Set `OFF` for pure headless server/daemon builds (`FreeCADCmd` only). |
| `BUILD_ENABLE_CXX20`| `ON` | FreeCAD 1.0+ requires C++20. |
| `BUILD_FEM` | `ON` | Compile FEM module. |
| `BUILD_CAM` | `ON` | Compile CAM/Path module. |
| `BUILD_ASSEMBLY`| `ON` | Compile Assembly module. |
| `FREECAD_USE_PCL` | `OFF` | Enable Point Cloud Library integration. |
