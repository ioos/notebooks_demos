#!/usr/bin/env python
# coding: utf-8

# # Using r-obistools and r-obis to explore the OBIS database
# 
# 
# The [Ocean Biogeographic Information System (OBIS)](http://www.iobis.org) is an open-access data and information system for marine biodiversity for science, conservation and sustainable development.
# 
# In this example we will use R libraries [`obistools`](https://iobis.github.io/obistools) and [`robis`](https://iobis.github.io/robis) to search data regarding marine turtles occurrence in the South Atlantic Ocean.
# 
# Let's start by loading the R-to-Python extension and check the database for the 7 known species of marine turtles found in the world's oceans.

# In[1]:


get_ipython().run_line_magic('load_ext', 'rpy2.ipython')


# In[2]:


get_ipython().run_cell_magic('R', '-o matches', "\nlibrary(obistools)\n\n\nspecies <- c(\n    'Caretta caretta',\n    'Chelonia mydas',\n    'Dermochelys coriacea',\n    'Eretmochelys imbricata',\n    'Lepidochelys kempii',\n    'Lepidochelys olivacea',\n    'Natator depressa'\n)\n\nmatches = match_taxa(species, ask=FALSE)")


# In[3]:


matches


# We got a nice DataFrame back with records for all 7 species of turtles and their corresponding `ID` in the database.
# 
# Now let us try to obtain the occurrence data for the South Atlantic. We will need a vector geometry for the ocean basin in the [well-known test (WKT)](https://en.wikipedia.org/wiki/Well-known_text) format to feed into the `robis` `occurrence` function.
# 
# In this example we converted a South Atlantic shapefile to WKT with geopandas, but one can also obtain geometries by simply drawing them on a map with [iobis maptool](http://iobis.org/maptool).

# In[4]:


import geopandas

gdf = geopandas.read_file("data/oceans.shp")

sa = gdf.loc[gdf["Oceans"] == "South Atlantic Ocean"]["geometry"].loc[0]

atlantic = sa.to_wkt()


# In[5]:


get_ipython().run_cell_magic('R', '-o turtles -i atlantic', 'library(robis)\n\n\nturtles = occurrence(\n    species,\n    geometry=atlantic,\n)\n\nnames(turtles)')


# In[6]:


set(turtles["scientificName"])


# Note that there are no occurrences for *Natator depressa* (Flatback sea turtle) in the South Atlantic.
# The Flatback sea turtle can only be found in the waters around the Australian continental shelf.
# 
# 
# With `ggplot2` we can quickly put together a of occurrences over time.

# In[7]:


get_ipython().run_cell_magic('R', '', '\nturtles$year <- as.numeric(format(as.Date(turtles$eventDate), "%Y"))\ntable(turtles$year)\n\nlibrary(ggplot2)\n\nggplot() +\n geom_histogram(\n     data=turtles,\n     aes(x=year, fill=scientificName),\n     binwidth=5) +\n scale_fill_brewer(palette=\'Paired\')')


# One would guess that the 2010 count increase would be due to an increase in the sampling effort, but the drop around 2010 seems troublesome. It can be a real threat to these species, or the observation efforts were defunded.
# 
# 
# To explore this dataset further we can make use of the `obistools`' R package. `obistools` has many visualization and quality control routines built-in. Here is an example on how to use `plot_map` to quickly visualize the data on a geographic context.

# In[8]:


get_ipython().run_cell_magic('R', '', "\nlibrary(dplyr)\n\ncoriacea <- turtles %>% filter(species=='Dermochelys coriacea')\nplot_map(coriacea, zoom=TRUE)")


# However, if we want to create a slightly more elaborate map with clusters and informative pop-ups, can use the python library `folium`.instead.

# In[9]:


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


# In[10]:


from folium.plugins import MarkerCluster

species_found = sorted(set(turtles["scientificName"]))

clusters = {s: MarkerCluster() for s in species_found}
groups = {s: folium.FeatureGroup(name=s) for s in species_found}


# In[11]:


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


# In[12]:


def embed_map(m):
    from IPython.display import HTML

    m.save("index.html")
    with open("index.html") as f:
        html = f.read()

    iframe = '<iframe srcdoc="{srcdoc}" style="width: 100%; height: 750px; border: none"></iframe>'
    srcdoc = html.replace('"', "&quot;")
    return HTML(iframe.format(srcdoc=srcdoc))


embed_map(m)


# We can get fancy and use shapely to "merge" the points that are on the ocean and get an idea of migrations routes.

# In[13]:


get_ipython().run_cell_magic('R', '-o land', '\nland <- check_onland(turtles)\n\nplot_map(land, zoom=TRUE)')


# First let's remove the entries that are on land.

# In[14]:


turtles.set_index("id", inplace=True)
land.set_index("id", inplace=True)
mask = turtles.index.isin(land.index)
ocean = turtles[~mask]


# Now we can use shapely's buffer to "connect" the points that are close to each other to visualize a possible migration path.

# In[15]:


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


# One interesting feature of this map is *Dermochelys coriacea*'s migration between Brazilian and African shores.
# 
# More information on [*Dermochelys coriacea*](http://www.iucnredlist.org/details/6494/0) and the other Sea Turtles can be found in the species [IUCN red list](http://www.iucnredlist.org).
