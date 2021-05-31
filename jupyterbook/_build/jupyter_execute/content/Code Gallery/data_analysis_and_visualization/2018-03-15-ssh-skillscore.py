#!/usr/bin/env python
# coding: utf-8

# # Investigating ocean models skill for sea surface height with IOOS catalog and Python
# 
# 
# The IOOS [catalog](https://ioos.noaa.gov/data/catalog) offers access to hundreds of datasets and data access services provided by the 11 regional associations.
# In the past we demonstrate how to tap into those datasets to obtain sea [surface temperature data from observations](http://ioos.github.io/notebooks_demos/notebooks/2016-12-19-exploring_csw),
# [coastal velocity from high frequency radar data](http://ioos.github.io/notebooks_demos/notebooks/2017-12-15-finding_HFRadar_currents),
# and a simple model vs observation visualization of temperatures for the [Boston Light Swim competition](http://ioos.github.io/notebooks_demos/notebooks/2016-12-22-boston_light_swim).
# 
# In this notebook we'll demonstrate a step-by-step workflow on how ask the catalog for a specific variable, extract only the model data, and match the nearest model grid point to an observation. The goal is to create an automated skill score for quick assessment of ocean numerical models.
# 
# 
# The first cell is only to reduce iris' noisy output,
# the notebook start on cell [2] with the definition of the parameters:
# - start and end dates for the search;
# - experiment name;
# - a bounding of the region of interest;
# - SOS variable name for the observations;
# - Climate and Forecast standard names;
# - the units we want conform the variables into;
# - catalogs we want to search.

# In[1]:


import warnings

# Suppresing warnings for a "pretty output."
warnings.simplefilter("ignore")


# In[2]:


get_ipython().run_cell_magic('writefile', 'config.yaml', "\ndate:\n    start: 2018-2-28 00:00:00\n    stop: 2018-3-5 00:00:00\n\nrun_name: 'latest'\n\nregion:\n    bbox: [-71.20, 41.40, -69.20, 43.74]\n    crs: 'urn:ogc:def:crs:OGC:1.3:CRS84'\n\nsos_name: 'water_surface_height_above_reference_datum'\n\ncf_names:\n    - sea_surface_height\n    - sea_surface_elevation\n    - sea_surface_height_above_geoid\n    - sea_surface_height_above_sea_level\n    - water_surface_height_above_reference_datum\n    - sea_surface_height_above_reference_ellipsoid\n\nunits: 'm'\n\ncatalogs:\n    - https://data.ioos.us/csw")


# To keep track of the information we'll setup a `config` variable and output them on the screen for bookkeeping.

# In[3]:


import os
import shutil
from datetime import datetime

from ioos_tools.ioos import parse_config

config = parse_config("config.yaml")

# Saves downloaded data into a temporary directory.
save_dir = os.path.abspath(config["run_name"])
if os.path.exists(save_dir):
    shutil.rmtree(save_dir)
os.makedirs(save_dir)

fmt = "{:*^64}".format
print(fmt("Saving data inside directory {}".format(save_dir)))
print(fmt(" Run information "))
print("Run date: {:%Y-%m-%d %H:%M:%S}".format(datetime.utcnow()))
print("Start: {:%Y-%m-%d %H:%M:%S}".format(config["date"]["start"]))
print("Stop: {:%Y-%m-%d %H:%M:%S}".format(config["date"]["stop"]))
print(
    "Bounding box: {0:3.2f}, {1:3.2f},"
    "{2:3.2f}, {3:3.2f}".format(*config["region"]["bbox"])
)


# To interface with the IOOS catalog we will use the [Catalogue Service for the Web (CSW)](https://live.osgeo.org/en/standards/csw_overview.html) endpoint and [python's OWSLib library](https://geopython.github.io/OWSLib).
# 
# The cell below creates the [Filter Encoding Specification (FES)](http://www.opengeospatial.org/standards/filter) with configuration we specified in cell [2]. The filter is composed of:
# - `or` to catch any of the standard names;
# - `not` some names we do not want to show up in the results;
# - `date range` and `bounding box` for the time-space domain of the search.

# In[4]:


