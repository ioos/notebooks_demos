# Calling R libraries from Python

In this example we will explore the **Coral Reef Evaluation and Monitoring Project (CREMP)** data available in the **Gulf of Mexico Coastal Ocean Observing System (GCOOS)** ERDDAP server.

To access the server we will use the [`rerddap`](https://github.com/ropensci/rerddap) library and export the data to Python for easier plotting.

The first step is to load the `rpy2` extension that will allow us to use the `R` libraries.

%load_ext rpy2.ipython

The first line below has a `%%R` to make it an `R` cell. The code below specify the `GCOOS` server and fetches the data information for the [`cremp_fk_v2_1996`](http://gcoos4.tamu.edu:8080/erddap/tabledap/cremp_fk_v2_1996.html) dataset.

For more information on `rerddap` please see [https://rmendels.github.io/Using_rerddap.nb.html](https://rmendels.github.io/Using_rerddap.nb.html).

%%R

library('rerddap')

url <- 'http://gcoos4.tamu.edu:8080/erddap/'
data_info <- rerddap::info('cremp_fk_1996_v20', url=url)

data_info

By inspecting the information above we can find the variables available in the dateset and use  the `tabledap` function to download them.

Note that the `%%R -o rdf` will export the `rdf` variable back to the Python workspace.

%%R -o rdf

fields <- c(
    'Samples',
    'depth',
    'time',
    'longitude',
    'latitude',
    'scientificName',
    'habitat',
    'genus',
    'quantificationValue'
)

rdf <- tabledap(
    data_info,
    fields=fields,
    url=url
)

Now we need to export the `R` `DataFrame` to a `pandas` objects and ensure that all numeric types are numbers and not strings.

import pandas as pd

from rpy2.robjects import pandas2ri

pandas2ri.activate()
df = pandas2ri.ri2py_dataframe(rdf)

cols = ["longitude", "latitude", "depth", "quantificationValue"]
df[cols] = df[cols].apply(pd.to_numeric)

df.head()

We can navigate to ERDDAP's [info page](http://gcoos4.tamu.edu:8080/erddap/info/cremp_fk_v2_1996/index.html) to find the variables description. Let's check what is `quantificationValue`:

    The is value of the derived information product, such as the numerical value for biomass. This term does not include units. Mean number of observed fish per species for 5 Minutes

We can see that `quantificationValue` has a lot of zero values,
let's remove that first to plot the data positions only where something was found.

# Filter invalid values (-999).

cremp_1996 = df.loc[df["quantificationValue"] >= 0]
cremp_1996.head()

What is the most common `genus` of Coral observed?

avg = cremp_1996.groupby("genus").mean()

avg

`rerddap`'s info request does not have enough metadata about the variables to explain the blank, and most abundant, `genus`. [Checking the sever](http://gcoos4.tamu.edu:8080/erddap/tabledap/cremp_fk_v2_1996.html) did not help figure that out. We'll remove that for now to deal with only those that are identified.

cremp_1996 = cremp_1996.loc[cremp_1996["genus"] != ""]

There are also many `genus` with zero biomass count. In this example we'll choose to do a biased analysis of occurrence and eliminate those where nothing was observed.

# Filter zero values (nothing was observed).

cremp_1996 = cremp_1996.loc[cremp_1996["quantificationValue"] > 0]

Now we can check the `quantificationValue` average by `genus`.

%matplotlib inline

avg = cremp_1996.groupby("genus").mean()  # re-compute the "biased" average.
ax = avg["quantificationValue"].plot(kind="bar")

and `habitat`.

ax = cremp_1996.groupby("habitat").mean()["quantificationValue"].plot(kind="bar")

It seems the most of the biomass was found around the `Dendrogyra` genus in Patch Reef habitats.
But where are those Coral Reefs? How is the distribution of top three species with more biomass around them?
With a `pandas` `DataFrame` it is easy to group the data by location and count the `genus` occurrence based on it.

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
from cartopy.mpl.ticker import LatitudeFormatter, LongitudeFormatter


def make_plot():
    bbox = [-82, -80, 24, 26]
    projection = ccrs.PlateCarree()

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(projection=projection))

    ax.set_extent(bbox)

    land = cfeature.NaturalEarthFeature(
        "physical", "land", "10m", edgecolor="face", facecolor=[0.85] * 3
    )

    ax.add_feature(land, zorder=0)
    ax.coastlines("10m", zorder=1)

    ax.set_xticks(np.linspace(bbox[0], bbox[1], 3), crs=projection)
    ax.set_yticks(np.linspace(bbox[2], bbox[3], 3), crs=projection)
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    return fig, ax

count = (
    cremp_1996.loc[cremp_1996["genus"] == "Acropora"]
    .groupby(["longitude", "latitude"])
    .count()
    .reset_index()
)


fig, ax = make_plot()
c = ax.scatter(
    count["longitude"],
    count["latitude"],
    s=200,
    c=count["genus"],
    alpha=0.5,
    cmap=plt.cm.get_cmap("viridis_r", 6),
    zorder=3,
)
cbar = fig.colorbar(c, shrink=0.75, extend="both")
cbar.ax.set_ylabel("Genus occurrence count")
ax.set_title("Acropora")

count = (
    cremp_1996.loc[cremp_1996["genus"] == "Dendrogyra"]
    .groupby(["longitude", "latitude"])
    .count()
    .reset_index()
)


fig, ax = make_plot()
c = ax.scatter(
    count["longitude"],
    count["latitude"],
    s=200,
    c=count["genus"],
    alpha=0.5,
    cmap=plt.cm.get_cmap("viridis_r", 6),
    zorder=3,
)
cbar = fig.colorbar(c, shrink=0.75, extend="both")
cbar.ax.set_ylabel("Genus occurrence count")
ax.set_title("Dendrogyra")

count = (
    cremp_1996.loc[cremp_1996["genus"] == "Orbicella"]
    .groupby(["longitude", "latitude"])
    .count()
    .reset_index()
)


fig, ax = make_plot()
c = ax.scatter(
    count["longitude"],
    count["latitude"],
    s=200,
    c=count["genus"],
    alpha=0.5,
    cmap=plt.cm.get_cmap("viridis_r", 6),
    zorder=3,
)
cbar = fig.colorbar(c, shrink=0.75, extend="both")
cbar.ax.set_ylabel("Genus occurrence count")
ax.set_title("Orbicella")

This demonstration showed the power of mixing `Python` and `R` to reduce developer time and allow the research to focus on the data and not the programming language.