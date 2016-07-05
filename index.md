---
layout: default
title: "index"
---

# CF-1.6 (iris)

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

**In [1]:**

{% highlight python %}
import iris

iris.FUTURE.netcdf_promote = True

url = ('http://omgsrv1.meas.ncsu.edu:8080/thredds/dodsC/fmrc/'
       'sabgom/SABGOM_Forecast_Model_Run_Collection_best.ncd')

cubes = iris.load(url)
{% endhighlight %}

    /home/filipe/miniconda/envs/notebooks_demos/lib/python2.7/site-packages/iris/fileformats/cf.py:1058: UserWarning: Ignoring formula terms variable u'h' referenced by data variable u'v' via variable u's_rho': Dimensions (u'eta_rho', u'xi_rho') do not span (u'time', u's_rho', u'eta_v', u'xi_v')
      warnings.warn(msg)
    /home/filipe/miniconda/envs/notebooks_demos/lib/python2.7/site-packages/iris/fileformats/cf.py:1058: UserWarning: Ignoring formula terms variable u'zeta' referenced by data variable u'v' via variable u's_rho': Dimensions (u'time', u'eta_rho', u'xi_rho') do not span (u'time', u's_rho', u'eta_v', u'xi_v')
      warnings.warn(msg)
    /home/filipe/miniconda/envs/notebooks_demos/lib/python2.7/site-packages/iris/fileformats/cf.py:1058: UserWarning: Ignoring formula terms variable u'h' referenced by data variable u'u' via variable u's_rho': Dimensions (u'eta_rho', u'xi_rho') do not span (u'time', u's_rho', u'eta_u', u'xi_u')
      warnings.warn(msg)
    /home/filipe/miniconda/envs/notebooks_demos/lib/python2.7/site-packages/iris/fileformats/cf.py:1058: UserWarning: Ignoring formula terms variable u'zeta' referenced by data variable u'u' via variable u's_rho': Dimensions (u'time', u'eta_rho', u'xi_rho') do not span (u'time', u's_rho', u'eta_u', u'xi_u')
      warnings.warn(msg)
    /home/filipe/miniconda/envs/notebooks_demos/lib/python2.7/site-packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1304: UserWarning: Ignoring netCDF variable u'chlorophyll' invalid units u'milligrams_chlorophyll meter-3'
      warnings.warn(msg.encode('ascii', errors='backslashreplace'))
    /home/filipe/miniconda/envs/notebooks_demos/lib/python2.7/site-packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1399: UserWarning: Gracefully filling 'time' dimension coordinate masked points
      warnings.warn(msg.format(str(cf_coord_var.cf_name)))
    /home/filipe/miniconda/envs/notebooks_demos/lib/python2.7/site-packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1304: UserWarning: Ignoring netCDF variable u'phytoplankton' invalid units u'millimole_nitrogen meter-3'
      warnings.warn(msg.encode('ascii', errors='backslashreplace'))
    /home/filipe/miniconda/envs/notebooks_demos/lib/python2.7/site-packages/iris/fileformats/netcdf.py:441: UserWarning: Unable to find coordinate for variable u'zeta'
      '{!r}'.format(name))
    /home/filipe/miniconda/envs/notebooks_demos/lib/python2.7/site-packages/iris/fileformats/netcdf.py:441: UserWarning: Unable to find coordinate for variable u'h'
      '{!r}'.format(name))
    /home/filipe/miniconda/envs/notebooks_demos/lib/python2.7/site-packages/iris/fileformats/netcdf.py:558: UserWarning: Unable to construct Ocean s-coordinate, generic form 1 factory due to insufficient source coordinates.
      warnings.warn('{}'.format(e))
    /home/filipe/miniconda/envs/notebooks_demos/lib/python2.7/site-packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1304: UserWarning: Ignoring netCDF variable u'NO3' invalid units u'millimole_N03 meter-3'
      warnings.warn(msg.encode('ascii', errors='backslashreplace'))
    /home/filipe/miniconda/envs/notebooks_demos/lib/python2.7/site-packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1304: UserWarning: Ignoring netCDF variable u'zooplankton' invalid units u'millimole_nitrogen meter-3'
      warnings.warn(msg.encode('ascii', errors='backslashreplace'))
    /home/filipe/miniconda/envs/notebooks_demos/lib/python2.7/site-packages/iris/fileformats/_pyke_rules/compiled_krb/fc_rules_cf_fc.py:1304: UserWarning: Ignoring netCDF variable u'NH4' invalid units u'millimole_NH4 meter-3'
      warnings.warn(msg.encode('ascii', errors='backslashreplace'))
    /home/filipe/miniconda/envs/notebooks_demos/lib/python2.7/site-packages/iris/_merge.py:365: FutureWarning: elementwise comparison failed; returning scalar instead, but in the future will perform elementwise comparison
      other_defn.attributes[key])]


