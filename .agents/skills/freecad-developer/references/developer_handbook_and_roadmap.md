# FreeCAD Developer Handbook & Core Reference

This reference compiles all C++ source documentation, compilation guides, internal algorithms, and developer resources.

---

## Developer Architecture & Internal Guides

| Subject / Guide | Category | Overview |
| :--- | :--- | :--- |
| **Advanced FreeCAD test system** (`Advanced_FreeCAD_test_system`) | Developer Core | **Obsolete**: This page has been moved to |
| **Arch Building** (`Arch_Building`) | Developer Core | The Arch Building is a special type of FreeCAD group object particularly suited for representing a whole building unit. They ar... |
| **Arch BuildingPart** (`Arch_BuildingPart`) | Developer Core | The BuildingPart object, produced by the BIM Level or BIM Building commands, replaces the old Arch Floor and Arch Building with... |
| **Artwork Test** (`Artwork_Test`) | Developer Core | For all icons in the source tree, see Artwork. |
| **C++ code testing** (`C++_code_testing`) | Developer Core | Beginning in late 2022 the developers of FreeCAD incorporated the Google Test (gtest) testing framework into FreeCAD builds. Th... |
| **Category:Developer Documentation** (`Category_Developer_Documentation`) | Developer Core | | | | | | --- | --- | --- | | Add Button to FEM Toolbar Tutorial | Add FEM Equation Tutorial | Add Workbench to Addon Manager |... |
| **Category:Packaging** (`Category_Packaging`) | Developer Core | | | | | | --- | --- | --- | | AppImage | Debian development | Debian Unstable | | Flatpak | Git buildpackage | Linux packaging ... |
| **Category:Test Framework** (`Category_Test_Framework`) | Developer Core | | | | | | --- | --- | --- | | Testing | |
| **Category:Testing** (`Category_Testing`) | Developer Core | | | | | | --- | --- | --- | | AppImage | Artwork Test | Continuous Integration | | Flatpak | LGTM | Testing | | Ubuntu Snap | C... |
| **CfdOF CFD Solver** (`CfdOF_CFD_Solver`) | Developer Core | Documentation for CfdOF CFD Solver. |
| **Compile on Docker** (`Compile_on_Docker`) | Developer Core | Among the options for building and installing FreeCAD, there is the option of using Docker. This method is primarily useful for... |
| **Compile on Linux** (`Compile_on_Linux`) | Developer Core | On recent Linux distributions, FreeCAD is generally easy to build, since all dependencies are usually provided by the package m... |
| **Compile on MacOS** (`Compile_on_MacOS`) | Developer Core | This page describes how to compile the FreeCAD source code on macOS. For other platforms, see Compiling. |
| **Compile on MinGW** (`Compile_on_MinGW`) | Developer Core | Download and install MSYS2 if you have not already. When launching MSYS2, use the \"MSYS2 MinGW 64-bit\" runtime unless you kno... |
| **Compile on Windows** (`Compile_on_Windows`) | Developer Core | Compiling FreeCAD on Windows requires several tools and libraries. |
| **Compile using Docker** (`Compile_using_Docker`) | Developer Core | Documentation for Compile using Docker. |
| **CompileOnMac** (`CompileOnMac`) | Developer Core | Documentation for CompileOnMac. |
| **CompileOnMinGW** (`CompileOnMinGW`) | Developer Core | Documentation for CompileOnMinGW. |
| **CompileOnWindows** (`CompileOnWindows`) | Developer Core | Documentation for CompileOnWindows. |
| **CompileOnWindows - Reducing Disk Footprint** (`CompileOnWindows_-_Reducing_Disk_Footprint`) | Developer Core | It is recommended that you know on practice, how to Compile on Windows with Qt Creator, before attempting this. |
| **Developer hub** (`Developer_hub`) | Developer Core | This is the place to come if you want to contribute to the development of the FreeCAD software. |
| **EM FHSolver** (`EM_FHSolver`) | Developer Core | The FHSolver tool inserts a FHSolver object. |
| **FEM ConstraintBodyHeatSource** (`FEM_ConstraintBodyHeatSource`) | Developer Core | Defines an internally generated body heat given in W/kg. |
| **FEM EquationFluxsolver** (`FEM_EquationFluxsolver`) | Developer Core | Documentation for FEM EquationFluxsolver. |
| **FEM Solver** (`FEM_Solver`) | Developer Core | This page collects information on the finite element solvers used by the FEM Workbench. The interface between a solver and Free... |
| **FEM SolverCalculiX** (`FEM_SolverCalculiX`) | Developer Core | The **Solver CalculiX (new framework)** command creates a SolverCalculix object, which uses the same framework as Elmer and Z88... |
| **FEM SolverCalculixCxxtools** (`FEM_SolverCalculixCxxtools`) | Developer Core | CalculiXccxTools enables usage of the CalculiX solver. It may be used for: |
| **FEM SolverControl** (`FEM_SolverControl`) | Developer Core | This command is used to control the FEM solver (write the input file, edit it, and trigger the solver). |
| **FEM SolverElmer** (`FEM_SolverElmer`) | Developer Core | Elmer is an open source multiphysical simulation software mainly developed by CSC - IT Center for Science (CSC). Elmer developm... |
| **FEM SolverElmer SolverSettings** (`FEM_SolverElmer_SolverSettings`) | Developer Core | Elmer is a multiphysics solver. Therefore you can use several main equations to solve problems. The different equations are lis... |
| **FEM SolverMystran** (`FEM_SolverMystran`) | Developer Core | The SolverMystran command enables usage of the MYSTRAN solver. It may be used for: |
| **FEM SolverRun** (`FEM_SolverRun`) | Developer Core | This command is used to easily trigger the FEM solver. It is a simplified version of the Solver job control which enables more ... |
| **FEM SolverZ88** (`FEM_SolverZ88`) | Developer Core | The SolverZ88 command enables usage of the Z88 solver. It may be used for: |
| **FreeCAD Build Tool** (`FreeCAD_Build_Tool`) | Developer Core | The **FreeCAD build tool** or **fcbt** is a python script located at ```python trunc/src/Tools/fcbt.py ``` It can be used to si... |
| **FreeCAD Philanthropy Open Source Hardware** (`FreeCAD_Philanthropy_Open_Source_Hardware`) | Developer Core | Documentation for FreeCAD Philanthropy Open Source Hardware. |
| **GSoC FEM Solver Z88** (`GSoC_FEM_Solver_Z88`) | Developer Core | **Obsolete**: This page has been moved to |
| **GSoC FEM Unit Tests** (`GSoC_FEM_Unit_Tests`) | Developer Core | FreeCAD is not only a traditional CAD platform but also aims at providing general engineering functionality. One of the most va... |
| **Git buildpackage** (`Git_buildpackage`) | Developer Core | To get around that, here are the short & simple steps to getting started with git-buildpackage. This should work on nearly any ... |
| **GitBuildpackage** (`GitBuildpackage`) | Developer Core | Documentation for GitBuildpackage. |
| **Give graphical access to a wide range of available ElmerSolver setting from within FreeCAD** (`Give_graphical_access_to_a_wide_range_of_available_ElmerSolver_setting_from_within_FreeCAD`) | Developer Core | This GSoC project aims at a full integration of ElmerSolver into FreeCAD. Since the graphical user interface of ElmerFEM called... |
| **Linux packaging** (`Linux_packaging`) | Developer Core | for Windows and MacOS, see Packaging. |
| **MacOS packaging** (`MacOS_packaging`) | Developer Core | Documentation for MacOS packaging. |
| **Macro Build Utility** (`Macro_Build_Utility`) | Developer Core | This macro is intended for use on large projects, ones involving hundreds of objects. It\'s use on a small single file project ... |
| **Macro ZTest Over 128** (`Macro_ZTest_Over_128`) | Developer Core | This macro is only used by programmers Test characters ASCII over 127 |
| **Mapping of main ElmerSolver setting for mechanical simulations** (`Mapping_of_main_ElmerSolver_setting_for_mechanical_simulations`) | Developer Core | This GSoC project aims at building a solid bridge between FreeCAD and ElmerFEM. Since the graphical user interface of ElmerFEM ... |
| **Mesh BuildRegularSolid** (`Mesh_BuildRegularSolid`) | Developer Core | The **Mesh BuildRegularSolid** command creates a regular parametric solid mesh object. |
| **New solver object for handling ElmerFEM execution in FEM-workbench** (`New_solver_object_for_handling_ElmerFEM_execution_in_FEM-workbench`) | Developer Core | This GSoC project aims at building a first bridge between FreeCAD and ElmerFEM. The intension is to use FreeCAD for geometrical... |
| **Packaging** (`Packaging`) | Developer Core | - Linux packaging. Information on AppImages, Debian packages, unstable and daily, and others. - Windows packaging. Information ... |
| **Part Builder** (`Part_Builder`) | Developer Core | A tool to create more complex shapes from various parametric geometric primitives. |
| **Part Shapebuilder** (`Part_Shapebuilder`) | Developer Core | Documentation for Part Shapebuilder. |
| **Source Integration Markup** (`Source_Integration_Markup`) | Developer Core | Documentation for Source Integration Markup. |
| **Source code management** (`Source_code_management`) | Developer Core | The main source code management tool for the FreeCAD project is Git, which can be easily installed in most operating systems fr... |
| **Source documentation** (`Source_documentation`) | Developer Core | The FreeCAD source code is commented to allow automatic programming documentation generation using Doxygen, a popular source co... |
| **Test Framework Workbench** (`Test_Framework_Workbench`) | Developer Core | Documentation for Test Framework Workbench. |
| **Testing** (`Testing`) | Developer Core | The Test Framework Workbench is not really a modelling workbench, but it contains a set of Python scripts to perform different ... |
| **The FreeCAD source code** (`The_FreeCAD_source_code`) | Developer Core | Below are some clues and useful information to get you on tracks if you are interested in exploring the FreeCAD code. |
| **Windows packaging** (`Windows_packaging`) | Developer Core | Documentation for Windows packaging. |
