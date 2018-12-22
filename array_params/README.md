# Array props
This project tests array parameters of simple and complex types as function in/out parameters and return values.

## Overview
As with the output params test project, with arrays we have to test calling to and from each language (C++, Blueprint, and Python)
and test the various ways array parameters can be used (input parameters, output parameters, and return values).

Additionally, we need to test a variety of data types since there is a lot of conversion and handler code specific to certain
data types.

The main classes in this project are:
- TestActor - implements methods with various parameters
- Tester - initiates calls to a TestActor, recording parameters passed and results returned
- TestRecorder - passed to both the TestActor and Tester; records events to generate a diffable test log

To ensure completeness, there are BP, C++, and Python implementations of TestActor and Tester. Using them, the project tests:
- C++ calling C++
- C++ calling BP
- C++ calling Py
- Py calling C++
- Py calling BP
- Py calling Py
- BP calling C++
- BP calling BP
- BP calling Py

For each pair of languages, the following scenarios are passed:
- a method that accepts as input an array parameter
- a method that returns an array as an output parameter
- a method that returns an array as the return parameter
- a jumbo test on a method that takes an array input parameter, has an array output parameter, and also returns an array as the return value

Each method in the above scenario also has some simple parameters (e.g. floats and ints) to test for corruption or leakage to other parameters.

For all of the above scenarios, array parameters of different types are tested:
- arrays of ints (to test simple types)
- arrays of bools (because they are handled a little differently in UE4 internally)
- arrays of FVectors (to test builtin structs)
- arrays of strings
- arrays of a simple test actor (to test UObject arrays)
- arrays of a simple test struct (to test UScriptStruct)

## Setup
To use this project:
1. Clone or download it.
1. Go into the array_params/Plugins directory and install UnrealEnginePython there (e.g. by cloning the repo).
1. In Windows Explorer, right click on array_params.uproject and choose the option to generate Visual Studio project files
1. Open array_params.sln, set array_params as the startup project, and then run it.

The tests run when you start PIE. After they have run initially, you can press the space bar to run them again.