**Aside:** the `iris.FUTURE.netcdf_promote = True` line  promotes netCDF formula
terms,
like sea surface height, to cubes.
This behavior will be default in future versions of `iris`.

**In [2]:**

{% highlight python %}
print(cubes)
{% endhighlight %}

    0: grid type logical switch / (no_unit) (-- : 64)
    1: chlorophyll concentration / (unknown) (time: 304; ocean_s_coordinate_g1: 36; -- : 320; -- : 440)
    2: mask on V-points / (1)              (-- : 319; -- : 440)
    3: mask on U-points / (1)              (-- : 320; -- : 439)
    4: tracers outflow, nudging inverse time scale / (second-1) (-- : 4; -- : 14)
    5: phytoplankton concentration / (unknown) (time: 304; ocean_s_coordinate_g1: 36; -- : 320; -- : 440)
    6: mask on RHO-points / (1)            (-- : 320; -- : 440)
    7: vertically integrated v-momentum component / (meter second-1) (time: 304; -- : 319; -- : 440)
    8: nonlinear model Laplacian mixing coefficient for tracers / (meter2 second-1) (-- : 14)
    9: free-surface inflow, nudging inverse time scale / (second-1) (-- : 4)
    10: background vertical mixing coefficient for tracers / (meter2 second-1) (-- : 14)
    11: 3D momentum inflow, nudging inverse time scale / (second-1) (-- : 4)
    12: 2D momentum outflow, nudging inverse time scale / (second-1) (-- : 4)
    13: nitrate concentration / (unknown)   (time: 304; ocean_s_coordinate_g1: 36; -- : 320; -- : 440)
    14: curvilinear coordinate metric in ETA / (meter-1) (-- : 320; -- : 440)
    15: 2D momentum inflow, nudging inverse time scale / (second-1) (-- : 4)
    16: curvilinear coordinate metric in XI / (meter-1) (-- : 320; -- : 440)
    17: 3D momentum outflow, nudging inverse time scale / (second-1) (-- : 4)
    18: zooplankton concentration / (unknown) (time: 304; ocean_s_coordinate_g1: 36; -- : 320; -- : 440)
    19: tracer point sources and simck activation switch / (1) (-- : 14)
    20: ammonium concentration / (unknown)  (time: 304; ocean_s_coordinate_g1: 36; -- : 320; -- : 440)
    21: mask on psi-points / (1)            (-- : 319; -- : 439)
    22: angle between XI-axis and EAST / (radians) (-- : 320; -- : 440)
    23: free-surface outflow, nudging inverse time scale / (second-1) (-- : 4)
    24: Tracers nudging/relaxation inverse time scale / (day-1) (-- : 14)
    25: Coriolis parameter at RHO-points / (second-1) (-- : 320; -- : 440)
    26: vertically integrated u-momentum component / (meter second-1) (time: 304; -- : 320; -- : 439)
    27: vertical momentum component / (meter second-1) (time: 304; ocean_s_coordinate_g1: 37; -- : 320; -- : 440)
    28: tracers inflow, nudging inverse time scale / (second-1) (-- : 4; -- : 14)
    29: bathymetry at RHO-points / (meter)  (-- : 320; -- : 440)
    30: eastward_sea_water_velocity_assuming_no_tide / (meter second-1) (time: 304; ocean_s_coordinate_g1: 36; -- : 320; -- : 439)
    31: forecast_period / (hours since 2016-06-01T00:00:00Z) (time: 304)
    32: northward_sea_water_velocity_assuming_no_tide / (meter second-1) (time: 304; ocean_s_coordinate_g1: 36; -- : 319; -- : 440)
    33: sea_surface_height / (meter)        (time: 304; -- : 320; -- : 440)
    34: sea_water_potential_temperature / (Celsius) (time: 304; ocean_s_coordinate_g1: 36; -- : 320; -- : 440)
    35: sea_water_salinity / (1)            (time: 304; ocean_s_coordinate_g1: 36; -- : 320; -- : 440)


