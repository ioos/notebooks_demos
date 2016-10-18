---
layout: notebook
title: ""
---


# CF, UGRID, and SGRID Conventions

### CF-1.6 (iris)

There are many Python libraries to read and write CF metdata, but only one
module that encapsulates CF in an object with an API:
[`iris`](http://scitools.org.uk/iris/).

    Iris seeks to provide a powerful, easy to use, and community-driven Python
library for analysing and visualising meteorological and oceanographic data
sets.

    With iris you can:

    - Use a single API to work on your data, irrespective of its original
format.
    - Read and write (CF-)netCDF, GRIB, and PP files.
    - Easily produce graphs and maps via integration with matplotlib and
cartopy.

<div class="prompt input_prompt">
In&nbsp;[1]:
</div>

```python
import iris

iris.FUTURE.netcdf_promote = True

url = ('http://omgsrv1.meas.ncsu.edu:8080/thredds/dodsC/fmrc/'
       'sabgom/SABGOM_Forecast_Model_Run_Collection_best.ncd')

cubes = iris.load(url)
```
<div class="warning" style="border:thin solid red">
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/cf.py:1059: UserWarning: Ignoring formula terms
variable 'zeta' referenced by data variable 'u' via variable 's_rho': Dimensions
('time', 'eta_rho', 'xi_rho') do not span ('time', 's_rho', 'eta_u', 'xi_u')
      warnings.warn(msg)
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/cf.py:1059: UserWarning: Ignoring formula terms
variable 'h' referenced by data variable 'u' via variable 's_rho': Dimensions
('eta_rho', 'xi_rho') do not span ('time', 's_rho', 'eta_u', 'xi_u')
      warnings.warn(msg)
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/cf.py:1059: UserWarning: Ignoring formula terms
variable 'zeta' referenced by data variable 'v' via variable 's_rho': Dimensions
('time', 'eta_rho', 'xi_rho') do not span ('time', 's_rho', 'eta_v', 'xi_v')
      warnings.warn(msg)
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/cf.py:1059: UserWarning: Ignoring formula terms
variable 'h' referenced by data variable 'v' via variable 's_rho': Dimensions
('eta_rho', 'xi_rho') do not span ('time', 's_rho', 'eta_v', 'xi_v')
      warnings.warn(msg)
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1783:
UserWarning: Gracefully filling 'time' dimension coordinate masked points
      warnings.warn(msg.format(str(cf_coord_var.cf_name)))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1783:
UserWarning: Gracefully filling 'time' dimension coordinate masked points
      warnings.warn(msg.format(str(cf_coord_var.cf_name)))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1783:
UserWarning: Gracefully filling 'time' dimension coordinate masked points
      warnings.warn(msg.format(str(cf_coord_var.cf_name)))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1686:
UserWarning: Ignoring netCDF variable 'chlorophyll' invalid units
'milligrams_chlorophyll meter-3'
      warnings.warn(msg)
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1783:
UserWarning: Gracefully filling 'time' dimension coordinate masked points
      warnings.warn(msg.format(str(cf_coord_var.cf_name)))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1783:
UserWarning: Gracefully filling 'time' dimension coordinate masked points
      warnings.warn(msg.format(str(cf_coord_var.cf_name)))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1783:
UserWarning: Gracefully filling 'time' dimension coordinate masked points
      warnings.warn(msg.format(str(cf_coord_var.cf_name)))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1783:
UserWarning: Gracefully filling 'time' dimension coordinate masked points
      warnings.warn(msg.format(str(cf_coord_var.cf_name)))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/netcdf.py:579: UserWarning: Unable to find coordinate
for variable 'zeta'
      '{!r}'.format(name))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/netcdf.py:579: UserWarning: Unable to find coordinate
for variable 'h'
      '{!r}'.format(name))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/netcdf.py:696: UserWarning: Unable to construct Ocean
s-coordinate, generic form 1 factory due to insufficient source coordinates.
      warnings.warn('{}'.format(e))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1686:
UserWarning: Ignoring netCDF variable 'zooplankton' invalid units
'millimole_nitrogen meter-3'
      warnings.warn(msg)
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1783:
UserWarning: Gracefully filling 'time' dimension coordinate masked points
      warnings.warn(msg.format(str(cf_coord_var.cf_name)))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1686:
UserWarning: Ignoring netCDF variable 'NO3' invalid units 'millimole_N03
meter-3'
      warnings.warn(msg)
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1783:
UserWarning: Gracefully filling 'time' dimension coordinate masked points
      warnings.warn(msg.format(str(cf_coord_var.cf_name)))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1686:
UserWarning: Ignoring netCDF variable 'phytoplankton' invalid units
'millimole_nitrogen meter-3'
      warnings.warn(msg)
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1783:
UserWarning: Gracefully filling 'time' dimension coordinate masked points
      warnings.warn(msg.format(str(cf_coord_var.cf_name)))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1686:
UserWarning: Ignoring netCDF variable 'NH4' invalid units 'millimole_NH4
meter-3'
      warnings.warn(msg)
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1783:
UserWarning: Gracefully filling 'time' dimension coordinate masked points
      warnings.warn(msg.format(str(cf_coord_var.cf_name)))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1783:
UserWarning: Gracefully filling 'time' dimension coordinate masked points
      warnings.warn(msg.format(str(cf_coord_var.cf_name)))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/netcdf.py:579: UserWarning: Unable to find coordinate
for variable 'zeta'
      '{!r}'.format(name))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/netcdf.py:579: UserWarning: Unable to find coordinate
for variable 'h'
      '{!r}'.format(name))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/netcdf.py:696: UserWarning: Unable to construct Ocean
s-coordinate, generic form 1 factory due to insufficient source coordinates.
      warnings.warn('{}'.format(e))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1783:
UserWarning: Gracefully filling 'time' dimension coordinate masked points
      warnings.warn(msg.format(str(cf_coord_var.cf_name)))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1783:
UserWarning: Gracefully filling 'time' dimension coordinate masked points
      warnings.warn(msg.format(str(cf_coord_var.cf_name)))
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/_cube_coord_common.py:51: FutureWarning: elementwise comparison
failed; returning scalar instead, but in the future will perform elementwise
comparison
      match = value == other[key]
    /home/filipe/miniconda3/envs/IOOS/lib/python3.4/site-
packages/iris/_merge.py:364: FutureWarning: elementwise comparison failed;
returning scalar instead, but in the future will perform elementwise comparison
      other_defn.attributes[key])]

</div>
**Aside:** the `iris.FUTURE.netcdf_promote = True` line  promotes netCDF formula
terms,
like sea surface height, to cubes.
This behavior will be default in future versions of `iris`.

<div class="prompt input_prompt">
In&nbsp;[2]:
</div>

```python
print(cubes)
```
<div class="output_area"><div class="prompt"></div>
<pre>
    0: vertically integrated u-momentum component / (meter second-1) (time: 352; -- : 320; -- : 439)
    1: free-surface inflow, nudging inverse time scale / (second-1) (-- : 4)
    2: nonlinear model Laplacian mixing coefficient for tracers / (meter2 second-1) (-- : 14)
    3: vertical momentum component / (meter second-1) (time: 352; ocean_s_coordinate_g1: 37; -- : 320; -- : 440)
    4: Tracers nudging/relaxation inverse time scale / (day-1) (-- : 14)
    5: tracers inflow, nudging inverse time scale / (second-1) (-- : 4; -- : 14)
    6: angle between XI-axis and EAST / (radians) (-- : 320; -- : 440)
    7: mask on U-points / (1)              (-- : 320; -- : 439)
    8: background vertical mixing coefficient for tracers / (meter2 second-1) (-- : 14)
    9: curvilinear coordinate metric in ETA / (meter-1) (-- : 320; -- : 440)
    10: mask on RHO-points / (1)            (-- : 320; -- : 440)
    11: 2D momentum inflow, nudging inverse time scale / (second-1) (-- : 4)
    12: curvilinear coordinate metric in XI / (meter-1) (-- : 320; -- : 440)
    13: free-surface outflow, nudging inverse time scale / (second-1) (-- : 4)
    14: chlorophyll concentration / (unknown) (time: 352; ocean_s_coordinate_g1: 36; -- : 320; -- : 440)
    15: 3D momentum inflow, nudging inverse time scale / (second-1) (-- : 4)
    16: Coriolis parameter at RHO-points / (second-1) (-- : 320; -- : 440)
    17: grid type logical switch / (1)      (-- : 64)
    18: zooplankton concentration / (unknown) (time: 352; ocean_s_coordinate_g1: 36; -- : 320; -- : 440)
    19: mask on V-points / (1)              (-- : 319; -- : 440)
    20: nitrate concentration / (unknown)   (time: 352; ocean_s_coordinate_g1: 36; -- : 320; -- : 440)
    21: phytoplankton concentration / (unknown) (time: 352; ocean_s_coordinate_g1: 36; -- : 320; -- : 440)
    22: ammonium concentration / (unknown)  (time: 352; ocean_s_coordinate_g1: 36; -- : 320; -- : 440)
    23: tracers outflow, nudging inverse time scale / (second-1) (-- : 4; -- : 14)
    24: 3D momentum outflow, nudging inverse time scale / (second-1) (-- : 4)
    25: 2D momentum outflow, nudging inverse time scale / (second-1) (-- : 4)
    26: tracer point sources and simck activation switch / (1) (-- : 14)
    27: vertically integrated v-momentum component / (meter second-1) (time: 352; -- : 319; -- : 440)
    28: mask on psi-points / (1)            (-- : 319; -- : 439)
    29: bathymetry at RHO-points / (meter)  (-- : 320; -- : 440)
    30: eastward_sea_water_velocity_assuming_no_tide / (meter second-1) (time: 352; ocean_s_coordinate_g1: 36; -- : 320; -- : 439)
    31: forecast_period / (hours since 2016-08-31T00:00:00Z) (time: 352)
    32: northward_sea_water_velocity_assuming_no_tide / (meter second-1) (time: 352; ocean_s_coordinate_g1: 36; -- : 319; -- : 440)
    33: sea_surface_height / (meter)        (time: 352; -- : 320; -- : 440)
    34: sea_water_potential_temperature / (Celsius) (time: 352; ocean_s_coordinate_g1: 36; -- : 320; -- : 440)
    35: sea_water_salinity / (1)            (time: 352; ocean_s_coordinate_g1: 36; -- : 320; -- : 440)

</pre>
</div>
- High level variable access via `standard_name`, `long_name`, or `var_name`
- Annoyingly verbose warnings when the data has compliance issues (see the units
warnings above)
- Raise error for non-compliant. (Iris will refuse to load the data!)
- Separation of each phenomena (`variable`) into its own cube\*
- The cube is a fully self-described format format with all the original
metadata (round-trip load-save to netCDF is lossless)
- The cube object interprets the `formula_terms` and `cell_methods`

<div class="prompt input_prompt">
In&nbsp;[3]:
</div>

