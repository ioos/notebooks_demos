# Using r-obistools and r-obis to explore the OBIS database


The [Ocean Biogeographic Information System (OBIS)](http://www.iobis.org) is an open-access data and information system for marine biodiversity for science, conservation and sustainable development.

In this example we will use R libraries [`obistools`](https://iobis.github.io/obistools) and [`robis`](https://iobis.github.io/robis) to search data regarding marine turtles occurrence in the South Atlantic Ocean.

Let's start by loading the R-to-Python extension and check the database for the 7 known species of marine turtles found in the world's oceans.

%load_ext rpy2.ipython

%%R -o matches

library(obistools)


species <- c(
    'Caretta caretta',
    'Chelonia mydas',
    'Dermochelys coriacea',
    'Eretmochelys imbricata',
    'Lepidochelys kempii',
    'Lepidochelys olivacea',
    'Natator depressa'
)

matches = match_taxa(species, ask=FALSE)

matches

We got a nice DataFrame back with records for all 7 species of turtles and their corresponding `ID` in the database.

Now let us try to obtain the occurrence data for the South Atlantic. We will need a vector geometry for the ocean basin in the [well-known test (WKT)](https://en.wikipedia.org/wiki/Well-known_text) format to feed into the `robis` `occurrence` function.

In this example we converted a South Atlantic shapefile to WKT with geopandas, but one can also obtain geometries by simply drawing them on a map with [iobis maptool](http://iobis.org/maptool).

import geopandas

gdf = geopandas.read_file("data/oceans.shp")

sa = gdf.loc[gdf["Oceans"] == "South Atlantic Ocean"]["geometry"].loc[0]

atlantic = sa.to_wkt()

%%R -o turtles -i atlantic
library(robis)


turtles = occurrence(
    species,
    geometry=atlantic,
)

names(turtles)

set(turtles["scientificName"])

Note that there are no occurrences for *Natator depressa* (Flatback sea turtle) in the South Atlantic.
The Flatback sea turtle can only be found in the waters around the Australian continental shelf.


With `ggplot2` we can quickly put together a of occurrences over time.

%%R

turtles$year <- as.numeric(format(as.Date(turtles$eventDate), "%Y"))
table(turtles$year)

library(ggplot2)

ggplot() +
 geom_histogram(
     data=turtles,
     aes(x=year, fill=scientificName),
     binwidth=5) +
 scale_fill_brewer(palette='Paired')

One would guess that the 2010 count increase would be due to an increase in the sampling effort, but the drop around 2010 seems troublesome. It can be a real threat to these species, or the observation efforts were defunded.


To explore this dataset further we can make use of the `obistools`' R package. `obistools` has many visualization and quality control routines built-in. Here is an example on how to use `plot_map` to quickly visualize the data on a geographic context.

%%R

library(dplyr)

coriacea <- turtles %>% filter(species=='Dermochelys coriacea')
plot_map(coriacea, zoom=TRUE)

However, if we want to create a slightly more elaborate map with clusters and informative pop-ups, can use the python library `folium`.instead.

import folium
from pandas import DataFrame


def filter_df(df):
    return df[["lifestage", "institutionCode", "individualCount", "sex", "eventDate"]]


def make_popup(row):
    classes = "table table-striped table-hover table-condensed table-responsive"
    html = DataFrame(row).to_html(classes=classes)
    return folium.Popup(html)


def make_marker(row, popup=None):
    location = row["decimalLatitude"], row["decimalLongitude"]
    return folium.Marker(location=location, popup=popup)

from folium.plugins import MarkerCluster

species_found = sorted(set(turtles["scientificName"]))

clusters = {s: MarkerCluster() for s in species_found}
groups = {s: folium.FeatureGroup(name=s) for s in species_found}

m = folium.Map()

for turtle in species_found:
    df = turtles.loc[turtles["scientificName"] == turtle]
    for k, row in df.iterrows():
        popup = make_popup(filter_df(row))
        make_marker(row, popup=popup).add_to(clusters[turtle])
    clusters[turtle].add_to(groups[turtle])
    groups[turtle].add_to(m)


m.fit_bounds(m.get_bounds())
folium.LayerControl().add_to(m)

def embed_map(m):
    from IPython.display import HTML

    m.save("index.html")
    with open("index.html") as f:
        html = f.read()

    iframe = '<iframe srcdoc="{srcdoc}" style="width: 100%; height: 750px; border: none"></iframe>'
    srcdoc = html.replace('"', "&quot;")
    return HTML(iframe.format(srcdoc=srcdoc))


embed_map(m)

We can get fancy and use shapely to "merge" the points that are on the ocean and get an idea of migrations routes.

%%R -o land

land <- check_onland(turtles)

plot_map(land, zoom=TRUE)

First let's remove the entries that are on land.

turtles.set_index("id", inplace=True)
land.set_index("id", inplace=True)
mask = turtles.index.isin(land.index)
ocean = turtles[~mask]

Now we can use shapely's buffer to "connect" the points that are close to each other to visualize a possible migration path.

from palettable.cartocolors.qualitative import Bold_6
from shapely.geometry import MultiPoint

colors = {s: c for s, c in zip(species_found, Bold_6.hex_colors)}
style_function = lambda color: (
    lambda feature: dict(color=color, weight=2, opacity=0.6)
)

m = folium.Map()

for turtle in species_found:
    df = ocean.loc[ocean["scientificName"] == turtle]
    positions = MultiPoint(
        list(zip(df["decimalLongitude"].values, df["decimalLatitude"].values))
    ).buffer(distance=2)
    folium.GeoJson(
        positions.__geo_interface__,
        name=turtle,
        tooltip=turtle,
        style_function=style_function(color=colors[turtle]),
    ).add_to(m)

m.fit_bounds(m.get_bounds())
folium.LayerControl().add_to(m)

m

One interesting feature of this map is *Dermochelys coriacea*'s migration between Brazilian and African shores.

More information on [*Dermochelys coriacea*](http://www.iucnredlist.org/details/6494/0) and the other Sea Turtles can be found in the species [IUCN red list](http://www.iucnredlist.org).