- High level variable access via `standard_name`, `long_name`, or `var_name`
- Annoyingly verbose warnings when the data has compliance issues (see the units
warnings above)
- Raise error for non-compliant. (Iris will refuse to load the data!)
- Separation of each phenomena (`variable`) into its own cube\*
- The cube is a fully self-described format format with all the original
metadata (round-trip load-save to netCDF is lossless)
- The cube object interprets the `formula_terms` and `cell_methods`

**In [3]:**

{% highlight python %}
cube = cubes.extract_strict('sea_surface_height')

print(cube)
{% endhighlight %}

    sea_surface_height / (meter)        (time: 304; -- : 320; -- : 440)
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
              bry_file: /gpfs_share/omg/omg/autosabgom/in/ncoda_bry_20160619.nc
              cdm_data_type: GRID
              clm_file: /gpfs_share/omg/omg/autosabgom/in/ncoda_clm_20160619.nc
              code_dir: /he_data/he/zxue/COAWST411
              compiler_command: /usr/local/apps/mpich/x86_64/pgi105/mx127..7/bin/mpif90
              compiler_flags: -fastsse   -Kieee -fastsse -Mipa=fast -tp k8-64 -Mfree
              compiler_system: pgi
              cpu: x86_64
              dia_file: /gpfs_share/omg/autosabgom/out/dia_20160619.nc
              featureType: GRID
              field: free-surface, scalar, series
              file: /gpfs_share/omg/autosabgom/out/his_20160619_0002.nc
              format: netCDF-3 classic file
              frc_file_01: /gpfs_share/omg/omg/autosabgom/in/nomads_forc_20160619.nc
              frc_file_02: /gpfs_share/omg/omg/autosabgom/in/SABGOM.OTIS.Ref18581117.8Cons
              frc_file_03: /gpfs_share/omg/omg/autosabgom/in/sabgom_river_79_clm_2015_2016.nc
              grd_file: /gpfs_share/omg/omg/autosabgom/in/sabgom_grd.nc.Etopo2.LP.r1_5.filled
              header_dir: /he_data/he/zxue/Projects/SABGOM_BIO
              header_file: mch_bio_nf.h
              his_base: /gpfs_share/omg/autosabgom/out/his_20160619
              history: ROMS/TOMS, Version 3.4, Sunday - June 19, 2016 -  2:48:58 AM ;
    FMRC Best...
              ini_file: /gpfs_share/omg/omg/autosabgom/in/ncoda_ini_20160619.nc
              location: Proto fmrc:SABGOM_Forecast_Model_Run_Collection
              os: Linux
              rst_file: /gpfs_share/omg/autosabgom/out/rst_20160619.nc
              script_file: /home/omg/autosabgom/sabgom_20160619.in
              spos_file: /home/omg/autosabgom/stations.in
              sta_file: /gpfs_share/omg/autosabgom/out/sta_20160619.nc
              svn_rev: 412M
              svn_url: https://www.myroms.org/svn/omlab/branches/jcwarner
              tiling: 008x004
              time: ocean_time
              title: ROMS/TOMS 3.0 - South-Atlantic Bight and Gulf of Mexico
              type: ROMS/TOMS history file


Requesting a vertical profile of temperature to see the `formula_terms`
interpretation in action. (Note that `ocean_s_coordinate_g1` is CF-1.7.)

**In [4]:**

{% highlight python %}
temp = cubes.extract_strict('sea_water_potential_temperature')

t_profile = temp[-1, :, 160, 220]
{% endhighlight %}

**In [5]:**

