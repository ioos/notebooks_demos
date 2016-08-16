from __future__ import absolute_import, division, print_function

import os
import fnmatch
import warnings
import requests
import numpy as np
import pandas as pd
from io import BytesIO
try:
    from urllib import urlopen
    from urlparse import urlparse
except ImportError:
    from urllib.request import urlopen
    from urllib.parse import urlparse

from contextlib import contextmanager
from lxml import etree
from owslib import fes

"""
Collection of functions used in the IOOS system-test exercise.

"""

rootpath = os.path.split(__file__)[0]
style = os.path.join(rootpath, 'data', 'style.css')


def parse_config(config_file):
    """Parse the yaml file with the configuration for each run."""
    import yaml
    import pytz
    import cf_units

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    # 1-week start of data normalized to UTC.
    config['date']['start'] = config['date']['start'].replace(tzinfo=pytz.utc)
    config['date']['stop'] = config['date']['stop'].replace(tzinfo=pytz.utc)

    # Units.
    config['units'] = cf_units.Unit(config['units'])

    return config


def fes_date_filter(start, stop, constraint='overlaps'):
    """
    Take datetime-like objects and returns a fes filter for date range
    (begin and end inclusive).
    NOTE: Truncates the minutes!!!

    Examples
    --------
    >>> from datetime import datetime, timedelta
    >>> stop = datetime(2010, 1, 1, 12, 30, 59).replace(tzinfo=pytz.utc)
    >>> start = stop - timedelta(days=7)
    >>> begin, end = fes_date_filter(start, stop, constraint='overlaps')
    >>> begin.literal, end.literal
    ('2010-01-01 12:00', '2009-12-25 12:00')
    >>> begin.propertyoperator, end.propertyoperator
    ('ogc:PropertyIsLessThanOrEqualTo', 'ogc:PropertyIsGreaterThanOrEqualTo')
    >>> begin, end = fes_date_filter(start, stop, constraint='within')
    >>> begin.literal, end.literal
    ('2009-12-25 12:00', '2010-01-01 12:00')
    >>> begin.propertyoperator, end.propertyoperator
    ('ogc:PropertyIsGreaterThanOrEqualTo', 'ogc:PropertyIsLessThanOrEqualTo')

    """
    start = start.strftime('%Y-%m-%d %H:00')
    stop = stop.strftime('%Y-%m-%d %H:00')
    if constraint == 'overlaps':
        propertyname = 'apiso:TempExtent_begin'
        begin = fes.PropertyIsLessThanOrEqualTo(propertyname=propertyname,
                                                literal=stop)
        propertyname = 'apiso:TempExtent_end'
        end = fes.PropertyIsGreaterThanOrEqualTo(propertyname=propertyname,
                                                 literal=start)
    elif constraint == 'within':
        propertyname = 'apiso:TempExtent_begin'
        begin = fes.PropertyIsGreaterThanOrEqualTo(propertyname=propertyname,
                                                   literal=start)
        propertyname = 'apiso:TempExtent_end'
        end = fes.PropertyIsLessThanOrEqualTo(propertyname=propertyname,
                                              literal=stop)
    else:
        raise NameError('Unrecognized constraint {}'.format(constraint))
    return begin, end


def service_urls(records, services):
    """
    Extract service_urls of a specific type (DAP, SOS) from csw records.
    Example: services=['urn:x-esri:specification:ServiceType:odp:url']

    For more strings check:
    https://raw.githubusercontent.com/OSGeo/Cat-Interop/master/LinkPropertyLookupTable.csv

    """
    urls = []
    for service in services:
        for key, rec in records.items():
            url = next((d['url'] for d in rec.references if
                        d['scheme'] == service), None)
            if url is not None:
                urls.append(url)
        urls = sorted(set(urls))
    return urls


