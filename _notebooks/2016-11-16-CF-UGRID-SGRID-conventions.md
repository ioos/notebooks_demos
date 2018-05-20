---
title: "Parsing Conventions and standards with Python"
layout: notebook

---

Metadata conventions, like the Climate and Forecast (CF) conventions,
can be cumbersome to adhere to but it will be very handy when you or other users manipulate the data later in time.

In this notebook we will explore three Python modules that parse [`CF-1.6`](http://cfconventions.org/cf-conventions/v1.6.0/cf-conventions.html),
[`UGRID-1.0`](http://ugrid-conventions.github.io/ugrid-conventions/),
and [`SGRID-0.3`](http://sgrid.github.io/sgrid/)

### CF-1.6 with iris

There are many Python libraries to read and write CF metdata,
but only [`iris`](http://scitools.org.uk/iris/) encapsulates CF in an object with an API.
From iris own docs:

*Iris seeks to provide a powerful, easy to use, and community-driven Python library for analysing and visualising meteorological and oceanographic data sets.*

With iris you can:

- Use a single API to work on your data, irrespective of its original format.
- Read and write (CF-)netCDF, GRIB, and PP files.
- Easily produce graphs and maps via integration with matplotlib and cartopy.

<div class="prompt input_prompt">
In&nbsp;[1]:
</div>

```python
import iris

iris.FUTURE.netcdf_promote = True

url = 'http://tds.marine.rutgers.edu/thredds/dodsC/roms/espresso/2013_da/his/ESPRESSO_Real-Time_v2_History_fmrc.ncd'

cubes = iris.load(url)
```
<div class="warning" style="border:thin solid red">
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/__init__.py:237: IrisDeprecation: setting the 'Future' property
'netcdf_promote' is deprecated and will be removed in a future release. Please
remove code that sets this property.
      warn_deprecated(msg.format(name))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/cf.py:1069: UserWarning: Ignoring formula terms
variable 'zeta' referenced by data variable 'v' via variable 's_rho': Dimensions
('run', 'time', 'eta_rho', 'xi_rho') do not span ('run', 'time', 's_rho',
'eta_v', 'xi_v')
      warnings.warn(msg)
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/cf.py:1069: UserWarning: Ignoring formula terms
variable 'h' referenced by data variable 'v' via variable 's_rho': Dimensions
('eta_rho', 'xi_rho') do not span ('run', 'time', 's_rho', 'eta_v', 'xi_v')
      warnings.warn(msg)
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/cf.py:1069: UserWarning: Ignoring formula terms
variable 'zeta' referenced by data variable 'u' via variable 's_rho': Dimensions
('run', 'time', 'eta_rho', 'xi_rho') do not span ('run', 'time', 's_rho',
'eta_u', 'xi_u')
      warnings.warn(msg)
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/cf.py:1069: UserWarning: Ignoring formula terms
variable 'h' referenced by data variable 'u' via variable 's_rho': Dimensions
('eta_rho', 'xi_rho') do not span ('run', 'time', 's_rho', 'eta_u', 'xi_u')
      warnings.warn(msg)
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/netcdf.py:585: UserWarning: Unable to find coordinate
for variable 'zeta'
      '{!r}'.format(name))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/netcdf.py:585: UserWarning: Unable to find coordinate
for variable 'h'
      '{!r}'.format(name))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/netcdf.py:705: UserWarning: Unable to construct Ocean
s-coordinate, generic form 1 factory due to insufficient source coordinates.
      warnings.warn('{}'.format(e))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/netcdf.py:585: UserWarning: Unable to find coordinate
for variable 'zeta'
      '{!r}'.format(name))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/netcdf.py:585: UserWarning: Unable to find coordinate
for variable 'h'
      '{!r}'.format(name))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/netcdf.py:705: UserWarning: Unable to construct Ocean
s-coordinate, generic form 1 factory due to insufficient source coordinates.
      warnings.warn('{}'.format(e))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1813:
FutureWarning: Conversion of the second argument of issubdtype from `str` to
`str` is deprecated. In future, it will be treated as `np.str_ ==
np.dtype(str).type`.
      if np.issubdtype(cf_var.dtype, np.str):

</div>
**Aside:** using `iris.FUTURE.netcdf_promote = True` we can promote netCDF formula terms,
like sea surface height, to first class cube objects.
This behavior will be default in future versions of `iris` and that line will not be needed after the next version of iris is released.

<div class="prompt input_prompt">
In&nbsp;[2]:
</div>

