# FreeCAD C++ and Python Bindings

FreeCAD binds C++ classes to Python using an internal code-generation system based on **XML template definitions** and **PyCXX/CPython C API**.

---

## 1. How Python Binding Works in FreeCAD

Instead of writing raw CPython boilerplate (`PyMethodDef`, `tp_getattro`, etc.) by hand, FreeCAD uses an XML specification:

```
ClassNamePy.xml (XML definition of Python API)
       │
       ▼ (src/Tools/generate.py)
ClassNamePy.h and ClassNamePyImp.cpp (Generated C++ wrappers)
       │
       ▼ (Developer implements custom logic)
ClassNamePyImp.cpp
```

---

## 2. Example: Defining `MyFeaturePy.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<GenerateModel xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <PythonExport 
      Father="DocumentObjectPy" 
      Name="MyFeaturePy" 
      Twin="MyFeature" 
      TwinPointer="MyFeature" 
      Include="Mod/MyMod/App/MyFeature.h" 
      Namespace="MyMod" 
      Doc="Python wrapper for MyFeature document object">
    
    <!-- Exposed Method -->
    <Methode Name="computeVolume" Doc="Calculates total volume of the feature">
      <PythonParameters>
        <Parameter Name="tolerance" Type="Float" Default="0.001" Doc="Computation tolerance"/>
      </PythonParameters>
    </Methode>

    <!-- Exposed Attribute -->
    <Attribute Name="IsLocked" ReadOnly="false">
      <DocString>Returns or sets lock state.</DocString>
    </Attribute>

  </PythonExport>
</GenerateModel>
```

---

## 3. Implementing the C++ Wrapper (`MyFeaturePyImp.cpp`)

The generator creates empty stubs in `MyFeaturePyImp.cpp`. The developer provides the logic:

```cpp
#include "PreCompiled.h"
#include "MyFeature.h"
#include "MyFeaturePy.h"

using namespace MyMod;

PyObject* MyFeaturePy::computeVolume(PyObject* args)
{
    double tolerance = 0.001;
    if (!PyArg_ParseTuple(args, "|d", &tolerance))
        return nullptr;

    try {
        double vol = getMyFeaturePtr()->calculateVolume(tolerance);
        return Py_BuildValue("d", vol);
    }
    catch (const Base::Exception& e) {
        PyErr_SetString(Base::BaseExceptionFreeCADError, e.what());
        return nullptr;
    }
}

Py::Boolean MyFeaturePy::getIsLocked() const
{
    return Py::Boolean(getMyFeaturePtr()->isLocked());
}

int MyFeaturePy::setIsLocked(Py::Boolean arg)
{
    getMyFeaturePtr()->setLocked(arg);
    return 0;
}
```

---

## 4. Best Practices for C++/Python Bindings

1. **Always Catch C++ Exceptions**:
   Never allow an unhandled C++ exception to escape into Python. Wrap calls in `try...catch (const Base::Exception& e)` and translate to `PyErr_SetString`.
2. **Use `Py::` Types for Clean RAII**:
   Use PyCXX types (`Py::String`, `Py::Dict`, `Py::List`, `Py::Boolean`) to avoid memory leaks from manual Python reference counting (`Py_INCREF`/`Py_DECREF`).
3. **Keep Heavy Math in C++**:
   Perform heavy numerical computation, OpenCASCADE algorithms, or mesh traversal in C++, exposing only high-level properties and controls to Python.
