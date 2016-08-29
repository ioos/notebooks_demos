from __future__ import absolute_import, division, print_function

from datetime import datetime

import netcdftime
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree as KDTree

import iris
import cf_units
from iris import Constraint
from iris.cube import CubeList
from iris.coords import AuxCoord, DimCoord
from iris.exceptions import CoordinateNotFoundError, CoordinateMultiDimError


iris.FUTURE.netcdf_promote = True
iris.FUTURE.netcdf_no_unlimited = True
iris.FUTURE.cell_datetime_objects = True


"""
Tools to manipulate iris cubes.

"""


def is_model(cube):
    """
    Heuristic way to find if a cube data is `modelResult` or not.
    WARNING: This function may return False positives and False
    negatives!!!

    Examples
    --------
    >>> import iris
    >>> iris.FUTURE.netcdf_promote = True
    >>> url = ("http://crow.marine.usf.edu:8080/thredds/dodsC/"
    ...        "FVCOM-Nowcast-Agg.nc")
    >>> cubes = iris.load_raw(url, 'sea_surface_height_above_geoid')
    >>> [is_model(cube) for cube in cubes]
    [True]
    >>> url = ("http://thredds.cdip.ucsd.edu/thredds/dodsC/cdip/archive/"
    ...        "043p1/043p1_d17.nc")
    >>> cubes = iris.load_raw(url, 'sea_surface_temperature')
    >>> [is_model(cube) for cube in cubes]
    [False]

    """
    # First criteria (Strong): "forecast" word in the time coord.
    try:
        coords = cube.coords(axis='T')
        for coord in coords:
            if 'forecast' in coord.name():
                return True
    except CoordinateNotFoundError:
        pass
    # Second criteria (Strong): `UGRID` cubes are models.
    conventions = cube.attributes.get('Conventions', 'None')
    if 'UGRID' in conventions.upper():
        return True
    # Third criteria (Strong): dimensionless coords are present.
    try:
        coords = cube.coords(axis='Z')
        for coord in coords:
            if 'ocean_' in coord.name():
                return True
    except CoordinateNotFoundError:
        pass
    # Forth criteria (weak): Assumes that all "GRID" attribute are models.
    cdm_data_type = cube.attributes.get('cdm_data_type', 'None')
    feature_type = cube.attributes.get('featureType', 'None')
    source = cube.attributes.get('source', 'None')
    if cdm_data_type.upper() == 'GRID' or feature_type.upper() == 'GRID':
        if 'AVHRR' not in source:
            return True
    return False


def z_coord(cube):
    """
    Return the canonical vertical coordinate.

    Examples
    --------
    >>> import iris
    >>> url = ("http://omgsrv1.meas.ncsu.edu:8080/thredds/dodsC/fmrc/sabgom/"
    ...        "SABGOM_Forecast_Model_Run_Collection_best.ncd")
    >>> cube = iris.load_cube(url, 'sea_water_potential_temperature')
    >>> str(z_coord(cube).name())
    'ocean_s_coordinate_g1'

    """
    non_dimensional = ['atmosphere_hybrid_height_coordinate',
                       'atmosphere_hybrid_sigma_pressure_coordinate',
                       'atmosphere_sigma_coordinate',
                       'atmosphere_sleve_coordinate',
                       'ocean_s_coordinate',
                       'ocean_s_coordinate_g1',
                       'ocean_s_coordinate_g2',
                       'ocean_sigma_coordinate',
                       'ocean_sigma_z_coordinate']
    z = None
    # If only one exists get that.
    try:
        z = cube.coord(axis='Z')
    except CoordinateNotFoundError:
        # If a named `z_coord` exist.
        try:
            z = cube.coord(axis='altitude')
        except CoordinateNotFoundError:
            # OK, let's use the non-dimensional names.
            for coord in cube.coords(axis='Z'):
                if coord.name() in non_dimensional:
                    z = coord
                    break
    return z