```python
print(cubes)
```
<div class="output_area"><div class="prompt"></div>
<pre>
    0: number of time-steps between the creation of history files / (1) (scalar cube)
    1: quadratic drag coefficient / (1)    (scalar cube)
    2: grid / (1)                          (scalar cube)
    3: curvilinear coordinate metric in XI / (meter-1) (-- : 82; -- : 130)
    4: Power-law shape barotropic filter parameter / (1) (scalar cube)
    5: 2D momentum inflow, nudging inverse time scale / (second-1) (-- : 4)
    6: mean density used in Boussinesq approximation / (kilogram meter-3) (scalar cube)
    7: bottom roughness / (meter)          (scalar cube)
    8: 2D momentum outflow, nudging inverse time scale / (second-1) (-- : 4)
    9: vertically integrated u-momentum component / (meter second-1) (forecast_reference_time: 1729; -- : 157; -- : 82; -- : 129)
    10: surface v-momentum stress / (newton meter-2) (forecast_reference_time: 1729; -- : 157; -- : 81; -- : 130)
    11: free-surface inflow, nudging inverse time scale / (second-1) (-- : 4)
    12: Power-law shape barotropic filter parameter / (1) (scalar cube)
    13: bottom u-momentum stress / (newton meter-2) (forecast_reference_time: 1729; -- : 157; -- : 82; -- : 129)
    14: background vertical mixing coefficient for momentum / (meter2 second-1) (scalar cube)
    15: mask on RHO-points / (1)            (-- : 82; -- : 130)
    16: shear production coefficient / (1)  (scalar cube)
    17: time averaged u-flux for 3D equations coupling / (meter3 second-1) (forecast_reference_time: 1729; -- : 157; -- : 82; -- : 129)
    18: nonlinear model Laplacian mixing coefficient for tracers / (meter2 second-1) (-- : 2)
    19: background vertical mixing coefficient for length scale / (meter2 second-1) (scalar cube)
    20: dissipation coefficient / (1)       (scalar cube)
    21: mask on V-points / (1)              (-- : 81; -- : 130)
    22: surface roughness / (meter)         (scalar cube)
    23: S-coordinate surface/bottom layer width / (meter) (scalar cube)
    24: minimum value of specific turbulent kinetic energy / (1) (scalar cube)
    25: Charnok factor for surface roughness / (1) (scalar cube)
    26: S-coordinate bottom control parameter / (1) (scalar cube)
    27: time averaged v-flux for 2D equations / (meter3 second-1) (forecast_reference_time: 1729; -- : 157; -- : 81; -- : 130)
    28: NetCDF-4/HDF5 file format deflate filer flag / (1) (scalar cube)
    29: domain length in the ETA-direction / (meter) (scalar cube)
    30: time averaged v-flux for 3D equations coupling / (meter3 second-1) (forecast_reference_time: 1729; -- : 157; -- : 81; -- : 130)
    31: curvilinear coordinate metric in ETA / (meter-1) (-- : 82; -- : 130)
    32: 3D momentum nudging/relaxation inverse time scale / (day-1) (scalar cube)
    33: minimum Value of dissipation / (1)  (scalar cube)
    34: surface net heat flux / (watt meter-2) (forecast_reference_time: 1729; -- : 157; -- : 82; -- : 130)
    35: number of time-steps between time-averaged records / (1) (scalar cube)
    36: linear drag coefficient / (meter second-1) (scalar cube)
    37: S-coordinate surface control parameter / (1) (scalar cube)
    38: number of time-steps between restart records / (1) (scalar cube)
    39: tracer point sources and sink activation switch / (1) (-- : 2)
    40: size of long time-steps / (second)  (scalar cube)
    41: wave amplitude factor for surface roughness / (1) (scalar cube)
    42: NetCDF-4/HDF5 file format shuffle filer flag / (1) (scalar cube)
    43: size of short time-steps / (second) (scalar cube)
    44: mask on U-points / (1)              (-- : 82; -- : 129)
    45: buoyancy production coefficient (plus) / (1) (scalar cube)
    46: tracers outflow, nudging inverse time scale / (second-1) (-- : 4; -- : 2)
    47: constant Schmidt number for PSI / (1) (scalar cube)
    48: surface flux due to Craig and Banner wave breaking / (1) (scalar cube)
    49: starting time-step for accumulation of time-averaged fields / (1) (scalar cube)
    50: bottom v-momentum stress / (newton meter-2) (forecast_reference_time: 1729; -- : 157; -- : 81; -- : 130)
    51: number of long time-steps / (1)     (scalar cube)
    52: vertical terrain-following transformation equation / (1) (scalar cube)
    53: turbulent length scale exponent / (1) (scalar cube)
    54: vertical terrain-following stretching function / (1) (scalar cube)
    55: buoyancy production coefficient (minus) / (1) (scalar cube)
    56: domain length in the XI-direction / (meter) (scalar cube)
    57: turbulent kinetic energy exponent / (1) (scalar cube)
    58: Power-law shape barotropic filter parameter / (1) (scalar cube)
    59: NetCDF-4/HDF5 file format deflate level parameter / (1) (scalar cube)
    60: background vertical mixing coefficient for tracers / (meter2 second-1) (-- : 2)
    61: slipperiness parameter / (1)        (scalar cube)
    62: tracers inflow, nudging inverse time scale / (second-1) (-- : 4; -- : 2)
    63: stability coefficient / (1)         (scalar cube)
    64: surface flux from wave dissipation / (1) (scalar cube)
    65: angle between XI-axis and EAST / (radians) (-- : 82; -- : 130)
    66: Coriolis parameter at RHO-points / (second-1) (-- : 82; -- : 130)
    67: 2D momentum nudging/relaxation inverse time scale / (day-1) (scalar cube)
    68: number of time-steps between history records / (1) (scalar cube)
    69: free-surface nudging/relaxation inverse time scale / (day-1) (scalar cube)
    70: time stamp assigned to model initilization / (days since 2006-01-01 00:00:00) (scalar cube)
    71: grid type logical switch / (1)      (scalar cube)
    72: 3D momentum inflow, nudging inverse time scale / (second-1) (-- : 4)
    73: constant Schmidt number for TKE / (1) (scalar cube)
    74: number of short time-steps / (1)    (scalar cube)
    75: nonlinear model Laplacian mixing coefficient for momentum / (meter2 second-1) (scalar cube)
    76: time averaged u-flux for 2D equations / (meter3 second-1) (forecast_reference_time: 1729; -- : 157; -- : 82; -- : 129)
    77: free-surface outflow, nudging inverse time scale / (second-1) (-- : 4)
    78: Tracers nudging/relaxation inverse time scale / (day-1) (-- : 2)
    79: surface u-momentum stress / (newton meter-2) (forecast_reference_time: 1729; -- : 157; -- : 82; -- : 129)
    80: 3D momentum outflow, nudging inverse time scale / (second-1) (-- : 4)
    81: stability exponent / (1)            (scalar cube)
    82: background vertical mixing coefficient for turbulent energy / (meter2 second-1) (scalar cube)
    83: vertically integrated v-momentum component / (meter second-1) (forecast_reference_time: 1729; -- : 157; -- : 81; -- : 130)
    84: number of time-steps between the creation of average files / (1) (scalar cube)
    85: vertical momentum component / (meter second-1) (forecast_reference_time: 1729; -- : 157; ocean_s_coordinate_g1: 37; -- : 82; -- : 130)
    86: mask on psi-points / (1)            (-- : 81; -- : 129)
    87: eastward_sea_water_velocity / (meter second-1) (forecast_reference_time: 1729; -- : 157; ocean_s_coordinate_g1: 36; -- : 82; -- : 129)
    88: northward_sea_water_velocity / (meter second-1) (forecast_reference_time: 1729; -- : 157; ocean_s_coordinate_g1: 36; -- : 81; -- : 130)
    89: sea_floor_depth / (meter)           (-- : 82; -- : 130)
    90: sea_surface_height / (meter)        (forecast_reference_time: 1729; -- : 157; -- : 82; -- : 130)
    91: sea_water_potential_temperature / (Celsius) (forecast_reference_time: 1729; -- : 157; ocean_s_coordinate_g1: 36; -- : 82; -- : 130)
    92: sea_water_salinity / (1)            (forecast_reference_time: 1729; -- : 157; ocean_s_coordinate_g1: 36; -- : 82; -- : 130)

</pre>
</div>
The advantages of the CF data model here are:

- high level variable access via `standard_name` or `long_name`;
- verbose warnings when there are compliance issues (see the units warnings above);
- raise errors for non-compliant datasets;
- separation of each phenomena (`variable`) into its own cube\*;
- each cube is a fully self-described format with all the original metadata;
- round-trip load-save to netCDF is lossless;
- free interpretation of the `formula_terms`, `cell_methods`, and `axis` that helps with dimensionless coordinates, climatological variables, and plotting routines respectively.

\* Most people miss the concept of a "dataset" when using `iris`,
but that is a consequence of the CF model.
Since there is no rule for unique names for the variables the dataset may contain the same phenomena with different coordinates,
hence iris decides to create an individual cube for each phenomena.

