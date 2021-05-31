#!/usr/bin/env python
# coding: utf-8

# # Aligning Data to Darwin Core - Sampling Event with Measurement or Fact using Python
# 
# This notebook was created for the [IOOS DMAC Code Sprint](https://www.glos.us/code-sprint/) Biological Data Session
# The data in this notebook were created specifically as an example and meant solely to be
# illustrative of the process for aligning data to the biological data standard - [Darwin Core](https://dwc.tdwg.org/).
# These data should not be considered actually occurrences of species and any measurements
# are also contrived. This notebook is meant to provide a step by step process for taking
# original data and aligning it to Darwin Core
# 
# First let's bring in the appropriate libraries to work with the tabular data files and generate the appropriate content for the DarwinCore requirements.

# In[1]:


import csv
import numpy as np
import pandas as pd
import pprint
import pyworms
import uuid


# Now we need to read in the raw data file using [pandas.read_csv()](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html). Here we display the first ten rows of data to give the user an idea of what observations are contained in the [raw file](https://github.com/ioos/notebooks_demos/blob/master/notebooks/data/dwc/raw/MadeUpDataForBiologicalDataTraining.csv).

# In[2]:


file = 'data/dwc/raw/MadeUpDataForBiologicalDataTraining.csv'
df = pd.read_csv(file, header=[0])
df.head()


# First we need to to decide if we will provide an **occurrence only** version of the data or a **sampling event with measurement or facts** version of the data. 
# 
# * **Occurrence only**: 
#   * Easier to create. 
#   * It's only one file to produce. 
#   * However, several pieces of information will be left out if we choose that option. 
# * **sampling event with measurement or fact (mof)**: 
#   * More difficult to create.
#   * composed of several files.
#   * Can capture all of the data in the file creating a lossless version.
# 
# Here we decide to use the **sampling event with measurement or fact (mof)** option to include as much information as we can.
# 
# First let's create the `eventID` and `occurrenceID` in the original file so that information can be reused for all necessary files down the line.

# In[3]:


df['eventID'] = df[['region', 'station', 'transect']].apply(lambda x: '_'.join(x.astype(str)), axis=1)
df['occurrenceID'] = uuid.uuid4()


# We will need to create *three* separate files to comply with the **sampling event** format.
# We'll start with the **event file** but we only need to include the columns that are relevant
# to the event file.

# # Event file

# Let's first make a copy of the DataFrame we pulled in. Only using the data fields of interest for the **event file**.

# In[4]:


event = df[['date', 'lat', 'lon', 'region', 'station', 'transect', 'depth', 'bottom type', 'eventID']].copy()


# Next we need to rename any columns of data to match directly to Darwin Core.

# In[5]:


event['decimalLatitude'] = event['lat']
event['decimalLongitude'] = event['lon']
event['minimumDepthInMeters'] = event['depth']
event['maximumDepthInMeters'] = event['depth']
event['habitat'] = event['bottom type']
event['island'] = event['region']


# We need to convert the date to [ISO format](https://en.wikipedia.org/wiki/ISO_8601) and add any missing, required, fields.

# In[6]:


event['eventDate'] = pd.to_datetime(event['date'],format='%m/%d/%Y')
event['basisOfRecord'] = 'HumanObservation'
event['geodeticDatum'] = 'EPSG:4326 WGS84'


# Then we'll remove any fields that we no longer need to clean things up a bit.

# In[7]:


event.drop(
    columns=['date', 'lat', 'lon', 'region', 'station', 'transect', 'depth', 'bottom type'],
    inplace=True)


# We have too many repeating rows of information. We can pare this down using eventID which
# is a unique identifier for each sampling event in the data.

# In[8]:


event.drop_duplicates(subset='eventID',inplace=True)


# Finally we write out the [event file](https://github.com/ioos/notebooks_demos/blob/master/notebooks/data/dwc/processed/MadeUpData_event.csv). We've printed ten random rows of the DataFrame to give an example of what the resultant file will look like.

# In[9]:


event.to_csv(
   'data/dwc/processed/MadeUpData_event.csv',
   header=True,
   index=False,
   date_format='%Y-%m-%d')

event.sample(n=5).sort_index()


# # Occurrence file
# For creating the **occurrence** file, we start by creating the DataFrame and renaming the fields that align directly with Darwin Core. Then, we'll add the required information that is missing.