```python
cube = cubes.extract_strict('sea_surface_height')

print(cube)
```
<div class="output_area"><div class="prompt"></div>
<pre>
    sea_surface_height / (meter)        (time: 352; -- : 320; -- : 440)
         Dimension coordinates:
              time                           x         -         -
         Auxiliary coordinates:
              forecast_reference_time        x         -         -
              latitude                       -         x         x
              longitude                      -         x         x
         Attributes:
              CPP_options: SABGOM, ADD_FSOBC, ADD_M2OBC, ANA_BPFLUX, ANA_BSFLUX, ANA_BTFLUX, ANA_SPFLUX,...
              Conventions: CF-1.4, _Coordinates
              DODS.strlen: 0
              DODS_EXTRA.Unlimited_Dimension: ocean_time
              EXTRA_DIMENSION.N: 36
              _CoordSysBuilder: ucar.nc2.dataset.conv.CF1Convention
              ana_file: ROMS/Functionals/ana_btflux.h, ROMS/Functionals/ana_nudgcoef.h, ROMS/F...
              bio_file: ROMS/Nonlinear/Biology/fennel.h
              bpar_file: /home/omg/autosabgom/bioFasham_038_Katja.in.U3C4
              bry_file: /gpfs_share/omg/omg/autosabgom/in/ncoda_bry_20161001.nc
              cdm_data_type: GRID
              clm_file: /gpfs_share/omg/omg/autosabgom/in/ncoda_clm_20161001.nc
              code_dir: /he_data/he/zxue/COAWST411
              compiler_command: /usr/local/apps/mpich/x86_64/pgi105/mx127..7/bin/mpif90
              compiler_flags: -fastsse   -Kieee -fastsse -Mipa=fast -tp k8-64 -Mfree
              compiler_system: pgi
              cpu: x86_64
              dia_file: /gpfs_share/omg/autosabgom/out/dia_20161001.nc
              featureType: GRID
              field: free-surface, scalar, series
              file: /gpfs_share/omg/autosabgom/out/his_20161001_0002.nc
              format: netCDF-3 classic file
              frc_file_01: /gpfs_share/omg/omg/autosabgom/in/nomads_forc_20161001.nc
              frc_file_02: /gpfs_share/omg/omg/autosabgom/in/SABGOM.OTIS.Ref18581117.8Cons
              frc_file_03: /gpfs_share/omg/omg/autosabgom/in/sabgom_river_79_clm_2015_2016.nc
              grd_file: /gpfs_share/omg/omg/autosabgom/in/sabgom_grd.nc.Etopo2.LP.r1_5.filled
              header_dir: /he_data/he/zxue/Projects/SABGOM_BIO
              header_file: mch_bio_nf.h
              his_base: /gpfs_share/omg/autosabgom/out/his_20161001
              history: ROMS/TOMS, Version 3.4, Saturday - October 1, 2016 -  2:45:21 AM ;
    FMRC...
              ini_file: /gpfs_share/omg/omg/autosabgom/in/ncoda_ini_20161001.nc
              location: Proto fmrc:SABGOM_Forecast_Model_Run_Collection
              os: Linux
              rst_file: /gpfs_share/omg/autosabgom/out/rst_20161001.nc
              script_file: /home/omg/autosabgom/sabgom_20161001.in
              spos_file: /home/omg/autosabgom/stations.in
              sta_file: /gpfs_share/omg/autosabgom/out/sta_20161001.nc
              svn_rev: 412M
              svn_url: https://www.myroms.org/svn/omlab/branches/jcwarner
              tiling: 008x004
              time: ocean_time
              title: ROMS/TOMS 3.0 - South-Atlantic Bight and Gulf of Mexico
              type: ROMS/TOMS history file

</pre>
</div>
Requesting a vertical profile of temperature to see the `formula_terms`
interpretation in action. (Note that `ocean_s_coordinate_g1` is CF-1.7.)

<div class="prompt input_prompt">
In&nbsp;[4]:
</div>

```python
temp = cubes.extract_strict('sea_water_potential_temperature')

t_profile = temp[-1, :, 160, 220]
```

<div class="prompt input_prompt">
In&nbsp;[5]:
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
            -0.01388889]), standard_name='ocean_s_coordinate_g1', units=Unit('1'), long_name='S-coordinate at RHO-points', var_name='s_rho', attributes={'_CoordinateZisPositive': 'up', 'positive': 'up', '_CoordinateAxes': 's_rho', '_CoordinateAxisType': 'GeoZ', '_CoordinateTransformType': 'Vertical', 'field': 's_rho, scalar', 'valid_max': 0.0, 'valid_min': -1.0}),
     AuxCoord(array([-191.77609919, -177.31818979, -164.63189452, -153.46146259,
            -143.57686355, -134.76867979, -126.84349508, -119.61989754,
            -112.92536662, -106.59451097, -100.46934092,  -94.40241117,
             -88.26358858,  -81.95064101,  -75.40258939,  -68.6128832 ,
             -61.63762684,  -54.59363281,  -47.64329638,  -40.96807911,
             -34.73750146,  -29.08276398,  -24.08189997,  -19.75825236,
             -16.08927766,  -13.02046402,  -10.47960537,   -8.38850944,
              -6.67110358,   -5.25816026,   -4.08942745,   -3.11403572,
              -2.28990739,   -1.58268361,   -0.96449515,   -0.41276096]), standard_name='sea_surface_height_above_reference_ellipsoid', units=Unit('meter'), attributes={'positive': 'up'})]



Iris knows about the metadata and can create fully annotated plots.

Be aware that too much automation lead to some weird plots. Like the `z-coord`
in the `x-direction` ;-)

<div class="prompt input_prompt">
In&nbsp;[6]:
</div>

```python
%matplotlib inline

import iris.quickplot as qplt

l, = qplt.plot(t_profile)
```