def make_filter(config):
    from owslib import fes
    from ioos_tools.ioos import fes_date_filter

    kw = dict(
        wildCard="*", escapeChar="\\", singleChar="?", propertyname="apiso:Subject"
    )

    or_filt = fes.Or(
        [fes.PropertyIsLike(literal=("*%s*" % val), **kw) for val in config["cf_names"]]
    )

    not_filt = fes.Not([fes.PropertyIsLike(literal="GRIB-2", **kw)])

    begin, end = fes_date_filter(config["date"]["start"], config["date"]["stop"])

    bbox_crs = fes.BBox(config["region"]["bbox"], crs=config["region"]["crs"])

    filter_list = [fes.And([bbox_crs, begin, end, or_filt, not_filt])]
    return filter_list


filter_list = make_filter(config)


# We need to wrap `OWSlib.csw.CatalogueServiceWeb` object with a custom function,
# ` get_csw_records`, to be able to paginate over the results.
# 
# In the cell below we loop over all the catalogs returns and extract the OPeNDAP endpoints.

# In[5]:


from ioos_tools.ioos import get_csw_records, service_urls
from owslib.csw import CatalogueServiceWeb

dap_urls = []
print(fmt(" Catalog information "))
for endpoint in config["catalogs"]:
    print("URL: {}".format(endpoint))
    try:
        csw = CatalogueServiceWeb(endpoint, timeout=120)
    except Exception as e:
        print("{}".format(e))
        continue
    csw = get_csw_records(csw, filter_list, esn="full")
    OPeNDAP = service_urls(csw.records, identifier="OPeNDAP:OPeNDAP")
    odp = service_urls(
        csw.records, identifier="urn:x-esri:specification:ServiceType:odp:url"
    )
    dap = OPeNDAP + odp
    dap_urls.extend(dap)

    print("Number of datasets available: {}".format(len(csw.records.keys())))

    for rec, item in csw.records.items():
        print("{}".format(item.title))
    if dap:
        print(fmt(" DAP "))
        for url in dap:
            print("{}.html".format(url))
    print("\n")

# Get only unique endpoints.
dap_urls = list(set(dap_urls))


# We found 10 dataset endpoints but only 9 of them have the proper metadata for us to identify the OPeNDAP endpoint,
# those that contain either `OPeNDAP:OPeNDAP` or `urn:x-esri:specification:ServiceType:odp:url` scheme.
# Unfortunately we lost the `COAWST` model in the process.
# 
# The next step is to ensure there are no observations in the list of endpoints.
# We want only the models for now.

# In[6]:


from ioos_tools.ioos import is_station
from timeout_decorator import TimeoutError

# Filter out some station endpoints.
non_stations = []
for url in dap_urls:
    try:
        if not is_station(url):
            non_stations.append(url)
    except (IOError, OSError, RuntimeError, TimeoutError) as e:
        print("Could not access URL {}.html\n{!r}".format(url, e))

dap_urls = non_stations

print(fmt(" Filtered DAP "))
for url in dap_urls:
    print("{}.html".format(url))


# Now we have a nice list of all the models available in the catalog for the domain we specified.
# We still need to find the observations for the same domain.
# To accomplish that we will use the `pyoos` library and search the [SOS CO-OPS](https://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/) services using the virtually the same configuration options from the catalog search.

# In[7]:


from pyoos.collectors.coops.coops_sos import CoopsSos

collector_coops = CoopsSos()

collector_coops.set_bbox(config["region"]["bbox"])
collector_coops.end_time = config["date"]["stop"]
collector_coops.start_time = config["date"]["start"]
collector_coops.variables = [config["sos_name"]]

ofrs = collector_coops.server.offerings
title = collector_coops.server.identification.title
print(fmt(" Collector offerings "))
print("{}: {} offerings".format(title, len(ofrs)))


# To make it easier to work with the data we extract the time-series as pandas tables and interpolate them to a common 1-hour interval index.

# In[8]:


import pandas as pd
from ioos_tools.ioos import collector2table

data = collector2table(
    collector=collector_coops,
    config=config,
    col="water_surface_height_above_reference_datum (m)",
)