# In[10]:


occurrence = df[['scientific name', 'eventID', 'occurrenceID', 'percent cover']].copy()
occurrence['scientificName'] = occurrence['scientific name']
occurrence['occurrenceStatus'] = np.where(occurrence['percent cover'] == 0, 'absent', 'present')


# ## Taxonomic Name Matching
# A requirement for [OBIS](https://obis.org/) is that all scientific names match to the [World Register of
# Marine Species (WoRMS)](http://www.marinespecies.org/) and a `scientificNameID` is included. A `scientificNameID` looks
# like this `urn:lsid:marinespecies.org:taxname:275730` with the last digits after
# the colon being the **WoRMS aphia ID**. We'll need to go out to WoRMS to grab this
# information. So, we create a lookup table of the unique scientific names found in the **occurrence** data we created above.

# In[11]:


lut_worms = pd.DataFrame(
    columns=['scientificName'],
    data=occurrence['scientificName'].unique())


# Next, we add the known columns that we can grab information from [WoRMS](http://www.marinespecies.org/) including the required `scientificNameID` and populate the look up table with empty values for those fields (to initialize the DataFrame for population later).

# In[12]:


headers = ['acceptedname', 'acceptedID', 'scientificNameID', 'kingdom', 'phylum',
           'class', 'order', 'family', 'genus', 'scientificNameAuthorship', 'taxonRank']

for head in headers:
    lut_worms[head] = ''


# Next, we perform a taxonomic lookup using the library [pyworms](https://pyworms.readthedocs.io/en/latest/). Using the function `pyworms.aphiaRecordsByMatchNames()` to collect the information and populate the look up table.
# 
# Here we print the scientific name of the species we are looking up and the matching response from WoRMS with the detailed species information.

# In[13]:


for index, row in lut_worms.iterrows():
    print('\n**Searching for scientific name = %s**' % row['scientificName'])
    resp = pyworms.aphiaRecordsByMatchNames(row['scientificName'])[0][0]
    pprint.pprint(resp)
    lut_worms.loc[index, 'acceptedname'] = resp['valid_name']
    lut_worms.loc[index, 'acceptedID'] = resp['valid_AphiaID']
    lut_worms.loc[index, 'scientificNameID'] = resp['lsid']
    lut_worms.loc[index, 'kingdom'] = resp['kingdom']
    lut_worms.loc[index, 'phylum'] = resp['phylum']
    lut_worms.loc[index, 'class'] = resp['class']
    lut_worms.loc[index, 'order'] = resp['order']
    lut_worms.loc[index, 'family'] = resp['family']
    lut_worms.loc[index, 'genus'] = resp['genus']
    lut_worms.loc[index, 'scientificNameAuthorship'] = resp['authority']
    lut_worms.loc[index, 'taxonRank'] = resp['rank']


# We then merge the lookup table of unique scientific names back into the **occurrence** data. Matching on the field `scientificName`. Then, we remove any unnecessary columns to clean up the DataFrame for writing. 

# In[14]:


occurrence = pd.merge(occurrence, lut_worms, how='left', on='scientificName')

occurrence.drop(
    columns=['scientific name', 'percent cover'],
    inplace=True)


# Finally, we write out the [occurrence file](https://github.com/ioos/notebooks_demos/blob/master/notebooks/data/dwc/processed/MadeUpData_Occurrence.csv). We've printed ten random rows of the DataFrame to give an example of what the resultant file will look like.

# In[15]:


# sort the columns on scientificName
occurrence.sort_values('scientificName', inplace=True)

# reorganize column order to be consistent with R example:
columns = ["scientificName","eventID","occurrenceID","occurrenceStatus","acceptedname","acceptedID",
           "scientificNameID","kingdom","phylum","class","order","family","genus","scientificNameAuthorship",
           "taxonRank"]

occurrence.to_csv(
   "data/dwc/processed/MadeUpData_Occurrence.csv",
   header=True,
   index=False,
   quoting=csv.QUOTE_ALL,
   columns=columns)

occurrence.sample(n=10).sort_index()


