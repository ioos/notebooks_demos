## Shore Station Compliance Checker Script

The IOOS Compliance Checker is a Python-based tool that helps users check the meta data compliance of a netCDF file. This software can be run in a web interface here: https://data.ioos.us/compliance/index.html The checker can also be run as a Python tool either on the command line or in a Python script.  This notebook demonstrates the python usage of the Compliance Checker.


### Purpose: 
Run the compliance checker python tool on a Scipps Pier shore station dataset to check for the metadata compliance.

The Scripps Pier automated shore station operated by Southern California Coastal Ocean Observing System (SCCOOS) at Scripps Institution of Oceanography (SIO) is mounted at a nominal depth of 5 meters MLLW. The instrument package includes a Seabird SBE 16plus SEACAT Conductivity, Temperature, and Pressure recorder, and a Seapoint Chlorophyll Fluorometer with a 0-50 ug/L gain setting.

### Dependencies: 
This script must be run in the "IOOS" environment for the compliance checker to work properly.

Written by: J.Bosch Feb. 10, 2017



import compliance_checker

print(compliance_checker.__version__)

# First import the compliance checker and test that it is installed properly.
from compliance_checker.runner import CheckSuite, ComplianceChecker

# Load all available checker classes.
check_suite = CheckSuite()
check_suite.load_all_available_checkers()

# Path to the Scripps Pier Data.


# See https://github.com/Unidata/netcdf-c/issues/1299
# for the reason we need to append `#fillmismatch` to the URL.
url = "http://data.ioos.us/thredds/dodsC/deployments/rutgers/ru29-20150623T1046/ru29-20150623T1046.nc3.nc#fillmismatch"

### Running Compliance Checker on the Scripps Pier shore station data
This code is written with all the arguments spelled out, following the usage instructions on the README section of compliance checker github page: https://github.com/ioos/compliance-checker

output_file = "buoy_testCC.txt"

return_value, errors = ComplianceChecker.run_checker(
    ds_loc=url,
    checker_names=["cf", "acdd"],
    verbose=True,
    criteria="normal",
    skip_checks=None,
    output_filename=output_file,
    output_format="text",
)

with open(output_file, "r") as f:
    print(f.read())

This Compliance Checker Report can be used to identify where file meta data can be improved.  A strong meta data record allows for greater utility of the data for a broader audience of data analysts.