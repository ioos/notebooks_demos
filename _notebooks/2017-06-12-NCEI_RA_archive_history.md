---
title: "Using NCEI geoportal REST API to collect information about IOOS Regional Association archived data"
layout: notebook

---

by Mathew Biddle, Faculty Specialist, UMD/ESSIC/CICS at the NOAA National Centers for Environmental Information (NCEI)

### IOOS regional associations archive their non-federal observational data with NOAA's National Center for Environmental Information (NCEI). In this notebook we will use the [RESTful](https://github.com/Esri/geoportal-server/wiki/REST-API-Syntax) services of the [NCEI geoportal](https://www.nodc.noaa.gov/archivesearch/catalog/search/search.page) to collect metadata from the Archival Information Packages found in the NCEI archives. The metadata information are stored in [ISO 19115-2](https://wiki.earthdata.nasa.gov/display/NASAISO/ISO+19115-2) xml files which the NCEI geoportal uses for discovery of Archival Information Packages (AIPs). This example uses the ISO metadata records to display publication information as well as plot the time coverage of each AIP at NCEI which meets the search criteria.

First we import the owslib and numpy package. This allows us to parse the ISO xml records and process the information we gather.

Initialize a counter for plotting and a list to collect the NCEI Accession identifiers (we use this in the plotting routine). Also, update the namespaces dictionary from owslib to include the approriate namespace reference for gmi and gml. 

For more information on ISO Namespaces see:  https://geo-ide.noaa.gov/wiki/index.php?title=ISO_Namespaces

<div class="prompt input_prompt">
In&nbsp;[1]:
</div>

```python
from owslib.iso import namespaces

# Append gmi namespace to namespaces dictionary.
namespaces.update({'gmi': 'http://www.isotc211.org/2005/gmi'})
namespaces.update({'gml': 'http://www.opengis.net/gml/3.2'})
```

### Now we select a Regional Association 
This is where the user identifies the Regional Association they are interested in. Simply uncomment the line that identifies the region of interest. The user can also omit the Regional Association to collect metadata information about all IOOS non-Federal observation data archived through the NCEI-IOOS pipeline.

<div class="prompt input_prompt">
In&nbsp;[2]:
</div>

```python
# Select RA

RAs = {
    'GLOS': 'Great Lakes Observing System',
    'SCCOOS': 'Southern California Coastal Ocean Observing System',
    'SECOORA': 'Southeast Coastal Ocean Observing Regional Association',
    'PacIOOS': 'Pacific Islands Ocean Observing System',
    'NANOOS': 'Northwest Association of Networked Ocean Observing Systems',
}

ra = RAs['SCCOOS']
```