def _get_surface_idx(cube):
    """
    Return the `cube` index for the surface layer of for any model grid
    (rgrid, ugrid, sgrid), and any non-dimensional coordinate.

    """
    z = z_coord(cube)
    if not z:
        msg = "Cannot find the surface for cube {!r}".format
        raise ValueError(msg(cube))
    else:
        if np.argmin(z.shape) == 0 and z.ndim == 2:
            points = z[:, 0].points
        elif np.argmin(z.shape) == 1 and z.ndim == 2:
            points = z[0, :].points
        else:
            points = z.points
        positive = z.attributes.get('positive', None)
        if positive == 'up':
            idx = np.unique(points.argmax(axis=0))[0]
        else:
            idx = np.unique(points.argmin(axis=0))[0]
        return idx


def get_surface(cube):
    """
    Work around `iris.cube.Cube.slices` error:
    The requested coordinates are not orthogonal.

    Examples
    --------
    >>> import iris
    >>> url = ("http://omgsrv1.meas.ncsu.edu:8080/thredds/dodsC/fmrc/sabgom/"
    ...        "SABGOM_Forecast_Model_Run_Collection_best.ncd")
    >>> cube = iris.load_cube(url, 'sea_water_potential_temperature')
    >>> cube.ndim == 4
    True
    >>> get_surface(cube).ndim == 3
    True

    """
    conventions = cube.attributes.get('Conventions', 'None')

    # Short-circuit if cube does not have a z-axis.
    if 'UGRID' not in conventions.upper() and cube.ndim == 3:
        return cube

    idx = _get_surface_idx(cube)
    if cube.ndim == 4 or 'UGRID' in conventions.upper():
        return cube[:, int(idx), ...]
    elif cube.ndim == 3 and 'UGRID' not in conventions.upper():
        return cube[int(idx), ...]
    else:
        msg = "Cannot find the surface for cube {!r}".format
        raise ValueError(msg(cube))


def time_coord(cube):
    """
    Return the variable attached to time axis and rename it to time.

    Examples
    --------
    >>> import iris
    >>> url = ("http://omgsrv1.meas.ncsu.edu:8080/thredds/dodsC/fmrc/sabgom/"
    ...        "SABGOM_Forecast_Model_Run_Collection_best.ncd")
    >>> cube = iris.load_cube(url, 'sea_water_potential_temperature')
    >>> str(time_coord(cube).name())
    'time'

    """
    try:
        cube.coord(axis='T').rename('time')
    except CoordinateNotFoundError:
        pass
    timevar = cube.coord('time')
    return timevar


def time_near(cube, datetime_obj):
    """
    Return the nearest index to a `datetime_obj`.

    Examples
    --------
    >>> import iris
    >>> from datetime import datetime
    >>> url = ("http://omgsrv1.meas.ncsu.edu:8080/thredds/dodsC/fmrc/sabgom/"
    ...        "SABGOM_Forecast_Model_Run_Collection_best.ncd")
    >>> cube = iris.load_cube(url, 'sea_water_potential_temperature')
    >>> isinstance(time_near(cube, datetime.utcnow()), np.integer)
    True

    """
    timevar = time_coord(cube)
    try:
        time = timevar.units.date2num(datetime_obj)
        idx = timevar.nearest_neighbour_index(time)
    except IndexError:
        idx = -1
    return idx


def time_slice(cube, start, stop=None):
    """
    Slice time by indexes using a nearest criteria.
    NOTE: Assumes time is the first dimension!

    Examples
    --------
    >>> import iris
    >>> from datetime import datetime, timedelta
    >>> url = ("http://omgsrv1.meas.ncsu.edu:8080/thredds/dodsC/fmrc/sabgom/"
    ...        "SABGOM_Forecast_Model_Run_Collection_best.ncd")
    >>> cube = iris.load_cube(url, 'sea_water_potential_temperature')
    >>> stop = datetime.utcnow()
    >>> start = stop - timedelta(days=7)
    >>> time_slice(cube, start, stop).shape[0] < cube.shape[0]
    True

    """
    istart = time_near(cube, start)
    if stop:
        istop = time_near(cube, stop)
        if istart == istop:
            raise ValueError('istart must be different from istop! '
                             'Got istart {!r} and '
                             ' istop {!r}'.format(istart, istop))
        return cube[istart:istop, ...]
    else:
        return cube[istart, ...]


