# Output Params
This project has a series of unit tests to make sure that sending values to and returning values from Python code works.

## Overview
A few wrinkles we have to deal with:
- Blueprint functions have no return values, but they can have zero or more output parameters
- C++ can optionally have a return value, and can also have zero or more output parameters
- From Python we need to be able to call any of those types of functions and properly receive back all output parameters and return values
- We need to be able to implement in Python any of those types of functions (so that we can subclass a BP or C++ parent class and override methods declared using any of those styles)

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

Obviously a number of these - like C++ calling BP - should just work, but they are included to ensure consistency across languages. They are also useful
as references when troubleshooting problems with the Python versions.

For each of the above scenarios, the project tests both the 'caller' and 'callee' side in the following scenarios:

| *Input parameters* | *Output parameters* | *Return value?*|
|---|---|---|
| 0 | 0 | N |
| 1 | 0 | N |
| 2 | 0 | N |
| 0 | 0 | Y |
| 0 | 0 | Y |
| 0 | 0 | Y |
| 0 | 1 | N |
| 1 | 1 | N |
| 2 | 1 | N |
| 0 | 1 | Y |
| 0 | 1 | Y |
| 0 | 1 | Y |
| 0 | 2 | N |
| 1 | 2 | N |
| 2 | 2 | N |
| 0 | 2 | Y |
| 0 | 2 | Y |
| 0 | 2 | Y |

## Setup
To use this project:
1. Clone or download it.
1. Go into the output_params/Plugins directory and install UnrealEnginePython there (e.g. by cloning the repo).
1. In Windows Explorer, right click on output_params.uproject and choose the option to generate Visual Studio project files
1. Open output_params.sln, set output_params as the startup project, and then run it.

The tests run when you start PIE. After they have run initially, you can press the space bar to run them again.