[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAhUAAAGHCAYAAAAHoqCrAAAABHNCSVQICAgIfAhkiAAAAAlwSFlz
AAAPYQAAD2EBqD+naQAAIABJREFUeJzs3Xd8VGX2x/HPoYMFbFhYUUBR7IK6qy4qNlwLrhViQexY
AXtbdW2oq1LFroBo1q7YAAsgYAXs2BZFVFRQNEgJUs7vj+fmxzBMIHNzw2Qm3/frNa/MPPfOnTMZ
SE6ech5zd0REREQqq1auAxAREZHCoKRCREREEqGkQkRERBKhpEJEREQSoaRCREREEqGkQkRERBKh
pEJEREQSoaRCREREEqGkQkRERBKhpEJEqh0z29vMlprZXjGee62ZLa2KuERk5ZRUSJUys+3N7Ekz
m2ZmC8zsezMbZWbn5jq2pJnZP8zsmlzHURlm1tDMronzyzzm651lZieVczjuHgJekeeaWZGZ9Yj5
GgXNzC43s8NzHYfkHyUVUmXMbA/gPWB74F7gHOA+YAlwfg5DqyoHA1fnOohKagRcA+yzml7vbGCF
pMLdxwIN3f2NKnzt4wAlFZldASipkKzVyXUAUtCuBH4HdnH3P1IPmNn6uQmpSlmVXNSsgbuXVsW1
M73canqdVXL3P3MdQyEwMwPquftCxSFVTT0VUpVaAp+mJxQA7v5LepuZnWBmE81svpn9ambFZvaX
tHP+bmaPmdm3ZlZqZtPN7A4za7CyQMyssZktTh12MbP1onH7mWnn3mVmM7J5TTN7iPBXN9E1l5rZ
kpTjZmY9zeyTaBjoJzO728yapL32NDMbbmYHmtl7ZlYKnLGS9zXGzD4ys7ZmNiH63n1tZmdmOHcD
M3sgeu0FZvaBmXVNOb4ZMJMwdHBtyvu4OuWcraLhrF+ja7xnZoelvc5J0fP2iL5PM81srpk9nZpM
mtk3wLbAPimv9Xp0bIU5FXE/+3K+b6OBQ4DNUl7765Tj9czs32b2Vcpr3WJm9dKus9TM+pvZ0Wb2
afT9f9PMtouOnxldY4GZjTaz5mnPz+bzyzam48zsE6AU6Bgduyh6nV+i15poZkelP5/QY9Ut5Xvz
YHRscPS5pce2wjyWVcRRof8Pkn/UUyFV6Vvgb2a2rbt/urITzexK4Drgv4Qhkg0IQyRjzWxnd58T
nXoM4QfeIOBXYDfgPKAZ0Lm867t7SfSDbS9gYNT8d2ApsJ6ZtXH3z1Lax6U8vSKveTewCbA/cDwr
/sV/L9AVeBDoB7SIrrGTme3p7mUJiANbA48C90TP+6K89xWdvy7wIvB49LxjgbvMbKG7D4bQ2wGM
AVoBA4Bp0fsabGaN3X0AMAvoHr2Xp6MbwEfRNbYFxgPfA72BedFrPWtmR7r7c2mxDQBmA9cCmwO9
orai6HgPwmfxB3BD9D37Oe29pYr12ZfjBqBx9Nye0WvPjd6nAc8DexA+g88JQ3i9gC2BI9OutRfQ
CbgzenwF8IKZ3QqcFbWvA1xK+Pz3T3uPFfn8so1pP8L3607gF8LnDeH/1HPAMKAe0AV43MwOdfeX
o3NOAB4A3iH8+wOYmhJvpvkq5bWXF0dF/z9IvnF33XSrkhvhh+efwCJgAnAzcABQJ+285tE5l6a1
bxM9/7KUtvoZXudSYDHwl1XEMwD4MeXxbcBoYAZwRtS2DmHOx7nZvmZ0/SUZzi1LXjqntR8QtXdJ
afsmev39K/g9Hh2d3yOlrS4wGfgRqB219YjOS32t2tHnUgKsEbWtF8V0dYbXehV4P8PnNx74POXx
SdE1RqSdd3v0ea6V0vYx8HqG19o7inevGJ/DNZk+hwzPfR74OkP7CdG/x93T2s+IYvpbSttSYD6w
aUrb6VH7D0CjlPYbo+c3j/H5ZRvTImCrDO+tftrj2oSk8ZW09j+ABzM8/6FyvmcrfM/Li4Ms/j/o
ln83DX9IlXH3Vwl/WT0H7ABcDIwEfkjrMj+K8JfiExaGJNYzs/UIXfFfAR1Srvn/47Fm1ig67y3C
UN7OqwhpHNDUzLaMHrcH3iD8Umyf0lZ2bhKvCXA0YW7Ja2nv733CX8cd0s7/JvreVdRilv1Fibsv
Ivw12xRoFzX/A/jJ3f+bct4SoD+wJuGXeLnMbJ0ozieAxmnvYxSwpZltnPIUT40pMo7wS2yzLN7b
sgtW/nOoqKOBz4Av097naMK/0/TP61V3/y7l8TvR1yfdfX6G9pZpz6/I55dtTGPcfYUerrTvYRNC
Ej0OaJt+bkIyxZHt/wfJIxr+kCrl7hOBo82sDrAjcAShy/YJM9vJ3T8HtiD8YvhfpksQ/roFwMw2
Ba4HDiP8QEw9r/EqwhlH+AHc3sx+IPwiupLQLXthdE57YA5Rl38Crwmhe7oJIUlK54RfHqlWGLNe
hRnuviCt7UvCe90MeDf6+lWG536Wct7KbBGddz1h6CBd2fv4MaXtu7Rzfou+rkMMCXwOFbUlYQhq
VoZjmT6v9PdZEn39PkO7seL7r8jnl21M0zKch5kdSvg3vxNQP+VQVdX1yBRHtv8fJI8oqZDVwt0X
A5OASWb2FaEb9RjCL4lahB9qB5H5h1vZWHctQhd8E8KY/heEcf1mwBBWMfHY3X+MJpntRZjvAeEv
3V+AvtEvrb8DE9xDf2xlXzNSizBX4Dgyr65I/0WR/gsmjvTXqeyqjrL3eRuhtymT9KSwvHHxrGNJ
6HOoqFqEYZleZI41PYko731W5v2nn5NtTCv8GzKz9oRewzGEuR4/EoYnTmHZPJdVKa/+R+1y2jP9
W872/4PkESUVkgsTo69l3eVTCT9cprl7pt6KMtsT/so50d0fKWs0s/3Lf8oKxhF6I6YBH7j7PDP7
kPBX5EGEbuDUWhPZvGZ5P3CnEiasvelVs5xuEzNrmPbXbusonmnR42mE95KuTfS1LMkq7z2UrYxY
5O6vxw91BRUtcJXEZ1/R154K7ODuoytx7WxU5PNLIqYjCb/kO0ZJPgBmdmqGc8v73vxGSOzSbZ5F
HFX9/0FySHMqpMqY2T7lHDok+vp59PVpQg9FxmqUZrZudLfsL7/0f7c9qfgvp3GEmeado/tEvRJv
EYZA6rD8yo9sXnNeFO/aae2PR9ddoTCWmdU2s8p23dchrNoou2Zd4EzCX3yTo+aXgI3MrHPKebUJ
M+7/AMZGzWVzAJb7xeHuswh/4Z5pZhtleB9x647MS3+tciTx2Wd67Uzf+8eBv5jZ6ekHzKyBmTWK
+Xrlqcjnl0RMSwjfq///Y9LMNidzkavyPpephDk126VcY2PgnxV4/TJV/f9Bckg9FVKVBkQ/7J4h
JBD1gD0JS+a+BgYDuPvXZnYVcJOZtQCeJfyia0n4YXUPcEd0janA7RbqV8whTPLMZm17WcLQGrg8
pf0NwmTGUkIV0DLZvOYkQo/LADMbSZgN/5i7v2Fm9wCXmdlOhImNi6IYjiYs83s6w/UqagZwSfS9
+4KwTHAH4HRftjTvXsIvqsFmtgvLlpTuTlh5MA/A3UvNbArQ2cy+JPxl+omHJcHnEL5/H5vZfYTP
cMPoGs1YfrJkeV386e2TgO7RkuL/ATNT/hpPPTeJzz7dJOBYM7ud8JnPdfcXgIdZtqyzA2GFTG1C
r84xwIEs+2WfhIp8fknE9AJwATDSzB4lfHZnE+ba7JB27iRgfzPrFcX3jbu/CxQDtxCWEfcH1iAk
RF9Qwcmeq+H/g+RSrpef6Fa4N8IPuvuATwnDCwsIP3z6ABtkOP+fhL+Y50S3Twlr2LdIOWcrwph+
CWFc9i5gO8JfYV0rGNdPhBn366e07RFdY3SG8yv0moS/ovumXD99id2phEl3cwmz3z8AbgI2TDnn
a+C5LL7HowmTSncm/KKZF12je4Zz1wfuj97Dguj1T8xw3l+jOBdE7/HqlGObE+bD/EBIwKYTxumP
SDnnpOh5bdOum2mZaFNgePT9WEK0vLSccyv6OVwDLK7A964R4Zf1r9E1vk45Vhu4KPrezifMu3mX
MMlxzZTzlgD90q67WdTeq5z3f2TMzy92TCnHuhEStPmE/19dybwctHUU29zoeg+mHNsP+DD69zGF
MB8j0zXKjaOi/x90y7+bRR+uiOQhC5Uh13P39L80JQ/o85NCk/M5FWbW3cw+NLOS6PammR2Ucry+
md1poazsHxZKBGvJkYiISDWT86SCsBTqUkKRl3bA68BzZlY2K70vYWLfUYSlgJsAT+UgThEREVmJ
ajn8YWa/EsYOnyLMgO7i7s9Ex7YiFOz5m4eJQyI1VtR9vq6775jrWCR7+vyk0FSr1R9RgZtjCROo
3iL0XNQBXis7x92/MLPphBnnSiqkRnN3lTTOY/r8pNBUi6QiWvP8FtCAsJTwCHf/3Mx2Bv70ZTtU
lvkZWGGtvIiIiOROtUgqCEucdiSsOT8KGGpme63kfGMlBW+izWk6EtbilyYXpoiISMFrQFg+PtLd
f83midUiqfBQMrasDPBkM9uNsFXz40A9M1s7rbeiKaG3ojwdgUdWclxERERW7njg0WyeUC2Sigxq
EXbQm0QoIrQfoSojZtYaaE4YLinPNIBhw4bRpk2blZwm+aRXr1706dMn12FIQvR5FhZ9noXjs88+
44QTToBydrtdmZwnFWZ2I/AyYWnpWoTMaG/gQHefY2YPAHeY2W+E+Rb9CbtIrmySZilAmzZtaNu2
QpVjJQ80btxYn2cB0edZWPR5FqSspw/kPKkg1J8fStixsoRQgvZAX7YTYi9CudcnCb0XIwh7EIiI
iEg1kvOkwt1PW8XxhYSdFM9bPRGJiIhIHNWhoqaIiIgUACUVkjeKiopyHYIkSJ9nYdHnKaCkQvKI
fmgVFn2ehUWfp4CSChEREUmIkgoRERFJRKWTCjOrbWY7mdk6SQQkIiIi+SnrpMLM+prZqdH92sBY
YDLwnZntk2x4IiIiki/i9FQcDXwY3T8MaAFsDfQBbkwoLhEREckzcZKK9YGfovsHA0+4+5fAg8D2
SQUmIiIi+SVOUvEzsE009HEQ8GrU3ohQTltERERqoDhluh8ibEn+I+DAK1H7X4HPE4pLRERE8kzW
SYW7X2tmnwCbEoY+FkaHlgA3JxmciIiI5I9YG4q5+5MZ2oZUPhwRERHJV1knFWZ29cqOu/t18cMR
ERGRfBWnp+KItMd1CctKFwNTASUVIiIiNVCcORU7p7eZ2drAYOCZBGISERGRPJTI3h/uPge4Brg+
ieuJiIhI/klyQ7HG0U1ERERqoDgTNc9PbwI2Bk4ERiQRlIiIiOSfOBM1e6U9XgrMAoYAvSsdkYiI
iOSlOBM1W1RFICIiIpLfkpxTISIiIjVYhXoqzOxpoJu7z4nul8vdj0wkMhEREckrFR3+KCFsHlZ2
X0RERGQ5FUoq3P3kTPdFREREymQ9p8LMGppZo5THm5lZTzM7MNnQREREJJ/Emaj5HNAVwMyaAO8C
FwLPmdlZCcYmIiIieSROnYq2LKtVcTTwE7AzcBRhM7G7kglNRESk+hk3DoqLYd48WLBg2a20dPnH
CxbAn39CrVrLbrVrr/jYbPnrpz4uu2+28vupt1q1Vryf/tq1a0OdOlC3brjVqwdrrQVNm1buexMn
qWgE/BHdPxB42t2XmtnbwGaVC0dERKR6+u03uOQSuP9+2GIL2GgjaNgw3NZbb9n9hg2hQYPwtV49
cIelS5fdlixZ/n4Z9+y/lndbunTF10197SVLYPFiWLQoJD5z5sA338DMmTBrVvzvUZyk4n/AP83s
GaAj0CdqbwrMiR+KiIhI9eMOjz0GPXuG3oe77oIzzgh/8Rei996D3XaL99w435LrgNuAacA77v5W
1H4g8H68MERERKqfadPgkEOgqAjat4fPPoPu3Qs3oYAwNBJXnDLdT5rZeMImYh+mHHoNeCZ+KCIi
ItXD4sXQty9cc00Y2hg+HA47LNdRVX9xhj9w958IEzRT295NJCIREZEcmjgxDG98+CGcdx5cf32Y
xCirlk2Z7grJtky3mV0OHAFsDSwA3gQudfcvU87ZkDDksj+wFvAFcKO7VzguERGRlZk7F/71L+jf
H3bYAd55B3bZJddR5ZdsynRXlfbAAGAiIZ7ewCgza+PuC6JzHgbWBg4FfgWOBx43s3bu/mGGa4qI
iFTYiy/CWWfBr7/CLbeESZl1YvXl12xZl+lOmrsfnPrYzLoBM4F2wPioeXegu7tPih7faGa9onOU
VIiISGyTJoX5EgceGFZ2tGiR64jyV6z5q2ZWx8z2N7MzzWytqG0TM1szgZiaEDYvm53SNgHobGbr
WNAFqA+MSeD1RESkhnKHiy+GNm3ghReUUFRW1p07ZrYZMAJoTvjF/gqhGNal0ePucYMxMwP6AuPd
fUrKoc7AY4Shj8XAPOAId/867muJiIiMGAGjR8Pzz2u4Iwlxeir6EeY/rEOYWFnmGWC/SsYzCNgG
6JLWfgPQGNiXMORxB/CEmW1bydcTEZEaasmSUCFz771DLQqpvDh52d+BPd39T1u+YPk0oFncQMxs
IHAw0N7df0xpbwmcA2zj7p9HzR+b2V5R+9nlXbNXr140btx4ubaioiKKiorihikiIgVi6FD45JOw
yiN9/42aori4mOLi4uXaSkrir82Ik1TUjm7p/sKyPUGyEiUUhwN7u/v0tMONCHMsPK19CavoaenT
pw9t27aNE5KIiBSw+fPD8tFjj41fkroQZPpDe/LkybRr1y7W9eIMf4wCeqY89miC5r+Bl7K9mJkN
IiwRPQ6YZ2YbRrcG0SmfA1OBe8xsVzNraWYXEmpWqIKniIhkrV+/sHnWTTflOpLCEiepuBDY08ym
AA2AR1k29HFpjOt1J9SgGAPMSLkdC+Dui4F/ALOA4YQlpCcAXd19ZIzXExGRGmzWLOjdO9SlaNUq
19EUljh7f3xvZjsSVmTsCKwJPAA8klKsKpvrrTKxcfepwDHZXltERCTdDTeEORRXXZXrSApP3L0/
FgOPRDcREZG8MHVqKHD173/DBhvkOprCU+HhDzNrZ2ajzWztDMcaR8d2TDY8ERGR5Fx5JTRtCj16
5DqSwpTNnIoLgdfdfU76AXcvIRTBujipwERERJL07rvw2GNh19FGjXIdTWHKJqn4K/DcSo4/D+xR
uXBERESS5x4KXW23HXTtmutoClc2cyqasfI6FHOBjSsXjoiISPJefBHGjoWXXoLamSotSSKy6amY
BWy1kuNbA79ULhwREZFkLV4Ml14K++4LBx2U62gKWzZJxavAlZkORBuBXRGdIyIiUm0MHgxTpsCt
t9bcctyrSzbDHzcAk8zsHeB24AtC6ew2hEmcrYGTE49QREQkpnnz4Oqr4bjjIGblaclChZMKd59q
ZvsDg4H/smwvDgOmAAe4+/8Sj1BERCSmPn3g119DwSupelkVv3L3icB2ZrYTsCUhofjS3T+oiuBE
RETimjkTbrkFzj0XWrTIdTQ1Q9yKmh8ASiRERKTauu46qFMnFLyS1SPOhmIiIiLV2pdfwj33wBVX
wLrr5jqamkNJhYiIFJwrroCNN4bzzst1JDVLrOEPERGR6uqtt+Cpp2DIEGjQINfR1CzZbCh2iplp
TzcREam2yspx77gjHH98rqOpebIZ/jgR+M7M3jSzS82sTVUFJSIiEkdxMYwfHwpdqRz36lfhpMLd
OxD29hgEtAPeNrOvzOx2M9vLzDQ/Q0REcubnn8Mcii5d4MADcx1NzZRVIuDuv7n7MHc/FtgAOA9o
CDwCzDSzoWZ2tJmtUQWxioiIZOQOZ58deicGDMh1NDVX7N4Fd//T3Ue4+9nuvilwEDAN+BdwQULx
iYiIrNITT8DTT8Odd8L66+c6mporsdUfUbXNicDVZlY3qeuKiIiszKxZcM45cNRRcMwxuY6mZquS
eRDuvqgqrisiIpLuvPPC8Medd+Y6ElGdChERyVvPPAOPPQaPPAIbbpjraEQrNkREJC/9+iucdRZ0
6gRFRbmORkBJhYiI5KmePWHhQrj7bjDLdTQCMZMKM2tvZsPM7C0zaxa1nWhmf082PBERkRW98AIM
Gwb9+oU9PqR6yDqpMLOjgJHAAmBnoH50qDFwRXKhiYiIrOj33+HMM+Hgg+HEE3MdjaSK01NxFdDd
3U8HUld5TADaJhKViIhIOS64AObODVuba9ijeomz+mMr4I0M7SVAk8qFIyIiUr6XX4aHHoL774e/
/CXX0Ui6OD0VPwFbZGj/O/B15cIRERHJrKQEzjgj7Otxyim5jkYyiZNU3Af0M7O/Ag5sYmbHA7cR
NhsTERFJ3MUXh/kU992nYY/qKs7wx82EZOQ1oBFhKGQhcJu7D0wwNhEREQBefTUkE3fdBc2b5zoa
KU/WSYW7O3Cjmf2HMAyyJjDF3ecmHZyIiMgff8Bpp0GHDmH4Q6qvrJIKM6sDlAI7ufsnwJQqiUpE
RCRy2WVh07DXX4daKtlYrWWVVLj7YjObDtSuonhERET+35gxMGgQ9O8PLVvmOhpZlTg5343ATWa2
bhIBmNnlZvaumc0xs5/N7Bkza53hvN3N7DUzm2tmJWY2xszqZ7qmiIjkv3nz4NRToX37sLW5VH9x
JmqeS5hLMcPMvgXmpR5092wLYLUHBgATo3h6A6PMrI27L4CQUAAvExKac4AlwI7A0hjxi4hIHrjy
SvjxRxg5UsMe+SJOUvFskgG4+8Gpj82sGzATaAeMj5rvAPq6+39STv0qyThERKT6mDAhDHncfjts
kakyklRLcVZ//LsqAknRhFD/YjaAmW0A/BV4xMwmAK2Az4Er3X1CFcciIiKr2fTp0Lkz7L47nH9+
rqORbFSrDiUzM6AvMN7dy1aWlE3NuQa4B+gITAZeM7NWqz9KERGpKrNnw0EHQd268OSTUFvLAvJK
1j0VZraU0JOQkbtX5p/AIGAbYM+UtrLE5253Hxrdv8DM9gNOAa4s72K9evWicePGy7UVFRVRVFRU
iRBFRKQqzJ8Phx4alo9OmKAtzVeH4uJiiouLl2srKSmJfT0LtayyeILZ4WlNdQlboJ8EXOPuD8QK
xGwgcBjQ3t2np7RvTthT5AR3fzSl/b/AIndfYeNbM2sLTJo0aRJt22rjVBGR6m7xYjjiiFCLYvRo
2G23XEdUc02ePJl27doBtHP3ydk8N86ciucyND9pZp8CnYGsk4oooTgc2Ds1oYheb5qZzSDsjpqq
NfBStq8lIiLVizt07w4jRsDzzyuhyGdxVn+U523CZmNZMbNBQBHQCZhnZhtGh0rcvTS6/x/gWjP7
CPgA6EZIMo6qbNAiIpJbV18NDzwAQ4eG+RSSvxJJKsysIXA+8H2Mp3cnzNEYk9Z+MjAUwN37RYWu
7gDWBT4E9nf3b+LGLCIiuTdoENxwA9xyC5y4wmC25Js4EzV/Y/mJmgasBcwHTsj2eu5eoRUo7n4r
cGu21xcRkerpySfh3HOhZ8+wrbnkvzg9Fb1YPqlYCswC3nH33xKJSkRECtqYMXD88dClSyhwZZbr
iCQJcZKK14HvPMOyETNrnj7RUkREJNVHH8Hhh8Nee8HgwSrBXUjifJTfABukN5rZetExERGRjKZN
C5MxW7WCp56CevVyHZEkKU5SUV4n1ZpAaTnHRESkhvvlF+jYERo2hJdfhrXXznVEkrQKD3+Y2R3R
XQeuM7P5KYdrE/bn+CDB2EREpEDMmweHHAK//x6qZW644aqfI/knmzkVO0dfDdge+DPl2J+EZZ63
JRSXiIgUiEWL4Nhj4dNPYexY7TpayCqcVLh7BwAzewjo4e5zqiwqEREpCO5w+ukwahS8+CKE6s9S
qOKU6T65KgIREZHCc8UVMGQIDBsGBx6Y62ikqsWqqGlmuwLHAM2B5ebuuvuRCcQlIiJ5rn9/uPnm
UIfi+ONzHY2sDlmv/jCzLsAEoA1wBGGX0m2AfYH4+6WKiEjBePTRUCnzoovgggtyHY2sLnGWlF4B
9HL3wwgTNHsQEozHARW+EhGp4V54Abp2Dbdbbsl1NLI6xUkqWgEvRvf/BNaIqmv2Ac5IKjAREck/
Y8fCMcdAp05w//2qllnTxPm4ZxM2EAP4Adguut8EaJREUCIikn8mToTDDoM99wzDH3US2Qdb8kmc
j3wccADwMfAE0M/M9o3aXkswNhERyRNTpoTy29tsA88+Cw0a5DoiyYU4ScW5QNk/lxuBRcAewFPA
DQnFJSIieWLatLBcdOON4aWXYM01cx2R5EpWSYWZ1QEOBUYCuPtS4OYqiEtERPLATz/B/vuHnolR
o2DddXMdkeRSVnMq3H0xcDfLeipERKSG+u230EOxYAG88kroqZCaLc5EzXeBnZIORERE8sfcuWGD
sBkzQkLRokWuI5LqIM6cikHAHWa2KTAJmJd60N0/SiIwERGpnhYuhCOPhI8/htdfD5MzRSBeUvHf
6Gv/lDYn7F7qhG3QRUSkAC1eDMcdB2+8ASNGwK675joiqU7iJBXq5BIRqYGWLg07jj73HDzzDOyz
T64jkuomzi6l31ZFICIiUn25w4UXhh1HH344FLkSSRergKqZnWhmE8xshpltFrX1NLPDkw1PRESq
g+uvh759YeBA7Tgq5YuzS+lZwB3AS4TS3GVzKH4HeiYXmoiIVAf9+8M118CNN8LZZ+c6GqnO4vRU
nAec7u43AktS2icC2ycSlYiIVAtDh0KPHmEL88svz3U0Ut3FSSpaAO9naF8IrFG5cEREpLp49lk4
5RQ47TS49VYwy3VEUt3FSSq+IXPxq4OAzyoXjoiIVAcjRkDnzqEexd13K6GQiomzpPQO4E4za0Co
TbGbmRUBlwOnJRmciIisfk88ESZjHnQQDBsGtVV9SCoozpLS+81sAWFH0kbAo8APQA93/+9Knywi
ItXagw+GWhRdusDgwVC3bq4jknwSp6cCd38EeMTMGgFruvvMZMMSEZHVrU8fuOAC6N4d7rwTasUq
OiA1Wex/MmbWFGgHtDazDZILSUREVif3sGT0ggvgsstg0CAlFBJP1j0VZrYWYVOxIpYlJUvM7DHg
HHcvSTA+ERGpQkuXQq9eoRZF794hqRCJK04uej/wV+AQQvGrxsChwC7APcmFJiIiVWnxYjj1VBgw
AO66SwloqhCVAAAgAElEQVSFVF6cpOJQ4BR3H+nuc9z9D3cfCZwOZF0N3swuN7N3zWyOmf1sZs+Y
WeuVnP+ymS01s04xYhcREcL25Z07h308hg0L8yhEKitOUvErkGmIowT4Lcb12gMDCL0f+wN1gVFm
1jD9RDPrRaji6TFeR0REgHnzwoZgL74Ydhs97rhcRySFIs7qjxuAO8ysq7v/CGBmGwH/Aa7P9mLu
fnDqYzPrBswkTAIdn9K+I2FvkV2Bn2LELSJS4/3+OxxyCHz0UShwpe3LJUlxkoqzgC2Ab81setTW
nFCmewMzO7PsRHdvG+P6TQg9EbPLGqJei0cJE0Fnmkq7iYhk7eefoWNH+O47eP112HXXXEckhSZO
UvFs4lFELGQLfYHx7j4l5VCfqO2FqnptEZFCNn067L8/zJ0Lb7wB226b64ikEMWpqPnvqggkMgjY
BtizrCGakLkvmfcbWalevXrRuHHj5dqKioooKiqqZJgiIvnjiy/ggAOgTh0YPx5atsx1RFJdFBcX
U1xcvFxbSUn8yhDmHn/Oo5mtSdpkT3efE/NaAwmrR9q7+/SU9j6E7dZTA60NLAXecPd9M1yrLTBp
0qRJtG0bZwRGRKQwfPABHHggbLABvPIKbLJJriOS6m7y5Mm0a9cOoJ27T87muXGKX7UABgL7AA1S
DxF+8We99UyUUBwO7J2aUER6A/eltX0C9AA0HCIiUo4334SDD4YttwyTMtdbL9cRSaGLM6diGCGB
OAX4mUou7zSzsuqcnYB5ZrZhdKjE3UujfUVmpj0H4Dt3/7Yyry0iUqhGjgzblu+6KwwfDmuvneuI
pCaIk1TsSOgS+SKhGLoTEpMxae0nA0PLeY7qVIiIZOAOffvCRReFXorHH4eGK1T9EakacZKK94BN
gUSSCnfPugCXu2c9xCIiUujmz4czzoBHHoFLLoGbboLa+mkpq1GcpOI04G4za0aY27Ao9aC7f5RE
YCIiUnHffgtHHAGffw7FxdClS64jkpooTlKxAdAKeCilzanERE0REYlv9Gg49lhYc0146y3Yccdc
RyQ1VZy9Px4E3gd2B1oCLdK+iojIauAO/fqFGhQ77QQTJyqhkNyK01OxGdDJ3f+XdDAiIlIxCxbA
mWeGXUYvugh69w7FrURyKc4/wdcJK0CUVIiI5MD06WG56JQpYVKmdhmV6iJOUvE80MfMtgc+ZsWJ
msOTCExERFY0diwccww0agQTJsDOO+c6IpFl4iQVd0dfr85wTBM1RUSqgDsMHAi9esFee4X6E+uv
n+uoRJYXp0ZErZXclFCIiCSstBROPhnOPz/cRo1SQiHVU6Wm9ZhZA3cvTSoYERFZ3vffh/kTH38c
JmWecEKuIxIpX9Y9FWZW28z+ZWY/AHPNrGXUfr2ZnZp4hCIiNdS4cdCuHfz0U5g/oYRCqrs4dSqu
BLoBlwB/prR/Qqi2KSIileAOd94J++4LbdqE+hNt2+Y6KpFVi5NUdAXOcPdHgCUp7R8CWycSlYhI
DbVgAXTrBueeC2edBa+8Ak2b5joqkYqJM6eiGZlrVNQC6lYuHBGRmuubb+Coo8L+HZo/IfkoTk/F
FKB9hvajCeW7RUQkSyNHhvkTv/8e9u9QQiH5KE5PxXXAkGiX0lrAkWa2FWFY5NAkgxMRKXRLl4YS
2//6Fxx0EAwbBuuum+uoROKJU6fiOULysD8wj5BktAEOc/dXkg1PRKRwlZSE7cqvuiokFS+8oIRC
8lusOhXuPh44IOFYRERqjE8+CfUnZs6E4cPhsMNyHZFI5cWpU/G1ma2Xob2JmX2dTFgiIoXr8cfh
b3+D+vXDclElFFIo4kzU3JzM+3vUJ6wMERGRDBYvhgsvhM6doVMnePtt2GKLXEclkpwKD3+YWaeU
hx3NrCTlcW1gP2BaQnGJiBSUmTNDMjFuHPTtG/bwMMt1VCLJymZOxbPRVweGpB1bREgoLkwgJhGR
gvL223D00aGn4vXXwy6jIoWowsMfZTuRAtOBpmm7k9Z3963c/YWqC1VEJL+4wz33hCSieXOYNEkJ
hRS2OEtKW7j7L1URjIhIoViwAE49Fbp3h9NPhzFjoJlmnUmBq9TW5yIisqLPPoPjjgvltocMga5d
cx2RyOoRZ/WHiIhk4A533x3KbZeWhnLbSiikJlFSISKSgFmz4PDDw86i3bqF+RM77ZTrqERWLw1/
iIhU0ogRIZFYskTVMaVmq1BSYWZrV/SC7j4nfjgiIvmjtBQuuwz69YOOHWHwYNhoo1xHJZI7Fe2p
+J1Qn2JlLDonU7VNEZGC8vHHYTLmV1+FpOLcc6GWBpSlhqtoUtGhSqMQEckT7jBgAFxyCWy5Jbz3
Hmy/fa6jEqkeKpRUuPvYqg5ERKS6++knOPnkMIfi/PPh5puhYcNcRyVSfcSeqGlmjYDmQL3Udnf/
qLJBiYhUNy+8AKecEoY4XnoJ/vGPXEckUv1knVSY2QbAQ0B5/6U0p0JECsb8+XDxxTBoEBx6KDzw
ADRtmuuoRKqnONOK+gJNgL8CC4CDgJOAr4BOK3leRmZ2uZm9a2ZzzOxnM3vGzFqnHF/HzPqb2edm
Ns/MvjWzftmsSBERieODD2CXXeDBB0NSMXy4EgqRlYmTVOwLXODuE4GlwLfuPgy4BLg8xvXaAwMI
Scr+QF1glJmVjVRuAmwMXABsR0hgDgLuj/FaIiKrVFoKV10Fu+4K9evD5MmhqJW2KhdZuThzKtYA
Zkb3fwM2AL4EPgbaZnsxdz849bGZdYuu3w4Y7+6fAseknPKNmV0JPGxmtdx9adbvQESkHGPGwBln
wLffhsTisstCYiEiqxanp+ILYKvo/ofAmWbWDOgO/JhATE0I9S5mr+KcOUooRCQps2fDaadBhw6w
4YZh6OOaa5RQiGQjTk9FX8JwBMC/gRHA8cCfQLfKBGNmFl1/vLtPKeec9YGrgHsq81oiIhDqTjz2
GPToAQsXwj33hORChaxEspd1UuHuj6Tcn2RmmwFbA9Pd/ZdKxjMI2AbYM9NBM1sLeBH4hJDQiIjE
Nm0anH02vPwyHH009O8PG2+8yqeJSDkqvaGYu88HJlf2OmY2EDgYaO/uKwyjmNmawEhCyfAj3X3J
qq7Zq1cvGjduvFxbUVERRUVFlQ1XRPLY4sWhKuZVV8E668Bzz0GnrNeuieS/4uJiiouLl2srKSmJ
fT1zX9WWHmBmdwD/cvd50f1yufsFWQcREorDgb3d/esMx9ciJBQLgIPdfeEqrtcWmDRp0iTats16
7qiIFLD334fTTw8rOs49F264AdbWAnWR/zd58mTatWsH0M7ds+o0qGhPxc6EpZ5l9xNjZoOAIkKN
i3lmtmF0qMTdS6MeileABoS5G01s2bquWZqsKSIVMX8+XHst3HEHtGkDb74Jf/tbrqMSKSwV3fuj
Q6b7CelOWO0xJq39ZGAoYWnprlHb/6KvZTuitgCmJxyPiBSYUaOge3eYMQOuvx4uugjq1l3180Qk
O1nPbzazB6PhiPT2NczswWyv5+613L12htvQ6PjYDMfKnqOEQkTKNXUqdO4MHTvC5puH7covv1wJ
hUhVibNo6iQg0758DYGulQtHRKTyZs0KS0TbtIHx4+Ghh+C118JW5SJSdSq8+iPaa8Oi21pmVppy
uDZh5cbMTM8VEVkd5s+HPn3glltCSe1rr4WePaFRo1xHJlIzZLOk9HfCPAYnlOVO58A1SQQlIpKN
xYth8GC4+mr45ZdQe+Kqq2D99XMdmUjNkk1S0YHQS/E6cBTLl9H+k7Cx2IwEYxMRWSl3eP75sD/H
Z59BUVFYItqyZa4jE6mZKpxUuPtYADNrAXynpZwikktvvw2XXALjxsG++8LDD0NYWi8iuRKnTPe3
ZtbEzHYDmpI22bNs1YaISFX48ku44gp46inYYYdQYrtjR21LLlIdZJ1UmNlhwCOELdD/IMylKOOE
2hIiIon6+We47rqw4VezZjBkCBx/PNSunevIRKRMnL0/bgceBK6I9v0QEakyv/4Kt90W9uqoVw9u
vjmU127QINeRiUi6OElFM6C/EgoRqUqzZ4eS2v36hcc9eoRKmOusk9u4RKR8cZKKkcAuwAobf4mI
VNbvv0PfvqHexOLFcN55IZnQ8lCR6i9OUvEi8B8z2wb4GFiUetDdhycRmIjULHPmQP/+cPvtUFoK
55wTVnc0bZrryESkouIkFfdFX6/OcMwJ1TVFRCpk7twwX+K222DevLDx16WXwsYb5zoyEclWnCWl
cfYLERFZzrx5MGgQ3Hpr6KU4/fSw2VezZrmOTETiitNT8f/MrIG7l676TBGRYP58uPvusD/H7Nlw
6qmh7kTz5rmOTEQqK87W57XN7F9m9gMw18xaRu3Xm9mpiUcoIgVhwYKwkqNVqzBX4rDD4KuvQoKh
hEKkMMQZyrgS6AZcQtjzo8wnwGkJxCQiBaQsmWjZEi68MFS//OILuP9+2HzzXEcnIkmKk1R0Bc5w
90eAJSntHwJbJxKViOS9BQvCao5WrUIycdBB8PnnYTfRVq1yHZ2IVIW4xa/+l6G9FlC3cuGISL4r
LYX77oPevUNp7RNPDNuQb7FFriMTkaoWp6diCtA+Q/vRwPuVC0dE8lVpaVga2qoV9OwJBxywrGdC
CYVIzRCnp+I6YIiZNSMkJUea2VaEYZFDkwxORKq/0tIwP6J3b/jpJzjhhNAzseWWuY5MRFa3rHsq
3P05QvKwPzCPkGS0AQ5z91eSDU9EqqvSUhg4MPRM9OgB++0Hn30Wdg9VQiFSM8WqU+Hu44EDEo5F
RPJAaSk88EDomfjxx7D9+FVXQevWuY5MRHItTp2Kr81svQztTcxMm4yJFKjSUrjzzjA/4vzzYZ99
YMoUGDpUCYWIBHEmam5O5v096hNWhohIAUlPJjp0CMnEsGGw1Va5jk5EqpMKD3+YWaeUhx3NrCTl
cW1gP2BaQnGJSI4tXBiGOW66KQxzHHdcGOZQIiEi5clmTsWz0VcHhqQdW0RIKC5MICYRyaGyZKJ3
b5gxA4qKQjKxtUrbicgqVDipKNud1My+AXZ191+qLCoRWe2UTIhIZcXZ+rxFVQQiIrmxcCE8+GAY
5lAyISKVEWeiJma2t5k9b2b/M7OvzGy4mWWqsiki1VRpKQwaFCZgnnMO7L03fPppmICphEJE4oiz
pPQE4FVgPtAfGAgsAF4zs+OSDU9EkjZ3Ltx+e9g19NxzoX37Zas5lEyISGXEKX51JXCJu/dJaetn
ZhcA/wIeTSQyEUnUb7+FvTn69YM5c6BrV7j0UtWYEJHkxEkqWgLPZ2gfDtxUuXBEJGk//wx9+oSh
jkWL4LTT4OKLoXnzXEcmIoUmTlLxHaEmRfr25/tFx0SkGpg+Hf7zn7DZV506Yd5Er16w4Ya5jkxE
ClWcpOJ2oL+Z7QS8Sahb8XegG9Aj24uZ2eXAEcDWhLkZbwKXuvuXKefUB+4AOhMqd44Eznb3mTHi
FyloX30FN98cymevvTZcfjmcdx6ss06uIxORQhdnSeldZvYTodDVsVHzZ0DnaAfTbLUHBgATo3h6
A6PMrI27L4jO6Qv8AzgKmAPcCTwVPVdEgI8+CstCn3gCmjYNicWZZ8Kaa+Y6MhGpKeLuUvoM8EwS
Abj7wamPzawbMBNoB4w3s7WBU4Au7j42Oudk4DMz283d300iDpF89c47cOON8PzzsNlmYTvyk0+G
Bg1yHZmI1DSxkgoAM9sFaEMY/vjM3SclFFOT6Jqzo8ftCHG+VnaCu39hZtOB3QElFVLjuMOIEWHO
xOjRYSnokCGhcFXdurmOTkRqqqyTCjP7C1AM7An8HjU3MbM3Cb0J38cNxsyMMNQx3t2nRM0bAX+6
+5y003+OjonUGH/+Cf/9b0gmPvkEdt01DHcccQTUzrR3sIjIahSnoub9QF2gjbuv6+7rEnosLDpW
GYOAbYCiCpxrhB4NkYI3Zw7cdlsoWHXSSWGYY8yYMPRx9NFKKESkeogz/LE3sIe7f1HWEA1HnAeM
jxuImQ0EDgbau/uMlEM/AfXMbO203oqmhN6KcvXq1YvGjRsv11ZUVERRUUVyFpHcmzEjFKu6+25Y
sACOPx4uugi23TbXkYlIISguLqa4uHi5tpKSktjXM/fs/tg3sy+BE9InSJrZbsCj7r5F1kGEhOJw
YG93/zrt2NrALMLQyjNRW2vgc+BvmSZqmllbYNKkSZNo27ZttuGI5NyUKaFnYtgwaNgQuneH88+H
Zs1yHZmIFLrJkyfTrl07gHbuPjmb58bpqbgYGGBm5wCT3N2jSZv9gIuyvZiZDSIMd3QC5plZWWme
Encvdfc5ZvYAcIeZ/Qb8QdhzZIJWfkghcYc33gjzJV58MSQQN90EZ5wR6k2IiFR3cZKKwUAj4B1g
cZhbSR1gMfCgmT1YdmI032JVuhPmRoxJaz8ZGBrd7wUsAZ4kFL8aAZwTI3aRamfJEnjmmZBMvPsu
bLddWMnRpQvUq5fr6EREKi5OUtEzyQDcfZWTRd19IXBedBMpCPPnh+Th9tth6lTo0AFeegkOOghC
ri4ikl/iVNQcUhWBiNQU338Pd94J994Lv/8OxxwTlonuskuuIxMRqZzYxa9EJDvvvAN9+4a6Emus
EXYLPfdcaNEi15GJiCRDSYVIFVq0CJ5+OiQTb78NrVqFbci7dYO11sp1dCIiyVJSIVIFZs+G++4L
+3B8/z3suy8MHw6HHAK14pScExHJA0oqRBL02WfQv3+YgLl0aShW1aMH7LBDriMTEal6WSUVZlYH
KAV2cvdPqiYkkfyydCmMGhWGOEaOhI02gssvD9uON22a6+hERFafrJIKd18c7Q6qnQakxps3Dx5+
OJTR/vxzaNsWhg6FY4+F+vVzHZ2IyOoXZ3T3RuAmM6tIYSuRgvPdd3DZZbDppnDOOWEfjnHjYOJE
OPFEJRQiUnPFmVNxLrAFMMPMvgXmpR50d222IQXHHcaOhQED4LnnwpLQ008PS0I33zzX0YmIVA9x
kopnE49CpJqaOzds6jVwIHz6KbRpEyZinniiloSKiKSLU1Hz31URiEh18uWXMGgQPPRQSCwOPzwk
Ex06qIS2iEh5Yi0pNbMmwNFAK+A/7j472m78Z3f/IckARVaXJUvg5ZdDr8TIkbD++mHORPfu0Lx5
rqMTEan+sk4qzGwH4FWgBNgcuA+YDRwJNAe6JhifSJWbPTv0SAwaBF9/HfbgGDIkrOJo0CDX0YmI
5I84PRV3AIPd/RIz+yOl/SXg0WTCEql6H3wQNvZ65JHQS9G5MxQXw2675ToyEZH8FCep2BU4M0P7
D8BGlQtHpGqV7cUxcCCMHw/NmsGVV4aVHCpUJSJSOXGSioXA2hnaWwOzKheOSNX48cew1fg994T7
++wDTz4ZJmDWUbF6EZFExPlxOhy42syOjR67mTUHbgGeSiwykUpauhTGjAkbez35JNSrB127hsmX
222X6+hERApPnKTiQuBJYCbQEBhLGPZ4C7gyudBE4pk2DQYPDpMtp02D1q3httvgpJOgSZMcByci
UsDi1KkoAQ4wsz2BHYE1gcnu/mrSwYlU1Pz5Ya7Egw/C6NGw5pph4uUpp8Duu6u2hIjI6hBnSWlX
4DF3nwBMSGmvB3Rx96EJxidSLnd4++2wHPSxx2DOnDBXYsgQOOqoUEpbRERWnzjDHw8BIwjDH6nW
io4pqZAq9eOPYXfQhx4Ku4M2bw49ekC3btCyZa6jExGpueIkFQZ4hva/EApiiSTuzz/h+edDIjFi
BNStC0ceGTb42ndfqBVnv10REUlUhZMKM3ufkEw48JqZLU45XBtoQejBEEnMhx+GROKRR+CXX0Jh
qoEDoUsXTboUEalusumpKNuddCdgJDA35difwDS0pFQS8Ouv8OijIZl4//1QlKpbt3DbdttcRyci
IuWpcFJRtjupmU0jTNQsraqgpOZZsgRGjQqJxHPPhRoThx4K114L//hHGO4QEZHqLc6S0iFVEYjU
TN9/H4pTPfAA/PADbL893HwzHH+8ymaLiOSbOEtKawO9gGMJu5LWSz3u7usmE5oUqqVL4dVX4a67
wuTLhg3hhBPg1FOhXTvVlBARyVdx5sxfA1wAPAY0Juxa+jSwFLg2scik4Pz6a6hs2bo1dOwIU6eG
1RszZoQEY5ddlFCIiOSzOEtKjwdOd/cXzexaoNjdp5rZR8DfgP5JBij5raxA1V13weOPh8fHHBMK
VO2xh5IIEZFCEiep2Aj4OLo/l9BbAfACcH0SQUn+mzs3LAO9666wLLRlS7j++rCCY4MNch2diIhU
hThJxffAxsB0YCpwIDAZ2JWwLbrUYJ98EhKJhx+GefPgsMPgllvggANUoEpEpNDFSSqeAfYD3gEG
AMPM7FTCpM0+CcYmeWLhQnjqqZBMjB8PG20EPXvC6afDppvmOjoREVld4iwpvSzl/mNm9i2wB/CV
uz+fZHBSvX3zDdxzT9gZdNYs6NAhzJv45z9VV0JEpCaK01OxHHd/G3g7gVgkDyxZAi+9FHolRoyA
xo3hpJOge3fYeutcRyciIrmU9Si3mU03s6FmdoqZtUoiCDNrb2bDzewHM1tqZp3Sjq9hZgPN7Dsz
m29mn5rZmUm8tlTMTz/BjTeGCZedOoWeifvvDwWr+vZVQiEiIvF6Kq4A9gIuA+43sx+AscAYYKy7
fxXjmmsAHwAPknn/kD7APsBxwLdAR2CQmf3g7i/EeD2pgD/+gHffhXvvhaefDkMaRUVw1lmhpoSI
iEiqOHMqhgHDAMxsY2Bv4FDgLkLPR+0Y1xxBtMOpWcbKBbsDQ9x9XPT4vqinYjfCUlaJadEi+Ppr
+PLLcPvii2X3f/wxnLP11qFoVdeusM46uY1XRESqr1hzKsysEbAnofegA9AW+BQYnVhky3sT6GRm
D7n7DDPrAGxJ2C1VVsE9VK1MTxq+/DIkFEuWhPMaNQrVLrfaCvbaK9zfZhvYeWcVqRIRkVWLs/fH
BEIS8TlhyONWwrDHb8mGtpzzgHuB781sMbCEUNVzQhW+Zt75/fflE4ayJOKrr0LNCIDatcO8iNat
wy6gW20V7rduDZtsouRBRETii9NT0QaYB0yJbp9WcUIBcD7wV8Iwy3TCnI5BZjbD3V8v70m9evWi
cePGy7UVFRVRVFRUlbFWqYULw54ZmYYrZs5cdt4mm4REYbfdwmZdZT0QLVpouaeIiATFxcUUFxcv
11ZSUhL7eubu2T/JbAfC0MfeQHtgEaHXYrS73x87mnDtpcA/3X149LgBUAIcHs29KDvvPqCZux+c
4RptgUmTJk2ibdu2lQmHb7+F0aPDEEF5t8WLK3e8oteYOROmTQu7fAKsvfayZKGst6F1a9hyS1hr
rUq9bRERqaEmT55Mu3btANq5++RsnhtrToW7fwR8BPQ3s3bAucAJQBegUklFBnWjW3r2s4R4u6xm
ZeJEOPnkcN8sDB+k3+rUydxe0eOp59SpA/XrZz7n738PCURZEtG0qYYrRESk+ogzp2JnQi/FPoRe
irUIG4wNJPRWZM3M1gC2AMp+RbY0sx2B2e7+nZmNBf5jZqWEJaX7AF2BnnFeLxv//GdYIVG7tn6B
i4iIrEycnor3gPeBNwi9EuPc/fdKxrELYeWIR7fbo/YhwClAZ6A3YSnruoTE4nJ3v7eSr7tKtbNe
ICsiIlIzxUkq1nX3OUkG4e5jWclQhrvPBE5N8jVFREQkWVnPSUg6oRAREZHCUOUTHUVERKRmUFIh
IiIiiVBSISIiIolQUiEiIiKJiLuh2F+ATkBzoF7qMXe/IIG4REREJM/EKX61HzAc+BrYGvgE2JxQ
uCqrcp4iIiJSOOIMf/QGbnP37YFS4ChgU2As8ESCsYmIiEgeiZNUtAGGRvcXAw3dfS5wNXBpUoGJ
iIhIfomTVMwD6kf3fwRapRxbv9IRiYiISF6KM1HzbWBPYArwEnC7mW0PHBkdExERkRooTlJxAbBm
dP+a6H5n4KvomIiIiNRAWScV7v51yv15QPdEIxIREZG8FKv4lZk1MbPTzKy3ma0btbU1s2bJhici
IiL5Ik6dih2AV4ESQn2K+4DZhDkVzYGuCcYnIiIieSJOT8UdwGB335JQp6LMS8BeiUQlIiIieSdO
UrErcE+G9h+AjSoXjoiIiOSrOEnFQmDtDO2tgVmVC0dERETyVZykYjhwtZnVjR67mTUHbgGeSiwy
ERERyStxkooLCbUpZgINCXt+/A/4A7gyudBEREQkn8SpU1ECHGBmewI7EhKMye7+atLBiYiISP6I
U1ETAHefAExIMBYRERHJYxUe/jCz3c3s0LS2rmb2jZnNNLN7zax+ec8XERGRwpbNnIqrgW3LHkSb
iD1AKIR1M3AYcHmi0YmIiEjeyCap2Al4LeVxF+Addz/d3e8AzgeOTTI4ERERyR/ZJBXrAD+nPN4b
eDnl8XvApkkEJSIiIvknm6TiZ6AFgJnVA9oCb6ccXwtYlFxoIiIikk+ySSpeAm42s/ZAb2A+MC7l
+A7A1ARjExERkTySzZLSfwFPE4pdzQVOcvc/U46fAoxKMDYRERHJIxVOKtz9F2AvM2sMzHX3JWmn
HENINkRERKQGiltRM1P77MqHIyIi8n/tnXncVVW5x78/ETQF9SYppQwFDjlx1QYUy3s1Bc2w9Ba3
vIopOZTWpxwqrgoO4FzaZDdNy3JKwyEVcMwBX3FAEXNCUXAABTFm1OC5fzzr6Ga/Z3rf9/Ce8748
389nfc7Zaz17r2etZ529n732s88KOiqtWfsjCIIgCIKgGeFUBEEQBEFQExrCqZD0BUm3SHpd0ipJ
w4rIfFrSzZL+KWmJpCmStqyHvkF9uOaaa+qtQlBDwp6di7BnAA3iVAAbAk8C3wMsXyipP/766jPA
F4EdgTOBFe2oY1Bn4qTVuQh7di7CngG0YZXSWmJmE4GJAJJUROQs4DYzy64t8nJ76BYEQRAEQXU0
ykGBndQAABLJSURBVExFSZKT8WVghqSJkt6U9LCkA+utWxAEQRAEH9LwTgWwGdAd+DH+r577ADcC
49O/ewZBEARB0AA0xOOPChQcn5vM7Bfp+1OSdgeOYfW/Ci+wPsDIkSPp0aPHagVDhgxh6NCha0rX
YA2ycOFCpk6dWm81ghoR9uxchD07JhMnTmTSpEmr5S1evLjwdf2WHk9mzeIi64qkVcBXzeyWtN0V
WAqMMbNxGblzgMFm1my2Ijkck9tJ5SAIgiDojAw2s4daskPDz1SY2fuSHgW2yRVtDcwqsduTwK5r
VLEgCIIg6Nw819IdGsKpkLQhMAAovPnxKUkDgQVm9ipwPnCtpAeAe4H9gAOAPYsdz8yWATEPFwRB
EATtSEM8/pC0J+4s5JX5o5kdkWQOB0YBWwDPA6eZ2a3tqWcQBEEQBKVpCKciCIIgCIKOT0d4pTQI
giAIgg5AOBVBEARBENSEDu1USOor6TJJMyUtkzRD0pj0GmpWbidJ90taLmmWpJOKHOvrkp5NMtMk
7dd+LQkKSBolabKkpZIWlJBZlUsrJX0jJ/Mfkh6XtELSC5JGtE8LgixV2rO3pNuSzFxJ50laJycT
9mxQJL1S5Pd4ck6m4jk4aBwkfU/Sy8leD0v6bLX7dminAtgWf2PkO8B2wA/xP8QaWxCQ1AOYhK8V
sgtwEjBG0siMzG7A1cClwL8DNwE3SdqufZoRZOgK/AW4pILcCGBzoBfwcdxmAEjqB9wK3A0MBC4G
LpO0T+3VDSpQ1p7JebgdfxNtEG7Xw4EzMjL9CHs2Mgacwuq/x18WCqs5BweNg6ThwIXAaGBnYBow
SVLPqg5gZp0qAScCL2a2jwXmA+tm8s4GnslsXwvckjtOE/CberdnbU34xWVBibJVwLAy+54LPJXL
uwa4vd7tWltTKXvir4e/D/TM5B0NvFP4zYY9GzvhzsL3y5RXPAdHapwEPAxcnNkW8BpwcjX7d/SZ
imJsAmSnWQcB95vZvzJ5k4BtJG2ctncD7sodZ1LKDxqTX0uaJ2mKpG/nygYR9uwoDAKmm9n8TN4k
YGNg+4xM2LOx+Ymk+ZKmSjpRUpdMWTXn4KABSKEDu+KzggCYexZ3UeXvrSH+/KpWSBoAHAf8KJPd
C5iZE30zU7Ywfb5ZRKbXGlAzaDunAvcAy4B9gd9I2tDMfpXKS9lzI0nrmdm77adqUIFStiqUTSsj
E/ZsDC7G/2xwAbA7cA5usxNTeTXn4KAx6Al0ofjvLf+v1kVpyJkKSWcXCcbLBwJtndtnC2ACcJ2Z
XV6pipTK/UlHpfKgSlpjz3KY2VgzazKzaWZ2PnAe/py2rBqF3VvbjsCptT3LUOn3WUkmaCUtsbGZ
XWRm95vZ02b2O+AE4Ph8wHy+ivQZ9usYVH09bNSZiguAKyrIfOD5SvoEfuf6oJkdnZObiwcQZdkM
76A3K8jkvbWgdbTInq1gCnCKpG5m9h6l7bkolQdto5b2nAvkI8s3z5QVPsOe7UtbbDwFv7b0A2ZQ
2n4Q59hGYz6wkjZcDxvSqTCzt4G3q5FNMxT3AI8CRxQRaQLOktTFzFamvH2B581sYUZmb+AXmf32
SflBG2mJPVvJzsA7mQtMEx4AmGVfwp41ocb2bAJGSeqZiavYF58SfzYjE/ZsR9po453xYOq30nY1
5+CgATBfwPNx/HpYWClcNL8+lj1Ih034q0szgDuBT+De1ebA5hmZjYA3gD/ir50OB5YAR2ZkdgPe
w2MxtgHGACuA7erdxrUtAb3x1wZPwy8sA1PaMJUfgDuP2wH98cjyJfhaMIVj9Et55yZ7fjfZ90v1
bt/alqqw5zp43MQEYCdgCH5HdGbYs/ETHoT5g2S7TwKHJPtdnpGpeA6O1DgJ+AawHDgM/9uG/8Md
zI9VtX+9G9DGxo/Ap2qyaRWwMie3I3AfHtg3GzixyLEOxpd5XQ48BQypd/vWxoRPueZtuhL4Yiof
ggeFLQQWpe8jixxnT+DxZM8ZwKH1btvamCrZM8n0xv+HYkm6IJ0LrBP2bPyEz0o04UGaS4GngZOB
rjm5iufgSI2TkuP+Svq9NQGfqXbfWFAsCIIgCIKa0JBvfwRBEARB0PEIpyIIgiAIgpoQTkUQBEEQ
BDUhnIogCIIgCGpCOBVBEARBENSEcCqCIAiCIKgJ4VQEQRAEQVATwqkIgiAIgqAmhFMRdBgkfUTS
XyUtTKskblQnPe6V9LM2HmO0pKntXW8L6hot6Yn2qKs9kfQ7SW+n8bNTvfVpbyTtmVYZ3Shtj5D0
Tqa8xeOyjfr0TfqUtEVe56CxCaeiEyOpp6RLJM2StELSHEkTJO1Wb91ayQhgML7ewMfNbFGd9WkL
5+OL9NSUdPIdVqPDdaq/25U0FF/PYH983aCn66tR3cjbNbu9RsZlGWYDvahsi6rGoqSZkvZqs1ZB
q2nIVUqDmjEet/GhwMv4Ymt7A5vWU6mWIqmrmb2PLyD2rJk9W2mfRsfMluHrIARtRNK6ZvavKkQH
AHPMbEob68uuttmpaO9xab5OxFsVBasgzXZsgq8xEtSJmKnopEjaGNgD+LGZ3W9mr5rZY2Z2rpnd
mpWTdJmkt9JjhbuyU5GSPiXpJklzJS2W9IiksncyknaSdI+kRemYj0raJZU1m1aX9ANJL2e2r5B0
o6RRkl4HnpN0L3ACUJgKvSfJHpKOvyjNxFwl6WO5428n6W9Jl0WS7pP0yUz5SEnPSFqePo+toovX
kXRumkqfI2l0vv8r9Otq/SCpi6RfSHpH0jxJ50j6g6Qbq6039aEBN6U+mllK+XT85yUtlfSSpDMk
dSkid5Sk2UnuOkk9MmWSdJqkV9NM2BOShmTKH5I0Lne8npLekzQ4bXeTdIGk1yQtkdQkac8y/V6Y
jTlG0s2SlgCjUv4Okm5P43SupCslfTSVXYEv3dwn2zepDT+V3+EuS204OFNXYbwNlfSYpBX4bBmS
DpT0eBo3L6a+6JLT80hJ41P/vSDpK7m21HRsVmpPJYqMy8Jv8bTMWL5E0roZmf+S9FSqb76kOyR9
JKNPuTHS7PGHpP3T2Fwm6W58ldpqGAZMLOXwpXqOSv29NPXnIEn95Y8Wl0ianO3/oBXUezW0SGts
lbku+CqeFwLdysjdCdyIrzbYHzgPv3PYJJXvBHyHD5caPx1fjXDLMsecji9zvFXa52Bgx1Q2Gpia
k/8BMDOzfUXS/Q/Ap1PaBF+C90HgYxn9DsdXLu0HfC6V35o51ieA+cBfUhsH4I9RtkrlhwCvAQcC
fYGvAvMoswomcC/wDnBqat+h+Mqbe7egX1frB+B/U73DgK2B3wD/BMZXWy/QE1+l91BgM2DTMm0Y
BXwe6AN8GV+a+sRM+WhgcWrHjriD+gLwp4zMD5M+X0+2Pgd4F+ifyr8HvJyr97hsHnAp8ACwO750
9o/wO+X+ZXRfBcxJduwHbAlsTFoyPekyEJgI3J326QGcAsxK42fTTL//A/hSOtZhqf4vpPI9U31P
4LN8n8TH4h7JPv+Txs3ewEvAqTk9Z+FLSX8KuAgf14UxsCbGZjXtWQlslLZHAAtyds+Oy8Jv8Wr8
d7gfmaXp8UcX7wHfx8fS9sAxwAZVjpG+SZ+d0nZvfGXM85L8N5OtP9C5TNsfAYZXGDez8fPRAOCv
wEx8jH8J2AZ4CLitnufujp7qrkCkNWhc+Fo6aS3DL7ZjSRf3VD44/eDzyxTPoMhy4pny6cB3y5Qv
LHXiy5+0Ul4xp+INYN2c3M+Beyq0+TPpBFQ4qY0DXgS6lJCfkT8RpRPz5DJ13Avcl8ubAoxL3/eo
1K9FTt5zgB9mttfBlx7OOxUl603bq4BhrRgrJwCP5Oz0Hh67UsgbAvwL2Cxtv4bPhOX1+WX63hO/
gAzOlE8GxqbvfYD3gV65Y9wJnFVG11XABUVsNiGXt2WSHVBinHXDl1v/fG6/S4E/p+8Fp+KAIjrm
234I8HpOzzGZ7Q3S2Nx3TYzNFrSnpU7FPGC9TN7RwML0fed0vN4ldKo0Rvqmfio4FeOA6Tn5s6ng
VOAO2vIKMnl7fD7ljcjkDQeWtvT3E+nDFDEVnRgzu1HSbcAX8ODG/YCTJR1pZlfid3M9gAWSsruu
j98JI2lDfHaiENy2birvU6bqnwG/l3QYcBdwvZmVnIovwXSr4jm5pF3xE+FA4N/48JFeH+C5lP+A
FZkSlbQB3s7fS7osU9QFvwstx1O57Tn47AD47E7Zfs3psREe7/JoIc/MVkl6HFBOvFy9VSNpOHB8
0qc7bteFObHZZjYns92E9+82kpbjJ/KHcvtMxtuPmc2XdBd+sS1MK++Gz3wB7ID39QtavaO64c5w
OR7PbQ8E9pK0OJdvqY0vFjnGAPxCf2eu/q5A9g0IK1Hf7pJOyeR1AbpJWt/MVqS86R8cxGxZ0m+z
zDFqOTarbU9LmWZm72a2m4DuknoD04B7gKclTQLuAG4ws3/KH5WVHSNF2BZ3OrI0VaHjMOBBqxy8
PT3z/c30+XQub31J3c1sSRX1BjnCqejkmNl7wN0pjZV0Ke4kXIlfTN7A717yF6/CietCfGr3BHx6
dzk+bditTJ2nS7oKn1bfHzhd0nAzuxm/M8jX1bXIYZZWals68U4EJgDfwu+o+qa8gn7Lyxyie/oc
iU+dZqkUiPd+btv40KGppl+LYbnt/L6V6q0KSYOAP+OPUe7AnYlv4o8eymG5z/x3cJ2zeVcBF0k6
HrfRNDN7JpV1x2c+dsHHRZZKJ/T8+OgO3AKcTPN+m0NxCvbfH7dXlndz28XqOw0Phl6NjEMB5e1V
67HZkvbUAjOzVcA+8jfK9sUd1bGSPgcsKMjl9suPkWrLyjEMt38lsvawMnkRb9hKwqlY+3gWf0YL
fvfSC1hpZrNLyO8O/MHMbgGQ1J0qAqfM7EXgYuBiSVcD3wZuxi/8vXLiO7ewDQW2BT4K/NTMXk/6
fS4n8xRwmIpE7JvZW/JA0P5mdm0rdShGNf2a1WORpDfxmJDJAJLWwfulpf8V8T5+N1uO3YFXzOyc
QoakfkXk+kjqZWZzM/utBJ43s8WS3sAf9TyYO3b2TvMm4Lf4LNk38TiZAk8kXTc3s8kVdK7EVOAg
YFa60FXDM/jFtq+ZPVhJuEh927RiBi5LrcdmW9pTjoGS1svMVuwGLDGz1zL6NgFNks7E40i+ZmYX
VTlG8m34Si6v7CvwaTb1P4FqAqzztMaBCcoQTkUnRR71fj1wOX7yWgx8FjgJP9FjZndJasLfFvgx
Hoi3BX6nM97MpuLPdQ+SVHhj5AyK30EX6l0ff9f9Bvw11t6p3uuTyN+BX0k6OcnsBwyl+dR7Ncwm
BYlJ+i0eUHhKTuZXeHDgdZLOTvUMAqaY2QxgDO74LMJnONbD4zI2MbOLWqFTtf2a55fAKEkv4Y9t
jscDAlt60nsF2FvSQ8C7ZlZsZmQG7jAMxx+5HIAHAeZ5F/ijpJPwQMiLgevMbF4qPx8YI3+T4kng
CHxK/1uFA6Qp/1vwAMptgWsyZTOSw3mlpBNxJ2MzYC98RmNCC9r9a/yu/lpJ5+F3yVvhz8iPNLNm
/WhmSyRdAPxc/tbGg6mdg/GYgT8l0WLj/Qzgb5JexcfxqtT2Hczs1Cp1runYbGN7ytENfwwzFr+h
GIOP14ITvzc+4/VW0r8n7hxAFWMkx2+BHyUbXpbaO6KCfkNxR3dWC9sFxfuipf0TZKl3UEekNZPw
E8FY/KKxAHcqnsFPCNmgqw3xqPRXgRX4RelKYItU3hePi1iSyo7Fn6H+rES9XfFI8Vfw6d1X0/G7
ZWSOSuWL8ECwn9A8UHN8kWM3C9TELxov8WEw6pfJRJMnmR3wRySL8ccPfwf6Zcr/G7/zXI4/y78X
OLBM3zZrP/6mx+Ut6Nd8QFwX/KL9TtJhHHAdcFUL6z0AeB53CGaWacM5+EVgYbLX9ykSsIcH5b2G
T/9fC2yckRHuxM1ObZwK7FOkrv2STZoF2aZ2j042XAG8jl+kty+j+0qKBKPiMQg3AG/j4/UfwIWZ
8tUCNTP5x+G/jRXAXOB2YI9UtlpgY26/ffA3V5YkuzXhDkxJPfHf4mFramy2tD1UF6g5PuXPS+Pl
ElIQMu4oTkj1LMNnQo+tdoyQe/sj5e2Pj+FlqT9GlLJBkr8SOKOKc+Jq9ihRd0l7R6ouKXVkEAQN
RAq0exafGRhdb32CtRP5/3tsbGYH1VuXYqTHhG8BQ83ssXrrE8TjjyBoCCT1wQPd7sPfEjkOn2q+
uo5qBUGjsyk+excORYMQEa5B0Biswv/I6xF8Sn17/E+tnq+nUkHQyJjZPDMbV1kyaC/i8UcQBEEQ
BDUhZiqCIAiCIKgJ4VQEQRAEQVATwqkIgiAIgqAmhFMRBEEQBEFNCKciCIIgCIKaEE5FEARBEAQ1
IZyKIAiCIAhqQjgVQRAEQRDUhHAqgiAIgiCoCf8PYZugQQrH5LEAAAAASUVORK5CYII=
)](CF-UGRID-SGRID-conventions_files/CF-UGRID-SGRID-conventions_11_0.png)