def sos_request(url='opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS', **kw):
    """
    Examples
    --------
    >>> try:
    ...     from urlparse import urlparse
    ... except ImportError:
    ...     from urllib.parse import urlparse
    >>> from datetime import date, datetime, timedelta
    >>> today = date.today().strftime("%Y-%m-%d")
    >>> start = datetime.strptime(today, "%Y-%m-%d") - timedelta(7)
    >>> bbox = [-87.40, 24.25, -74.70, 36.70]
    >>> sos_name = 'water_surface_height_above_reference_datum'
    >>> offering='urn:ioos:network:NOAA.NOS.CO-OPS:WaterLevelActive'
    >>> params = dict(observedProperty=sos_name,
    ...               eventTime=start.strftime('%Y-%m-%dT%H:%M:%SZ'),
    ...               featureOfInterest='BBOX:{0},{1},{2},{3}'.format(*bbox),
    ...               offering=offering)
    >>> uri = 'http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS'
    >>> url = sos_request(uri, **params)
    >>> bool(urlparse(url).scheme)
    True

    """
    url = parse_url(url)
    offering = 'urn:ioos:network:NOAA.NOS.CO-OPS:CurrentsActive'
    params = dict(service='SOS',
                  request='GetObservation',
                  version='1.0.0',
                  offering=offering,
                  responseFormat='text/csv')
    params.update(kw)
    r = requests.get(url, params=params)
    r.raise_for_status()
    content = r.headers['Content-Type']
    if 'excel' in content or 'csv' in content:
        return r.url
    else:
        raise TypeError('Bad url {}'.format(r.url))


def _get_value(sensor, name='longName'):
    value = None
    sml = sensor.get(name, None)
    if sml:
        value = sml.value
    return value


def get_coops_metadata(station):
    """
    Get longName and sensorName for specific station from COOPS SOS using
    DescribeSensor and owslib.swe.sensor.sml.SensorML.

    Examples
    --------
    >>> long_name, station_id = get_coops_metadata(8651370)
    >>> long_name
    'Duck, NC'
    >>> station_id
    'urn:ioos:station:NOAA.NOS.CO-OPS:8651370'

    """
    from owslib.swe.sensor.sml import SensorML
    url = ('opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?'
           'service=SOS&'
           'request=DescribeSensor&version=1.0.0&'
           'outputFormat=text/xml;'
           'subtype="sensorML/1.0.1/profiles/ioos_sos/1.0"&'
           'procedure=urn:ioos:station:NOAA.NOS.CO-OPS:%s') % station
    url = parse_url(url)
    xml = etree.parse(urlopen(url))
    root = SensorML(xml)
    if not root.members or len(root.members) > 1:
        msg = "Expected 1 member, got {}".format
        raise ValueError(msg(len(root.members)))
    system = root.members[0]

    # NOTE: Some metadata of interest.
    # system.description
    # short_name = _get_value(system.identifiers, name='shortName')
    # [c.values() for c in system.components]

    long_name = _get_value(system.identifiers, name='longName')
    long_name = long_name.split('station, ')[-1].strip()
    station_id = _get_value(system.identifiers, name='stationID')

    return long_name, station_id