def _minmax(v):
    return np.min(v), np.max(v)


def _get_indices(cube, bbox):
    """
    Get the 4 corner indices of a `cube` given a `bbox`.

    Examples
    --------
    >>> import iris
    >>> url = ("http://omgsrv1.meas.ncsu.edu:8080/thredds/dodsC/fmrc/sabgom/"
    ...        "SABGOM_Forecast_Model_Run_Collection_best.ncd")
    >>> cube = iris.load_cube(url, 'sea_water_potential_temperature')
    >>> bbox = [-87.40, 24.25, -74.70, 36.70]
    >>> idxs = _get_indices(cube, bbox)
    >>> [isinstance(idx, np.integer) for idx in idxs]
    [True, True, True, True]
    >>> idxs
    (27, 320, 164, 429)

    """
    from oceans import wrap_lon180
    lons = cube.coord('longitude').points
    lats = cube.coord('latitude').points
    lons = wrap_lon180(lons)

    inregion = np.logical_and(np.logical_and(lons > bbox[0],
                                             lons < bbox[2]),
                              np.logical_and(lats > bbox[1],
                                             lats < bbox[3]))
    region_inds = np.where(inregion)
    imin, imax = _minmax(region_inds[0])
    jmin, jmax = _minmax(region_inds[1])
    return imin, imax+1, jmin, jmax+1


def bbox_extract_2Dcoords(cube, bbox):
    """
    Extract a sub-set of a cube inside a lon, lat bounding box
    bbox = [lon_min lon_max lat_min lat_max].
    NOTE: This is a work around too subset an iris cube that has
    2D lon, lat coords.

    Examples
    --------
    >>> import iris
    >>> url = ("http://omgsrv1.meas.ncsu.edu:8080/thredds/dodsC/fmrc/sabgom/"
    ...        "SABGOM_Forecast_Model_Run_Collection_best.ncd")
    >>> cube = iris.load_cube(url, 'sea_water_potential_temperature')
    >>> bbox = [-87.40, 24.25, -74.70, 36.70]
    >>> new_cube = bbox_extract_2Dcoords(cube, bbox)
    >>> cube.shape != new_cube.shape
    True

    """
    imin, imax, jmin, jmax = _get_indices(cube, bbox)
    return cube[..., imin:imax, jmin:jmax]


def bbox_extract_1Dcoords(cube, bbox):
    """
    Same as bbox_extract_2Dcoords but for 1D coords.

    Examples
    --------
    >>> import iris
    >>> url = "http://oos.soest.hawaii.edu/thredds/dodsC/pacioos/hycom/global"
    >>> cube = iris.load_cube(url, 'sea_water_potential_temperature')
    >>> bbox = [272.6, 24.25, 285.3, 36.70]
    >>> new_cube = bbox_extract_1Dcoords(cube, bbox)
    >>> cube.shape != new_cube.shape
    True

    """
    lat = Constraint(latitude=lambda cell: bbox[1] <= cell <= bbox[3])
    lon = Constraint(longitude=lambda cell: bbox[0] <= cell <= bbox[2])
    cube = cube.extract(lon & lat)
    return cube