<div class="prompt input_prompt">
In&nbsp;[7]:
</div>

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(3, 7))

t = t_profile.data
z = t_profile.coord('sea_surface_height_above_reference_ellipsoid').points

l, = ax.plot(t, z)
```


[![](data:image/png;base64,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
RU5ErkJggg==
)](CF-UGRID-SGRID-conventions_files/CF-UGRID-SGRID-conventions_12_0.png)


\* Most people miss the concept of a "dataset" when using `iris`, but that is a
consequence of the CF model since there are no unique names to the variables and
the same dataset might contain phenomena with different coordinates.

Aside: note that the [xarray](http://xarray.pydata.org/en/stable/) **does** have
a dataset concept, but it infringes the CF model in many places to do so.



For more on iris see: https://ocefpaf.github.io/python4oceanographers/blog/2014/
12/29/iris_ocean_models/

# UGRID-1.0 (pyugrid)

http://ugrid-conventions.github.io/ugrid-conventions/

<div class="prompt input_prompt">
In&nbsp;[8]:
</div>

```python
import pyugrid

url = 'http://crow.marine.usf.edu:8080/thredds/dodsC/FVCOM-Nowcast-Agg.nc'

ugrid = pyugrid.UGrid.from_ncfile(url)
```

In a nutshell the `pyugrid` loads the data into a `ugrid` object that parsing
and exposing the underlying grid topology.

<div class="prompt input_prompt">
In&nbsp;[9]:
</div>

```python
lon = ugrid.nodes[:, 0]
lat = ugrid.nodes[:, 1]
triangles = ugrid.faces[:]
```

Sometimes the topology is incomplete but, if the data is UGRID compliant,
`pyugrid` can derive the rest for you.

<div class="prompt input_prompt">
In&nbsp;[10]:
</div>

```python
ugrid.build_edges()
```

<div class="prompt input_prompt">
In&nbsp;[11]:
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


[![](data:image/png;base64,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
/wHdlKK83JBuJgAAAABJRU5ErkJggg==
)](CF-UGRID-SGRID-conventions_files/CF-UGRID-SGRID-conventions_20_0.png)


There is some effort to integrate `pyugrid` into `iris` to augment the cube
object to be both CF and UGRID aware by adding convenience plotting and slicing
methods with pyugrid. You can see the full pyugrid example [here](https://ocefpa
f.github.io/python4oceanographers/blog/2015/07/20/pyugrid/).

# SGRID-0.3 (pysgrid)


http://sgrid.github.io/sgrid/

<div class="prompt input_prompt">
In&nbsp;[12]:
</div>

```python
import pysgrid

