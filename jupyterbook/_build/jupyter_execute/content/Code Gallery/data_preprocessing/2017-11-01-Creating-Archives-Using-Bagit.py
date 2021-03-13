# Using BagIt to tag oceanographic data


[`BagIt`](https://en.wikipedia.org/wiki/BagIt) is a packaging format that supports storage of arbitrary digital content. The "bag" consists of arbitrary content and "tags," the metadata files. `BagIt` packages can be used to facilitate data sharing with federal archive centers - thus ensuring digital preservation of oceanographic datasets within IOOS and its regional associations. NOAA NCEI supports reading from a Web Accessible Folder (WAF) containing bagit archives. For an example please see: http://ncei.axiomdatascience.com/cencoos/


On this notebook we will use the [python interface](http://libraryofcongress.github.io/bagit-python) for `BagIt` to create a "bag" of a time-series profile data. First let us load our data from a comma separated values file (`CSV`).

import os

import pandas as pd

fname = os.path.join("data", "dsg", "timeseriesProfile.csv")

df = pd.read_csv(fname, parse_dates=["time"])
df.head()

Instead of "bagging" the `CSV` file we will use this create a metadata rich netCDF file.

We can convert the table to a `DSG`, Discrete Sampling Geometry, using `pocean.dsg`. The first thing we need to do is to create a mapping from the data column names to the netCDF `axes`.

axes = {"t": "time", "x": "lon", "y": "lat", "z": "depth"}

Now we can create a [Orthogonal Multidimensional Timeseries Profile](http://cfconventions.org/cf-conventions/v1.6.0/cf-conventions.html#_orthogonal_multidimensional_array_representation_of_time_series) object...

import os
import tempfile

from pocean.dsg import OrthogonalMultidimensionalTimeseriesProfile as omtsp

output_fp, output = tempfile.mkstemp()
os.close(output_fp)

ncd = omtsp.from_dataframe(df.reset_index(), output=output, axes=axes, mode="a")

... And add some extra metadata before we close the file.

naming_authority = "ioos"
st_id = "Station1"

ncd.naming_authority = naming_authority
ncd.id = st_id
print(ncd)
ncd.close()

Time to create the archive for the file with `BagIt`. We have to create a folder for the bag.

temp_bagit_folder = tempfile.mkdtemp()
temp_data_folder = os.path.join(temp_bagit_folder, "data")

Now we can create the bag and copy the netCDF file to a `data` sub-folder.

import shutil

import bagit

bag = bagit.make_bag(temp_bagit_folder, checksum=["sha256"])

shutil.copy2(output, temp_data_folder + "/parameter1.nc")

Last, but not least, we have to set bag metadata and update the existing bag with it.

urn = "urn:ioos:station:{naming_authority}:{st_id}".format(
    naming_authority=naming_authority, st_id=st_id
)

bag_meta = {
    "Bag-Count": "1 of 1",
    "Bag-Group-Identifier": "ioos_bagit_testing",
    "Contact-Name": "Kyle Wilcox",
    "Contact-Phone": "907-230-0304",
    "Contact-Email": "axiom+ncei@axiomdatascience.com",
    "External-Identifier": urn,
    "External-Description": "Sensor data from station {}".format(urn),
    "Internal-Sender-Identifier": urn,
    "Internal-Sender-Description": "Station - URN:{}".format(urn),
    "Organization-address": "1016 W 6th Ave, Ste. 105, Anchorage, AK 99501, USA",
    "Source-Organization": "Axiom Data Science",
}


bag.info.update(bag_meta)
bag.save(manifests=True, processes=4)

That is it! Simple and efficient!!

The cell below illustrates the bag directory tree.

(Note that the commands below will not work on Windows and some \*nix systems may require the installation of the command `tree`, however, they are only need for this demonstration.)

!tree $temp_bagit_folder
!cat $temp_bagit_folder/manifest-sha256.txt

We can add more files to the bag as needed.

shutil.copy2(output, temp_data_folder + "/parameter2.nc")
shutil.copy2(output, temp_data_folder + "/parameter3.nc")
shutil.copy2(output, temp_data_folder + "/parameter4.nc")

bag.save(manifests=True, processes=4)

!tree $temp_bagit_folder
!cat $temp_bagit_folder/manifest-sha256.txt