def subset(cube, bbox):
    """
    Subsets cube with 1D or 2D lon, lat coords.
    Using `intersection` instead of `extract` we deal with 0--360
    longitudes automagically.

    Examples
    --------
    >>> import iris
    >>> url = "http://oos.soest.hawaii.edu/thredds/dodsC/pacioos/hycom/global"
    >>> cube = iris.load_cube(url, 'sea_water_potential_temperature')
    >>> bbox = [272.6, 24.25, 285.3, 36.70]
    >>> new_cube = subset(cube, bbox)
    >>> cube.shape != new_cube.shape
    True

    """
    if (cube.coord(axis='X').ndim == 1 and cube.coord(axis='Y').ndim == 1):
        # Workaround `cube.intersection` hanging up on FVCOM models.
        title = cube.attributes.get('title', 'untitled')
        featureType = cube.attributes.get('featureType', None)
        if (('FVCOM' in title) or ('ESTOFS' in title) or
           featureType == 'timeSeries'):
            cube = bbox_extract_1Dcoords(cube, bbox)
        else:
            cube = cube.intersection(longitude=(bbox[0], bbox[2]),
                                     latitude=(bbox[1], bbox[3]))
    elif (cube.coord(axis='X').ndim == 2 and
          cube.coord(axis='Y').ndim == 2):
        cube = bbox_extract_2Dcoords(cube, bbox)
    else:
        msg = "Cannot deal with X:{!r} and Y:{!r} dimensions."
        raise CoordinateMultiDimError(msg.format(cube.coord(axis='X').ndim),
                                      cube.coord(axis='y').ndim)
    return cube


def _filter_none(lista):
    return [x for x in lista if x is not None]


def _in_list(cube, name_list):
    return cube.standard_name in name_list


def quick_load_cubes(url, name_list, callback=None, strict=False):
    """
    Return all cubes found using a `name_list` of standard_names.  The cubes
    found can be transformed via a `callback` function.
    If `strict` is set to True the function will return only one cube is
    possible, otherwise an exception will be raise.

    TODO: Create a criteria to choose a sensor.
    buoy = "http://129.252.139.124/thredds/dodsC/fldep.stlucieinlet..nc"
    buoy = "http://129.252.139.124/thredds/dodsC/lbhmc.cherrygrove.pier.nc"

    Examples
    --------
    >>> import iris
    >>> url = ("http://omgsrv1.meas.ncsu.edu:8080/thredds/dodsC/fmrc/sabgom/"
    ...        "SABGOM_Forecast_Model_Run_Collection_best.ncd")
    >>> name_list = ['sea_water_potential_temperature']
    >>> cubes = quick_load_cubes(url, name_list)
    >>> cube = quick_load_cubes(url, name_list, strict=True)
    >>> isinstance(cubes, list)
    True
    >>> isinstance(cube, iris.cube.Cube)
    True
    """

    cubes = iris.load_raw(url, callback=callback)
    cubes = CubeList([cube for cube in cubes if _in_list(cube, name_list)])
    cubes = _filter_none(cubes)
    if not cubes:
        raise ValueError('Cannot find {!r} in {}.'.format(name_list, url))
    if strict:
        if len(cubes) == 1:
            return cubes[0]
        else:
            msg = "> 1 cube found!  Expected just one.\n {!r}".format
        raise ValueError(msg(cubes))
    return cubes


def proc_cube(cube, bbox=None, time=None, constraint=None, units=None):
    """
    Constraining by `bbox`, `time`, and iris `constraint` object.
    and the `units` can be converted.

    Examples
    --------
    >>> import pytz
    >>> import iris
    >>> from datetime import date, datetime, timedelta
    >>> url = ('http://omgsrv1.meas.ncsu.edu:8080/thredds/dodsC/fmrc/sabgom/'
    ...        'SABGOM_Forecast_Model_Run_Collection_best.ncd')
    >>> today = date.today().timetuple()
    >>> stop = datetime(today.tm_year, today.tm_mon, today.tm_mday, 12)
    >>> start = stop - timedelta(days=7)
    >>> bbox = [-87.40, 24.25, -74.70, 36.70]
    >>> name_list = ['sea_water_potential_temperature']
    >>> cube = quick_load_cubes(url, name_list, strict=True)
    >>> new_cube = proc_cube(cube, bbox=bbox, time=(start, stop))
    >>> cube.shape != new_cube.shape
    True

    """

    if constraint:
        cube = cube.extract(constraint)
        if not cube:
            raise ValueError('No cube using {!r}'.format(constraint))
    if bbox:
        cube = subset(cube, bbox)
        if not cube:
            raise ValueError('No cube using {!r}'.format(bbox))
    if time:
        if isinstance(time, datetime):
            start, stop = time, None
        elif isinstance(time, tuple):
            start, stop = time[0], time[1]
        else:
            raise ValueError('Time must be start or (start, stop).'
                             '  Got {!r}'.format(time))
        cube = time_slice(cube, start, stop)
    if units:
        if cube.units != units:
            cube.convert_units(units)
    return cube


