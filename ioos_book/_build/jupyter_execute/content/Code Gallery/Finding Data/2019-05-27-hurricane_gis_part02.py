# Accessing data from SOS using NHC GIS files
## Part 2: finding data programmatically with PyOOS

This post is the part 2 of 4 of a notebook series on how to obtain IOOS/NOAA data starting from a Hurricane track GIS format.

We will download Sea Surface Height (SSH) data from the
[Sensor Observation Service (SOS)](https://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/)
along the hurricane track.

For the instructions on how to obtain the GIS data for Hurricane Michael please the the [first notebook in the series](https://ioos.github.io/notebooks_demos/notebooks/2019-02-26-hurricane_gis_part01/). The function below loads and extract the hurricane radii and points.

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

With this functions we can figure out the geographic bounding box and the start/end dates of the event.

radii, pts = load_best_track(code="al14", year="2018")

start = radii.index[0]
end = radii.index[-1]
bbox = tuple(radii["geometry"].total_bounds)

strbbox = ", ".join(format(v, ".2f") for v in bbox)
print(f"bbox: {strbbox}\nstart: {start}\n  end: {end}")

Now that we have a bounding box for the collection of radii, and the start and end dates of the hurricane record, we can create a track-like path with shapely based on the individual points.

import shapely

coords = zip(pts["LON"], pts["LAT"])
track = shapely.geometry.LineString(coords)

The cell below is the main difference from what we did in [part 1](https://ioos.github.io/notebooks_demos/notebooks/2019-02-26-hurricane_gis_part01/), here we will use the bonding box and event dates with a [PyOOS collector](https://github.com/ioos/pyoos) to fetch all the data available in that scope.

import cf_units
from ioos_tools.ioos import collector2table
from pyoos.collectors.coops.coops_sos import CoopsSos
from retrying import retry


# We need to retry in case of failure b/c the server cannot handle
# the high traffic during events like hurricanes.
@retry(stop_max_attempt_number=5, wait_fixed=3000)
def get_coops(start, end, sos_name, units, bbox, verbose=False):
    collector = CoopsSos()
    collector.set_bbox(bbox)
    collector.end_time = end
    collector.start_time = start
    collector.variables = [sos_name]
    ofrs = collector.server.offerings
    title = collector.server.identification.title
    config = dict(units=units, sos_name=sos_name,)

    data = collector2table(
        collector=collector,
        config=config,
        col=f"{sos_name} ({units.format(cf_units.UT_ISO_8859_1)})",
    )

    # Clean the table.
    table = dict(
        station_name=[s._metadata.get("station_name") for s in data],
        station_code=[s._metadata.get("station_code") for s in data],
        sensor=[s._metadata.get("sensor") for s in data],
        lon=[s._metadata.get("lon") for s in data],
        lat=[s._metadata.get("lat") for s in data],
        depth=[s._metadata.get("depth", "NA") for s in data],
    )

    table = pd.DataFrame(table).set_index("station_name")
    if verbose:
        print("Collector offerings")
        print(f"{title}: {len(ofrs)} offerings")
    return data, table

We can limit the type of data we want using a `units` and `sos_name` argument. Here are interest in sea level (`water_surface_height_above_reference_datum`) in meters,

ssh, ssh_table = get_coops(
    start=start,
    end=end,
    sos_name="water_surface_height_above_reference_datum",
    units=cf_units.Unit("meters"),
    bbox=bbox,
)

ssh_table.tail()

and wind speed in meters per seconds.

wind_speed, wind_speed_table = get_coops(
    start=start, end=end, sos_name="wind_speed", units=cf_units.Unit("m/s"), bbox=bbox,
)

wind_speed_table.tail()

We only want the stations were we have both sea level and wind speed, so let's try to find a set where that is true.

common = set(ssh_table["station_code"]).intersection(wind_speed_table["station_code"])

ssh_obs, win_obs = [], []

for station in common:
    ssh_obs.extend([obs for obs in ssh if obs._metadata["station_code"] == station])
    win_obs.extend(
        [obs for obs in wind_speed if obs._metadata["station_code"] == station]
    )

Finally we can now interpolate all the records to a 15 min. Most of them are original in 6 min, which is too dense for plotting.

index = pd.date_range(
    start=start.replace(tzinfo=None), end=end.replace(tzinfo=None), freq="15min"
)

ssh_observations = []
for series in ssh_obs:
    _metadata = series._metadata
    series.index = series.index.tz_localize(None)
    obs = series.reindex(index=index, limit=1, method="nearest")
    obs._metadata = _metadata
    obs.name = _metadata["station_name"]
    ssh_observations.append(obs)

winds_observations = []
for series in win_obs:
    _metadata = series._metadata
    series.index = series.index.tz_localize(None)
    obs = series.reindex(index=index, limit=1, method="nearest")
    obs._metadata = _metadata
    obs.name = _metadata["station_name"]
    winds_observations.append(obs)

Now that we have the data all that is left to do is to create interactive [Bokeh plots](https://bokeh.pydata.org/en/latest/),

from bokeh.embed import file_html
from bokeh.models import HoverTool, LinearAxis, Range1d
from bokeh.plotting import figure
from bokeh.resources import CDN
from folium import IFrame

# Plot defaults.
tools = "pan,box_zoom,reset"
width, height = 750, 250

def make_plot(ssh, wind):
    p = figure(
        toolbar_location="above",
        x_axis_type="datetime",
        width=width,
        height=height,
        tools=tools,
        title=ssh.name,
    )

    p.yaxis.axis_label = "wind speed (m/s)"
    l0 = p.line(
        x=wind.index,
        y=wind.values,
        line_width=5,
        line_cap="round",
        alpha=0.5,
        line_join="round",
        legend="wind speed (m/s)",
        color="#9900cc",
    )

    p.extra_y_ranges = {}
    p.extra_y_ranges["y2"] = Range1d(start=-1, end=3.5)
    p.add_layout(LinearAxis(y_range_name="y2", axis_label="ssh (m)"), "right")

    l1 = p.line(
        x=ssh.index,
        y=ssh.values,
        line_width=5,
        line_cap="round",
        line_join="round",
        legend="ssh (m)",
        color="#0000ff",
        alpha=0.5,
        y_range_name="y2",
    )

    p.legend.location = "top_left"
    p.add_tools(
        HoverTool(tooltips=[("wind speed (m/s)", "@y"),], renderers=[l0]),
        HoverTool(tooltips=[("ssh (m)", "@y"),], renderers=[l1]),
    )
    return p

add the plots to a [folium map](https://python-visualization.github.io/folium/) marker,

def make_marker(p, location, fname):
    html = file_html(p, CDN, fname)
    iframe = IFrame(html, width=width + 45, height=height + 80)

    popup = folium.Popup(iframe, max_width=2650)
    icon = folium.Icon(color="green", icon="stats")
    marker = folium.Marker(location=location, popup=popup, icon=icon)
    return marker

and finally the map itself where we will show all the data we found.

import folium
from folium.plugins import Fullscreen, MarkerCluster
from ioos_tools.ioos import get_coordinates

lon = track.centroid.x
lat = track.centroid.y

m = folium.Map(location=[lat, lon], tiles="OpenStreetMap", zoom_start=4)

Fullscreen(position="topright", force_separate_button=True).add_to(m)

marker_cluster0 = MarkerCluster(name="Observations")
marker_cluster0.add_to(m)

We can color code the hurricane state in the track.

colors = {
    "LO": "lightyellow",
    "EX": "yellow",
    "TD": "yellow",
    "TS": "orange",
    "HU": "red",
}


def style_function(feature):
    return {
        "fillOpacity": 0,
        "color": "black",
        "stroke": 1,
        "weight": 0.5,
        "opacity": 0.2,
    }


for date, row in pts.iterrows():
    storm_type = row["STORMTYPE"]
    location = row["LAT"], row["LON"]
    popup = f"{date}<br>{storm_type}"
    folium.CircleMarker(
        location=location, radius=10, fill=True, color=colors[storm_type], popup=popup,
    ).add_to(m)

Add the track and markers.

for ssh, wind in zip(ssh_observations, winds_observations):
    fname = ssh._metadata["station_code"]
    location = ssh._metadata["lat"], ssh._metadata["lon"]
    p = make_plot(ssh, wind)
    marker = make_marker(p, location=location, fname=fname)
    marker.add_to(marker_cluster0)

folium.LayerControl().add_to(m)

p = folium.PolyLine(get_coordinates(bbox), color="#009933", weight=1, opacity=0.2)

p.add_to(m)

And display the final map!

def embed_map(m):
    from IPython.display import HTML

    m.save("index.html")
    with open("index.html") as f:
        html = f.read()

    iframe = '<iframe srcdoc="{srcdoc}" style="width: 100%; height: 750px; border: none"></iframe>'
    srcdoc = html.replace('"', "&quot;")
    return HTML(iframe.format(srcdoc=srcdoc))


embed_map(m)