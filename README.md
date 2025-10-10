# DHNpype

**A simple district heating and cooling modeller**

---


## Project Overview

**DHNpype** models steady-state heat losses and flow properties for a single branch (supply + return) of a district heating & cooling network pipeline.

The software was developed as part of a reserach project at the University of Ljubljana (Slovenia) to support studies of energy transformation scenarios. 

Support from the 3DIVERSE project (www.3dvierse.eu, LIFE21-CET-PDA-3DiVERSE, No. 101077343) is gratefully acknowledged.


## It calculates:

	- Section-by-section distribution of heat flow losses 
	- Temperature and mass flow evolution along the pipeline
	- System-level cumulative losses
	- Total heat flow in the system
	- Fluid velocities


## Core assumptions:

	- 1D flow with no heat generation inside the pipeline
	- Steady-state thermal and hydraulic conditions
	- Uniform properties per section
	- Constant thermal conductivities


## Project Structure

dhnpype/
├── data
│   ├── network_config_data
│   │   └── input_reference.csv           # Network/branch topology data 
│   ├── __init__.py                       # API
│   ├── display_input_data.py             # Reads and displays input data in a CSV file
│   └── insulation_thickness.json         # Pipe & insulation standard thickness data              
├── src
│   ├── utils
│   │   ├── __init__.py                   # API
│   │   ├── constants.py                  # List of constants used in the program
│   │   ├── exceptions.py                 # List of custom exceptions
│   │   ├── functions.py                  # List of functions used in the program
│   │   └── validation.py                 # Validation of insulation damage input
│   ├── __init__.py                       # Public API & version  
│   ├── branch.py                         # Main calculation orchestrator 
│   ├── config_data.py                    # Model initial setup
│   ├── data_input.py                     # Reading input data from a CSV file 
│   ├── data_output.py                    # Dataframes containing analyses results
│   ├── main.py                           # Main script for running the program when used with Python
│   ├── model_param.py                    # Physical parameters (thermal properties, convection)
│   └── plots.py                          # Visualisation of data
├── tutorials
│   ├── figures
│   │   └── logo.png                      # dhnpype logo
│   └── one_branch.ipynb                  # An example of a 1-branch network simulation in a Jupyter notebook        
├── AUTHOR                                # List of contributors
├── LICENSE                               # Software license
├── README.md                             # This file
└── requirements.txt                      # Package dependencies