url = ('http://geoport.whoi.edu/thredds/dodsC/clay/usgs/users/'
       'jcwarner/Projects/Sandy/triple_nest/00_dir_NYB05.ncml')

sgrid = pysgrid.load_grid(url)
```

The `pysgrid` module is similar to `pyugrid`. The grid topology is parsed into a
Python object with methods and attributes that translate the SGRID conventions.

<div class="prompt input_prompt">
In&nbsp;[13]:
</div>

```python
sgrid.edge1_coordinates, sgrid.edge1_dimensions, sgrid.edge1_padding
```




    (('lon_u', 'lat_u'),
     'xi_u: xi_psi eta_u: eta_psi (padding: both)',
     [GridPadding(mesh_topology_var='grid', face_dim='eta_u', node_dim='eta_psi', padding='both')])



<div class="prompt input_prompt">
In&nbsp;[14]:
</div>

```python
u_var = sgrid.u

u_var.center_axis, u_var.node_axis
```




    (1, 0)



<div class="prompt input_prompt">
In&nbsp;[15]:
</div>

```python
v_var = sgrid.v
v_var.center_axis, v_var.node_axis
```




    (0, 1)



<div class="prompt input_prompt">
In&nbsp;[16]:
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



The API is "raw" but comprehensive. There is plenty of room to create
convinience methods using the low level access provided by the library.

See below an example of the API and some convenience methods to `slice`, `pad`,
`average`, and `rotate` the structure grid.

(Ideally all that could be done in the background in a high level object like
the iris cube.)

<div class="prompt input_prompt">
In&nbsp;[17]:
</div>

```python
from netCDF4 import Dataset

