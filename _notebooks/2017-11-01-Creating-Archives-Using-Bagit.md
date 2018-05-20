---
title: "Using BagIt to tag oceanographic data"
layout: notebook

---


[`BagIt`](https://en.wikipedia.org/wiki/BagIt) is a packaging format that supports storage of arbitrary digital content. The "bag" consists of arbitrary content and "tags," the metadata files. `BagIt` packages can be used to facilitate data sharing with federal archive centers - thus ensuring digital preservation of oceanographic datasets within IOOS and its regional associations. NOAA NCEI supports reading from a Web Accessible Folder (WAF) containing bagit archives. For an example please see: http://ncei.axiomdatascience.com/cencoos/


On this notebook we will use the [python interface](http://libraryofcongress.github.io/bagit-python) for `BagIt` to create a "bag" of a time-series profile data. First let us load our data from a comma separated values file (`CSV`).

<div class="prompt input_prompt">
In&nbsp;[1]:
</div>

```python
import os
import pandas as pd


fname = os.path.join('data', 'dsg', 'timeseriesProfile.csv')

df = pd.read_csv(fname, parse_dates=['time'])
df.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time</th>
      <th>lon</th>
      <th>lat</th>
      <th>depth</th>
      <th>station</th>
      <th>humidity</th>
      <th>temperature</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1990-01-01 00:00:00</td>
      <td>-76.5</td>
      <td>37.5</td>
      <td>0.0</td>
      <td>Station1</td>
      <td>89.708794</td>
      <td>15.698009</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1990-01-01 00:00:00</td>
      <td>-76.5</td>
      <td>37.5</td>
      <td>10.0</td>
      <td>Station1</td>
      <td>55.789471</td>
      <td>10.916656</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1990-01-01 00:00:00</td>
      <td>-76.5</td>
      <td>37.5</td>
      <td>20.0</td>
      <td>Station1</td>
      <td>50.176994</td>
      <td>15.666663</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1990-01-01 00:00:00</td>
      <td>-76.5</td>
      <td>37.5</td>
      <td>30.0</td>
      <td>Station1</td>
      <td>36.855045</td>
      <td>1.158752</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1990-01-01 01:00:00</td>
      <td>-76.5</td>
      <td>37.5</td>
      <td>0.0</td>
      <td>Station1</td>
      <td>65.016937</td>
      <td>31.059647</td>
    </tr>
  </tbody>
</table>
</div>



Instead of "bagging" the `CSV` file we will use this create a metadata rich netCDF file.

We can convert the table to a `DSG`, Discrete Sampling Geometry, using `pocean.dsg`. The first thing we need to do is to create a mapping from the data column names to the netCDF `axes`.

<div class="prompt input_prompt">
In&nbsp;[2]:
</div>

```python
axes = {
    't': 'time',
    'x': 'lon',
    'y': 'lat',
    'z': 'depth'
}
```

Now we can create a [Orthogonal Multidimensional Timeseries Profile](http://cfconventions.org/cf-conventions/v1.6.0/cf-conventions.html#_orthogonal_multidimensional_array_representation_of_time_series) object...

<div class="prompt input_prompt">
In&nbsp;[3]:
</div>

```python
import os
import tempfile
from pocean.dsg import OrthogonalMultidimensionalTimeseriesProfile as omtsp

output_fp, output = tempfile.mkstemp()
os.close(output_fp)

ncd = omtsp.from_dataframe(
    df.reset_index(),
    output=output,
    axes=axes,
    mode='a'
)
```

... And add some extra metadata before we close the file.

<div class="prompt input_prompt">
In&nbsp;[4]:
</div>

```python
naming_authority = 'ioos'
st_id = 'Station1'

ncd.naming_authority = naming_authority
ncd.id = st_id
print(ncd)
ncd.close()
```
<div class="output_area"><div class="prompt"></div>
<pre>
    <class 'pocean.dsg.timeseriesProfile.om.OrthogonalMultidimensionalTimeseriesProfile'>
    root group (NETCDF4 data model, file format HDF5):
        Conventions: CF-1.6
        date_created: 2017-11-27T15:11:00Z
        featureType: timeSeriesProfile
        cdm_data_type: TimeseriesProfile
        naming_authority: ioos
        id: Station1
        dimensions(sizes): station(1), time(100), depth(4)
        variables(dimensions): <class 'str'> [4mstation[0m(station), float64 [4mlat[0m(station), float64 [4mlon[0m(station), int32 [4mcrs[0m(), float64 [4mtime[0m(time), int32 [4mdepth[0m(depth), int32 [4mindex[0m(time,depth,station), float64 [4mhumidity[0m(time,depth,station), float64 [4mtemperature[0m(time,depth,station)
        groups: 
    

</pre>
</div>
Time to create the archive for the file with `BagIt`. We have to create a folder for the bag.

<div class="prompt input_prompt">
In&nbsp;[5]:
</div>

```python
temp_bagit_folder = tempfile.mkdtemp()
temp_data_folder = os.path.join(temp_bagit_folder, 'data')
```

Now we can create the bag and copy the netCDF file to a `data` sub-folder.

<div class="prompt input_prompt">
In&nbsp;[6]:
</div>

```python
import bagit
import shutil

bag = bagit.make_bag(
    temp_bagit_folder,
    checksum=['sha256']
)

shutil.copy2(output, temp_data_folder + '/parameter1.nc')
```




    '/tmp/tmp5qrdn3qe/data/parameter1.nc'



Last, but not least, we have to set bag metadata and update the existing bag with it.

<div class="prompt input_prompt">
In&nbsp;[7]:
</div>

```python
urn = 'urn:ioos:station:{naming_authority}:{st_id}'.format(
    naming_authority=naming_authority,
    st_id=st_id
)

bag_meta = {
    'Bag-Count': '1 of 1',
    'Bag-Group-Identifier': 'ioos_bagit_testing',
    'Contact-Name': 'Kyle Wilcox',
    'Contact-Phone': '907-230-0304',
    'Contact-Email': 'axiom+ncei@axiomdatascience.com',
    'External-Identifier': urn,
    'External-Description':
        'Sensor data from station {}'.format(urn),
    'Internal-Sender-Identifier': urn,
    'Internal-Sender-Description':
        'Station - URN:{}'.format(urn),
    'Organization-address':
        '1016 W 6th Ave, Ste. 105, Anchorage, AK 99501, USA',
    'Source-Organization': 'Axiom Data Science',
}


bag.info.update(bag_meta)
bag.save(manifests=True, processes=4)
```

That is it! Simple and efficient!!

The cell below illustrates the bag directory tree.

(Note that the commands below will not work on Windows and some \*nix systems may require the installation of the command `tree`, however, they are only need for this demonstration.)

<div class="prompt input_prompt">
In&nbsp;[8]:
</div>

```python
!tree $temp_bagit_folder
!cat $temp_bagit_folder/manifest-sha256.txt
```
<div class="output_area"><div class="prompt"></div>
<pre>
    [01;34m/tmp/tmp5qrdn3qe[00m
    ├── bag-info.txt
    ├── bagit.txt
    ├── [01;34mdata[00m
    │   └── parameter1.nc
    ├── manifest-sha256.txt
    └── tagmanifest-sha256.txt
    
    1 directory, 5 files
    63d47afc3b8b227aac251a234ecbb9cfc6cc01d1dd1aa34c65969fdabf0740f1  data/parameter1.nc

</pre>
</div>
We can add more files to the bag as needed.

<div class="prompt input_prompt">
In&nbsp;[9]:
</div>

```python
shutil.copy2(output, temp_data_folder + '/parameter2.nc')
shutil.copy2(output, temp_data_folder + '/parameter3.nc')
shutil.copy2(output, temp_data_folder + '/parameter4.nc')

bag.save(manifests=True, processes=4)
```

<div class="prompt input_prompt">
In&nbsp;[10]:
</div>

```python
!tree $temp_bagit_folder
!cat $temp_bagit_folder/manifest-sha256.txt
```
<div class="output_area"><div class="prompt"></div>
<pre>
    [01;34m/tmp/tmp5qrdn3qe[00m
    ├── bag-info.txt
    ├── bagit.txt
    ├── [01;34mdata[00m
    │   ├── parameter1.nc
    │   ├── parameter2.nc
    │   ├── parameter3.nc
    │   └── parameter4.nc
    ├── manifest-sha256.txt
    └── tagmanifest-sha256.txt
    
    1 directory, 8 files
    63d47afc3b8b227aac251a234ecbb9cfc6cc01d1dd1aa34c65969fdabf0740f1  data/parameter1.nc
    63d47afc3b8b227aac251a234ecbb9cfc6cc01d1dd1aa34c65969fdabf0740f1  data/parameter2.nc
    63d47afc3b8b227aac251a234ecbb9cfc6cc01d1dd1aa34c65969fdabf0740f1  data/parameter3.nc
    63d47afc3b8b227aac251a234ecbb9cfc6cc01d1dd1aa34c65969fdabf0740f1  data/parameter4.nc

</pre>
</div><br>
Right click and choose Save link as... to
[download](https://raw.githubusercontent.com/ioos/notebooks_demos/master/notebooks/2017-11-01-Creating-Archives-Using-Bagit.ipynb)
this notebook, or click [here](https://beta.mybinder.org/v2/gh/ioos/notebooks_demos/master?filepath=notebooks/2017-11-01-Creating-Archives-Using-Bagit.ipynb) to run a live instance of this notebook.