df = dict(
    station_name=[s._metadata.get("station_name") for s in data],
    station_code=[s._metadata.get("station_code") for s in data],
    sensor=[s._metadata.get("sensor") for s in data],
    lon=[s._metadata.get("lon") for s in data],
    lat=[s._metadata.get("lat") for s in data],
    depth=[s._metadata.get("depth") for s in data],
)

pd.DataFrame(df).set_index("station_code")


# In[9]:


index = pd.date_range(
    start=config["date"]["start"].replace(tzinfo=None),
    end=config["date"]["stop"].replace(tzinfo=None),
    freq="1H",
)

# Preserve metadata with `reindex`.
observations = []
for series in data:
    _metadata = series._metadata
    series.index = series.index.tz_localize(None)
    obs = series.reindex(index=index, limit=1, method="nearest")
    obs._metadata = _metadata
    observations.append(obs)


# The next cell saves those time-series as CF-compliant netCDF files on disk,
# to make it easier to access them later.

# In[10]:


import iris
from ioos_tools.tardis import series2cube

attr = dict(
    featureType="timeSeries",
    Conventions="CF-1.6",
    standard_name_vocabulary="CF-1.6",
    cdm_data_type="Station",
    comment="Data from http://opendap.co-ops.nos.noaa.gov",
)


cubes = iris.cube.CubeList([series2cube(obs, attr=attr) for obs in observations])

outfile = os.path.join(save_dir, "OBS_DATA.nc")
iris.save(cubes, outfile)


# We still need to read the model data from the list of endpoints we found.
# 
# The next cell takes care of that.
# We use `iris`, and a set of custom functions from the `ioos_tools` library,
# that downloads only the data in the domain we requested.

# In[11]:


from ioos_tools.ioos import get_model_name
from ioos_tools.tardis import is_model, proc_cube, quick_load_cubes
from iris.exceptions import ConstraintMismatchError, CoordinateNotFoundError, MergeError

print(fmt(" Models "))
cubes = dict()
for k, url in enumerate(dap_urls):
    print("\n[Reading url {}/{}]: {}".format(k + 1, len(dap_urls), url))
    try:
        cube = quick_load_cubes(url, config["cf_names"], callback=None, strict=True)
        if is_model(cube):
            cube = proc_cube(
                cube,
                bbox=config["region"]["bbox"],
                time=(config["date"]["start"], config["date"]["stop"]),
                units=config["units"],
            )
        else:
            print("[Not model data]: {}".format(url))
            continue
        mod_name = get_model_name(url)
        cubes.update({mod_name: cube})
    except (
        RuntimeError,
        ValueError,
        ConstraintMismatchError,
        CoordinateNotFoundError,
        IndexError,
    ) as e:
        print("Cannot get cube for: {}\n{}".format(url, e))


# Now we can match each observation time-series with its closest grid point (0.08 of a degree) on each model.
# This is a complex and laborious task! If you are running this interactively grab a coffee and sit comfortably :-)
# 
# Note that we are also saving the model time-series to files that align with the observations we saved before.

# In[12]:


import iris
from ioos_tools.tardis import (
    add_station,
    ensure_timeseries,
    get_nearest_water,
    make_tree,
)
from iris.pandas import as_series

for mod_name, cube in cubes.items():
    fname = "{}.nc".format(mod_name)
    fname = os.path.join(save_dir, fname)
    print(fmt(" Downloading to file {} ".format(fname)))
    try:
        tree, lon, lat = make_tree(cube)
    except CoordinateNotFoundError:
        print("Cannot make KDTree for: {}".format(mod_name))
        continue
    # Get model series at observed locations.
    raw_series = dict()
    for obs in observations:
        obs = obs._metadata
        station = obs["station_code"]
        try:
            kw = dict(k=10, max_dist=0.08, min_var=0.01)
            args = cube, tree, obs["lon"], obs["lat"]
            try:
                series, dist, idx = get_nearest_water(*args, **kw)
            except RuntimeError as e:
                print("Cannot download {!r}.\n{}".format(cube, e))
                series = None
        except ValueError:
            status = "No Data"
            print("[{}] {}".format(status, obs["station_name"]))
            continue
        if not series:
            status = "Land   "
        else:
            raw_series.update({station: series})
            series = as_series(series)
            status = "Water  "
        print("[{}] {}".format(status, obs["station_name"]))
    if raw_series:  # Save cube.
        for station, cube in raw_series.items():
            cube = add_station(cube, station)
        try:
            cube = iris.cube.CubeList(raw_series.values()).merge_cube()
        except MergeError as e:
            print(e)
        ensure_timeseries(cube)
        try:
            iris.save(cube, fname)
        except AttributeError:
            # FIXME: we should patch the bad attribute instead of removing everything.
            cube.attributes = {}
            iris.save(cube, fname)
        del cube
    print("Finished processing [{}]".format(mod_name))


