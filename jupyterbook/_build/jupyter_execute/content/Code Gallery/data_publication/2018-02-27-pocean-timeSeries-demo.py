#!/usr/bin/env python
# coding: utf-8

# # Creating a CF-1.6 timeSeries using pocean
# 
# 
# IOOS recommends to data providers that their netCDF files follow the CF-1.6 standard. In this notebook we will create a [CF-1.6 compliant](http://cfconventions.org/latest.html) file that follows file that follows the [Discrete Sampling Geometries](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/build/ch09.html) (DSG) of a `timeSeries` from a pandas DataFrame.
# 
# The `pocean` module can handle all the DSGs described in the CF-1.6 document: `point`, `timeSeries`, `trajectory`, `profile`, `timeSeriesProfile`, and `trajectoryProfile`. These DSGs array may be represented in the netCDF file as:
# 
# - **orthogonal multidimensional**: when the coordinates along the element axis of the features are identical;
# - **incomplete multidimensional**: when the features within a collection do not all have the same number but space is not an issue and using longest feature to all features is convenient;
# - **contiguous ragged**: can be used if the size of each feature is known;
# - **indexed ragged**: stores the features interleaved along the sample dimension in the data variable.
# 
# Here we will use the orthogonal multidimensional array to represent time-series data from am hypothetical current meter. We'll use fake data for this example for convenience.
# 
# Our fake data represents a current meter located at 10 meters depth collected last week.

# In[1]:


from datetime import datetime, timedelta

import numpy as np
import pandas as pd

x = np.arange(100, 110, 0.1)
start = datetime.now() - timedelta(days=7)

df = pd.DataFrame(
    {
        "time": [start + timedelta(days=n) for n in range(len(x))],
        "longitude": -48.6256,
        "latitude": -27.5717,
        "depth": 10,
        "u": np.sin(x),
        "v": np.cos(x),
        "station": "fake buoy",
    }
)


df.tail()


# Let's take a look at our fake data.

# In[2]:


get_ipython().run_line_magic('matplotlib', 'inline')


import matplotlib.pyplot as plt
from oceans.plotting import stick_plot

q = stick_plot([t.to_pydatetime() for t in df["time"]], df["u"], df["v"])

ref = 1
qk = plt.quiverkey(
    q, 0.1, 0.85, ref, f"{ref} m s$^{-1}$", labelpos="N", coordinates="axes"
)

plt.xticks(rotation=70)


# `pocean.dsg` is relatively simple to use. The user must provide a DataFrame, like the one above, and a dictionary of attributes that maps to the data and adhere to the DSG conventions desired. 
# 
# Because we want the file to work seamlessly with ERDDAP we also added some ERDDAP specific attributes like `cdm_timeseries_variables`, and `subsetVariables`.

# In[3]:


attributes = {
    "global": {
        "title": "Fake mooring",
        "summary": "Vector current meter ADCP @ 10 m",
        "institution": "Restaurant at the end of the universe",
        "cdm_timeseries_variables": "station",
        "subsetVariables": "depth",
    },
    "longitude": {"units": "degrees_east", "standard_name": "longitude",},
    "latitude": {"units": "degrees_north", "standard_name": "latitude",},
    "z": {"units": "m", "standard_name": "depth", "positive": "down",},
    "u": {"units": "m/s", "standard_name": "eastward_sea_water_velocity",},
    "v": {"units": "m/s", "standard_name": "northward_sea_water_velocity",},
    "station": {"cf_role": "timeseries_id"},
}


# We also need to map the our data axes to [`pocean`'s defaults](https://github.com/pyoceans/pocean-core/blob/master/pocean/utils.py#L50-L59). This step is not needed if the data axes are already named like the default ones.

# In[4]:


axes = {"t": "time", "x": "longitude", "y": "latitude", "z": "depth"}


# In[5]:


from pocean.dsg.timeseries.om import OrthogonalMultidimensionalTimeseries
from pocean.utils import downcast_dataframe

df = downcast_dataframe(df)  # safely cast depth np.int64 to np.int32
dsg = OrthogonalMultidimensionalTimeseries.from_dataframe(
    df, output="fake_buoy.nc", attributes=attributes, axes=axes,
)


# The `OrthogonalMultidimensionalTimeseries` saves the DataFrame into a CF-1.6 TimeSeries DSG.

# In[6]:


get_ipython().system('ncdump -h fake_buoy.nc')


#  It also outputs the dsg object for inspection. Let us check a few things to see if our objects was created as expected. (Note that some of the metadata was "free" due t the built-in defaults in `pocean`.

# In[7]:


dsg.getncattr("featureType")


# In[8]:


type(dsg)


# In addition to standard `netCDF4-python` object `.variables` method `pocean`'s DSGs provides an "categorized" version of the variables in the `data_vars`, `ancillary_vars`, and the DSG axes methods.

# In[9]:


[(v.standard_name) for v in dsg.data_vars()]


# In[10]:


dsg.axes("T")


# In[11]:


dsg.axes("Z")


# In[12]:


dsg.vatts("station")


# In[13]:


dsg["station"][:]


# In[14]:


dsg.vatts("u")


# We can easily round-trip back to the pandas DataFrame object.

# In[15]:


dsg.to_dataframe().head()


# For more information on `pocean` please check the [API docs](https://pyoceans.github.io/pocean-core/docs/api/pocean.html).