nc = Dataset(url)
u_velocity = nc.variables[u_var.variable]
v_velocity = nc.variables[v_var.variable]

v_idx = 0  # Bottom.
time_idx = -1  # Last time step.

u_data = u_velocity[time_idx, v_idx, u_var.center_slicing[-2], u_var.center_slicing[-1]]
v_data = v_velocity[time_idx, v_idx, v_var.center_slicing[-2], v_var.center_slicing[-1]]

# Average at the center.
from pysgrid.processing_2d import avg_to_cell_center

u_avg = avg_to_cell_center(u_data, u_var.center_axis)
v_avg = avg_to_cell_center(v_data, v_var.center_axis)

# Rotate the grid.
from pysgrid.processing_2d import rotate_vectors

angles = nc.variables[sgrid.angle.variable][sgrid.angle.center_slicing]
u_rot, v_rot = rotate_vectors(u_avg, v_avg, angles)

# Compute the speed.
from pysgrid.processing_2d import vector_sum

uv_vector_sum = vector_sum(u_rot, v_rot)
```

All this could be hidden from an end user when plotting.

<div class="prompt input_prompt">
In&nbsp;[18]:
</div>

```python
lon_var_name, lat_var_name = sgrid.face_coordinates

sg_lon = getattr(sgrid, lon_var_name)
sg_lat = getattr(sgrid, lat_var_name)

