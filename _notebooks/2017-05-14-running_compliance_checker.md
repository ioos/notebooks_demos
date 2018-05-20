---
title: ""
layout: notebook

---
## Shore Station Compliance Checker Script

The IOOS Compliance Checker is a Python-based tool that helps users check the meta data compliance of a netCDF file. This software can be run in a web interface here: https://data.ioos.us/compliance/index.html The checker can also be run as a Python tool either on the command line or in a Python script.  This notebook demonstrates the python usage of the Compliance Checker.


### Purpose: 
Run the compliance checker python tool on a Scipps Pier shore station dataset to check for the metadata compliance.

The Scripps Pier automated shore station operated by Southern California Coastal Ocean Observing System (SCCOOS) at Scripps Institution of Oceanography (SIO) is mounted at a nominal depth of 5 meters MLLW. The instrument package includes a Seabird SBE 16plus SEACAT Conductivity, Temperature, and Pressure recorder, and a Seapoint Chlorophyll Fluorometer with a 0-50 ug/L gain setting.

### Dependencies: 
This script must be run in the "IOOS" environment for the compliance checker to work properly.

Written by: J.Bosch Feb. 10, 2017



<div class="prompt input_prompt">
In&nbsp;[1]:
</div>

```python
import compliance_checker

print(compliance_checker.__version__)
```
<div class="output_area"><div class="prompt"></div>
<pre>
    4.0.0

</pre>
</div>
<div class="prompt input_prompt">
In&nbsp;[2]:
</div>

```python
# First import the compliance checker and test that it is installed properly.
from compliance_checker.runner import ComplianceChecker, CheckSuite

# Load all available checker classes.
check_suite = CheckSuite()
check_suite.load_all_available_checkers()
```

<div class="prompt input_prompt">
In&nbsp;[3]:
</div>

```python
# Path to the Scripps Pier Data.

buoy_path = 'https://data.nodc.noaa.gov/thredds/dodsC/ioos/sccoos/scripps_pier/scripps_pier-2016.nc'
```

### Running Compliance Checker on the Scripps Pier shore station data
This code is written with all the arguments spelled out, following the usage instructions on the README section of compliance checker github page: https://github.com/ioos/compliance-checker

<div class="prompt input_prompt">
In&nbsp;[4]:
</div>

```python
output_file = 'buoy_testCC.txt'

return_value, errors = ComplianceChecker.run_checker(
    ds_loc=buoy_path,
    checker_names=['cf', 'acdd'],
    verbose=True,
    criteria='normal',
    skip_checks=None,
    output_filename=output_file,
    output_format='text'
)
```
<div class="warning" style="border:thin solid red">
    Using cached standard name table v28 from
/home/filipe/.local/share/compliance-checker/cf-standard-name-table-test-28.xml

</div>
<div class="prompt input_prompt">
In&nbsp;[5]:
</div>

```python
with open(output_file, 'r') as f:
    print(f.read())
```
<div class="output_area"><div class="prompt"></div>
<pre>
    
    
    --------------------------------------------------------------------------------
                             IOOS Compliance Checker Report                         
                                      cf:1.6 check                                  
    --------------------------------------------------------------------------------
                                   Corrective Actions                               
    scripps_pier-2016.nc has 1 potential issue
    
    
                                        Warnings                                    
    --------------------------------------------------------------------------------
    Name                                     Reasoning
    §2.3 Naming Conventions for attributes:  attribute time:_Netcdf4Dimid should
                                             begin with a letter and be composed of
                                             letters, digits, and underscores
    
    
    --------------------------------------------------------------------------------
                             IOOS Compliance Checker Report                         
                                     acdd:1.3 check                                 
    --------------------------------------------------------------------------------
                                   Corrective Actions                               
    scripps_pier-2016.nc has 17 potential issues
    
    
                                   Highly Recommended                               
    --------------------------------------------------------------------------------
    Name                         Reasoning
    variable aux1:               Var aux1 missing attribute
                                 coverage_content_type Var aux1 missing
                                 attribute standard_name
    variable aux3:               Var aux3 missing attribute
                                 coverage_content_type Var aux3 missing
                                 attribute standard_name
    variable aux4:               Var aux4 missing attribute
                                 coverage_content_type Var aux4 missing
                                 attribute standard_name
    variable chlorophyll:        Var chlorophyll missing attribute
                                 coverage_content_type
    variable chlorophyll_raw:    Var chlorophyll_raw missing attribute
                                 coverage_content_type
    variable conductivity:       Var conductivity missing attribute
                                 coverage_content_type
    variable currentDraw:        Var currentDraw missing attribute
                                 coverage_content_type Var currentDraw
                                 missing attribute standard_name
    variable diagnosticVoltage:  Var diagnosticVoltage missing attribute
                                 coverage_content_type Var
                                 diagnosticVoltage missing attribute
                                 standard_name
    variable pressure:           Var pressure missing attribute
                                 coverage_content_type
    variable salinity:           Var salinity missing attribute
                                 coverage_content_type
    variable sigmat:             Var sigmat missing attribute
                                 coverage_content_type
    variable temperature:        Var temperature missing attribute
                                 coverage_content_type
    

</pre>
</div>
This Compliance Checker Report can be used to identify where file meta data can be improved.  A strong meta data record allows for greater utility of the data for a broader audience of data analysts.
<br>
Right click and choose Save link as... to
[download](https://raw.githubusercontent.com/ioos/notebooks_demos/master/notebooks/2017-05-14-running_compliance_checker.ipynb)
this notebook, or click [here](https://beta.mybinder.org/v2/gh/ioos/notebooks_demos/master?filepath=notebooks/2017-05-14-running_compliance_checker.ipynb) to run a live instance of this notebook.