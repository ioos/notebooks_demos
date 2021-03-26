# Accessing data from SOS using NHC GIS files Part 1

This post is the part 1 of 4 of a notebook series on how to obtain IOOS/NOAA data
starting from a Hurricane track GIS format.

We will download Sea Surface Height (SSH) data from the
[Sensor Observation Service (SOS)](https://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/)
closest to where Hurricane Michael made landfall.

The first step is to obtain Hurricane Michael's GIS data from the 
[National Hurricane Center (NHC)](https://www.nhc.noaa.gov/gis/).

The function below downloads the "best track"
and load all the information we will use into two
[GeoPandas dataframes](http://geopandas.org), one for the radii shape and another one for the track points.

The inputs for the function based on the NHC storms code:

- 2 char for region `al` &rarr; Atlantic
- 2 char for number `14` is Michael
- and 4 char for year, `2018`

import os
from pathlib import Path

import geopandas
import pandas as pd


def load_best_track(code="al14", year="2018"):
    fname = Path(f"{code}{year}_best_track.zip")

    if not fname.is_file():
        import urllib.request

        url = f"https://www.nhc.noaa.gov/gis/best_track/{fname}"
        urllib.request.urlretrieve(url, fname)

    os.environ["CPL_ZIP_ENCODING"] = "UTF-8"

    radii = geopandas.read_file(
        f"/{code.upper()}{year}_radii.shp", vfs=f"zip://{fname}"
    )

    pts = geopandas.read_file(f"/{code.upper()}{year}_pts.shp", vfs=f"zip://{fname}")

    pts["str"] = pts["DTG"].astype(int).astype(str)

    pts.index = pd.to_datetime(pts["str"], format="%Y%m%d%H", errors="coerce").values

    radii.index = pd.to_datetime(
        radii["SYNOPTIME"], format="%Y%m%d%H", errors="coerce"
    ).values
    return radii, pts

Now we can easily load track data and obtain the information we need to start querying the SOS service.

radii, pts = load_best_track(code="al14", year="2018")

start = radii.index[0]
stop = radii.index[-1]
bbox = radii["geometry"].total_bounds

The only two pieces of information that will not come from the GIS file are
the variable of interest and the buoy.
The former is user defined and the latter could be auto-discovered.
We will cover that in a future notebook.

variable = "water_surface_height_above_reference_datum"

buoy = "8728690"

For the sake of better understanding the SOS service we will create the data endpoint "by hand."
In the cell below we "fill" the URL with the information we got above.

url = (
    "https://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?"
    "service=SOS"
    "&request=GetObservation"
    "&version=1.0.0"
    f"&observedProperty={variable}"
    f"&offering=urn:ioos:station:NOAA.NOS.CO-OPS:{buoy}"
    "&responseFormat=text/csv"
    f"&eventTime={start:%Y-%m-%dT%H:%M:%SZ}/{stop:%Y-%m-%dT%H:%M:%SZ}"
    "&result=VerticalDatum==urn:ogc:def:datum:epsg::5103"
    "&dataType=PreliminarySixMinute"
)

print(url)

Now we can easily load the SSH data as a pandas `DataFrame`.

df = pd.read_csv(url, index_col="date_time", parse_dates=True)

df.head()

To make it easy to navigate the DataFrame let's create a helper function that
extracts the metadata from the columns.
(Pandas DataFrames are table formats so the metadata are columns with value
repeated over the data length.)

def extract_metadata(col):
    value = col.unique()
    if len(value) > 1:
        raise ValueError(f"Expected a single value but got {len(value)}")
    return value.squeeze().tolist()

import hvplot.pandas  # noqa

col = df.columns[df.columns.str.startswith(variable)]
sensor_id = extract_metadata(df["sensor_id"])

df[col].hvplot.line(
    figsize=(9, 2.75), legend=False, grid=True, title=sensor_id,
)

We can use the dataframe to filter the GIS data near the highest water level and create an interactive map highlight the radii of the hurricane during the SSH time-series period.

idxmax = df[col].idxmax().squeeze()

dedup = radii.loc[~radii.index.duplicated(keep="first")]
overlap = dedup.iloc[dedup.index.get_loc(idxmax, method="nearest")]

import folium
from folium.plugins import Fullscreen

location = (
    extract_metadata(df["latitude (degree)"]),
    extract_metadata(df["longitude (degree)"]),
)

m = folium.Map(location=location, zoom_start=5)
Fullscreen().add_to(m)

folium.Marker(location=location, popup=sensor_id).add_to(m)

for geom in radii["geometry"]:
    folium.GeoJson(geom.__geo_interface__).add_to(m)

style_function = lambda feature: {"fillColor": "#FF5733", "opacity": "0.15"}

folium.GeoJson(
    overlap["geometry"].__geo_interface__, style_function=style_function
).add_to(m)

m

Here we constructed the SOS data endpoint manually but
IOOS maintains a Python library,
[pyoos](https://github.com/ioos/pyoos),
for collecting Met/Ocean observations from the SOS service and more:

- IOOS SWE SOS 1.0 Services
- NERRS Observations - SOAP
- NDBC Observations - SOS
- CO-OPS Observations - SOS
- STORET Water Quality - WqxOutbound via REST 
- USGS NWIS Water Quality - WqxOutbound via REST
- USGS Instantaneous Values - WaterML via REST
- NWS AWC Observations - XML via REST
- HADS

In the next notebooks in this series we will demostrante how to use `pyoos`
to find the data endpoint automatically.