lon_data = sgrid.center_lon[sg_lon.center_slicing]
lat_data = sgrid.center_lat[sg_lat.center_slicing]
```

<div class="prompt input_prompt">
In&nbsp;[19]:
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
In&nbsp;[20]:
</div>

```python
sub = 10
scale = 0.06

fig, ax = make_map()

kw = dict(scale=1.0/scale, pivot='middle', width=0.003, color='black')
q = plt.quiver(lon_data[::sub, ::sub], lat_data[::sub, ::sub],
               u_rot[::sub, ::sub], v_rot[::sub, ::sub], zorder=2, **kw)

cs = plt.pcolormesh(lon_data[::sub, ::sub],
                    lat_data[::sub, ::sub],
                    uv_vector_sum[::sub, ::sub], zorder=1, cmap=plt.cm.rainbow)

c = ax.coastlines('10m')
```


[![](data:image/png;base64,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
BMC//vUv5s+fz0cffUS3bt0AydEUydEMydEMydEMydEMydEcydI8uTGZn5sxY4a3u+A1Wms2bdrE
0KFDS23zwgsvkJiYSHx8PCEhIXzwwQe88MILTJs2jbvuuqugXTDnaJLkaIbkaIbkaIbkaIbkaI5k
aZ4UBH4umKfe+uWXXzh69Ci33Xab0/ULFy7k+eefZ8qUKXTs2JEVK1YwevRoRo0axfjx44u0DeYc
TZIczZAczZAczZAczZAczZEszZNLhoTfWrJkCTExMfTq1avEuhUrVjBs2DD+8Ic/8Pe//53du3dz
1113ceONN/LWW2+hlPJCj4UQQgghfI8UBMJvLV68mJtuuomIiIgiy7ds2cLgwYPp06cPH374IWfP
nuW2226jUaNGfPbZZ4SFhXmpx0IIIYQQvkcKAj83depUb3fBK06dOsWGDRu4/fbbiyzfvXs3t9xy
Cx07duTLL78kNDSUO++8k/T0dBYvXkyNGjWc7i9YczRNcjRDcjRDcjRDcjRDcjRHsjRPCgI/l56e
7u0uVCqbzcbnn39Onz59CA8PZ9CgQQXrDh06xM0330zDhg1ZvHgx0dHRzJ8/n59++okFCxbQtGnT
UvcbbDl6iuRohuRohuRohuRohuRojmRpntJae7sPXqWU6gxs27ZtG507d/Z2d0QptNYsXbqUf/zj
H2zfvp3+/fvz4osvFvyfnTx5kl69epGXl8e6deto0KABubm5tGvXjrZt2/Ltt996+RkIIYQQQlSu
+Ph44uLiAOK01vGltZNZhoTP01ozbtw4XnvtNXr16sWaNWuKDCS+cOECAwYMIDU1taAYAJg7dy6J
iYksWLDAW10XQgghhPB5UhAIn5abm8vo0aP54IMPePPNN3nkkUeKzBCUkZHBwIEDOXjwIGvWrKFF
ixYAZGdn89xzzzFkyBA6derkre4LIYQQQvg8GUPg586cOePtLnhMVlYWw4YNY+7cuXz00Uc8+uij
JaYLffLJJ9myZQtLliyhY8eOBctnz57N4cOHefbZZ136WYGcY2WSHM2QHM2QHM2QHM2QHM2RLM2T
gsDPjRgxwttd8IjU1FQGDhzI4sWL+eqrr7jnnntKtPniiy+YOXMmb7zxBj169ChYnpGRwZQpU7j7
7rtp3769Sz8vUHOsbJKjGZKjGZKjGZKjGZKjOZKleXLJkJ975plnvN0F47TWDBw4kK1bt/Ldd9/R
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
IYLY/wOOwwYsurB+UQAAAABJRU5ErkJggg==
)](CF-UGRID-SGRID-conventions_files/CF-UGRID-SGRID-conventions_34_0.png)


\* CF convention do describe the angle variable for grids that needs rotation,
but there is no action expected like in the `formula_terms`.
`pysgrid` must be improved to abstract that action when needed via a simpler
method.

```xml
<entry id="angle_of_rotation_from_east_to_x">
    <canonical_units>degree</canonical_units>
    <grib></grib>
    <amip></amip>
    <description>The quantity with standard name
angle_of_rotation_from_east_to_x is the angle, anticlockwise reckoned positive,
between due East and (dr/di)jk, where r(i,j,k) is the vector 3D position of the
point with coordinate indices (i,j,k).  It could be used for rotating vector
fields between model space and latitude-longitude space.</description>
</entry>
```

For more examples using pysgrid see this [post]((https://ocefpaf.github.io/pytho
n4oceanographers/blog/2015/12/07/pysgrid/). See also
[this](https://gist.github.com/ocefpaf/62940cbe5c7674a6f3e9) trick to plot the
vectors at the center of the cells.