# With the matched set of models and observations time-series it is relatively easy to compute skill score metrics on them. In cells [13] to [16] we apply both mean bias and root mean square errors to the time-series.

# In[13]:


from ioos_tools.ioos import stations_keys


def rename_cols(df, config):
    cols = stations_keys(config, key="station_name")
    return df.rename(columns=cols)


# In[14]:


from ioos_tools.ioos import load_ncs
from ioos_tools.skill_score import apply_skill, mean_bias

dfs = load_ncs(config)

df = apply_skill(dfs, mean_bias, remove_mean=False, filter_tides=False)
skill_score = dict(mean_bias=df.to_dict())

# Filter out stations with no valid comparison.
df.dropna(how="all", axis=1, inplace=True)
df = df.applymap("{:.2f}".format).replace("nan", "--")


# In[15]:


from ioos_tools.skill_score import rmse

dfs = load_ncs(config)

df = apply_skill(dfs, rmse, remove_mean=True, filter_tides=False)
skill_score["rmse"] = df.to_dict()

# Filter out stations with no valid comparison.
df.dropna(how="all", axis=1, inplace=True)
df = df.applymap("{:.2f}".format).replace("nan", "--")


# In[16]:


import pandas as pd

# Stringfy keys.
for key in skill_score.keys():
    skill_score[key] = {str(k): v for k, v in skill_score[key].items()}

mean_bias = pd.DataFrame.from_dict(skill_score["mean_bias"])
mean_bias = mean_bias.applymap("{:.2f}".format).replace("nan", "--")

skill_score = pd.DataFrame.from_dict(skill_score["rmse"])
skill_score = skill_score.applymap("{:.2f}".format).replace("nan", "--")


# Last but not least we can assemble a GIS map, cells [17-23],
# with the time-series plot for the observations and models,
# and the corresponding skill scores.

# In[17]:


import folium
from ioos_tools.ioos import get_coordinates


def make_map(bbox, **kw):
    line = kw.pop("line", True)
    zoom_start = kw.pop("zoom_start", 5)

    lon = (bbox[0] + bbox[2]) / 2
    lat = (bbox[1] + bbox[3]) / 2
    m = folium.Map(
        width="100%", height="100%", location=[lat, lon], zoom_start=zoom_start
    )

    if line:
        p = folium.PolyLine(
            get_coordinates(bbox), color="#FF0000", weight=2, opacity=0.9,
        )
        p.add_to(m)
    return m


# In[18]:


bbox = config["region"]["bbox"]

m = make_map(bbox, zoom_start=8, line=True, layers=True)


# In[19]:


all_obs = stations_keys(config)

from glob import glob
from operator import itemgetter

import iris
from folium.plugins import MarkerCluster

iris.FUTURE.netcdf_promote = True

big_list = []
for fname in glob(os.path.join(save_dir, "*.nc")):
    if "OBS_DATA" in fname:
        continue
    cube = iris.load_cube(fname)
    model = os.path.split(fname)[1].split("-")[-1].split(".")[0]
    lons = cube.coord(axis="X").points
    lats = cube.coord(axis="Y").points
    stations = cube.coord("station_code").points
    models = [model] * lons.size
    lista = zip(models, lons.tolist(), lats.tolist(), stations.tolist())
    big_list.extend(lista)