Aside: note that the [xarray](http://xarray.pydata.org/en/stable/) **does** have a dataset concept,
but it infringes the CF model in many places to do so.
We recommend `xarray` when CF compliance is not a requirement.


For more on iris see [this example](http://bit.ly/2geJhGU).

Moving on, let's extract a single phenomena from the list of cubes above.

<div class="prompt input_prompt">
In&nbsp;[3]:
</div>

```python
cube = cubes.extract_strict('sea_surface_height')

print(cube)
```
<div class="output_area"><div class="prompt"></div>
<pre>
    sea_surface_height / (meter)        (forecast_reference_time: 1729; -- : 157; -- : 82; -- : 130)
         Dimension coordinates:
              forecast_reference_time                           x          -         -        -
         Auxiliary coordinates:
              time                                              x          x         -        -
              latitude                                          -          -         x        x
              longitude                                         -          -         x        x
         Attributes:
              CPP_options: MyCPP, ADD_FSOBC, ADD_M2OBC, ANA_BSFLUX, ANA_BTFLUX, ASSUMED_SHAPE, AVERAGES,...
              Conventions: CF-1.4, SGRID-0.3
              DODS_EXTRA.Unlimited_Dimension: ocean_time
              EXTRA_DIMENSION.N: 36
              _ChunkSizes: [  1  82 130]
              _CoordSysBuilder: ucar.nc2.dataset.conv.CF1Convention
              ana_file: ROMS/Functionals/ana_btflux.h, /home/julia/ROMS/espresso/RealTime/Comp...
              avg_base: espresso_avg_4424
              bry_file: ../Data/espresso_bdry_new.nc
              cdm_data_type: GRID
              clm_file: ../Data/espresso_clm_new.nc
              code_dir: /home/julia/ROMS/espresso/svn1409
              compiler_command: /opt/pgisoft/openmpi/bin/mpif90
              compiler_flags:  -O3 -Mfree
              compiler_system: pgi
              cpu: x86_64
              featureType: GRID
              field: free-surface, scalar, series
              file: espresso_his_4424_0001.nc
              flt_file: espresso_flt_4424.nc
              format: netCDF-4/HDF5 file
              fpos_file: /home/om/cron/glider_floats/data/maracoos_floats.in
              frc_file_01: /home/om/roms/espresso/Data/espresso_tide_c05_20060101.nc
              frc_file_02: ../Data/espresso_river.nc
              frc_file_03: ../Data/rain_ncepnam_3hourly_MAB_and_GoM.nc
              frc_file_04: ../Data/swrad_ncepnam_3hourly_MAB_and_GoM.nc
              frc_file_05: ../Data/Tair_ncepnam_3hourly_MAB_and_GoM.nc
              frc_file_06: ../Data/Pair_ncepnam_3hourly_MAB_and_GoM.nc
              frc_file_07: ../Data/Qair_ncepnam_3hourly_MAB_and_GoM.nc
              frc_file_08: ../Data/lwrad_down_ncepnam_3hourly_MAB_and_GoM.nc
              frc_file_09: ../Data/Uwind_ncepnam_3hourly_MAB_and_GoM.nc
              frc_file_10: ../Data/Vwind_ncepnam_3hourly_MAB_and_GoM.nc
              grd_file: /home/om/roms/espresso/Data/espresso_grid_c05.nc
              header_dir: /home/julia/ROMS/espresso/RealTime/Compile/fwd
              header_file: espresso.h
              his_base: espresso_his_4424
              history: ROMS/TOMS, Version 3.5, Wednesday - February 14, 2018 -  5:11:59 AM ;
    FMRC...
              ini_file: /home/julia/ROMS/espresso/RealTime/Storage/run04/espresso_ini_4424.nc
              location: Proto fmrc:espresso_2013_da_his
              os: Linux
              rst_file: espresso_rst_4424.nc
              script_file: nl_ocean_espresso.in
              summary: Operational nowcast/forecast system version 2 for MARACOOS project (http://maracoos.org)....
              svn_rev: exported
              svn_url: https://www.myroms.org/svn/src/trunk
              tiling: 004x002
              time: ocean_time
              title: ROMS ESPRESSO Real-Time Operational IS4DVAR Forecast System Version 2 (NEW)...
              type: ROMS/TOMS history file

</pre>
</div>
Requesting a vertical profile of temperature to see the `formula_terms` parsing in action.
(Note that `ocean_s_coordinate_g1` is actually `CF-1.7` but was backported to `iris` because it is widely adopted and the CF conventions document evolves quite slowly.)

<div class="prompt input_prompt">
In&nbsp;[4]:
</div>

```python
temp = cubes.extract_strict('sea_water_potential_temperature')

print(temp)
```
<div class="output_area"><div class="prompt"></div>
<pre>
    sea_water_potential_temperature / (Celsius) (forecast_reference_time: 1729; -- : 157; ocean_s_coordinate_g1: 36; -- : 82; -- : 130)
         Dimension coordinates:
              forecast_reference_time                                   x          -                           -        -        -
              ocean_s_coordinate_g1                                     -          -                           x        -        -
         Auxiliary coordinates:
              time                                                      x          x                           -        -        -
              sea_surface_height                                        x          x                           -        x        x
              S-coordinate stretching curves at RHO-points              -          -                           x        -        -
              latitude                                                  -          -                           -        x        x
              longitude                                                 -          -                           -        x        x
              sea_floor_depth                                           -          -                           -        x        x
         Derived coordinates:
              sea_surface_height_above_reference_ellipsoid              x          x                           x        x        x
         Scalar coordinates:
              S-coordinate parameter, critical depth: 5.0 meter
         Attributes:
              CPP_options: MyCPP, ADD_FSOBC, ADD_M2OBC, ANA_BSFLUX, ANA_BTFLUX, ASSUMED_SHAPE, AVERAGES,...
              Conventions: CF-1.4, SGRID-0.3
              DODS_EXTRA.Unlimited_Dimension: ocean_time
              EXTRA_DIMENSION.N: 36
              _ChunkSizes: [  1  36  82 130]
              _CoordSysBuilder: ucar.nc2.dataset.conv.CF1Convention
              ana_file: ROMS/Functionals/ana_btflux.h, /home/julia/ROMS/espresso/RealTime/Comp...
              avg_base: espresso_avg_4424
              bry_file: ../Data/espresso_bdry_new.nc
              cdm_data_type: GRID
              clm_file: ../Data/espresso_clm_new.nc
              code_dir: /home/julia/ROMS/espresso/svn1409
              compiler_command: /opt/pgisoft/openmpi/bin/mpif90
              compiler_flags:  -O3 -Mfree
              compiler_system: pgi
              cpu: x86_64
              featureType: GRID
              field: temperature, scalar, series
              file: espresso_his_4424_0001.nc
              flt_file: espresso_flt_4424.nc
              format: netCDF-4/HDF5 file
              fpos_file: /home/om/cron/glider_floats/data/maracoos_floats.in
              frc_file_01: /home/om/roms/espresso/Data/espresso_tide_c05_20060101.nc
              frc_file_02: ../Data/espresso_river.nc
              frc_file_03: ../Data/rain_ncepnam_3hourly_MAB_and_GoM.nc
              frc_file_04: ../Data/swrad_ncepnam_3hourly_MAB_and_GoM.nc
              frc_file_05: ../Data/Tair_ncepnam_3hourly_MAB_and_GoM.nc
              frc_file_06: ../Data/Pair_ncepnam_3hourly_MAB_and_GoM.nc
              frc_file_07: ../Data/Qair_ncepnam_3hourly_MAB_and_GoM.nc
              frc_file_08: ../Data/lwrad_down_ncepnam_3hourly_MAB_and_GoM.nc
              frc_file_09: ../Data/Uwind_ncepnam_3hourly_MAB_and_GoM.nc
              frc_file_10: ../Data/Vwind_ncepnam_3hourly_MAB_and_GoM.nc
              grd_file: /home/om/roms/espresso/Data/espresso_grid_c05.nc
              header_dir: /home/julia/ROMS/espresso/RealTime/Compile/fwd
              header_file: espresso.h
              his_base: espresso_his_4424
              history: ROMS/TOMS, Version 3.5, Wednesday - February 14, 2018 -  5:11:59 AM ;
    FMRC...
              ini_file: /home/julia/ROMS/espresso/RealTime/Storage/run04/espresso_ini_4424.nc
              location: Proto fmrc:espresso_2013_da_his
              os: Linux
              rst_file: espresso_rst_4424.nc
              script_file: nl_ocean_espresso.in
              summary: Operational nowcast/forecast system version 2 for MARACOOS project (http://maracoos.org)....
              svn_rev: exported
              svn_url: https://www.myroms.org/svn/src/trunk
              tiling: 004x002
              time: ocean_time
              title: ROMS ESPRESSO Real-Time Operational IS4DVAR Forecast System Version 2 (NEW)...
              type: ROMS/TOMS history file

</pre>
</div>
<div class="prompt input_prompt">
In&nbsp;[5]:
</div>

```python
temp = cubes.extract_strict('sea_water_potential_temperature')

# Surface at the last time step.
T = temp[-1, -1, -1, ...]

# Random profile at the last time step.
t_profile = temp[-1, -1, :, 42, 42]
```

<div class="prompt input_prompt">
In&nbsp;[6]:
</div>

```python
t_profile.coords(axis='Z')
```




    [DimCoord(array([-0.98611111, -0.95833333, -0.93055556, -0.90277778, -0.875     ,
            -0.84722222, -0.81944444, -0.79166667, -0.76388889, -0.73611111,
            -0.70833333, -0.68055556, -0.65277778, -0.625     , -0.59722222,
            -0.56944444, -0.54166667, -0.51388889, -0.48611111, -0.45833333,
            -0.43055556, -0.40277778, -0.375     , -0.34722222, -0.31944444,
            -0.29166667, -0.26388889, -0.23611111, -0.20833333, -0.18055556,
            -0.15277778, -0.125     , -0.09722222, -0.06944444, -0.04166667,
            -0.01388889]), standard_name='ocean_s_coordinate_g1', units=Unit('1'), long_name='S-coordinate at RHO-points', var_name='s_rho', attributes={'_CoordinateAxes': 's_rho', '_CoordinateAxisType': 'GeoZ', '_CoordinateTransformType': 'Vertical', '_CoordinateZisPositive': 'up', 'field': 's_rho, scalar', 'positive': 'up', 'valid_max': 0.0, 'valid_min': -1.0}),
     AuxCoord(array([-27.93991926, -26.02657111, -24.33268167, -22.82656981,
            -21.47974051, -20.26625215, -19.16214531, -18.14494758,
            -17.19328798, -16.28667866, -15.40554864, -14.53163314,
            -13.64881192, -12.74442096, -11.81090648, -10.84745705,
             -9.86102258,  -8.86607324,  -7.88272573,  -6.93345862,
             -6.03927123,  -5.21641605,  -4.47455945,  -3.81659303,
             -3.23972423,  -2.73720038,  -2.30007696,  -1.91866789,
             -1.58354969,  -1.28614678,  -1.01899546,  -0.77579426,
             -0.55133081,  -0.34134892,  -0.14239628,   0.04832434]), standard_name='sea_surface_height_above_reference_ellipsoid', units=Unit('meter'), attributes={'positive': 'up'})]



Iris knows about the metadata and can create fully annotated plots.

<div class="prompt input_prompt">
In&nbsp;[7]:
</div>

```python
%matplotlib inline

import numpy.ma as ma
import iris.quickplot as qplt

T.data = ma.masked_invalid(T.data)

qplt.pcolormesh(T);
```
<div class="warning" style="border:thin solid red">
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/matplotlib/cbook/deprecation.py:106: MatplotlibDeprecationWarning: The
mpl_toolkits.axes_grid module was deprecated in version 2.1. Use
mpl_toolkits.axes_grid1 and mpl_toolkits.axisartist provies the same
functionality instead.
      warnings.warn(message, mplDeprecation, stacklevel=1)
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/iris/fileformats/netcdf.py:395: RuntimeWarning: invalid value
encountered in greater
      var = variable[keys]

</div>

![png](data:image/png;base64,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
)


<div class="prompt input_prompt">
In&nbsp;[8]:
</div>

```python
qplt.plot(t_profile);
```


![png](data:image/png;base64,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
)


Be aware that too much automation may lead to some weird plots.

For example, the z-coord is in the x-direction and the automatic naming of the z to Sea surface height is above the reference ellipsoid in the second plot. Another example is the lack of proper coordinates in the first plot.

In these cases, manual plotting is more appropriate.

<div class="prompt input_prompt">
In&nbsp;[9]:
</div>

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(3, 7))

t = t_profile.data
z = t_profile.coord('sea_surface_height_above_reference_ellipsoid').points

ax.plot(t, z);
```


![png](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAANUAAAGfCAYAAADI9Jc9AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEgAACxIB0t1+/AAAADl0RVh0U29mdHdhcmUAbWF0cGxvdGxpYiB2ZXJzaW9uIDIuMS4yLCBodHRwOi8vbWF0cGxvdGxpYi5vcmcvNQv5yAAAGu9JREFUeJzt3XuU1OWd5/H3ty7dTQMNzR2B7gYFFG8IHQNeohPZM5qb0Vw0mxhjMsO4m+zs7F8Zj2fPzuRMduJMEv9xZhJ2T+LoujGZREdHkyhMLptB0QDiBRGCQDfN/dJ0N/Slbt/9o6oZJI2A9VRX/ao+r3M4p7uq+vk9rfXp53m+v+f3K3N3RCScWLk7IFJtFCqRwBQqkcAUKpHAFCqRwBQqkcAUKpHAFCqRwBQqkcAS5e7AqaZMmeJtbW3l7obIiDZs2HDY3aee7XUVFaq2tjbWr19f7m6IjMjMOs7ldZr+iQSmUIkEplCJBKZQiQSmUIkEplCJBKZQiQSmUIkEplCJBKZQiQSmUIkEplCJBKZQiQRW8lCZ2c1mttXMtpvZn5f6eCLlVtJQmVkc+DvgFmAR8BkzW1TKY4qci2P9KTbv7SlJ26Ueqa4Gtrv7DndPAY8Dt5b4mCJn9Xe/3M7tf/8CpbjtealDNQvYfcr3XYXHTjKzlWa23szWHzp0qMTdEclrmdTIUCbHob6h4G2XOlQ2wmPv+NPg7qvcvd3d26dOPeuVyiJBzJnUCEDH0f7gbZc6VF3AnFO+nw3sLfExRc5qdnM+VHu6B4K3XepQ/RaYb2ZzzawOuBN4usTHFDmrWRPHANDVHX6kKumNX9w9Y2ZfAZ4D4sD33H1zKY8pci7G1MWZNLaOvT2Dwdsu+d2U3P2nwE9LfRyR8zV1XH0kCxUiFWvK+DoOH1eoRIKZPLaeoydSwdtVqKRmTWxMcqw/HbxdhUpq1sTGOnoH02RzYXdVKFRSsyaMSeIOxwczQdtVqKRmNTXki9+9g2GngAqV1KzxDUkAegYUKpEghkeq40Oa/okEMba+ECqtqUTCGFcYqU6kFCqRIMYVRqo+jVQiYTTWxQEYSGWDtqtQSc1qrMuPVP0KlUgY8ZjRkIxpTSUSUmNdQtM/kZDGJOOa/omENKYuzmBaoRIJprEuTr/WVCLhNCTjDGikEgmnIRlnMJ0L2qZCJTWtIRHTmkokJBUqRAJrSGhNJRJUQzKmNZVISPXJOEMZjVQiweQLFbmgn1OlUElNq0/mL/9IZcNNARUqqWkNhVCFXFcpVFLT6hP5CIRcVylUUtOGQ5XKaKQSCaLu5EilUIkEUZ/Ir6mGtKYSCaM+qTWVSFBaU4kEVq81lUhYdfHCyV+FSiSM4eqfdlSIBFKnk78iYdWpUCESVl1coRIJSjsqRAKrV6FCJKxkYfqXzugiRZEg4jEjHjPSGqlEwknGTdM/kZDq4jFV/0RCqkvENP0TCakurlCJBJVMaPonElQyHlOhQiSkZDxGOqvzVCLB1MUjcp7KzP7CzPaY2abCvw+V6lgixUjGY2QCjlSJYC2N7EF3/2aJjyFSFK2pRAJLRGX6V/AVM3vNzL5nZs0lPpbIe1JR56nMbI2ZvTHCv1uBfwAuBBYD+4BvnaGNlWa23szWHzp0qJjuiLwnyXgs6C71otZU7r7iXF5nZv8LeOYMbawCVgG0t7eH+81EzlEyKtuUzGzmKd/eBrxRqmOJFCMZC7tLvZTVv78xs8WAA7uAPynhsUTes0TcolFSd/e7StW2SEjJSipUiFQDhUoksETMyOS0908kmETgbUoKldS8uriRzuVwDxMshUpqXiIewx2ygaaACpXUvETcAIKtqxQqqXnJWOGGmoEqgAqV1LyTI1WgYoVCJTUvMXzr55xGKpEgkjGNVCJBDY9UCpVIIMnCmkrTP5FA4oXpn85TiQSSUEldJKykSuoiYZ0sVGhNJRLGcEk91K2fFSqpeSpUiAR2ckeFChUiYQwXKjRSiQQyPP3TpR8igQyfp1JJXSSQf79IUWsqkSASqv6JhKU1lUhgw2sqjVQigZwcqXSeSiSMhKZ/ImEldPJXJKyT56kUKpEwtKYSCezfd6mHaU+hkppXyBRZfUCBSBhmRjxmZLVNSSSceMAPflOoRMifq8opVCLhxE0jlUhQ8bhGKpGgNFKJBBaPGTmV1EXCicdMl9OLhBSPmU7+ioSUP/mrUIkEEzeFSiSomAoVImHFzQi09U+hEgEw0y51kaDi2vsnEpZK6iKBxVT9EwkrHjMCDVQKlQjkL6nXSCUSUMwqZE1lZp8ys81mljOz9tOeu8/MtpvZVjP7w+K6KVJaIat/iSJ//g3gduC7pz5oZouAO4FLgQuANWa2wN2zRR5PpCQq5tIPd9/i7ltHeOpW4HF3H3L3ncB24OpijiVSSmZGoCs/SrammgXsPuX7rsJjIhUpZhCq/HfW6Z+ZrQFmjPDU/e7+1Jl+bITHRuyxma0EVgK0tLScrTsiJWFAoCXV2UPl7iveQ7tdwJxTvp8N7D1D+6uAVQDt7e2Bfi2R8xMzw0f+u3/+bQVp5fc9DdxpZvVmNheYD7xcomOJFM0qZZe6md1mZl3AcuBZM3sOwN03Az8C3gR+DnxZlT+pZGYEq/4VVVJ39yeBJ8/w3NeBrxfTvshoiY1UBXivbYVrSiS6YlYh56lEqkV++hemLYVKhHyhwjVSiYQT8NyvQiUCw+epArUVqB2RSAtZUleoRBh5X917pVCJBKZQiQSmUIkEplCJBKZQiRToPJVIQGbh6n8KlUhgCpVIYAqVSGAKlUhgCpVIQaXf+EUkUnLuxANVABUqEfJX/cYUKpFwcjkn1KkqhUqE/PRPI5VIQDl34oHuU6ZQiZBfU4XaqqRQiQDuHuyGmgqVCKr+iQSX00glEpbWVCKBues8lUhQ6WyOZCxMHBQqESCTdRJxTf9EgknnnERcI5VIMJlsjqR2VIiEk87mNP0TCSmTdZKa/omEk87lFCqRkDJZJ6E1lUg46ayqfyJBZXI5kipUiISTn/5ppBIJZiiTpT6pUIkEkcnmSGedMcl4kPYUKql5g5kcAA0aqUTCGEhlATRSiYQymM6Hql6hEgljOFQaqUQCGUwPr6kUKpEgBjRSiYQ1PP1T9U8kkIGTodJIJRLEoEIlElbfYAaA8Q2JIO0pVFLzegfTAEwYkwzSXlGhMrNPmdlmM8uZWfspj7eZ2YCZbSr8+07xXRUpjd6BDHXxGPWJMGNMsePdG8DtwHdHeO5td19cZPsiJdc7mKZpTCLYbZ+LCpW7b4Fw96AWKYfegTRNDWGmflDaNdVcM3vFzH5tZteX8DgiRekZSDM+0HoKzmGkMrM1wIwRnrrf3Z86w4/tA1rc/YiZLQX+2cwudffeEdpfCawEaGlpOfeeiwTSO5ihKVDlD84hVO6+4nwbdfchYKjw9QYzextYAKwf4bWrgFUA7e3tfr7HEilW30CaOc1jgrVXkumfmU01s3jh63nAfGBHKY4lUqx8oaJC1lRmdpuZdQHLgWfN7LnCUx8AXjOzV4EfA/e6+9HiuioSnrvTO5AJWqgotvr3JPDkCI//BPhJMW2LjIaBdJZUNkfTmHBrKu2okJp2sHcIgGnjG4K1qVBJTdvfOwjAjCaFSiSIA8OhmlAfrE2FSmravp58qKZrpBIJY3/PIGPr4oyPyDYlkYp3oHeQ6RPCjVKgUEmN2987GLRIAQqV1LgDPQqVSDC5nHOwb0jTP5FQDp8YIpNzjVQioew9NnyOSqESCWLb/j4A5k8bF7RdhUpq1tYDfTQkY7ROHhu0XYVKatbW/X3MnzaeeCzsPVYUKqlZb+3vY+GM8cHbVaikJh05PsTh40NcrFCJhLH1QL5IsWC6QiUSxNZC5U8jlUggW/f30dyYZOr4cNdRDVOopCYNFylKcXdlhUpqTi7nbDvQx8ISrKdAoZIa1HG0n/5UloUzmkrSvkIlNefffncIgGXzJpWkfYVKas4vtx6idXIjc6eE3Z40TKGSmjKYzvLC24e5ccHUkn0ElEIlNeXlnUcZTOe4ceG0kh1DoZKa8quth6hLxFg2b3LJjqFQSU351daDLJ83mTF18ZIdQ6GSmtF5pJ8dh09w48KpJT2OQiU141fbDgKUdD0FCpXUkF++dbCkpfRhCpXUhMF0lhd3HOEPSjxKgUIlNeKlQin9hhKvp0Chkhrx5MYuxiTjLC9hKX2YQiVVb/vBPp56dS+fv6aVhmTpSunDFCqpeg+u+R2NyTh/8oELR+V4CpVUtS37enn2tX3cc+1cJo2tG5VjKlRS1R5cvY3xDQn++Pp5o3ZMhUqq1utdPTz/5gH+6Lp5TGgM90mJZ6NQSdV6cM02JoxJcs91baN6XIVKqtLGzm5+8dZBVn5gHk0BP8/3XChUUpUeXL2NSWPr+MI1baN+bIVKqs7LO4/ym98d5t4b5jG2PjHqx1eopOp8e/VWpo6v565lbWU5vkIlVeWF7YdZt+Mo//nGC0t6IeK7UaikanQe6eevnt3CjKYGPnN1S9n6MfoTTpHAjg9l+Ptfbud//2Yn8Zjx4B1XjsoevzNRqCSycjnniVf28MDP3+JQ3xC3XTWLr958cfAPxj5fCpVE0oaOo3ztX97k1a4erpwzke/etZQlLc3l7hagUEnE7OsZ4Bs/e4unNu1lelM93/70lXx88SxigT+3txgKlUTCQCrLqv+3g3/49XZyDl/5g4v4TzdeWJbzUGdTeT0SOYW788xr+/jrn25hb88gH758Jn9+y8XMmdRY7q6dkUIlFev1rh6+9sxmfrurm0Uzm/j2HYtLemfZUIoKlZn9LfBRIAW8Ddzj7scKz90HfAnIAn/q7s8V2VepEQf7Bvnmc1v5pw1dTGqs469vv5xPt88hXkHrpndT7Ei1GrjP3TNm9gBwH/BVM1sE3AlcClwArDGzBe6eLfJ4UsWGMlm+v3YXD/1iO0OZLH98/Ty+8sGLRn2XebGKCpW7P3/Kt+uATxa+vhV43N2HgJ1mth24GnixmONJdXJ3nn/zAP/zp1voONLPikumcf+HF5X8ppelEnJN9UXgh4WvZ5EP2bCuwmO/x8xWAisBWlrKt7VEymPr/j6+9sxm1m4/wvxp43jki1fzgQWlvzdfKZ01VGa2BpgxwlP3u/tThdfcD2SAx4Z/bITX+0jtu/sqYBVAe3v7iK+R6nP0RIoHV2/jsZc6GN+Q5C8/dimffX8LiXj0t6OeNVTuvuLdnjezu4GPADe5+3AouoA5p7xsNrD3vXZSqkcqk+Oxlzp4cPU2TqSy3LWslT9bsYDmUbrT0Wgotvp3M/BV4AZ37z/lqaeB/2tm3yZfqJgPvFzMsSSauk+keGV3Nxs68v9e3d3DQDrL9fOn8N8/sogF08eXu4vBFbumegioB1YXPj91nbvf6+6bzexHwJvkp4VfVuWv+uVyzo7Dx08GaENHN28fOgFAPGZcekETd7xvDh+8eBrXz59Sss/cLbdiq38XvctzXwe+Xkz7UtlODGV4tesYGwsB2th5jJ6BNAATG5MsbWnm9iWzWdrazBWzJ9BYVxt7DWrjt5SiuTt7jg3kw9PRzYbObrbs6yObyy+jF0wfx4cun8GSlmaWtjYzd8rYqh2JzkahkhENZbJs3tvLxo5uNnbmR6IDvUMANNbFuaplIl++8UKWtDZz1ZzmUb1ZZaVTqASAQ31DbOzsPjmVe21PD6lMDoA5k8awfN5klrY2s6S1mYXTx1dF6btUFKoalM052w70vWMq13EkX7yti8e4bFYTdy9vzYeopZlpTeW9kjZqFKoa0DuYZlPnsUIxoZtXOo9xfCgDwJRxdSxtbeaz729haWszl14woaz3d6gGClWVcXc6jvTnS9qF6dzWA324Q8xg4YwmPn7VBSxtbWZpyyTmTBpTswWFUlGoIm4wneX1PT0nzwtt7OjmyIkUAOPrE1zV2swtl81kaWszV86ZwPiI7fiOIoUqYg70Dr7j5OrmvT2ks/my9twpY7lx4bT8KNTazPxp4yrq3g21QqGqYJlsjrf2970jRHuODQBQn4hx5eyJfOm6eYWCwkQmj6svc48FFKqKcqw/xSuFgsKGjm427T7GQDq/u2t6Uz3trZP44nVzWdrazKKZTdQlVNauRApVmZy6T25jxzE2dHaz/eBxIL9PbtHM/D65JYWp3AUTGlRQiAiFapQMpLK8srv7jPvklrQ0c9tVs1jSki8o1Mo+uWqk/3MltuvwCR5+YRc/3tB18tzQ/GnjuOWy/D65Ja3NzJsyVgWFKqJQlYC782/bD/Pw2l38YutBEjHjw5fP5NbFs7iqZSITG6vngjz5fQpVQP2pDE9s3MPDL+xi+8HjTBlXx3/54Hw+9/4WbfWpIQpVALuP9vPoug4ef7mT3sEMl81q4lufupKPXDmT+oS2/NQaheo9cnfW7TjKwy/sZPWbBzAzbr5sBvdc08bS1mZV6mqYQnWeBtNZntq0h++v3cVb+/tobkxy7w0X8rllrVwwcUy5uycVQKE6R/t6Bnj0xQ5+8HIn3f1pLp4xngc+cTm3Lp6lXd3yDgrVu3B3NnZ28721u/j5G/txd1ZcMp17rp3LsnmTNMWTESlUIxjKZHn2tX18f+0uXt/TQ1NDgi9dN5e7lrVW9Ee4SGVQqE5xsG+Qx9Z18thLnRw+PsRF08bxVx+/jNuXzNIOBzlneqcAr+4+xvfX7uTZ1/eRyTkfXDiNL1zbxnUXVe+96aR0ajZU6WyOn72xn4fX7mRj5zHG1Sf43LJW7l7eRltEP21CKkPNherI8SF+8HInj67r4EDvEG2TG/mLjy7iE0tn66pYCaJmQrV5bw8Pr93FU6/uJZXJcf38KXzj9iu4YcFUbWaVoKo6VJlsjjVbDvC9tbt4eedRxiTjfLp9Nl+4po2LplXfjfGlMlRlqI71p/jhb3fzyIsd7Dk2wOzmMdz/oUv49PvmMGGMpnhSWlUVqmP9Kf7mua08sbGLwXSO5fMm8z8+uoibLpkemQ9hluirqlB98/mt/Oi3u/nk0tl84do2Lp7RVO4uSQ2qmlD1DqZ5YuMePn7VLL7xiSvK3R2pYVVzO54nNnTRn8ry+eWt5e6K1LiqCJW788i6DhbPmcgVsyeWuztS46oiVGu3H2HHoRMapaQiVEWo/vHFXUweW8eHLp9Z7q6IRD9UXd39/OuWA9zxvjm6WFAqQuRD9dhLnQB8dpmmflIZIh2qwXSWx1/uZMUl05ml+0NIhYh0qJ59bR/d/Wnuvqat3F0ROSnSoXrkxV1cOHUs11w4udxdETkpsqHatPsYr3b18Pnlbbo6VypKZEP1yIu7GFsX5/Yls8rdFZF3iGSojhwf4pnX9nH7El2tK5UnkqH64frdpDI57tIOCqlAkQtVNuc8tq6T5fMms2C6rt6VyhO5UP3rlgPsOTagfX5SsSIXqkfXdTBzQgP/YdH0cndFZESRClXHkRP85neH+Y9Xt5CIR6rrUkMi9c7ccfgEANfOn1LmnoicWaRCdaLwQdTj6qvmLgBShSIVqv6hLACNdbrEQypXpEJ1XCOVRECkQjU8/dPH2kglKypUZva3ZvaWmb1mZk+a2cTC421mNmBmmwr/vhOisydSWeriMeoSkfpbIDWm2HfnauAyd78C2Abcd8pzb7v74sK/e4s8DpAfqRrrtZ6SylZUqNz9eXfPFL5dB8wuvktndiKVYaymflLhQs6jvgj87JTv55rZK2b2azO7/kw/ZGYrzWy9ma0/dOjQux7gxFCGsRqppMKd9c++ma0BZozw1P3u/lThNfcDGeCxwnP7gBZ3P2JmS4F/NrNL3b339EbcfRWwCqC9vd3frS/9qSxjVfmTCnfWd6i7r3i3583sbuAjwE3u7oWfGQKGCl9vMLO3gQXA+mI6e3xI0z+pfMVW/24Gvgp8zN37T3l8qpnFC1/PA+YDO4o5FuRP/mr6J5Wu2D/7DwH1wOrCfSLWFSp9HwC+ZmYZIAvc6+5HizyWRiqJhKLeoe5+0Rke/wnwk2LaHkl/KqM1lVS8SJ1FPTGU1XkqqXiRCVUqkyOVzTFO0z+pcJEJVX+qsO9P0z+pcJEJ1YlU/rKPcZr+SYWLTqi0Q10iInKh0rVUUukiE6r+lK76lWiITKiGMvlQ6dMSpdJFJlSpTH6vbVK3JpMKF5l3aDqbA6AuoY/NkcoWuVAlYpHpstSoyLxDh0OV1P0ppMJF5h2ayg6vqTT9k8oWmVBlhtdUKlRIhYvMO/Tk9E+hkgoXmXdoOquSukRDZN6hqczwSKU1lVS2yIQqnc2RiBmFy/ZFKlZkQpXJuaZ+EgmReZemMjlN/SQSIhOqdDanDyaQSIjMuzSdzWn6J5EQmXdpOuskNP2TCIhMqFIaqSQiIvMuzWRz2qIkkRCZd2k6q5K6RENk3qX5QoXWVFL5IhOqVCZHQiOVREBk3qVprakkIiLzLs1vU9L0TypfZEKV36YUme5KDYvM7V4f+MQV1CcVKql8kQnVlXMmlrsLIudEf/pFAlOoRAJTqEQCU6hEAlOoRAJTqEQCU6hEAlOoRAJTqEQCU6hEAlOoRAJTqEQCU6hEAlOoRAJTqEQCM3cvdx9OMrNDQEe5+3EepgCHy92JMqq137/V3aee7UUVFaqoMbP17t5e7n6US63//mei6Z9IYAqVSGAKVXFWlbsDZVbrv/+ItKYSCUwjlUhgCtVZmNlCM9t0yr9eM/uz014zwcz+xcxeNbPNZnZPufpbCmb23wq/1xtm9gMzazjt+Xoz+6GZbTezl8ysrTw9rQwK1Vm4+1Z3X+zui4GlQD/w5Gkv+zLwprtfCdwIfMvM6ka3p6VhZrOAPwXa3f0yIA7cedrLvgR0u/tFwIPAA6Pby8qiUJ2fm4C33f30E9QOjDczA8YBR4HMaHeuhBLAGDNLAI3A3tOevxX4x8LXPwZuKvy3qEkK1fm5E/jBCI8/BFxC/s32OvBf3T03mh0rFXffA3wT6AT2AT3u/vxpL5sF7C68PgP0AJNHs5+VRKE6R4Xp3MeAfxrh6T8ENgEXAIuBh8ysaRS7VzJm1kx+JJpL/vcba2afO/1lI/xozZaVFapzdwuw0d0PjPDcPcATnrcd2AlcPKq9K50VwE53P+TuaeAJ4JrTXtMFzAEoTBEnkJ8C1ySF6tx9hpGnfpCfGt0EYGbTgYXAjlHqV6l1AsvMrLGwTroJ2HLaa54G7i58/UngF17DJ0B18vccmFkj+TXDPHfvKTx2L4C7f8fMLgAeBmaSnwp9w93/T5m6G5yZ/SVwB/niyyvAHwH3A+vd/elCif1R4CryI9Sd7l4tf1TOm0IlEpimfyKBKVQigSlUIoEpVCKBKVQigSlUIoEpVCKBKVQigf1/6inHc4xwVskAAAAASUVORK5CYII=
)


### UGRID-1.0 with pyugrid

The Unstructured Grids convention encompasses any type of grid topology,
and the details of the convention are documented in [https://ugrid-conventions.github.io/ugrid-conventions](http://bit.ly/2gvtmqQ).
Right now `pyugrid` supports only triangular topologies, more will be added in the near future.

In a nutshell the `pyugrid` parses and exposes the underlying grid topology in a python object.

<div class="prompt input_prompt">
In&nbsp;[10]:
</div>

```python
import pyugrid

url = 'http://crow.marine.usf.edu:8080/thredds/dodsC/FVCOM-Nowcast-Agg.nc'

ugrid = pyugrid.UGrid.from_ncfile(url)
```

Sometimes the topology is incomplete but,
if the data is `UGRID` compliant,
`pyugrid` can derive the rest for you.

<div class="prompt input_prompt">
In&nbsp;[11]:
</div>

```python
ugrid.build_edges()
```

The topology can be extracted from `ugrid` object and used for plotting.

<div class="prompt input_prompt">
In&nbsp;[12]:
</div>

```python
lon = ugrid.nodes[:, 0]
lat = ugrid.nodes[:, 1]
triangles = ugrid.faces[:]
```

<div class="prompt input_prompt">
In&nbsp;[13]:
</div>

```python
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER


def make_map(projection=ccrs.PlateCarree()):
    fig, ax = plt.subplots(figsize=(8, 6),
                           subplot_kw=dict(projection=projection))
    ax.coastlines(resolution='50m')
    gl = ax.gridlines(draw_labels=True)
    gl.xlabels_top = gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    return fig, ax


fig, ax = make_map()

kw = dict(marker='.', linestyle='-', alpha=0.25, color='darkgray')
ax.triplot(lon, lat, triangles, **kw)
ax.coastlines()
ax.set_extent([-88, -79.5, 24, 32])
```


![png](data:image/png;base64,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
)


There is some effort in the development community to integrate `pyugrid` into `iris` to augment the cube object to be both CF and UGRID aware.
It will add convenience plotting and slicing methods.

Check a longer `pyugrid` example [here](http://bit.ly/2gaZLCy).

### SGRID-0.3 with `pysgrid`

The Staggered Grid conventions help users to interpret grids from models like ROMS and DELFT,
where the variables are defined in different grids.
The specs are detailed in [https://sgrid.github.io/sgrid](https://sgrid.github.io/sgrid).

The `pysgrid` module is similar to `pyugrid`. The grid topology is parsed into a Python object with methods and attributes that translate the SGRID conventions.

<div class="prompt input_prompt">
In&nbsp;[14]:
</div>

```python
import pysgrid

url = ('http://geoport.whoi.edu/thredds/dodsC/'
       'coawst_4/use/fmrc/coawst_4_use_best.ncd')

sgrid = pysgrid.load_grid(url)
```

All the raw grid information is present, like edges, dimensions, padding, grid center, and slicing.

<div class="prompt input_prompt">
In&nbsp;[15]:
</div>

```python
sgrid.edge1_coordinates, sgrid.edge1_dimensions, sgrid.edge1_padding
```




    (('lon_u', 'lat_u'),
     'xi_u: xi_psi eta_u: eta_psi (padding: both)',
     [GridPadding(mesh_topology_var='grid', face_dim='eta_u', node_dim='eta_psi', padding='both')])



<div class="prompt input_prompt">
In&nbsp;[16]:
</div>

```python
u_var = sgrid.u

u_var.center_axis, u_var.node_axis
```




    (1, 0)



<div class="prompt input_prompt">
In&nbsp;[17]:
</div>

```python
v_var = sgrid.v
v_var.center_axis, v_var.node_axis
```




    (0, 1)



<div class="prompt input_prompt">
In&nbsp;[18]:
</div>

```python
u_var.center_slicing, v_var.center_slicing
```




    ((slice(None, None, None),
      slice(None, None, None),
      slice(1, -1, None),
      slice(None, None, None)),
     (slice(None, None, None),
      slice(None, None, None),
      slice(None, None, None),
      slice(1, -1, None)))



The API is "raw" but comprehensive.
There is plenty of room to create convenience methods using the low level access provided by the library.

See below an example of the API and some simple convenience methods to `slice`, `pad`, `average`, and `rotate` the structure grid for plotting.

<div class="prompt input_prompt">
In&nbsp;[19]:
</div>

```python
from netCDF4 import Dataset

nc = Dataset(url)
u_velocity = nc.variables[u_var.variable]
v_velocity = nc.variables[v_var.variable]

v_idx = 0  # surface
time_idx = -1  # Last time step.

u = u_velocity[time_idx, v_idx, u_var.center_slicing[-2], u_var.center_slicing[-1]]
v = v_velocity[time_idx, v_idx, v_var.center_slicing[-2], v_var.center_slicing[-1]]

# Average at the center.
from pysgrid.processing_2d import avg_to_cell_center

u = avg_to_cell_center(u, u_var.center_axis)
v = avg_to_cell_center(v, v_var.center_axis)

# **Rotate the grid.
from pysgrid.processing_2d import rotate_vectors

angles = nc.variables[sgrid.angle.variable][sgrid.angle.center_slicing]
u, v = rotate_vectors(u, v, angles)

# Compute the speed.
from pysgrid.processing_2d import vector_sum

speed = vector_sum(u, v)
```
<div class="warning" style="border:thin solid red">
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/ipykernel/__main__.py:10: RuntimeWarning: invalid value encountered in
less
    /home/filipe/miniconda3/envs/IOOS/lib/python3.6/site-
packages/ipykernel/__main__.py:11: RuntimeWarning: invalid value encountered in
less

</div>
\*\* CF convention does describe the angle variable for grids that needs rotation, but there is no action expected. For example, in the formula_terms, pysgrid must be improved to abstract that action when needed via a simpler method.

```xml
<entry id="angle_of_rotation_from_east_to_x">
    <canonical_units>degree</canonical_units>
    <grib></grib>
    <amip></amip>
    <description>The quantity with standard name angle_of_rotation_from_east_to_x is the angle, anticlockwise reckoned positive, between due East and (dr/di)jk, where r(i,j,k) is the vector 3D position of the point with coordinate indices (i,j,k).  It could be used for rotating vector fields between model space and latitude-longitude space.</description>
</entry>
```

<div class="prompt input_prompt">
In&nbsp;[20]:
</div>

```python
lon_var_name, lat_var_name = sgrid.face_coordinates

sg_lon = getattr(sgrid, lon_var_name)
sg_lat = getattr(sgrid, lat_var_name)

lon = sgrid.center_lon[sg_lon.center_slicing]
lat = sgrid.center_lat[sg_lat.center_slicing]
```

Ideally all the steps above could be performed in the background, in a high level object method call, like the `iris` cube plotting methods.

Let's subset and center the velocity for better visualization (not a mandatory step but recommended).

<div class="prompt input_prompt">
In&nbsp;[21]:
</div>

```python
def is_monotonically_increasing(arr, axis=0):
    return np.all(np.diff(arr, axis=axis) > 0)


def is_monotonically_decreasing(arr, axis=0):
    return np.all(np.diff(arr, axis=axis) < 0)


def is_monotonic(arr):
    return (is_monotonically_increasing(arr) or
            is_monotonically_decreasing(arr))


def extent_bounds(arr, bound_position=0.5, axis=0):
    if not is_monotonic(arr):
        msg = "Array {!r} must be monotonic to guess bounds".format
        raise ValueError(msg(arr))

    x = arr.copy()
    x = np.c_[x[:, 0], (bound_position * (x[:, :-1] + x[:, 1:])), x[:, -1]]
    x = np.r_[x[0, :][None, ...], (bound_position * (x[:-1, :] + x[1:, :])), x[-1, :][None, ...]]

    return x
```

<div class="prompt input_prompt">
In&nbsp;[22]:
</div>

```python
import numpy as np

# For plotting reasons we will subsample every 10th point here
# 100 times less data!
sub = 10

lon = lon[::sub, ::sub]
lat = lat[::sub, ::sub]
u, v = u[::sub, ::sub], v[::sub, ::sub]
speed = speed[::sub, ::sub]

x = extent_bounds(lon)
y = extent_bounds(lat)
```

Now we can use quiver to plot the velocity components in a single grid. 

<div class="prompt input_prompt">
In&nbsp;[23]:
</div>

```python
def make_map(projection=ccrs.PlateCarree(), figsize=(9, 9)):
    fig, ax = plt.subplots(figsize=figsize,
                           subplot_kw=dict(projection=projection))
    gl = ax.gridlines(draw_labels=True)
    gl.xlabels_top = gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    return fig, ax
```

<div class="prompt input_prompt">
In&nbsp;[24]:
</div>

```python
scale = 0.06

fig, ax = make_map()

kw = dict(scale=1.0/scale, pivot='middle', width=0.003, color='black')
q = plt.quiver(lon, lat, u, v, zorder=2, **kw)

plt.pcolormesh(x, y, speed, zorder=1, cmap=plt.cm.rainbow)

c = ax.coastlines('10m')
ax.set_extent([-73.5, -62.5, 38, 46])
```


![png](data:image/png;base64,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
)


For more examples on `pysgrid` check this [post](http://bit.ly/2fKVk0x) out.
<br>
Right click and choose Save link as... to
[download](https://raw.githubusercontent.com/ioos/notebooks_demos/master/notebooks/2016-11-16-CF-UGRID-SGRID-conventions.ipynb)
this notebook, or click [here](https://beta.mybinder.org/v2/gh/ioos/notebooks_demos/master?filepath=notebooks/2016-11-16-CF-UGRID-SGRID-conventions.ipynb) to run a live instance of this notebook.