{% highlight python %}
t_profile.coords(axis='Z')
{% endhighlight %}




    [DimCoord(array([-0.98611111, -0.95833333, -0.93055556, -0.90277778, -0.875     ,
            -0.84722222, -0.81944444, -0.79166667, -0.76388889, -0.73611111,
            -0.70833333, -0.68055556, -0.65277778, -0.625     , -0.59722222,
            -0.56944444, -0.54166667, -0.51388889, -0.48611111, -0.45833333,
            -0.43055556, -0.40277778, -0.375     , -0.34722222, -0.31944444,
            -0.29166667, -0.26388889, -0.23611111, -0.20833333, -0.18055556,
            -0.15277778, -0.125     , -0.09722222, -0.06944444, -0.04166667,
            -0.01388889]), standard_name=u'ocean_s_coordinate_g1', units=Unit('1'), long_name=u'S-coordinate at RHO-points', var_name='s_rho', attributes={'_CoordinateAxes': 's_rho', 'positive': 'up', 'field': 's_rho, scalar', '_CoordinateZisPositive': 'up', '_CoordinateTransformType': 'Vertical', '_CoordinateAxisType': 'GeoZ'}),
     AuxCoord(array([-191.77943183, -177.32755917, -164.64656091, -153.48079307,
            -143.60032123, -134.79581523, -126.87393959, -119.65335818,
            -112.96162249, -106.63341022, -100.51079767,  -94.4464011 ,
             -88.3101417 ,  -81.99983003,  -75.45451247,  -68.66764125,
             -61.69529733,  -54.65424444,  -47.70681005,  -41.03437994,
             -34.80640379,  -29.15402739,  -24.15525144,  -19.83340911,
             -16.16596635,  -13.09843406,  -10.55863632,   -8.4684135 ,
              -6.75172473,   -5.33937136,   -4.17112655,   -3.19614208,
              -2.37235786,   -1.66542937,   -1.04749903,   -0.49599521]), standard_name='sea_surface_height_above_reference_ellipsoid', units=Unit('meter'), attributes={'positive': 'up'})]



Iris knows about the metadata and can create fully annotated plots.

Be aware that too much automation lead to some weird plots. Like the `z-coord`
in the `x-direction` ;-)

**In [6]:**

{% highlight python %}
%matplotlib inline

import iris.quickplot as qplt

l, = qplt.plot(t_profile)
{% endhighlight %}


![png]({{ site.baseurl}}/index_files/index_10_0.png)


**In [7]:**

{% highlight python %}
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(3, 7))

t = t_profile.data
z = t_profile.coord('sea_surface_height_above_reference_ellipsoid').points

l, = ax.plot(t, z)
{% endhighlight %}


![png]({{ site.baseurl}}/index_files/index_11_0.png)


\* Most people miss the concept of a "dataset" when using `iris`, but that is a
consequence of the CF model since there are no unique names to the variables and
the same dataset might contain phenomena with different coordinates.