def add_mesh(cube, url):
    """
    Adds the unstructured mesh info the to cube.  Soon in an iris near you!

    """
    from pyugrid import UGrid
    ug = UGrid.from_ncfile(url)
    cube.mesh = ug
    cube.mesh_dimension = 1
    return cube


def _make_aux_coord(cube, axis='Y'):
    """Make any given coordinate an Auxiliary Coordinate."""
    coord = cube.coord(axis=axis)
    cube.remove_coord(coord)
    if cube.ndim == 2:
        cube.add_aux_coord(coord, 1)
    else:
        cube.add_aux_coord(coord)
    return cube


def ensure_timeseries(cube):
    """Ensure that the cube is CF-timeSeries compliant."""
    if not cube.coord('time').shape == cube.shape[0]:
        cube.transpose()
    _make_aux_coord(cube, axis='Y')
    _make_aux_coord(cube, axis='X')

    cube.attributes.update({'featureType': 'timeSeries'})
    cube.coord("station_code").attributes = dict(cf_role='timeseries_id')
    return cube


def add_station(cube, station):
    """Add a station Auxiliary Coordinate and its name."""
    kw = dict(var_name="station", long_name="station_code")
    coord = iris.coords.AuxCoord(station, **kw)
    cube.add_aux_coord(coord)
    return cube


def remove_ssh(cube):
    """
    Remove all `aux_coords` but time.  Should that has the same shape as
    the data.  NOTE: This also removes `aux_factories` to avoid update error
    when removing the coordinate.

    Examples
    --------
    >>> import iris
    >>> url = ("http://omgsrv1.meas.ncsu.edu:8080/thredds/dodsC/fmrc/sabgom/"
    ...        "SABGOM_Forecast_Model_Run_Collection_best.ncd")
    >>> cube = iris.load_cube(url, 'sea_water_potential_temperature')
    >>> cube = get_surface(cube)
    >>> len(cube.coords())
    10
    >>> cube = remove_ssh(cube)
    >>> len(cube.coords())
    8

    """
    for factory in cube.aux_factories:
        cube.remove_aux_factory(factory)
    for coord in cube.aux_coords:
        if coord.shape == cube.shape:
            if 'time' not in coord.name():
                cube.remove_coord(coord.name())
    return cube


def cube2series(cube):
    """
    Take a cube data and metadata and return a rich `pandas.Series`.

    """
    time = cube.coord('time')
    index = time.units.num2date(time.points)
    data = cube.data.squeeze()
    series = pd.Series(data=data, index=index)
    series._metadata = dict(
        station=cube.coord('station').points[0],
        station_name=cube.coord('station_name').points[0],
        station_code=cube.coord('station_code').points[0],
        sensor=cube.coord('sensor').points[0],
        lon=cube.coord('lon').points[0],
        lat=cube.coord('lat').points[0],
        depth=cube.coord('depth').points[0],
        standard_name=cube.standard_name,
        units=cube.units
        )
    return series