### Next we generate a geoportal query and georss feed
To find more information about how to compile a geoportal query, have a look at [REST API Syntax](https://github.com/Esri/geoportal-server/wiki/REST-API-Syntax) and the [NCEI Search Tips](https://www.nodc.noaa.gov/search/granule/catalog/searchtips/searchtips.page) for the [NCEI geoportal](https://data.nodc.noaa.gov/geoportal/catalog/search/search.page). The example provided is specfic to the NCEI-IOOS data pipeline project and only searches for non-federal timeseries data collected by each Regional Association. 

The query developed here can be updated to search for any Archival Information Packages at NCEI, therefore the user should develop the appropriate query using the [NCEI Geoportal](https://data.nodc.noaa.gov/geoportal/catalog/search/search.page) and update this portion of the code to identify the REST API of interest.

<div class="prompt input_prompt">
In&nbsp;[3]:
</div>

```python
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

# Generate geoportal query and georss feed.

# Base geoportal url.
baseurl = (
    'https://data.nodc.noaa.gov/'
    'geoportal/rest/find/document'
    '?searchText='
)

# Identify the project.
project = (
    'dataThemeprojects:'
    '"Integrated Ocean Observing System '
    'Data Assembly Centers Data Stewardship Program"'
)

# Identify the Regional Association
ra = ' AND "{}" '.format(ra)

# Identify the platform.
platform = 'AND "FIXED PLATFORM"'

# Identify the amount of records and format of the response: 1 to 1010 records.
records = '&start=1&max=1010'

# Identify the format of the response: georss.
response_format = '&f=georss'

# Combine the URL.
url = '{}{}'.format(baseurl, quote(project + ra + platform) + records + response_format)

print('Identified response format:\n{}'.format(url))
print('\nSearch page response:\n{}'.format(url.replace(response_format, '&f=searchPage')))
```
<div class="output_area"><div class="prompt"></div>
<pre>
    Identified response format:
    https://data.nodc.noaa.gov/geoportal/rest/find/document?searchText=dataThemeprojects%3A%22Integrated%20Ocean%20Observing%20System%20Data%20Assembly%20Centers%20Data%20Stewardship%20Program%22%20AND%20%22Southern%20California%20Coastal%20Ocean%20Observing%20System%22%20AND%20%22FIXED%20PLATFORM%22&start=1&max=1010&f=georss
    
    Search page response:
    https://data.nodc.noaa.gov/geoportal/rest/find/document?searchText=dataThemeprojects%3A%22Integrated%20Ocean%20Observing%20System%20Data%20Assembly%20Centers%20Data%20Stewardship%20Program%22%20AND%20%22Southern%20California%20Coastal%20Ocean%20Observing%20System%22%20AND%20%22FIXED%20PLATFORM%22&start=1&max=1010&f=searchPage

</pre>
</div>
### Time to query the portal and parse out the georrs response
Here we are opening the specified REST API and parsing it into a string. Then, since we identified it as a georss xml format above, we parse it using the etree package. We then pull out all the ISO metadata record links and print them out so the user can browse to the metadata record and look for what items they might be interested in.

<div class="prompt input_prompt">
In&nbsp;[4]:
</div>

```python
# Query the NCEI Geoportal and parse the georss response.

from lxml import etree

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

f = urlopen(url)  # Open georss response.
url_string = f.read()  # Read response into string.

# Create etree object from georss response.
url_root = etree.fromstring(url_string)
# Find all iso record links.
iso_record = url_root.findall('channel/item/link')
print('Found %i records' % len(iso_record))
for item in iso_record:
    print(item.text)  # URL to ISO19115-2 record.
```
<div class="output_area"><div class="prompt"></div>
<pre>
    Found 4 records
    https://data.nodc.noaa.gov/geoportal/rest/document?id=%7B39551FC8-BFF1-48A6-9250-18B02A6AC9C6%7D
    https://data.nodc.noaa.gov/geoportal/rest/document?id=%7B5EBDCCAB-E9ED-4C9D-A3FF-99EB69042DA0%7D
    https://data.nodc.noaa.gov/geoportal/rest/document?id=%7B18120F26-D96D-4677-8DF8-0A5A8D79EC1B%7D
    https://data.nodc.noaa.gov/geoportal/rest/document?id=%7BED88A565-52E1-43EF-9C48-F8FAA377107E%7D

</pre>
</div>
### Lets plot up what we have found
Now that we have all the ISO metadata records we are interested in, it's time to do something fun with them. In this example we want to generate a timeseries plot of the data coverage for the "Southern California Coastal Ocean Observing System" stations we have archived at NCEI.

First we set up the figure and import some modules to facilitate plotting and string parsing.

Next, we loop through each iso record to collect metadata information about each package. The example here shows how to collect the following items:
   1. NCEI Archival Information Package (AIP) Accession ID (7-digit Accession Number) 
   2. The first date the archive package was published.
   3. The platform code identified from the provider.
   4. The version number and date it was published.
   5. The current AIP size, in MB.
   6. The bounding time, for each AIP found.

There are plenty of other metadata elements to collect from the ISO records, so we recommend browsing to one of the records and having a look at the items of interest to your community.

Then, the process plots each AIP as a timeseries showing the time coverage. 

<div class="prompt input_prompt">
In&nbsp;[5]:
</div>

```python
# Process each iso record.
%matplotlib inline

from datetime import datetime
import re

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from owslib import util

fig, ax = plt.subplots(figsize=(15, 12))

i = 0
accenos = []

# For each accession in geo.rss response.
for item in iso_record:
    # Opens the iso xml web reference.
    iso_url = urlopen(item.text)
    # Creates tree element.
    iso_tree = etree.ElementTree(file=urlopen(item.text))
    # Gets the root from tree element.
    root = iso_tree.getroot()
    # Pulls out identifier string.
    ident = root.find(
        util.nspath_eval(
            'gmd:fileIdentifier/gco:CharacterString',
            namespaces
        )
    )
    # Pulls out 7-digit accession number from identifier.
    acce = re.search('[0-9]{7}', util.testXMLValue(ident))
    # Adds accession number to accenos list.
    accenos.append(acce.group(0))
    print('Accession Number = %s' % acce.group(0))

    # Collect Publication date information.
    date_path = (
        'gmd:identificationInfo/'
        'gmd:MD_DataIdentification/'
        'gmd:citation/'
        'gmd:CI_Citation/'
        'gmd:date/'
        'gmd:CI_Date/'
        'gmd:date/gco:Date'
    )
    # First published date.
    pubdate = root.find(util.nspath_eval(date_path, namespaces))
    print('First published date = %s' % util.testXMLValue(pubdate))

    # Collect Provider Platform Codes (if it has it).
    for tag in root.getiterator(
        util.nspath_eval('gco:CharacterString', namespaces)
    ):
        if tag.text == 'Provider Platform Codes':
            # Backs up to the MD_keywords element.
            node = tag.getparent().getparent().getparent().getparent()
            for item in node.findall(
                util.nspath_eval(
                    'gmd:keyword/gco:CharacterString', namespaces
                )
            ):
                print('Provider Platform Code = %s' % item.text)

    # Pull out the version information.
    # Iterate through each processing step which is an NCEI version.
    for tag in root.getiterator(
        util.nspath_eval('gmd:processStep', namespaces)
    ):
        # Only parse gco:DateTime and gmd:title/gco:CharacterString.
        vers_title = (
            'gmi:LE_ProcessStep/'
            'gmi:output/'
            'gmi:LE_Source/'
            'gmd:sourceCitation/'
            'gmd:CI_Citation/'
            'gmd:title/gco:CharacterString'
        )
        vers_date = (
            'gmi:LE_ProcessStep/'
            'gmd:dateTime/gco:DateTime'
        )
        if (
            tag.findall(util.nspath_eval(vers_date, namespaces)) and
            tag.findall(util.nspath_eval(vers_title, namespaces))
        ):
            # Extract dateTime for each version.
            datetimes = tag.findall(util.nspath_eval(vers_date, namespaces))
            # Extract title string (contains version number).
            titles = tag.findall(util.nspath_eval(vers_title, namespaces))
            print('{} = '.format(util.testXMLValue(titles[0]),
                                 util.testXMLValue(datetimes[0])))

    # Collect package size information.
    # Iterate through transfersize nodes.
    for tag in root.getiterator(
        util.nspath_eval('gmd:transferSize', namespaces)
    ):
        # Only go into first gco:Real (where size exists).
        if tag.find(
            util.nspath_eval('gco:Real', namespaces)
        ).text:
            # Extract size.
            sizes = tag.find(util.nspath_eval('gco:Real', namespaces))
            print('Current AIP Size = %s MB' % sizes.text)
            break
        # Only use first size instance, all gco:Real attributes are the same.
        break

    # Bounding time for AIP.
    for tag in root.getiterator(
        util.nspath_eval('gml:TimePeriod', namespaces)
    ):
        # If text exists in begin or end position nodes.
        if (
            tag.find(util.nspath_eval('gml:beginPosition', namespaces)).text and
            tag.find(util.nspath_eval('gml:endPosition', namespaces)).text
        ):
            start_date = tag.find(
                util.nspath_eval('gml:beginPosition', namespaces)
            ).text
            end_date = tag.find(
                util.nspath_eval('gml:endPosition', namespaces)
            ).text
    print('Bounding Time = %s TO %s\n' % (start_date, end_date))

    # Plotting routine for each accession, plot start-end as timeseries for each accession.
    # Create datetime objects for start_date and end_date.
    date1 = datetime(
        int(start_date.split('-')[0]),
        int(start_date.split('-')[1]),
        int(start_date.split('-')[2])
    )
    date2 = datetime(
        int(end_date.split('-')[0]),
        int(end_date.split('-')[1]),
        int(end_date.split('-')[2])
    )
    dates = [date1, date2]
    i += 1  # Counter for plotting.
    y = [i, i]
    # Plot the timeseries.
    ax.plot_date(x=dates, y=y, fmt='-', color='b', linewidth=6.0)

# Clean up the plot.
ax.set_ylim([0, i + 1])
years = mdates.YearLocator()
months = mdates.MonthLocator()
yearsFmt = mdates.DateFormatter('%Y')
ax.xaxis.grid(True)
ax.xaxis.set_major_locator(years)
ax.xaxis.set_major_formatter(yearsFmt)  # Format the xaxis labels.
ax.xaxis.set_minor_locator(months)
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.grid(True)
ax.set(yticks=np.arange(1, len(accenos)+1))
ax.tick_params(which='both', direction='out')
ax.set_yticklabels(accenos)
plt.ylabel('NCEI Accession Number')
title = ax.set_title('%s Data Archived at NCEI' % ra)
```
<div class="output_area"><div class="prompt"></div>
<pre>
    Accession Number = 0157035
    First published date = 2016-11-23
    NCEI Accession 0157035 v1.1 = 
    NCEI Accession 0157035 v2.2 = 
    NCEI Accession 0157035 v3.3 = 
    Current AIP Size = 52.084 MB
    Bounding Time = 2005-06-16 TO 2016-12-31
    
    Accession Number = 0157036
    First published date = 2016-11-23
    NCEI Accession 0157036 v1.1 = 
    NCEI Accession 0157036 v2.2 = 
    NCEI Accession 0157036 v3.3 = 
    Current AIP Size = 48 MB
    Bounding Time = 2005-09-16 TO 2016-12-31
    
    Accession Number = 0157016
    First published date = 2016-11-22
    NCEI Accession 0157016 v1.1 = 
    NCEI Accession 0157016 v2.2 = 
    Current AIP Size = 52.208 MB
    Bounding Time = 2005-06-16 TO 2015-07-13
    
    Accession Number = 0157034
    First published date = 2016-11-23
    NCEI Accession 0157034 v1.1 = 
    NCEI Accession 0157034 v2.2 = 
    NCEI Accession 0157034 v3.3 = 
    Current AIP Size = 89.956 MB
    Bounding Time = 2005-06-16 TO 2016-12-31
    

</pre>
</div>

![png](data:image/png;base64,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
AJiEgAkAAMAkBEwAAAAmIWACAAAwCQETAACASQiYAAAATELABAAAYBICJgAAAJMQMAEAAJiEgAkA
AMAkBEwAAAAmIWACAAAwCQETAACASQiYAAAATELABAAAYBICJgAAAJMQMAEAAJiEgAkAAMAkBEwA
AAAmIWACAAAwCQETAACASQiYAAAATELABAAAYBICJgAAAJMQMAEAAJiEgAkAAMAkBEwAAAAmIWAC
AAAwCQETAACASQiYAAAATELABAAAYBICJgAAAJMQMAEAAJiEgAkAAMAkBEwAAAAmIWACAAAwCQET
AACASQiYAAAATELABAAAYBICJgAAAJMQMAEAAJiEgAkAAMAkBEwAAAAmIWACAAAwCQETAACASQiY
AAAATELABAAAYBICJgAAAJMQMAEAAJiEgAkAAMAkBEwAAAAmIWACAAAwCQETAACASQiYAAAATELA
BAAAYBICJgAAAJMQMAEAAJiEgAkAAMAkBEwAAAAmIWACAAAwCQETAACASQiYAAAATELABAAAYBIC
JgAAAJMQMAEAAJiEgAkAAMAkBEwAAAAmIWACAAAwCQETAACASQiYAAAATELABAAAYBICJgAAAJMQ
MAEAAJjEvotceFXdI8mzk+yT5IXd/fSqemySY5McluSa3X32OO1Kktcn+dQ4+2u7+7iqukWSV84s
9iZJntzdz6qqg8ZxhyY5LcmDuvvcqjoyyVOTfDvJhUmO7e53ztR1tSQfS3Jidz92IRu/IFVbXcFm
Vra6gG1gZasL2CZWtrqAbWJlqwvYJla2uoBtYmWrC9gmVra6gG1iZasL2CZWtrqAbWJlqwvYJla2
uoBtYuXie91bV8WeWtgRzKraJ8nzk9wzya2SPKSqbpXkXUnunuT0dWZ7R3fffrwdlyTd/fHVYUnu
mOSCJCeO0z8pyVu6+2ZJ3jI+znj/duM8j0jywjXreWqSt020qQAAAGSxXWSPSPKJ7j61u7+Z5G+S
HNnd/9bdp+3hMu+W5JPdvRpOj0xywnj/hCT3S5Lu3tl9cd7fP8nF2b+q7pjkkCRv3MMaAAAAWMci
u8heL8kZM4/PTHKnXcxzl6r6UJLPJnlCd39kzfijkrxi5vEh3f25JOnuz1XVtVZHVNX9kzwtybWS
/OQ47ApJnpnk5zKE1Q1V1aOTPDpJDjnkkOzYsWPDaXfu3Lnp+Gmt7KX1AAAAW2nvZYzpLDJgrne2
4Ga9iD+Q5EbdvbOq7pXkdUludvHCqvZLct8kvznPyrv7xCQnVtUPZ+gSe/ckv5Tk5O4+o3ZxMmN3
vyDJC5Lk8MMP75WVlQ2n3bFjRzYbDwAAsLuWMWMsMmCemeQGM4+vn+HI5Lq6+6sz90+uqj+tqoNX
LwKU4VzOD3T3WTOznVVV1xmPXl4nyRfWWe7bq+qwqjo4yV2S/K+q+qUkV02yX1Xt7O4nrZ0PAACA
3bPIczDfl+RmVXXj8ejjUUlO2mjiqrp2jYcVq+qIsbZzZiZ5SC7dPTbj8o4e7x+d4Sq0qaqbzizr
Dkn2S3JOdz+0u2/Y3YcmeUKSly5buOzevre3vnXHltew1TdtoB20g3bQDtpBO2gH7aAdpmqHZbSw
I5jdfeH4kyT/lOFnSl7c3R+pqscn+Y0k107y71V1cnc/KskDk/xiVV2Y5GtJjlq9UE9VXSXJjyX5
hTWreXqSV1XVI5N8OslPj8N/KsnDqupb47IePHPRHwAAABZgob+D2d0nJzl5zbDnJHnOOtM+L8nz
NljOBUmusc7wc7LOxXq6+xlJnrGL2o5Pcvxm0wAAADC/RXaRBQAA4HJEwAQAAGASAiYAAACTEDAB
AACYhIAJAADAJARMAAAAJiFgAgAAMAkBEwAAgEkImAAAAExCwAQAAGASAiYAAACTEDABAACYhIAJ
AADAJARMAAAAJiFgAgAAMAkBEwAAgEkImAAAAExCwAQAAGASAiYAAACTEDABAACYhIAJAADAJARM
AAAAJiFgAgAAMAkBEwAAgEkImAAAAExCwAQAAGASAiYAAACTEDABAACYhIAJAADAJARMAAAAJiFg
AgAAMAkBEwAAgEkImAAAAExCwAQAAGASAiYAAACTEDABAACYhIAJAADAJARMAAAAJiFgAgAAMAkB
EwAAgEkImAAAAExCwAQAAGASAiYAAACTEDABAACYhIAJAADAJARMAAAAJiFgAgAAMAkBEwAAgEkI
mAAAAExCwAQAAGASAiYAAACTEDABAACYhIAJAADAJARMAAAAJiFgAgAAMAkBEwAAgEkImAAAAExC
wAQAAGASAiYAAACTEDABAACYhIAJAADAJARMAAAAJiFgAgAAMAkBEwAAgEkImAAAAExCwAQAAGAS
AiYAAACTEDABAACYhIAJAADAJARMAAAAJiFgAgAAMAkBEwAAgEkImAAAAExCwAQAAGASAiYAAACT
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
Dx6XdVFVPSHJW8YAekqSv1xUGwAAAFyeLPR3MMeurievGfacJM9ZZ9rnJXneBsu5IMk11hl+ToYr
y64d/owkz9hgWW9Kcts5ygcAAGA3LLKLLAAAAJcjAiYAAACTEDABAACYhIAJAADAJARMAAAAJiFg
AgAAMAkBEwAAgEkImAAAAExCwAQAAGASAiYAAACTEDABAACYhIAJAADAJARMAAAAJiFgAgAAMAkB
EwAAgEkImAAAAExCwAQAAGASAiYAAACTEDABAACYhIAJAADAJARMAAAAJiFgAgAAMAkBEwAAgEkI
mAAAAExCwAQAAGASAiYAAACTEDABAACYhIAJAADAJARMAAAAJiFgAgAAMAkBEwAAgEkImAAAAExC
wAQAAGASAiYAAACTEDABAACYhIAJAADAJARMAAAAJiFgAgAAMAkBEwAAgEkImAAAAExCwAQAAGAS
AiYAAACTEDABAACYhIAJAADAJARMAAAAJiFgAgAAMAkBEwAAgEkImAAAAExCwAQAAGASAiYAAACT
EDABAACYhIAJAADAJARMAAAAJiFgAgAAMAkBEwAAgEkImAAAAExCwAQAAGASAiYAAACTEDABAACY
hIAJAADAJARMAAAAJiFgAgAAMAkBEwAAgEkImAAAAExCwAQAAGASAiYAAACTEDABAACYhIAJAADA
JARMAAAAJiFgAgAAMAkBEwAAgEkImAAAAExCwAQAAGASAiYAAACTEDABAACYhIAJAADAJARMAAAA
JiFgAgAAMAkBEwAAgEkImAAAAExCwAQAAGASAiYAAACTEDABAACYhIAJAADAJARMAAAAJiFgAgAA
MAkBEwAAgEkImAAAAExCwAQAAGASAiYAAACTEDABAACYhIAJAADAJARMAAAAJiFgAgAAMAkBEwAA
gEkImAAAAExCwAQAAGASAiYAAACTEDABAACYhIAJAADAJARMAAAAJiFgAgAAMAkBEwAAgEkImAAA
AExCwAQAAGASAiYAAACTEDABAACYhIAJAADAJARMAAAAJiFgAgAAMAkBEwAAgEkImAAAAExCwAQA
AGASAiYAAACTEDABAACYhIAJAADAJARMAAAAJiFgAgAAMAkBEwAAgEkImAAAAExCwAQAAGAS+y5y
4VV1jyTPTrJPkhd299Or6rFJjk1yWJJrdvfZ47QrSV6f5FPj7K/t7uOq6hZJXjmz2JskeXJ3P6uq
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
AAC0+F/oq+RoLLteLQAAAABJRU5ErkJggg==
)


This procedure has been developed as an example of how to use NCEI's geoportal REST API's to collect information about packages that have been archived at NCEI. The intention is to provide some guidance and ways to collect this information without having to request it directly from NCEI. There are a significant amount of metadata elements which NCEI makes available through their ISO metadata records. Therefore, anyone interested in collecting other information from the records at NCEI should have a look at the ISO metadata records and determine which items are of interest to their community. Then, update the example code provided to collect that information.

<br>
Right click and choose Save link as... to
[download](https://raw.githubusercontent.com/ioos/notebooks_demos/master/notebooks/2017-06-12-NCEI_RA_archive_history.ipynb)
this notebook, or click [here](https://beta.mybinder.org/v2/gh/ioos/notebooks_demos/master?filepath=notebooks/2017-06-12-NCEI_RA_archive_history.ipynb) to run a live instance of this notebook.