Aside: note that the [xarray](http://xarray.pydata.org/en/stable/) **does** have
a dataset concept, but it infringes the CF model in many places to do so.



For more on iris see: https://ocefpaf.github.io/python4oceanographers/blog/2014/
12/29/iris_ocean_models/

# UGRID-1.0 (pyugrid)

http://ugrid-conventions.github.io/ugrid-conventions/

**In [8]:**

{% highlight python %}
import pyugrid

url = 'http://crow.marine.usf.edu:8080/thredds/dodsC/FVCOM-Nowcast-Agg.nc'

ugrid = pyugrid.UGrid.from_ncfile(url)
{% endhighlight %}

In a nutshell the `pyugrid` loads the data into a `ugrid` object that parsing
and exposing the underlying grid topology.

**In [9]:**

{% highlight python %}
lon = ugrid.nodes[:, 0]
lat = ugrid.nodes[:, 1]
triangles = ugrid.faces[:]
{% endhighlight %}

Sometimes the topology is incomplete but, if the data is UGRID compliant,
`pyugrid` can derive the rest for you.

**In [10]:**

{% highlight python %}
ugrid.build_edges()
{% endhighlight %}

**In [11]:**

{% highlight python %}
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
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
{% endhighlight %}


![png]({{ site.baseurl}}/index_files/index_19_0.png)


There is some effort to integrate `pyugrid` into `iris` to augment the cube
object to be both CF and UGRID aware by adding convenience plotting and slicing
methods with pyugrid. You can see the full pyugrid example [here](https://ocefpa
f.github.io/python4oceanographers/blog/2015/07/20/pyugrid/).

# SGRID-0.3 (pysgrid)


http://sgrid.github.io/sgrid/

**In [12]:**

{% highlight python %}
import pysgrid

url = ('http://geoport.whoi.edu/thredds/dodsC/clay/usgs/users/'
       'jcwarner/Projects/Sandy/triple_nest/00_dir_NYB05.ncml')


sgrid = pysgrid.from_ncfile(url)
{% endhighlight %}

The `pysgrid` module is similar to `pyugrid`. The grid topology is parsed into a
Python object with methods and attributes that translate the SGRID conventions.

**In [13]:**

{% highlight python %}
sgrid.edge1_coordinates, sgrid.edge1_dimensions, sgrid.edge1_padding
{% endhighlight %}




    ((u'lon_u', u'lat_u'),
     u'xi_u: xi_psi eta_u: eta_psi (padding: both)',
     [GridPadding(mesh_topology_var=u'grid', face_dim=u'eta_u', node_dim=u'eta_psi', padding=u'both')])



**In [14]:**

{% highlight python %}
u_var = sgrid.u

u_var.center_axis, u_var.node_axis
{% endhighlight %}




    (1, 0)



**In [15]:**

{% highlight python %}
v_var = sgrid.v
v_var.center_axis, v_var.node_axis
{% endhighlight %}




    (0, 1)



**In [16]:**

{% highlight python %}
u_var.center_slicing, v_var.center_slicing
{% endhighlight %}




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

**In [17]:**

{% highlight python %}
# Center slice.

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

# Rotate the grid*.
from pysgrid.processing_2d import rotate_vectors

angles = nc.variables[sgrid.angle.variable][sgrid.angle.center_slicing]
u_rot, v_rot = rotate_vectors(u_avg, v_avg, angles)

# Compute the speed.
from pysgrid.processing_2d import vector_sum

uv_vector_sum = vector_sum(u_rot, v_rot)
{% endhighlight %}

    /home/filipe/miniconda/envs/notebooks_demos/lib/python2.7/site-packages/pysgrid/processing_2d.py:22: RuntimeWarning: invalid value encountered in sqrt
      vector_sum = np.sqrt(x_arr**2 + y_arr**2)


All this could be hidden from an end user when plotting.

**In [18]:**

{% highlight python %}
grid_cell_centers = sgrid.centers

lon_var_name, lat_var_name = sgrid.face_coordinates

sg_lon = getattr(sgrid, lon_var_name)
sg_lat = getattr(sgrid, lat_var_name)

lon_data = grid_cell_centers[..., 0][sg_lon.center_slicing]
lat_data = grid_cell_centers[..., 1][sg_lat.center_slicing]
{% endhighlight %}

**In [19]:**

{% highlight python %}
import numpy as np
import matplotlib.pyplot as plt

import cartopy.crs as ccrs
from cartopy.io import shapereader
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER


def make_map(projection=ccrs.PlateCarree(), figsize=(9, 9)):
    fig, ax = plt.subplots(figsize=figsize,
                           subplot_kw=dict(projection=projection))
    gl = ax.gridlines(draw_labels=True)
    gl.xlabels_top = gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    return fig, ax
{% endhighlight %}

**In [20]:**

{% highlight python %}
sub = 10
scale = 0.06

fig, ax = make_map()

kw = dict(scale=1.0/scale, pivot='middle', width=0.003, color='black')
q = plt.quiver(lon_data[::sub, ::sub], lat_data[::sub, ::sub],
               u_rot[::sub, ::sub], v_rot[::sub, ::sub], zorder=2, **kw)

cs = plt.pcolormesh(lon_data[::sub, ::sub],
                    lat_data[::sub, ::sub],
                    uv_vector_sum[::sub, ::sub], zorder=1, cmap=plt.cm.rainbow)

_ = ax.coastlines('10m')
{% endhighlight %}


![png]({{ site.baseurl}}/index_files/index_33_0.png)


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

For more examples using pysgrid see this [post](https://ocefpaf.github.io/pytho
n4oceanographers/blog/2015/12/07/pysgrid/). See also
[this](https://gist.github.com/ocefpaf/62940cbe5c7674a6f3e9) trick to plot the
vectors at the center of the cells.