def series2cube(series, attr=None):
    """
    Convert a metadata rich `pandas.Series` to a CF compliant timeSeries.
    http://cfconventions.org/Data/cf-convetions/cf-conventions-1.6/build/cf-conventions.html#idp5577536

    The metadata expected are: standard_name, units, station_code,
    station_name, station, sensor, lon, lat, depth and time.
    The last two are added as cube coords while the rest are added as either
    auxiliary coords or cube metadata.

    """

    data = np.ma.masked_invalid(series.values)
    cube = iris.cube.Cube(
        data=np.atleast_2d(data),
        standard_name=series._metadata['standard_name'],
        units=series._metadata['units'])
    if attr:
        cube.attributes.update(attr)

    _add_iris_coord(cube,
                    name='time',
                    points=series.index,
                    dim=1,
                    units=cf_units.Unit('hours since epoch',
                                        calendar=cf_units.CALENDAR_GREGORIAN))

    _add_iris_coord(cube,
                    name='depth',
                    points=np.float_(series._metadata['depth']),
                    dim=0,
                    units=cf_units.Unit('m'))

    _add_iris_coord(cube,
                    name='station_code',
                    points=int(series._metadata['station_code']),
                    dim=0, aux=True)

    _add_iris_coord(cube,
                    name='station',
                    points=str(series._metadata['station']),
                    dim=0, aux=True)

    _add_iris_coord(cube,
                    name='sensor',
                    points=str(series._metadata['sensor']),
                    dim=0, aux=True)

    _add_iris_coord(cube,
                    name='station_name',
                    points=str(series._metadata['station_name']),
                    dim=0, aux=True)

    _add_iris_coord(cube,
                    name='lon',
                    points=np.float_(series._metadata['lon']),
                    units=cf_units.Unit('degrees'),
                    dim=0, aux=True)

    _add_iris_coord(cube,
                    name='lat',
                    points=np.float_(series._metadata['lat']),
                    units=cf_units.Unit('degrees'),
                    dim=0, aux=True)
    return cube


def _add_iris_coord(cube, name, points, dim, units=None, aux=False):
    """
    Helper function to add a coordinate to an existing cube.

    """
    # Convert pandas datetime objects to python datetime obejcts.
    if isinstance(points, pd.tseries.index.DatetimeIndex):
        points = points.to_pydatetime()

    # Convert datetime objects to Iris' current datetime representation.
    if isinstance(points, np.ndarray) and points.dtype == object:
        dt_types = (datetime, netcdftime.datetime)
        if all([isinstance(i, dt_types) for i in points]):
            points = units.date2num(points)

    points = np.array(points)
    if np.issubdtype(points.dtype, np.number) and not aux:
        coord = DimCoord(points, units=units)
        coord.rename(name)
        cube.add_dim_coord(coord, dim)
    else:
        coord = AuxCoord(points, units=units)
        coord.rename(name)
        cube.add_aux_coord(coord, dim)


def make_tree(cube):
    """
    Return a scipy KDTree object to search a cube.
    NOTE: iris does have its own implementation for searching with KDTrees, but
    it does not work for 2D coords like this one.

    Examples
    --------
    >>> import iris
    >>> from scipy.spatial import cKDTree as KDTree
    >>> url = ("http://omgsrv1.meas.ncsu.edu:8080/thredds/dodsC/fmrc/sabgom/"
    ...        "SABGOM_Forecast_Model_Run_Collection_best.ncd")
    >>> cube = iris.load_cube(url, 'sea_water_potential_temperature')
    >>> cube = get_surface(cube)
    >>> tree, lon, lat = make_tree(cube)
    >>> isinstance(tree, KDTree)
    True

    """
    lon = cube.coord(axis='X').points
    lat = cube.coord(axis='Y').points
    # Structured models with 1D lon, lat.
    if (lon.ndim == 1) and (lat.ndim == 1) and (cube.ndim == 3):
        lon, lat = np.meshgrid(lon, lat)
    # Unstructured are already paired!
    tree = KDTree(list(zip(lon.ravel(), lat.ravel())))
    return tree, lon, lat


def is_water(cube, min_var=0.01):
    """
    Use only data where the standard deviation of the time cube exceeds
    0.01 m (1 cm) this eliminates flat line model time cube that come from
    land points that should have had missing values.
    (Accounts for wet-and-dry models.)

    """
    arr = np.ma.masked_invalid(cube.data).filled(fill_value=0)
    if arr.std() <= min_var:
        return False
    return True