def ndbc2df(collector, ndbc_id):
    """
    Ugly hack because `collector.raw(responseFormat="text/csv")`
    Usually times out.

    """
    from netCDF4 import MFDataset, date2index, num2date
    # FIXME: Only sea_water_temperature for now.
    if len(collector.variables) > 1:
        msg = "Expected only 1 variables to download, got {}".format
        raise ValueError(msg(collector.variables))
    if collector.variables[0] == 'sea_water_temperature':
        columns = 'sea_water_temperature (C)'
        ncvar = 'sea_surface_temperature'
        data_type = 'stdmet'
        # adcp, adcp2, cwind, dart, mmbcur, ocean, oceansites, pwind,
        # swden, tao-ctd, wlevel, z-hycom
    else:
        msg = "Do not know how to download {}".format
        raise ValueError(msg(collector.variables))

    uri = 'http://dods.ndbc.noaa.gov/thredds/dodsC/data/{}'.format(data_type)
    url = ('%s/%s/' % (uri, ndbc_id))
    urls = url_lister(url)

    filetype = "*.nc"
    file_list = [filename for filename in fnmatch.filter(urls, filetype)]
    files = [fname.split('/')[-1] for fname in file_list]
    urls = ['%s/%s/%s' % (uri, ndbc_id, fname) for fname in files]

    if not urls:
        raise Exception("Cannot find data at {!r}".format(url))
    nc = MFDataset(urls)

    kw = dict(calendar='gregorian', select='nearest')
    time_dim = nc.variables['time']
    time = num2date(time_dim[:], units=time_dim.units,
                    calendar=kw['calendar'])

    idx_start = date2index(collector.start_time.replace(tzinfo=None),
                           time_dim, **kw)
    idx_stop = date2index(collector.end_time.replace(tzinfo=None),
                          time_dim, **kw)
    if idx_start == idx_stop:
        raise Exception("No data within time range"
                        " {!r} and {!r}".format(collector.start_time,
                                                collector.end_time))
    data = nc.variables[ncvar][idx_start:idx_stop, ...].squeeze()

    time_dim = nc.variables['time']
    time = time[idx_start:idx_stop].squeeze()
    df = pd.DataFrame(data=data, index=time, columns=[columns])
    df.index.name = 'date_time'
    return df


def pyoos2df(collector, station_id, df_name=None):
    """
    Request CSV response from SOS and convert to Pandas dataframe.

    """
    collector.features = [station_id]
    try:
        response = collector.raw(responseFormat="text/csv")
        kw = dict(parse_dates=True, index_col='date_time')
        df = pd.read_csv(BytesIO(response), **kw)
    except requests.exceptions.ReadTimeout:
        df = ndbc2df(collector, station_id)
    # FIXME: Workaround to get only 1 sensor.
    df = df.reset_index()
    kw = dict(subset='date_time', keep='last')
    df = df.drop_duplicates(**kw).set_index('date_time')
    if df_name:
        df.name = df_name
    return df


def _extract_columns(name, cube):
    """
    Workaround to extract data from a cube and create a dataframe
    following SOS boilerplate.

    """
    try:
        from HTMLParser import HTMLParser
    except ImportError:
        from html.parser import HTMLParser
    station = cube.attributes.get('abstract', None)
    if not station:
        station = name.replace('.', '_')

    parser = HTMLParser()
    station = parser.unescape(station)

    sensor = 'NA'
    lon = cube.coord(axis='X').points[0]
    lat = cube.coord(axis='Y').points[0]
    time = cube.coord(axis='T')
    time = time.units.num2date(cube.coord(axis='T').points)[0]
    date_time = time.strftime('%Y-%M-%dT%H:%M:%SZ')
    data = cube.data.mean()
    return station, sensor, lat, lon, date_time, data


def secoora2df(buoys, varname):
    secoora_obs = dict()
    for station, cube in buoys.items():
        secoora_obs.update({station: _extract_columns(station, cube)})

    df = pd.DataFrame.from_dict(secoora_obs, orient='index')
    df.reset_index(inplace=True)
    columns = {'index': 'station',
               0: 'name',
               1: 'sensor',
               2: 'lat',
               3: 'lon',
               4: 'date_time',
               5: varname}

    df.rename(columns=columns, inplace=True)
    df.set_index('name', inplace=True)
    return df


def _guess_name(model_full_name):
    """
    Examples
    --------
    >>> some_names = ['USF FVCOM - Nowcast Aggregation',
    ...               'ROMS/TOMS 3.0 - New Floria Shelf Application',
    ...               'COAWST Forecast System : USGS : US East Coast and Gulf'
    ...               'of Mexico (Experimental)',
    ...               'HYbrid Coordinate Ocean Model (HYCOM): Global',
    ...               'ROMS ESPRESSO Real-Time Operational IS4DVAR Forecast'
    ...               'System Version 2 (NEW) 2013-present FMRC History'
    ...               '(Best)']
    >>> [_guess_name(model_full_name) for model_full_name in some_names]
    ['USF_FVCOM', 'ROMS/TOMS', 'COAWST_USGS', 'HYCOM', 'ROMS_ESPRESSO']

    """
    words = []
    for word in model_full_name.split():
        if word.isupper():
            words.append(_remove_parenthesis(word))
    mod_name = ' '.join(words)
    if not mod_name:
        mod_name = ''.join([c for c in model_full_name.split('(')[0]
                            if c.isupper()])
    if len(mod_name.split()) > 1:
        mod_name = '_'.join(mod_name.split()[:2])
    return mod_name