# # Measurement Or Fact
# The last file we need to create is the **measurement or fact (mof)** file. The measurement or fact includes measurements/facts about the event (temp, salinity, etc) as well as about the occurrence (percent cover, abundance, weight, length, etc). They are linked to the events using `eventID` and to the occurrences using `occurrenceID`. [Measurements or facts](http://rs.gbif.org/extension/dwc/measurements_or_facts.xml) are any other generic observations that are associated with resources that are described using Darwin Core (eg. water temperature observations). See https://dwc.tdwg.org/rdf/#2-implementation-guide for more information.
# 
# For the various `TypeID` fields (eg. `measurementTypeID`) include URI's from the [BODC NERC vocabulary](https://www.bodc.ac.uk/resources/vocabularies/vocabulary_search/) or other nearly permanent source, where possible. For example, [*water temperature*](http://vocab.nerc.ac.uk/collection/P25/current/WTEMP/) in the BODC NER vocabulary, the URI is `http://vocab.nerc.ac.uk/collection/P25/current/WTEMP/`.
# 
# We then populate the appropriate fields with the information we have available. The `measurementValue` field is populated with the observed values of the measurement described in the `measurementType` and `measurementUnit` field.
# 
# Below we walk through creating three independent DataFrames for *temperature*, *rugosity*, and *percent cover*. Populating each DataFrame with all of the information we have available and removing duplicative fields. We finally concatenate all the **measurements or facts** together into one DataFrame.

# In[16]:


temperature = df[['eventID', 'temperature', 'date']].copy()
temperature['occurrenceID'] = ''
temperature['measurementType'] = 'temperature'
temperature['measurementTypeID'] = 'http://vocab.nerc.ac.uk/collection/P25/current/WTEMP/'
temperature['measurementValue'] = temperature['temperature']
temperature['measurementUnit'] = 'Celsius'
temperature['measurementUnitID'] = 'http://vocab.nerc.ac.uk/collection/P06/current/UPAA/'
temperature['measurementAccuracy'] = 3
temperature['measurementDeterminedDate'] = pd.to_datetime(temperature['date'],format='%m/%d/%Y')
temperature['measurementMethod'] = ''
temperature.drop(columns=['temperature', 'date'],inplace=True)

rugosity = df[['eventID', 'rugosity', 'date']].copy()
rugosity['occurrenceID'] = ''
rugosity['measurementType'] = 'rugosity'
rugosity['measurementTypeID'] = ''
rugosity['measurementValue'] = rugosity['rugosity'].map('{:,.6f}'.format)
rugosity['measurementUnit'] = ''
rugosity['measurementUnitID'] = ''
rugosity['measurementAccuracy'] = ''
rugosity['measurementDeterminedDate'] = pd.to_datetime(rugosity['date'],format='%m/%d/%Y')
rugosity['measurementMethod'] = ''
rugosity.drop(columns=['rugosity', 'date'],inplace=True)

percent_cover = df[['eventID', 'occurrenceID', 'percent cover', 'date']].copy()
percent_cover['measurementType'] = 'Percent Cover'
percent_cover['measurementTypeID'] = 'http://vocab.nerc.ac.uk/collection/P01/current/SDBIOL10/'
percent_cover['measurementValue'] = percent_cover['percent cover']
percent_cover['measurementUnit'] = 'Percent/100m^2'
percent_cover['measurementUnitID'] = ''
percent_cover['measurementAccuracy'] = 5
percent_cover['measurementDeterminedDate'] = pd.to_datetime(percent_cover['date'],format='%m/%d/%Y')
percent_cover['measurementMethod'] = ''
percent_cover.drop(columns=['percent cover', 'date'],inplace=True)

measurementorfact = pd.concat([temperature, rugosity, percent_cover])


# Finally, we write the [measurement or fact file](https://github.com/ioos/notebooks_demos/blob/master/notebooks/data/dwc/processed/MadeUpData_mof.csv). We've printed ten random rows of the DataFrame to give an example of what the resultant file will look like.

# In[17]:


measurementorfact.to_csv('data/dwc/processed/MadeUpData_mof.csv',
                         index=False,
                         header=True,
                         date_format='%Y-%m-%d')
measurementorfact.sample(n=10)


# **Author:** Mathew Biddle
# 
# This notebook is a Python implementation of the R notebook created by Abby Benson [IOOS_DMAC_DataToDWC_Notebook_event.R](https://github.com/ioos/bio_data_guide/blob/master/Standardizing%20Marine%20Biological%20Data/datasets/example_script_with_fake_data/IOOS_DMAC_DataToDwC_Notebook_event.R).