def get_nearest_series(cube, tree, xi, yi, k=10, max_dist=0.04):
    """
    Find `k` nearest model data points from an iris `cube` at station
    lon: `xi`, lat: `yi` up to `max_dist` in degrees.  Must provide a Scipy's
    KDTree `tree`.

    Examples
    --------
    >>> import iris
    >>> from scipy.spatial import cKDTree as KDTree
    >>> url = ("http://omgsrv1.meas.ncsu.edu:8080/thredds/dodsC/fmrc/sabgom/"
    ...        "SABGOM_Forecast_Model_Run_Collection_best.ncd")

    >>> cube = iris.load_cube(url, 'sea_water_potential_temperature')
    >>> cube = get_surface(cube)
    >>> tree, lon, lat = make_tree(cube)
    >>> series, dist, idx = get_nearest_series(cube, tree,
    ...                                        lon[0, 10], lat[0, 10],
    ...                                        k=10, max_dist=0.04)
    >>> idx == (0, 10)
    True
    >>> is_water(series, min_var=0.01)
    False
    >>> series, dist, idx = get_nearest_series(cube, tree,
    ...                                        -75.7135500943, 36.1640944084,
    ...                                        k=10, max_dist=0.04)
    >>> is_water(series, min_var=0.01)
    True

    """
    distances, indices = tree.query(np.array([xi, yi]).T, k=k)
    if indices.size == 0:
        raise ValueError("No data found.")
    # Get data up to specified distance.
    mask = distances <= max_dist
    distances, indices = distances[mask], indices[mask]
    if distances.size == 0:
        msg = "No data near ({}, {}) max_dist={}.".format
        raise ValueError(msg(xi, yi, max_dist))
    # Unstructured model.
    if (cube.coord(axis='X').ndim == 1) and (cube.ndim == 2):
        i = j = indices
        unstructured = True
    # Structured model.
    else:
        unstructured = False
        if cube.coord(axis='X').ndim == 2:  # CoordinateMultiDim
            i, j = np.unravel_index(indices, cube.coord(axis='X').shape)
        else:
            shape = (cube.coord(axis='Y').shape[0],
                     cube.coord(axis='X').shape[0])
            i, j = np.unravel_index(indices, shape)
    series, dist, idx = None, None, None
    IJs = list(zip(i, j))
    for dist, idx in zip(distances, IJs):
        idx = tuple([int(kk) for kk in idx])
        if unstructured:  # NOTE: This would be so elegant in py3k!
            idx = (idx[0],)
        # This weird syntax allow for idx to be len 1 or 2.
        series = cube[(slice(None),)+idx]
    return series, dist, idx


def get_nearest_water(cube, tree, xi, yi, k=10, max_dist=0.04, min_var=0.01):
    """
    Legacy function.  Use `get_nearest_series`+`is_water` instead!

    """
    distances, indices = tree.query(np.array([xi, yi]).T, k=k)
    if indices.size == 0:
        raise ValueError("No data found.")
    # Get data up to specified distance.
    mask = distances <= max_dist
    distances, indices = distances[mask], indices[mask]
    if distances.size == 0:
        msg = "No data near ({}, {}) max_dist={}.".format
        raise ValueError(msg(xi, yi, max_dist))
    # Unstructured model.
    if (cube.coord(axis='X').ndim == 1) and (cube.ndim == 2):
        i = j = indices
        unstructured = True
    # Structured model.
    else:
        unstructured = False
        if cube.coord(axis='X').ndim == 2:  # CoordinateMultiDim
            i, j = np.unravel_index(indices, cube.coord(axis='X').shape)
        else:
            shape = (cube.coord(axis='Y').shape[0],
                     cube.coord(axis='X').shape[0])
            i, j = np.unravel_index(indices, shape)
    IJs = list(zip(i, j))
    for dist, idx in zip(distances, IJs):
        idx = tuple([int(kk) for kk in idx])
        if unstructured:  # NOTE: This would be so elegant in py3k!
            idx = (idx[0],)
        # This weird syntax allow for idx to be len 1 or 2.
        series = cube[(slice(None),)+idx]
        if is_water(series, min_var=0.01):
            break
        else:
            series = None
            continue
    return series, dist, idx


if __name__ == '__main__':
    import doctest
    doctest.testmod()