def _remove_parenthesis(word):
    """
    Examples
    --------
    >>> _remove_parenthesis("(ROMS)")
    'ROMS'

    """
    try:
        return word[word.index("(") + 1:word.rindex(")")]
    except ValueError:
        return word


def _sanitize(name):
    """
    Examples
    --------
    >>> _sanitize('ROMS/TOMS')
    'ROMS_TOMS'
    >>> _sanitize('USEAST model')
    'USEAST_model'
    >>> _sanitize('GG1SST, SST')
    'GG1SST_SST'

    """
    name = name.replace(', ', '_')
    name = name.replace('/', '_')
    name = name.replace(' ', '_')
    name = name.replace(',', '_')
    return name


def get_model_name(cube, url, titles):
    """
    Return a model short and long name from a cube.

    Examples
    --------
    >>> import iris
    >>> import warnings
    >>> url = ('http://omgsrv1.meas.ncsu.edu:8080/thredds/dodsC/fmrc/sabgom/'
    ...        'SABGOM_Forecast_Model_Run_Collection_best.ncd')
    >>> with warnings.catch_warnings():
    ...     warnings.simplefilter("ignore")  # Suppress iris warnings.
    ...     cube = iris.load_cube(url, "sea_water_potential_temperature")
    >>> get_model_name(cube, url)
    ('SABGOM', 'ROMS/TOMS 3.0 - South-Atlantic Bight and Gulf of Mexico')

    """
    url = parse_url(url)
    # [model_full_name]: if there is no title assign the URL.
    try:
        model_full_name = cube.attributes.get('title', url)
    except AttributeError:
        model_full_name = url
    # [mod_name]: first searches the titles dictionary, if not try to guess.
    for mod_name, uri in titles.items():
        if url == uri:
            return mod_name, model_full_name
    warnings.warn('Model %s not in the list.  Guessing' % url)
    mod_name = _guess_name(model_full_name)
    mod_name = _sanitize(mod_name)
    return mod_name, model_full_name


def is_station(url):
    from netCDF4 import Dataset
    with Dataset(url) as nc:
        station = False
        if hasattr(nc, 'cdm_data_type'):
            if nc.cdm_data_type.lower() == 'station':
                station = True
    return station


# Web/Misc.
def url_lister(url):
    """
    Extract all href links from a given URL.

    """
    import lxml.html
    urls = []
    connection = urlopen(url)
    dom = lxml.html.fromstring(connection.read())
    for link in dom.xpath('//a/@href'):
        urls.append(link)
    return urls


def parse_url(url):
    """
    This will preserve any given scheme but will add http if none is
    provided.

    Examples
    --------
    >>> parse_url('www.google.com')
    'http://www.google.com'
    >>> parse_url('https://www.google.com')
    'https://www.google.com'

    """
    if not urlparse(url).scheme:
        url = "http://{}".format(url)
    return url


def to_html(df, css=style):
    """
    Return a pandas table HTML representation with the datagrid css.
    Examples
    --------
    >>> from IPython.display import HTML
    >>> from pandas import DataFrame
    >>> df = DataFrame(np.empty((5, 5)))
    >>> html = to_html(df)
    >>> isinstance(html, HTML)
    True

    """
    from IPython.display import HTML
    with open(css, 'r') as f:
        style = """<style>{}</style>""".format(f.read())
    table = dict(style=style, table=df.to_html())
    return HTML('{style}<div class="datagrid">{table}</div>'.format(**table))


def save_html(fname, HTML):
    with open(fname, 'w') as f:
        f.writelines(HTML.data)


