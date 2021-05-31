#!/usr/bin/env python
# coding: utf-8

# # IOOS GTS Statistics
# 
# The Global Telecommunication System (GTS) is a coordinated effort for rapid distribution of observations.
# The GTS monthly reports show the number of messages released to GTS for each station.
# The reports contain the following fields:
# 
# - location ID: Identifier that station messages are released under to the GTS;
# - region: Designated IOOS Regional Association (only for IOOS regional report);
# - sponsor: Organization that owns and maintains the station;
# - Met: Total number of met messages released to the GTS
# - Wave: Total number of wave messages released to the GTS
# 
# In this notebook we will explore the statistics of the messages IOOS is releasing to GTS.
# 
# The first step is to download the data. We will use an ERDDAP server that [hosts the CSV files](https://ferret.pmel.noaa.gov/generic/erddap/files/ioos_obs_counts/) with the ingest data.

# In[1]:


from datetime import date

from erddapy import ERDDAP

server = "http://osmc.noaa.gov/erddap"
e = ERDDAP(server=server, protocol="tabledap")

e.dataset_id = "ioos_obs_counts"
e.variables = ["time", "locationID", "region", "sponsor", "met", "wave"]
e.constraints = {
    "time>=": "2019-09",
    "time<": "2020-11",
}


# In[2]:


df = e.to_pandas(parse_dates=True)

df["locationID"] = df["locationID"].str.lower()

df.tail()


# The table has all the ingest data from 2019-01-01 to 2020-06-01. We can now explore it grouping the data by IOOS Regional Association (RA).

# In[3]:


groups = df.groupby("region")

ax = groups.sum().plot(kind="bar", figsize=(11, 3.75))
ax.yaxis.get_major_formatter().set_scientific(False)
ax.set_ylabel("# observations");


# Let us check the monthly sum of data released both for individuak met and wave and the totdals.

# In[4]:


import pandas as pd

df["time (UTC)"] = pd.to_datetime(df["time (UTC)"])
# Remove time-zone info for easier plotting, it is all UTC.
df["time (UTC)"] = df["time (UTC)"].dt.tz_localize(None)

groups = df.groupby(pd.Grouper(key="time (UTC)", freq="M"))


# We can create a table of observations per month,

# In[5]:


s = groups.sum()
totals = s.assign(total=s["met"] + s["wave"])
totals.index = totals.index.to_period("M")

totals


# and visualize it in a bar plot.

# In[6]:


get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(11, 3.75))

s.plot(ax=ax, kind="bar")
ax.set_xticklabels(
    labels=s.index.to_series().dt.strftime("%Y-%b"),
    rotation=70,
    rotation_mode="anchor",
    ha="right",
)
ax.yaxis.get_major_formatter().set_scientific(False)
ax.set_ylabel("# observations")


# Those plots are interesting to understand the RAs role in the GTS ingest and how much data is being released over time. It would be nice to see those per buoy on a map.
# 
# For that we need to get the position of the NDBC buoys. Let's get a table of all the buoys and match with what we have in the GTS data.

# In[7]:


import xml.etree.ElementTree as et

import pandas as pd
import requests


def make_ndbc_table():
    url = "https://www.ndbc.noaa.gov/activestations.xml"
    with requests.get(url) as r:
        elems = et.fromstring(r.content)
    df = pd.DataFrame([elem.attrib for elem in list(elems)])
    df["id"] = df["id"].str.lower()
    return df.set_index("id")


buoys = make_ndbc_table()
buoys["lon"] = buoys["lon"].astype(float)
buoys["lat"] = buoys["lat"].astype(float)

buoys.head()


# For simplificty we will plot the total of observations per buoys.

# In[8]:


groups = df.groupby("locationID")
location_sum = groups.sum()


# In[9]:


buoys = buoys.T

extra_cols = pd.DataFrame({k: buoys.get(k) for k, row in location_sum.iterrows()}).T
extra_cols = extra_cols[["lat", "lon", "type", "pgm", "name"]]

map_df = pd.concat([location_sum, extra_cols], axis=1)
map_df = map_df.loc[map_df["met"] + map_df["wave"] > 0]


# And now we can overlay an HTML table with the buoy information and ingest data totals.

# In[10]:


from ipyleaflet import AwesomeIcon, Marker, Map, LegendControl, FullScreenControl, Popup
from ipywidgets import HTML


m = Map(center=(35, -95), zoom=4)
m.add_control(FullScreenControl())

legend = LegendControl(
    {
        "wave": "#FF0000",
        "met": "#FFA500",
        "both": "#008000"
    },
    name="GTS",
    position="bottomright",
)
m.add_control(legend)


def make_popup(row):
    classes = "table table-striped table-hover table-condensed table-responsive"
    return pd.DataFrame(row[["met", "wave", "type", "name", "pgm"]]).to_html(
        classes=classes
    )

for k, row in map_df.iterrows():
    if (row["met"] + row["wave"]) > 0:
        location = row["lat"], row["lon"]
        if row["met"] == 0:
            color = "red"
        elif row["wave"] == 0:
            color = "orange"
        else:
            color = "green"
        marker = Marker(
            draggable=False,
            icon=AwesomeIcon(name="life-ring", marker_color=color),
            location=location,
        )
        msg = HTML()
        msg.value = make_popup(row)
        marker.popup = msg
        m.add_layer(marker)
m