big_list.sort(key=itemgetter(3))
df = pd.DataFrame(big_list, columns=["name", "lon", "lat", "station"])
df.set_index("station", drop=True, inplace=True)
groups = df.groupby(df.index)


locations, popups = [], []
for station, info in groups:
    sta_name = all_obs[station]
    for lat, lon, name in zip(info.lat, info.lon, info.name):
        locations.append([lat, lon])
        popups.append("[{}]: {}".format(name, sta_name))

MarkerCluster(locations=locations, popups=popups, name="Cluster").add_to(m)


# In[20]:


titles = {
    "coawst_4_use_best": "COAWST_4",
    "pacioos_hycom-global": "HYCOM",
    "NECOFS_GOM3_FORECAST": "NECOFS_GOM3",
    "NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST": "NECOFS_MassBay",
    "NECOFS_FVCOM_OCEAN_BOSTON_FORECAST": "NECOFS_Boston",
    "SECOORA_NCSU_CNAPS": "SECOORA/CNAPS",
    "roms_2013_da_avg-ESPRESSO_Real-Time_v2_Averages_Best": "ESPRESSO Avg",
    "roms_2013_da-ESPRESSO_Real-Time_v2_History_Best": "ESPRESSO Hist",
    "OBS_DATA": "Observations",
}


# In[21]:


from itertools import cycle

from bokeh.embed import file_html
from bokeh.models import HoverTool, Legend
from bokeh.palettes import Category20
from bokeh.plotting import figure
from bokeh.resources import CDN
from folium import IFrame

# Plot defaults.
colors = Category20[20]
colorcycler = cycle(colors)
tools = "pan,box_zoom,reset"
width, height = 750, 250


def make_plot(df, station):
    p = figure(
        toolbar_location="above",
        x_axis_type="datetime",
        width=width,
        height=height,
        tools=tools,
        title=str(station),
    )
    leg = []
    for column, series in df.iteritems():
        series.dropna(inplace=True)
        if not series.empty:
            if "OBS_DATA" not in column:
                bias = mean_bias[str(station)][column]
                skill = skill_score[str(station)][column]
                line_color = next(colorcycler)
                kw = dict(alpha=0.65, line_color=line_color)
            else:
                skill = bias = "NA"
                kw = dict(alpha=1, color="crimson")
            line = p.line(
                x=series.index,
                y=series.values,
                line_width=5,
                line_cap="round",
                line_join="round",
                **kw
            )
            leg.append(("{}".format(titles.get(column, column)), [line]))
            p.add_tools(
                HoverTool(
                    tooltips=[
                        ("Name", "{}".format(titles.get(column, column))),
                        ("Bias", bias),
                        ("Skill", skill),
                    ],
                    renderers=[line],
                )
            )
    legend = Legend(items=leg, location=(0, 60))
    legend.click_policy = "mute"
    p.add_layout(legend, "right")
    p.yaxis[0].axis_label = "Water Height (m)"
    p.xaxis[0].axis_label = "Date/time"
    return p


def make_marker(p, station):
    lons = stations_keys(config, key="lon")
    lats = stations_keys(config, key="lat")

    lon, lat = lons[station], lats[station]
    html = file_html(p, CDN, station)
    iframe = IFrame(html, width=width + 40, height=height + 80)

    popup = folium.Popup(iframe, max_width=2650)
    icon = folium.Icon(color="green", icon="stats")
    marker = folium.Marker(location=[lat, lon], popup=popup, icon=icon)
    return marker


# In[22]:


dfs = load_ncs(config)

for station in dfs:
    sta_name = all_obs[station]
    df = dfs[station]
    if df.empty:
        continue
    p = make_plot(df, station)
    marker = make_marker(p, station)
    marker.add_to(m)

folium.LayerControl().add_to(m)


# In[23]:


def embed_map(m):
    from IPython.display import HTML

    m.save("index.html")
    with open("index.html") as f:
        html = f.read()

    iframe = '<iframe srcdoc="{srcdoc}" style="width: 100%; height: 750px; border: none"></iframe>'
    srcdoc = html.replace('"', "&quot;")
    return HTML(iframe.format(srcdoc=srcdoc))


embed_map(m)