@contextmanager
def time_limit(seconds=10):
    """
    Raise a TimeoutException after n `seconds`.

    """
    import signal

    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


class TimeoutException(Exception):
    """
    Timeout Exception.

    Example
    -------
    >>> def long_function_call():
    ...     import time
    ...     sec = 0
    ...     while True:
    ...         sec += 1
    ...         time.sleep(1)
    >>> try:
    ...     with time_limit(3):
    ...         long_function_call()
    ... except TimeoutException as msg:
    ...     print('{!r}'.format(msg))
    TimeoutException('Timed out!',)
    """
    pass


def make_map(bbox, **kw):
    """
    Creates a folium map instance for SECOORA.

    Examples
    --------
    >>> from folium import Map
    >>> bbox = [-87.40, 24.25, -74.70, 36.70]
    >>> m = make_map(bbox)
    >>> isinstance(m, Map)
    True

    """
    import folium

    line = kw.pop('line', True)
    layers = kw.pop('layers', True)
    hf_radar = kw.pop('hf_radar', True)
    zoom_start = kw.pop('zoom_start', 5)

    lon, lat = np.array(bbox).reshape(2, 2).mean(axis=0)
    m = folium.Map(width='100%', height='100%',
                   location=[lat, lon], zoom_start=zoom_start)

    if hf_radar:
        url = 'http://hfrnet.ucsd.edu/thredds/wms/HFRNet/USEGC/6km/hourly/RTV'
        w = folium.WmsTileLayer(url,
                                name='HF Radar',
                                format='image/png',
                                layers='surface_sea_water_velocity',
                                attr='HFRNet',
                                overlay=True,
                                transparent=True)
        w.add_to(m)
    if layers:
        add = 'MapServer/tile/{z}/{y}/{x}'
        base = 'http://services.arcgisonline.com/arcgis/rest/services'
        ESRI = dict(Imagery='World_Imagery/MapServer',
                    Ocean_Base='Ocean/World_Ocean_Base',
                    Topo_Map='World_Topo_Map/MapServer',
                    Street_Map='World_Street_Map/MapServer',
                    Physical_Map='World_Physical_Map/MapServer',
                    Terrain_Base='World_Terrain_Base/MapServer',
                    NatGeo_World_Map='NatGeo_World_Map/MapServer',
                    Shaded_Relief='World_Shaded_Relief/MapServer',
                    Ocean_Reference='Ocean/World_Ocean_Reference',
                    Navigation_Charts='Specialty/World_Navigation_Charts')
        for name, url in ESRI.items():
            url = '{}/{}/{}'.format(base, url, add)

            w = folium.TileLayer(tiles=url,
                                 name=name,
                                 attr='ESRI',
                                 overlay=True)
            w.add_to(m)

    if line:  # Create the map and add the bounding box line.
        p = folium.PolyLine(get_coordinates(bbox),
                            color='#FF0000',
                            weight=2,
                            opacity=0.9,
                            latlon=True)
        m.add_children(p)

    m.add_children(folium.LayerControl())
    return m


def get_coordinates(bbox):
    """
    Create bounding box coordinates for the map.  It takes flat or
    nested list/numpy.array and returns 5 points that closes square
    around the borders.

    Examples
    --------
    >>> bbox = [-87.40, 24.25, -74.70, 36.70]
    >>> len(get_coordinates(bbox))
    5

    """
    bbox = np.asanyarray(bbox).ravel()
    if bbox.size == 4:
        bbox = bbox.reshape(2, 2)
        coordinates = []
        coordinates.append([bbox[0][1], bbox[0][0]])
        coordinates.append([bbox[0][1], bbox[1][0]])
        coordinates.append([bbox[1][1], bbox[1][0]])
        coordinates.append([bbox[1][1], bbox[0][0]])
        coordinates.append([bbox[0][1], bbox[0][0]])
    else:
        raise ValueError('Wrong number corners.'
                         '  Expected 4 got {}'.format(bbox.size))
    return coordinates
