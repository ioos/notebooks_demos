---
layout: notebook
title: ""
---


## Exploring a THREDDS catalog with Unidata's Siphon

<div class="prompt input_prompt">
In&nbsp;[1]:
</div>

```python
from siphon.catalog import TDSCatalog

catalog = TDSCatalog('http://thredds.cencoos.org/thredds/catalog.xml')
```

### Siphon return some useful attributes.

<div class="prompt input_prompt">
In&nbsp;[2]:
</div>

```python
info = """
Catalog information
-------------------

Base THREDDS URL: {}
Catalog name: {}
Catalog URL: {}
Metadata: {}
""".format(catalog.base_tds_url,
           catalog.catalog_name,
           catalog.catalog_url,
           catalog.metadata)

print(info)
```
<div class="output_area"><div class="prompt"></div>
<pre>
    
    Catalog information
    -------------------
    
    Base THREDDS URL: http://thredds.cencoos.org
    Catalog name: CeNCOOS
    Catalog URL: http://thredds.cencoos.org/thredds/catalog.xml
    Metadata: {}
    

</pre>
</div>
### Sadly this dataset had no metadata :-(
### What kind of services are avialable?

<div class="prompt input_prompt">
In&nbsp;[3]:
</div>

```python
for service in catalog.services:
    print(service.name)
```
<div class="output_area"><div class="prompt"></div>
<pre>
    all
    allandsos
    wms

</pre>
</div>
### The catalog refs...

<div class="prompt input_prompt">
In&nbsp;[4]:
</div>

```python
print('\n'.join(catalog.catalog_refs.keys()))
```
<div class="output_area"><div class="prompt"></div>
<pre>
    Global
    Dynamic
    Static
    HF RADAR, US West Coast
    HF RADAR, US West Coast (GNOME Format)

</pre>
</div>
### ... and datasets.

<div class="prompt input_prompt">
In&nbsp;[5]:
</div>

```python
print('\n'.join(catalog.datasets.keys()))
```
<div class="output_area"><div class="prompt"></div>
<pre>
    California Coastal Regional Ocean Modeling System (ROMS) Nowcast
    California Coastal Regional Ocean Modeling System (ROMS) Forecast
    Monterey Bay (MB) Regional Ocean Modeling System (ROMS) Nowcast
    Monterey Bay (MB) Regional Ocean Modeling System (ROMS) Forecast
    Southern California Bight (SCB) Regional Ocean Modeling System (ROMS) Nowcast
    UCSC California Current System Model
    HAB Cellular Domoic Acid Forecast
    HAB Cellular Domoic Acid Nowcast
    HAB Particulate Domoic Acid Forecast
    HAB Particulate Domoic Acid Nowcast
    HAB Pseudo Nitzschia Forecast
    HAB Pseudo Nitzschia Nowcast
    Coupled Ocean/Atmosphere Mesoscale Prediction System (COAMPS) Relative Humidity
    Coupled Ocean/Atmosphere Mesoscale Prediction System (COAMPS) Total Precipitation
    Coupled Ocean/Atmosphere Mesoscale Prediction System (COAMPS) Visibility
    Coupled Ocean/Atmosphere Mesoscale Prediction System (COAMPS) Wind 10 m
    Coupled Ocean/Atmosphere Mesoscale Prediction System (COAMPS) Air Temp 2 m
    Coupled Ocean/Atmosphere Mesoscale Prediction System (COAMPS) Cloud Base
    Coupled Ocean/Atmosphere Mesoscale Prediction System (COAMPS) Ground and Sea Temp
    Coupled Ocean/Atmosphere Mesoscale Prediction System (COAMPS) Pressure Reduce to MSL
    Coupled Ocean/Atmosphere Mesoscale Prediction System (COAMPS) Net Short-wave Radiation Surface
    Coupled Ocean/Atmosphere Mesoscale Prediction System (COAMPS) IR Heat Flux
    Coupled Ocean/Atmosphere Mesoscale Prediction System (COAMPS) Monthly Averaged Winds
    Coupled Ocean/Atmosphere Mesoscale Prediction System (COAMPS) Wind 10 m (Historical)
    Coupled Ocean/Atmosphere Mesoscale Prediction System (COAMPS) Ground and Sea Temp (Historical)
    Coupled Ocean/Atmosphere Mesoscale Prediction System (COAMPS) Air Temp 2 m (Historical)
    Hybrid Coordinate Ocean Model
    Southern California Regional NCOM Model
    Maurer Meteorological Data
    Global 1-km Sea Surface Temperature (G1SST)
    High Resolution Chlorophyll-a concentration from MODIS/Aqua (1 Day Composite)
    High Resolution Chlorophyll-a concentration from MODIS/Aqua (8 Day Composite)
    High Resolution Chlorophyll-a concentration from MODIS/Aqua (1 Month Composite)
    High Resolution Sea Surface Temperature from the Advanced Very-High Resolution Radiometer (1 Day Composite)
    High Resolution Sea Surface Temperature from the Advanced Very-High Resolution Radiometer (8 Day Composite)
    High Resolution Sea Surface Temperature from the Advanced Very-High Resolution Radiometer (1 Month Composite)
    Ocean Surface Currents Monthly Averaged - CORDC High-Frequency Radar (US West Coast), 6 km

</pre>
</div>
### What is a catalog ref?

<div class="prompt input_prompt">
In&nbsp;[6]:
</div>

```python
ref = catalog.catalog_refs['Global']

[value for value in dir(ref) if not value.startswith('__')]
```




    ['follow', 'href', 'name', 'title']



<div class="prompt input_prompt">
In&nbsp;[7]:
</div>

```python
info = """
Href: {}
Name: {}
Title: {}
""".format(
    ref.href,
    ref.name,
    ref.title)

print(info)
```
<div class="output_area"><div class="prompt"></div>
<pre>
    
    Href: http://thredds.cencoos.org/thredds/global.xml
    Name: 
    Title: Global
    

</pre>
</div>
### Those are attributes holding the metadata of that ref. Let's take a look at
the `follow` is a method.

<div class="prompt input_prompt">
In&nbsp;[8]:
</div>

```python
cat = ref.follow()

print(type(cat))
```
<div class="output_area"><div class="prompt"></div>
<pre>
    <class 'siphon.catalog.TDSCatalog'>

</pre>
</div>
### We followed that `ref` to a new catalog! Here are the data from the *Global*
catalog object.

<div class="prompt input_prompt">
In&nbsp;[9]:
</div>

```python
print('\n'.join(cat.datasets.keys()))
```
<div class="output_area"><div class="prompt"></div>
<pre>
    NCEP Reanalysis Daily Averages Surface Flux
    Global 1-km Sea Surface Temperature (G1SST)
    NCEP Global Forecast System Model (GFS)
    Aquarius V 3.0 Scatterometer Daily Aggregate
    Aquarius V 3.0 Scatterometer Seven-Day Aggregate
    Aquarius V 3.0 Scatterometer Monthly Aggregate
    Aquarius V 3.0 Radiometer Daily Aggregate
    Aquarius V 3.0 Radiometer Seven-Day Aggregate
    Aquarius V 3.0 Radiometer Monthly Aggregate
    Aquarius V 4.0 Scatterometer Daily Aggregate
    Aquarius V 4.0 Scatterometer Seven-Day Aggregate
    Aquarius V 4.0 Scatterometer Monthly Aggregate
    Aquarius V 4.0 Radiometer Daily Aggregate
    Aquarius V 4.0 Radiometer Seven-Day Aggregate
    Aquarius V 4.0 Radiometer Monthly Aggregate

</pre>
</div>
### Let's extract the Global SST from both the main catalog and the
"subcatalog."

<div class="prompt input_prompt">
In&nbsp;[10]:
</div>

```python
dataset = 'Global 1-km Sea Surface Temperature (G1SST)'

ds0 = catalog.datasets[dataset]
ds1 = cat.datasets[dataset]

ds0 is ds1, ds0 == ds1
```




    (False, False)



### Not sure if they are really different datasets or if siphon just spawn a new
instance that comparison is bogus. Let's check the metadata.

<div class="prompt input_prompt">
In&nbsp;[11]:
</div>

```python
ds0.url_path, ds1.url_path
```




    ('G1_SST_US_WEST_COAST.nc', 'G1_SST_GLOBAL.nc')



### Aha! They are different datasets! Siphon has a `ncss` (NetCDF subset
service) too. Here is the docstring:

> This module contains code to support making data requests to
the NetCDF subset service (NCSS) on a THREDDS Data Server (TDS). This includes
forming proper queries as well as parsing the returned data.

### But it seems that the catalog must offer the `NetcdfSubset` in the
access_urls. Let's see if we have that in this catalog.

<div class="prompt input_prompt">
In&nbsp;[12]:
</div>

```python
for name, ds in catalog.datasets.items():
    if ds.access_urls:
        print(name)
```

### All empty... Maybe that is just a metadata issue because we can see
`NetcdfSubset` in the page.

<div class="prompt input_prompt">
In&nbsp;[13]:
</div>

```python
from IPython.display import IFrame

url = 'http://thredds.cencoos.org/thredds/catalog.html?dataset=G1_SST_US_WEST_COAST'

IFrame(url, width=800, height=550)
```





        <iframe
            width="800"
            height="550"
            src="http://thredds.cencoos.org/thredds/catalog.html?dataset=G1_SST_US_WEST_COAST"
            frameborder="0"
            allowfullscreen
        ></iframe>
        



### So let's try something else for now. We can get access the WMS service and
overlay the data in a slippy map.

<div class="prompt input_prompt">
In&nbsp;[14]:
</div>

```python
services = [service for service in catalog.services if service.name == 'wms']

services
```




    [<siphon.catalog.SimpleService at 0x7fe06d3620b8>]



### Found only one. So we can squeeze that out.

<div class="prompt input_prompt">
In&nbsp;[15]:
</div>

```python
service = services[0]
```

<div class="prompt input_prompt">
In&nbsp;[16]:
</div>

```python
url = service.base
url
```




    'http://pdx.axiomalaska.com/ncWMS/wms'



We do not know what is avilable there but we can explore the service with
`owslib`.

<div class="prompt input_prompt">
In&nbsp;[17]:
</div>

```python
from owslib.wms import WebMapService

service = WebMapService(url)

print('\n'.join(service.contents.keys()))
```
<div class="output_area"><div class="prompt"></div>
<pre>
    NDFD_2016_Total_Snowfall/Total_snowfall
    NDFD_2016_Minimum_Temperature/Minimum_temperature
    NDFD_2016_Significant_height_of_wind_waves/Significant_height_of_wind_waves
    NDFD_2016_Total_Precipitation/Total_precipitation
    NDFD_2016_Wind_Speed_Gust/Wind_speed_gust
    NDFD_2016_Maximum_Temperature/Maximum_temperature
    NDFD_2016_Aggregate/Wind_direction_from_which_blowing
    NDFD_2016_Aggregate/Wind_speed
    NDFD_2016_Aggregate/Temperature_tendency_by_all_radiation
    NDFD_2016_Aggregate/Relative_humidity
    NDFD_2016_Aggregate/Total_cloud_cover
    NDFD_2016_Aggregate/Dew_point_temperature
    NDFD_2016_Aggregate/Temperature
    NDFD_2016_Aggregate/eastward_wind
    NDFD_2016_Aggregate/northward_wind
    NDFD_2016_Aggregate/wind
    COAST_WATCH_JPLMURSST41CLIM/mean_sst
    COAST_WATCH_JPLMURSST41ANOM1DAY/sstAnom
    COAST_WATCH_JPLMURSST41ANOMMDAY/sstAnom
    COAST_WATCH_JPLMURSST41/analysed_sst
    WEST_COAST_WAVE_1/U-component_of_wind
    WEST_COAST_WAVE_1/Significant_height_of_swell_waves
    WEST_COAST_WAVE_1/Significant_height_of_wind_waves
    WEST_COAST_WAVE_1/Direction_of_swell_waves
    WEST_COAST_WAVE_1/Mean_period_of_swell_waves
    WEST_COAST_WAVE_1/Mean_period_of_wind_waves
    WEST_COAST_WAVE_1/Significant_height_of_combined_wind_waves_and_swell
    WEST_COAST_WAVE_1/Direction_of_wind_waves
    WEST_COAST_WAVE_1/Primary_wave_direction
    WEST_COAST_WAVE_1/V-component_of_wind
    WEST_COAST_WAVE_1/Primary_wave_mean_period
    WEST_COAST_WAVE_1/wind
    WEST_COAST_WAVE_2/U-component_of_wind
    WEST_COAST_WAVE_2/Significant_height_of_swell_waves
    WEST_COAST_WAVE_2/Significant_height_of_wind_waves
    WEST_COAST_WAVE_2/Direction_of_swell_waves
    WEST_COAST_WAVE_2/Mean_period_of_swell_waves
    WEST_COAST_WAVE_2/Mean_period_of_wind_waves
    WEST_COAST_WAVE_2/Significant_height_of_combined_wind_waves_and_swell
    WEST_COAST_WAVE_2/Direction_of_wind_waves
    WEST_COAST_WAVE_2/Primary_wave_direction
    WEST_COAST_WAVE_2/V-component_of_wind
    WEST_COAST_WAVE_2/Primary_wave_mean_period
    WEST_COAST_WAVE_2/wind
    GOA_RUNOFF_SWE_DEPTH/topo
    GOA_RUNOFF_SWE_DEPTH/swed
    GOA_RUNOFF_DISCHARGE/topo
    GOA_RUNOFF_DISCHARGE/strm
    GOA_RUNOFF_DISCHARGE/q
    MBON_FKNMS_2016_05/CLASS
    MBON_FKNMS_2016_05/PROB
    MBON_MBNMS_2016_05/CLASS
    MBON_MBNMS_2016_05/PROB
    OUTER_BANKS_HF_RADAR/u
    OUTER_BANKS_HF_RADAR/v
    OUTER_BANKS_HF_RADAR/sea_water_velocity
    EAST_FLORIDA_SHELF/eastward_current
    EAST_FLORIDA_SHELF/northward_current
    EAST_FLORIDA_SHELF/eastward_current_accuracy
    EAST_FLORIDA_SHELF/northward_current_accuracy
    EAST_FLORIDA_SHELF/sea_water_velocity
    EAST_FLORIDA_SHELF/sea_water_velocity_accuracy
    AOOS_TOM_RAVENS_INUNDATION/S1
    AOOS_TOM_RAVENS_INUNDATION/TAUMAX
    AOOS_TOM_RAVENS_INUNDATION/ALFAS
    AOOS_TOM_RAVENS_INUNDATION/DPS0
    AOOS_TOM_RAVENS_INUNDATION/GSQS
    AOOS_TOM_RAVENS_INUNDATION/KCS
    AOOS_TOM_RAVENS_INUNDATION/PPARTITION
    AOOS_TOM_RAVENS_INUNDATION/DP0
    GFS/Relative_humidity_height_above_ground
    GFS/u-component_of_wind_height_above_ground
    GFS/v-component_of_wind_height_above_ground
    GFS/Ice_cover_surface
    GFS/Pressure_reduced_to_MSL_msl
    GFS/Pressure_surface
    GFS/Snow_depth_surface
    GFS/Temperature_surface
    GFS/Wind_speed_gust_surface
    GFS/Pressure_height_above_ground
    GFS/Temperature_height_above_ground
    GFS/wind
    NWS_ETSURGE_2-1_ALA3KM_STORMSURGE/Extra_Tropical_Storm_Surge
    NWS_ETSURGE_2-1_CON2P5KM_STORMSURGE/Extra_Tropical_Storm_Surge
    NWS_ETSURGE_2-1_ALA3KM_STORMTIDE/UnknownParameter_D10_C3_250
    NWS_ETSURGE_2-1_CON2P5KM_STORMTIDE/UnknownParameter_D10_C3_250
    NWS_ETSURGE_ALA3KM/Extra_Tropical_Storm_Surge
    NWS_ETSURGE_CON2P5KM/Extra_Tropical_Storm_Surge
    GOA_RUNOFF/topo
    GOA_RUNOFF/strm
    GOA_RUNOFF/q
    Aquarius_V4_scat_wind_speed_Daily/scat_wind_speed
    Aquarius_V4_scat_wind_speed_Weekly/scat_wind_speed
    Aquarius_V4_scat_wind_speed_Monthly/scat_wind_speed
    Aquarius_V4_SSS_Daily/SSS
    Aquarius_V4_SSS_Weekly/SSS
    Aquarius_V4_SSS_Monthly/SSS
    MUR2/analysed_sst
    MUR2/sea_ice_fraction
    GEBCO2014_NORTHERN_HEM/elevation
    GEBCO2014/elevation
    NAM_12_CONUS_ALASKA/Ice_cover_Proportion
    NAM_12_CONUS_ALASKA/Water_temperature
    NAM_12_CONUS_ALASKA/Snow_Cover
    NAM_12_CONUS_ALASKA/Vegetation
    NAM_12_CONUS_ALASKA/Water_equivalent_of_accumulated_snow_depth
    NAM_12_CONUS_ALASKA/Pressure_surface
    NAM_12_CONUS_ALASKA/Pressure_reduced_to_MSL
    NAM_12_CONUS_ALASKA/Temperature_height_above_ground
    NAM_12_CONUS_ALASKA/Temperature_surface
    NAM_12_CONUS_ALASKA/V-component_of_wind_height_above_ground
    NAM_12_CONUS_ALASKA/U-component_of_wind_height_above_ground
    NAM_12_CONUS_ALASKA/Precipitation_rate
    NAM_12_CONUS_ALASKA/Total_cloud_cover
    NAM_12_CONUS_ALASKA/Visibility
    NAM_12_CONUS_ALASKA/Snow_depth
    NAM_12_CONUS_ALASKA/Relative_humidity_height_above_ground
    NAM_12_CONUS_ALASKA/Albedo
    NAM_12_CONUS_ALASKA/Wind_speed_gust
    NAM_12_CONUS_ALASKA/wind
    UF_NAM_2D_EC/zeta
    UF_NAM_2D_SE/zeta
    UF_NAM_2D_NG/zeta
    UF_NAM_2D_SW/zeta
    UF_NAM_3D_EC/zeta
    UF_NAM_3D_EC/hsig
    UF_NAM_3D_EC/salinity
    UF_NAM_3D_EC/uvelocity
    UF_NAM_3D_EC/vvelocity
    UF_NAM_3D_EC/sea_water_velocity
    UF_NAM_3D_NG/zeta
    UF_NAM_3D_NG/hsig
    UF_NAM_3D_NG/salinity
    UF_NAM_3D_NG/uvelocity
    UF_NAM_3D_NG/vvelocity
    UF_NAM_3D_NG/sea_water_velocity
    UF_NAM_3D_SE/zeta
    UF_NAM_3D_SE/hsig
    UF_NAM_3D_SE/salinity
    UF_NAM_3D_SE/uvelocity
    UF_NAM_3D_SE/vvelocity
    UF_NAM_3D_SE/sea_water_velocity
    UF_NAM_3D_SW/zeta
    UF_NAM_3D_SW/hsig
    UF_NAM_3D_SW/salinity
    UF_NAM_3D_SW/uvelocity
    UF_NAM_3D_SW/vvelocity
    UF_NAM_3D_SW/sea_water_velocity
    USF_WEST_FLORIDA_SHELF_WFS/zeta
    USF_WEST_FLORIDA_SHELF_WFS/salt
    USF_WEST_FLORIDA_SHELF_WFS/temp
    NCSU_SABGOM_3/salt
    NCSU_SABGOM_3/temp
    NCSU_SABGOM_3/u_rho
    NCSU_SABGOM_3/v_rho
    NCSU_SABGOM_3/zeta
    NCSU_SABGOM_3/sea_water_velocity
    NCSU_SABGOM_2/chlorophyll
    NCSU_SABGOM_2/phytoplankton
    NCSU_SABGOM_2/zooplankton
    NCSU_SABGOM_1/NH4
    NCSU_SABGOM_1/NO3
    NSCU/w
    NSCU/Dwave
    NSCU/Hwave
    NSCU/Lwave
    NSCU/evaporation
    NSCU/latent
    NSCU/lwrad
    NSCU/rain
    NSCU/sensible
    NSCU/shflux
    NSCU/ssflux
    NSCU/zeta
    NSCU/salt
    NSCU/temp
    NSCU/u_rho
    NSCU/v_rho
    NSCU/svstr
    NSCU/sea_water_velocity
    HAB_PSEUDO_NITZSCHIA_FORECAST/forecast_pseudo_nitzschia
    HAB_PSEUDO_NITZSCHIA_NOWCAST/pseudo_nitzschia
    HAB_PARTICULATE_DOMOIC_ACID_NOWCAST/particulate_domoic_acid
    HAB_PARTICULATE_DOMOIC_ACID_FORECAST/forecast_particulate_domoic_acid
    HAB_CELLULAR_DOMOIC_ACID_NOWCAST/cellular_domoic_acid
    HAB_CELLULAR_DOMOIC_ACID_FORECAST/forecast_cellular_domoic_acid
    G1_SST_GLOBAL/analysed_sst
    G1_SST_GLOBAL/mask
    G1_SST_GLOBAL/analysis_error
    COAMPS_MONTHLY_WINDS/v
    COAMPS_MONTHLY_WINDS/u
    COAMPS_MONTHLY_WINDS/wind
    COAMPS_4KM_IR_FLUX/IR_heat_flux
    COAMPS_4KM_SOL_RAD/Net_short-wave_radiation_surface
    FALMOUTH/v
    FALMOUTH/angle
    FALMOUTH/f
    FALMOUTH/h
    FALMOUTH/mask_rho
    FALMOUTH/pm
    FALMOUTH/pn
    FALMOUTH/mask_psi
    FALMOUTH/wetdry_mask_rho
    FALMOUTH/zeta
    FALMOUTH/bvstr
    FALMOUTH/vbar
    FALMOUTH/wetdry_mask_v
    FALMOUTH/salt
    FALMOUTH/temp
    FALMOUTH/u_rho
    FALMOUTH/v_rho
    FALMOUTH/mask_v
    FALMOUTH/u
    FALMOUTH/AKv
    FALMOUTH/gls
    FALMOUTH/omega
    FALMOUTH/tke
    FALMOUTH/w
    FALMOUTH/mask_u
    FALMOUTH/bustr
    FALMOUTH/ubar
    FALMOUTH/wetdry_mask_u
    FALMOUTH/sea_water_velocity
    SNAP_SEA_ICE_ATLAS/sic_con_pct
    GLOS_BATH/topo
    GLOS_ERIE_SATELLITE_CDOM/cdom
    GLOS_ERIE_SATELLITE_CHL/chl
    GLOS_ERIE_SATELLITE_DOC/doc
    GLOS_ERIE_SATELLITE_NC/Band1
    GLOS_ERIE_SATELLITE_NC/Band2
    GLOS_ERIE_SATELLITE_NC/Band3
    GLOS_ERIE_SATELLITE_SM/sm
    GLOS_ERIE_SATELLITE_SST/sst
    GLOS_HURON_SATELLITE_CDOM/cdom
    GLOS_HURON_SATELLITE_DOC/doc
    GLOS_HURON_SATELLITE_CHL/chl
    GLOS_HURON_SATELLITE_NC/Band1
    GLOS_HURON_SATELLITE_NC/Band2
    GLOS_HURON_SATELLITE_NC/Band3
    GLOS_HURON_SATELLITE_SM/sm
    GLOS_HURON_SATELLITE_SST/sst
    GLOS_MICHIGAN_SATELLITE_CDOM/cdom
    GLOS_MICHIGAN_SATELLITE_DOC/doc
    GLOS_MICHIGAN_SATELLITE_CHL/chl
    GLOS_MICHIGAN_SATELLITE_NC/Band1
    GLOS_MICHIGAN_SATELLITE_NC/Band2
    GLOS_MICHIGAN_SATELLITE_NC/Band3
    GLOS_MICHIGAN_SATELLITE_SM/sm
    GLOS_MICHIGAN_SATELLITE_SST/sst
    GLOS_ONTARIO_SATELLITE_CDOM/cdom
    GLOS_ONTARIO_SATELLITE_DOC/doc
    GLOS_ONTARIO_SATELLITE_CHL/chl
    GLOS_ONTARIO_SATELLITE_NC/Band1
    GLOS_ONTARIO_SATELLITE_NC/Band2
    GLOS_ONTARIO_SATELLITE_NC/Band3
    GLOS_ONTARIO_SATELLITE_SM/sm
    GLOS_ONTARIO_SATELLITE_SST/sst
    GLOS_SUPERIOR_SATELLITE_CDOM/cdom
    GLOS_SUPERIOR_SATELLITE_DOC/doc
    GLOS_SUPERIOR_SATELLITE_CHL/chl
    GLOS_SUPERIOR_SATELLITE_NC/Band1
    GLOS_SUPERIOR_SATELLITE_NC/Band2
    GLOS_SUPERIOR_SATELLITE_NC/Band3
    GLOS_SUPERIOR_SATELLITE_SM/sm
    GLOS_SUPERIOR_SATELLITE_SST/sst
    CORDC_MONTHLY/v
    CORDC_MONTHLY/u
    CORDC_MONTHLY/sea_water_velocity
    WAVE_MODEL_CA01/wintermean_waveheights
    WAVE_MODEL_CA01/fallextreme_orbitalvelocities
    WAVE_MODEL_CA01/fallextreme_peakperiods
    WAVE_MODEL_CA01/fallextreme_waveheights
    WAVE_MODEL_CA01/fallmean_orbitalvelocities
    WAVE_MODEL_CA01/fallmean_peakperiods
    WAVE_MODEL_CA01/fallmean_waveheights
    WAVE_MODEL_CA01/springextreme_orbitalvelocities
    WAVE_MODEL_CA01/springextreme_peakperiods
    WAVE_MODEL_CA01/springextreme_waveheights
    WAVE_MODEL_CA01/springmean_orbitalvelocities
    WAVE_MODEL_CA01/springmean_peakperiods
    WAVE_MODEL_CA01/springmean_waveheights
    WAVE_MODEL_CA01/summerextreme_orbitalvelocities
    WAVE_MODEL_CA01/summerextreme_peakperiods
    WAVE_MODEL_CA01/summerextreme_waveheights
    WAVE_MODEL_CA01/summermean_orbitalvelocities
    WAVE_MODEL_CA01/summermean_peakperiods
    WAVE_MODEL_CA01/summermean_waveheights
    WAVE_MODEL_CA01/winterextreme_orbitalvelocities
    WAVE_MODEL_CA01/winterextreme_peakperiods
    WAVE_MODEL_CA01/winterextreme_waveheights
    WAVE_MODEL_CA01/wintermean_orbitalvelocities
    WAVE_MODEL_CA01/wintermean_peakperiods
    WAVE_MODEL_CA02/wintermean_waveheights
    WAVE_MODEL_CA02/fallextreme_orbitalvelocities
    WAVE_MODEL_CA02/fallextreme_peakperiods
    WAVE_MODEL_CA02/fallextreme_waveheights
    WAVE_MODEL_CA02/fallmean_orbitalvelocities
    WAVE_MODEL_CA02/fallmean_peakperiods
    WAVE_MODEL_CA02/fallmean_waveheights
    WAVE_MODEL_CA02/springextreme_orbitalvelocities
    WAVE_MODEL_CA02/springextreme_peakperiods
    WAVE_MODEL_CA02/springextreme_waveheights
    WAVE_MODEL_CA02/springmean_orbitalvelocities
    WAVE_MODEL_CA02/springmean_peakperiods
    WAVE_MODEL_CA02/springmean_waveheights
    WAVE_MODEL_CA02/summerextreme_orbitalvelocities
    WAVE_MODEL_CA02/summerextreme_peakperiods
    WAVE_MODEL_CA02/summerextreme_waveheights
    WAVE_MODEL_CA02/summermean_orbitalvelocities
    WAVE_MODEL_CA02/summermean_peakperiods
    WAVE_MODEL_CA02/summermean_waveheights
    WAVE_MODEL_CA02/winterextreme_orbitalvelocities
    WAVE_MODEL_CA02/winterextreme_peakperiods
    WAVE_MODEL_CA02/winterextreme_waveheights
    WAVE_MODEL_CA02/wintermean_orbitalvelocities
    WAVE_MODEL_CA02/wintermean_peakperiods
    WAVE_MODEL_CA03/wintermean_waveheights
    WAVE_MODEL_CA03/fallextreme_orbitalvelocities
    WAVE_MODEL_CA03/fallextreme_peakperiods
    WAVE_MODEL_CA03/fallextreme_waveheights
    WAVE_MODEL_CA03/fallmean_orbitalvelocities
    WAVE_MODEL_CA03/fallmean_peakperiods
    WAVE_MODEL_CA03/fallmean_waveheights
    WAVE_MODEL_CA03/springextreme_orbitalvelocities
    WAVE_MODEL_CA03/springextreme_peakperiods
    WAVE_MODEL_CA03/springextreme_waveheights
    WAVE_MODEL_CA03/springmean_orbitalvelocities
    WAVE_MODEL_CA03/springmean_peakperiods
    WAVE_MODEL_CA03/springmean_waveheights
    WAVE_MODEL_CA03/summerextreme_orbitalvelocities
    WAVE_MODEL_CA03/summerextreme_peakperiods
    WAVE_MODEL_CA03/summerextreme_waveheights
    WAVE_MODEL_CA03/summermean_orbitalvelocities
    WAVE_MODEL_CA03/summermean_peakperiods
    WAVE_MODEL_CA03/summermean_waveheights
    WAVE_MODEL_CA03/winterextreme_orbitalvelocities
    WAVE_MODEL_CA03/winterextreme_peakperiods
    WAVE_MODEL_CA03/winterextreme_waveheights
    WAVE_MODEL_CA03/wintermean_orbitalvelocities
    WAVE_MODEL_CA03/wintermean_peakperiods
    WAVE_MODEL_CA04/wintermean_waveheights
    WAVE_MODEL_CA04/fallextreme_orbitalvelocities
    WAVE_MODEL_CA04/fallextreme_peakperiods
    WAVE_MODEL_CA04/fallextreme_waveheights
    WAVE_MODEL_CA04/fallmean_orbitalvelocities
    WAVE_MODEL_CA04/fallmean_peakperiods
    WAVE_MODEL_CA04/fallmean_waveheights
    WAVE_MODEL_CA04/springextreme_orbitalvelocities
    WAVE_MODEL_CA04/springextreme_peakperiods
    WAVE_MODEL_CA04/springextreme_waveheights
    WAVE_MODEL_CA04/springmean_orbitalvelocities
    WAVE_MODEL_CA04/springmean_peakperiods
    WAVE_MODEL_CA04/springmean_waveheights
    WAVE_MODEL_CA04/summerextreme_orbitalvelocities
    WAVE_MODEL_CA04/summerextreme_peakperiods
    WAVE_MODEL_CA04/summerextreme_waveheights
    WAVE_MODEL_CA04/summermean_orbitalvelocities
    WAVE_MODEL_CA04/summermean_peakperiods
    WAVE_MODEL_CA04/summermean_waveheights
    WAVE_MODEL_CA04/winterextreme_orbitalvelocities
    WAVE_MODEL_CA04/winterextreme_peakperiods
    WAVE_MODEL_CA04/winterextreme_waveheights
    WAVE_MODEL_CA04/wintermean_orbitalvelocities
    WAVE_MODEL_CA04/wintermean_peakperiods
    WAVE_MODEL_CA05/wintermean_waveheights
    WAVE_MODEL_CA05/fallextreme_orbitalvelocities
    WAVE_MODEL_CA05/fallextreme_peakperiods
    WAVE_MODEL_CA05/fallextreme_waveheights
    WAVE_MODEL_CA05/fallmean_orbitalvelocities
    WAVE_MODEL_CA05/fallmean_peakperiods
    WAVE_MODEL_CA05/fallmean_waveheights
    WAVE_MODEL_CA05/springextreme_orbitalvelocities
    WAVE_MODEL_CA05/springextreme_peakperiods
    WAVE_MODEL_CA05/springextreme_waveheights
    WAVE_MODEL_CA05/springmean_orbitalvelocities
    WAVE_MODEL_CA05/springmean_peakperiods
    WAVE_MODEL_CA05/springmean_waveheights
    WAVE_MODEL_CA05/summerextreme_orbitalvelocities
    WAVE_MODEL_CA05/summerextreme_peakperiods
    WAVE_MODEL_CA05/summerextreme_waveheights
    WAVE_MODEL_CA05/summermean_orbitalvelocities
    WAVE_MODEL_CA05/summermean_peakperiods
    WAVE_MODEL_CA05/summermean_waveheights
    WAVE_MODEL_CA05/winterextreme_orbitalvelocities
    WAVE_MODEL_CA05/winterextreme_peakperiods
    WAVE_MODEL_CA05/winterextreme_waveheights
    WAVE_MODEL_CA05/wintermean_orbitalvelocities
    WAVE_MODEL_CA05/wintermean_peakperiods
    WAVE_MODEL_CA06/wintermean_waveheights
    WAVE_MODEL_CA06/fallextreme_orbitalvelocities
    WAVE_MODEL_CA06/fallextreme_peakperiods
    WAVE_MODEL_CA06/fallextreme_waveheights
    WAVE_MODEL_CA06/fallmean_orbitalvelocities
    WAVE_MODEL_CA06/fallmean_peakperiods
    WAVE_MODEL_CA06/fallmean_waveheights
    WAVE_MODEL_CA06/springextreme_orbitalvelocities
    WAVE_MODEL_CA06/springextreme_peakperiods
    WAVE_MODEL_CA06/springextreme_waveheights
    WAVE_MODEL_CA06/springmean_orbitalvelocities
    WAVE_MODEL_CA06/springmean_peakperiods
    WAVE_MODEL_CA06/springmean_waveheights
    WAVE_MODEL_CA06/summerextreme_orbitalvelocities
    WAVE_MODEL_CA06/summerextreme_peakperiods
    WAVE_MODEL_CA06/summerextreme_waveheights
    WAVE_MODEL_CA06/summermean_orbitalvelocities
    WAVE_MODEL_CA06/summermean_peakperiods
    WAVE_MODEL_CA06/summermean_waveheights
    WAVE_MODEL_CA06/winterextreme_orbitalvelocities
    WAVE_MODEL_CA06/winterextreme_peakperiods
    WAVE_MODEL_CA06/winterextreme_waveheights
    WAVE_MODEL_CA06/wintermean_orbitalvelocities
    WAVE_MODEL_CA06/wintermean_peakperiods
    WAVE_MODEL_CA07/wintermean_waveheights
    WAVE_MODEL_CA07/fallextreme_orbitalvelocities
    WAVE_MODEL_CA07/fallextreme_peakperiods
    WAVE_MODEL_CA07/fallextreme_waveheights
    WAVE_MODEL_CA07/fallmean_orbitalvelocities
    WAVE_MODEL_CA07/fallmean_peakperiods
    WAVE_MODEL_CA07/fallmean_waveheights
    WAVE_MODEL_CA07/springextreme_orbitalvelocities
    WAVE_MODEL_CA07/springextreme_peakperiods
    WAVE_MODEL_CA07/springextreme_waveheights
    WAVE_MODEL_CA07/springmean_orbitalvelocities
    WAVE_MODEL_CA07/springmean_peakperiods
    WAVE_MODEL_CA07/springmean_waveheights
    WAVE_MODEL_CA07/summerextreme_orbitalvelocities
    WAVE_MODEL_CA07/summerextreme_peakperiods
    WAVE_MODEL_CA07/summerextreme_waveheights
    WAVE_MODEL_CA07/summermean_orbitalvelocities
    WAVE_MODEL_CA07/summermean_peakperiods
    WAVE_MODEL_CA07/summermean_waveheights
    WAVE_MODEL_CA07/winterextreme_orbitalvelocities
    WAVE_MODEL_CA07/winterextreme_peakperiods
    WAVE_MODEL_CA07/winterextreme_waveheights
    WAVE_MODEL_CA07/wintermean_orbitalvelocities
    WAVE_MODEL_CA07/wintermean_peakperiods
    WAVE_MODEL_CA08/wintermean_waveheights
    WAVE_MODEL_CA08/fallextreme_orbitalvelocities
    WAVE_MODEL_CA08/fallextreme_peakperiods
    WAVE_MODEL_CA08/fallextreme_waveheights
    WAVE_MODEL_CA08/fallmean_orbitalvelocities
    WAVE_MODEL_CA08/fallmean_peakperiods
    WAVE_MODEL_CA08/fallmean_waveheights
    WAVE_MODEL_CA08/springextreme_orbitalvelocities
    WAVE_MODEL_CA08/springextreme_peakperiods
    WAVE_MODEL_CA08/springextreme_waveheights
    WAVE_MODEL_CA08/springmean_orbitalvelocities
    WAVE_MODEL_CA08/springmean_peakperiods
    WAVE_MODEL_CA08/springmean_waveheights
    WAVE_MODEL_CA08/summerextreme_orbitalvelocities
    WAVE_MODEL_CA08/summerextreme_peakperiods
    WAVE_MODEL_CA08/summerextreme_waveheights
    WAVE_MODEL_CA08/summermean_orbitalvelocities
    WAVE_MODEL_CA08/summermean_peakperiods
    WAVE_MODEL_CA08/summermean_waveheights
    WAVE_MODEL_CA08/winterextreme_orbitalvelocities
    WAVE_MODEL_CA08/winterextreme_peakperiods
    WAVE_MODEL_CA08/winterextreme_waveheights
    WAVE_MODEL_CA08/wintermean_orbitalvelocities
    WAVE_MODEL_CA08/wintermean_peakperiods
    WAVE_MODEL_CA09/wintermean_waveheights
    WAVE_MODEL_CA09/fallextreme_orbitalvelocities
    WAVE_MODEL_CA09/fallextreme_peakperiods
    WAVE_MODEL_CA09/fallextreme_waveheights
    WAVE_MODEL_CA09/fallmean_orbitalvelocities
    WAVE_MODEL_CA09/fallmean_peakperiods
    WAVE_MODEL_CA09/fallmean_waveheights
    WAVE_MODEL_CA09/springextreme_orbitalvelocities
    WAVE_MODEL_CA09/springextreme_peakperiods
    WAVE_MODEL_CA09/springextreme_waveheights
    WAVE_MODEL_CA09/springmean_orbitalvelocities
    WAVE_MODEL_CA09/springmean_peakperiods
    WAVE_MODEL_CA09/springmean_waveheights
    WAVE_MODEL_CA09/summerextreme_orbitalvelocities
    WAVE_MODEL_CA09/summerextreme_peakperiods
    WAVE_MODEL_CA09/summerextreme_waveheights
    WAVE_MODEL_CA09/summermean_orbitalvelocities
    WAVE_MODEL_CA09/summermean_peakperiods
    WAVE_MODEL_CA09/summermean_waveheights
    WAVE_MODEL_CA09/winterextreme_orbitalvelocities
    WAVE_MODEL_CA09/winterextreme_peakperiods
    WAVE_MODEL_CA09/winterextreme_waveheights
    WAVE_MODEL_CA09/wintermean_orbitalvelocities
    WAVE_MODEL_CA09/wintermean_peakperiods
    WAVE_MODEL_CA10/wintermean_waveheights
    WAVE_MODEL_CA10/fallextreme_orbitalvelocities
    WAVE_MODEL_CA10/fallextreme_peakperiods
    WAVE_MODEL_CA10/fallextreme_waveheights
    WAVE_MODEL_CA10/fallmean_orbitalvelocities
    WAVE_MODEL_CA10/fallmean_peakperiods
    WAVE_MODEL_CA10/fallmean_waveheights
    WAVE_MODEL_CA10/springextreme_orbitalvelocities
    WAVE_MODEL_CA10/springextreme_peakperiods
    WAVE_MODEL_CA10/springextreme_waveheights
    WAVE_MODEL_CA10/springmean_orbitalvelocities
    WAVE_MODEL_CA10/springmean_peakperiods
    WAVE_MODEL_CA10/springmean_waveheights
    WAVE_MODEL_CA10/summerextreme_orbitalvelocities
    WAVE_MODEL_CA10/summerextreme_peakperiods
    WAVE_MODEL_CA10/summerextreme_waveheights
    WAVE_MODEL_CA10/summermean_orbitalvelocities
    WAVE_MODEL_CA10/summermean_peakperiods
    WAVE_MODEL_CA10/summermean_waveheights
    WAVE_MODEL_CA10/winterextreme_orbitalvelocities
    WAVE_MODEL_CA10/winterextreme_peakperiods
    WAVE_MODEL_CA10/winterextreme_waveheights
    WAVE_MODEL_CA10/wintermean_orbitalvelocities
    WAVE_MODEL_CA10/wintermean_peakperiods
    WAVE_MODEL_CA11/wintermean_waveheights
    WAVE_MODEL_CA11/fallextreme_orbitalvelocities
    WAVE_MODEL_CA11/fallextreme_peakperiods
    WAVE_MODEL_CA11/fallextreme_waveheights
    WAVE_MODEL_CA11/fallmean_orbitalvelocities
    WAVE_MODEL_CA11/fallmean_peakperiods
    WAVE_MODEL_CA11/fallmean_waveheights
    WAVE_MODEL_CA11/springextreme_orbitalvelocities
    WAVE_MODEL_CA11/springextreme_peakperiods
    WAVE_MODEL_CA11/springextreme_waveheights
    WAVE_MODEL_CA11/springmean_orbitalvelocities
    WAVE_MODEL_CA11/springmean_peakperiods
    WAVE_MODEL_CA11/springmean_waveheights
    WAVE_MODEL_CA11/summerextreme_orbitalvelocities
    WAVE_MODEL_CA11/summerextreme_peakperiods
    WAVE_MODEL_CA11/summerextreme_waveheights
    WAVE_MODEL_CA11/summermean_orbitalvelocities
    WAVE_MODEL_CA11/summermean_peakperiods
    WAVE_MODEL_CA11/summermean_waveheights
    WAVE_MODEL_CA11/winterextreme_orbitalvelocities
    WAVE_MODEL_CA11/winterextreme_peakperiods
    WAVE_MODEL_CA11/winterextreme_waveheights
    WAVE_MODEL_CA11/wintermean_orbitalvelocities
    WAVE_MODEL_CA11/wintermean_peakperiods
    WAVE_MODEL_CA12/wintermean_waveheights
    WAVE_MODEL_CA12/fallextreme_orbitalvelocities
    WAVE_MODEL_CA12/fallextreme_peakperiods
    WAVE_MODEL_CA12/fallextreme_waveheights
    WAVE_MODEL_CA12/fallmean_orbitalvelocities
    WAVE_MODEL_CA12/fallmean_peakperiods
    WAVE_MODEL_CA12/fallmean_waveheights
    WAVE_MODEL_CA12/springextreme_orbitalvelocities
    WAVE_MODEL_CA12/springextreme_peakperiods
    WAVE_MODEL_CA12/springextreme_waveheights
    WAVE_MODEL_CA12/springmean_orbitalvelocities
    WAVE_MODEL_CA12/springmean_peakperiods
    WAVE_MODEL_CA12/springmean_waveheights
    WAVE_MODEL_CA12/summerextreme_orbitalvelocities
    WAVE_MODEL_CA12/summerextreme_peakperiods
    WAVE_MODEL_CA12/summerextreme_waveheights
    WAVE_MODEL_CA12/summermean_orbitalvelocities
    WAVE_MODEL_CA12/summermean_peakperiods
    WAVE_MODEL_CA12/summermean_waveheights
    WAVE_MODEL_CA12/winterextreme_orbitalvelocities
    WAVE_MODEL_CA12/winterextreme_peakperiods
    WAVE_MODEL_CA12/winterextreme_waveheights
    WAVE_MODEL_CA12/wintermean_orbitalvelocities
    WAVE_MODEL_CA12/wintermean_peakperiods
    WAVE_MODEL_CA13/wintermean_waveheights
    WAVE_MODEL_CA13/fallextreme_orbitalvelocities
    WAVE_MODEL_CA13/fallextreme_peakperiods
    WAVE_MODEL_CA13/fallextreme_waveheights
    WAVE_MODEL_CA13/fallmean_orbitalvelocities
    WAVE_MODEL_CA13/fallmean_peakperiods
    WAVE_MODEL_CA13/fallmean_waveheights
    WAVE_MODEL_CA13/springextreme_orbitalvelocities
    WAVE_MODEL_CA13/springextreme_peakperiods
    WAVE_MODEL_CA13/springextreme_waveheights
    WAVE_MODEL_CA13/springmean_orbitalvelocities
    WAVE_MODEL_CA13/springmean_peakperiods
    WAVE_MODEL_CA13/springmean_waveheights
    WAVE_MODEL_CA13/summerextreme_orbitalvelocities
    WAVE_MODEL_CA13/summerextreme_peakperiods
    WAVE_MODEL_CA13/summerextreme_waveheights
    WAVE_MODEL_CA13/summermean_orbitalvelocities
    WAVE_MODEL_CA13/summermean_peakperiods
    WAVE_MODEL_CA13/summermean_waveheights
    WAVE_MODEL_CA13/winterextreme_orbitalvelocities
    WAVE_MODEL_CA13/winterextreme_peakperiods
    WAVE_MODEL_CA13/winterextreme_waveheights
    WAVE_MODEL_CA13/wintermean_orbitalvelocities
    WAVE_MODEL_CA13/wintermean_peakperiods
    WAVE_MODEL_CA14/wintermean_waveheights
    WAVE_MODEL_CA14/fallextreme_orbitalvelocities
    WAVE_MODEL_CA14/fallextreme_peakperiods
    WAVE_MODEL_CA14/fallextreme_waveheights
    WAVE_MODEL_CA14/fallmean_orbitalvelocities
    WAVE_MODEL_CA14/fallmean_peakperiods
    WAVE_MODEL_CA14/fallmean_waveheights
    WAVE_MODEL_CA14/springextreme_orbitalvelocities
    WAVE_MODEL_CA14/springextreme_peakperiods
    WAVE_MODEL_CA14/springextreme_waveheights
    WAVE_MODEL_CA14/springmean_orbitalvelocities
    WAVE_MODEL_CA14/springmean_peakperiods
    WAVE_MODEL_CA14/springmean_waveheights
    WAVE_MODEL_CA14/summerextreme_orbitalvelocities
    WAVE_MODEL_CA14/summerextreme_peakperiods
    WAVE_MODEL_CA14/summerextreme_waveheights
    WAVE_MODEL_CA14/summermean_orbitalvelocities
    WAVE_MODEL_CA14/summermean_peakperiods
    WAVE_MODEL_CA14/summermean_waveheights
    WAVE_MODEL_CA14/winterextreme_orbitalvelocities
    WAVE_MODEL_CA14/winterextreme_peakperiods
    WAVE_MODEL_CA14/winterextreme_waveheights
    WAVE_MODEL_CA14/wintermean_orbitalvelocities
    WAVE_MODEL_CA14/wintermean_peakperiods
    WAVE_MODEL_CA15/wintermean_waveheights
    WAVE_MODEL_CA15/fallextreme_orbitalvelocities
    WAVE_MODEL_CA15/fallextreme_peakperiods
    WAVE_MODEL_CA15/fallextreme_waveheights
    WAVE_MODEL_CA15/fallmean_orbitalvelocities
    WAVE_MODEL_CA15/fallmean_peakperiods
    WAVE_MODEL_CA15/fallmean_waveheights
    WAVE_MODEL_CA15/springextreme_orbitalvelocities
    WAVE_MODEL_CA15/springextreme_peakperiods
    WAVE_MODEL_CA15/springextreme_waveheights
    WAVE_MODEL_CA15/springmean_orbitalvelocities
    WAVE_MODEL_CA15/springmean_peakperiods
    WAVE_MODEL_CA15/springmean_waveheights
    WAVE_MODEL_CA15/summerextreme_orbitalvelocities
    WAVE_MODEL_CA15/summerextreme_peakperiods
    WAVE_MODEL_CA15/summerextreme_waveheights
    WAVE_MODEL_CA15/summermean_orbitalvelocities
    WAVE_MODEL_CA15/summermean_peakperiods
    WAVE_MODEL_CA15/summermean_waveheights
    WAVE_MODEL_CA15/winterextreme_orbitalvelocities
    WAVE_MODEL_CA15/winterextreme_peakperiods
    WAVE_MODEL_CA15/winterextreme_waveheights
    WAVE_MODEL_CA15/wintermean_orbitalvelocities
    WAVE_MODEL_CA15/wintermean_peakperiods
    NODC_ARCTIC_REGIONAL_ClIMATOLOGY/sea_water_salinity
    NODC_ARCTIC_REGIONAL_ClIMATOLOGY/mean_sea_water_temperature
    COAMPS_4KM_RLTV_HUM/relative_humidity
    COAMPS_4KM_TTL_PRCP/total_precipitation_12-hour
    ERDATSSTA8DAY/sst
    ERDATSSTA1DAY/sst
    CA_DAS/zeta
    CA_DAS/temp
    CA_DAS/salt
    CA_DAS/u
    CA_DAS/v
    CA_DAS/sea_water_velocity
    WAVE_3/U-component_of_wind
    WAVE_3/Significant_height_of_swell_waves
    WAVE_3/Significant_height_of_wind_waves
    WAVE_3/Direction_of_swell_waves
    WAVE_3/Mean_period_of_swell_waves
    WAVE_3/Mean_period_of_wind_waves
    WAVE_3/Significant_height_of_combined_wind_waves_and_swell
    WAVE_3/Direction_of_wind_waves
    WAVE_3/Primary_wave_direction
    WAVE_3/V-component_of_wind
    WAVE_3/Primary_wave_mean_period
    WAVE_3/wind
    WAVE_1/Secondary_wave_mean_period
    WAVE_1/Mean_period_of_wind_waves
    WAVE_1/Wind_direction
    WAVE_1/Direction_of_wind_waves
    WAVE_1/v_wind
    WAVE_1/Primary_wave_direction
    WAVE_1/Secondary_wave_direction
    WAVE_1/Sig_height_of_wind_waves_and_swell
    WAVE_1/u_wind
    WAVE_1/Primary_wave_mean_period
    WAVE_1/wind
    G1_SST_US_WEST_COAST/analysed_sst
    COAMPS_4KM_VISIB/visibility
    COAMPS_4KM_CLD_BASE/cloud_base
    HIRE_WEST_CONUS/Temperature_surface
    HIRE_WEST_CONUS/Total_cloud_cover
    HIRE_WEST_CONUS/Total_precipitation
    HIRE_WEST_CONUS/Relative_humidity_surface
    HIRE_WEST_CONUS/V-component_of_wind_altitude_above_msl
    HIRE_WEST_CONUS/U-component_of_wind_altitude_above_msl
    HIRE_WEST_CONUS/wind_altitude_above_msl
    HYCOM/salinity
    HYCOM/temperature
    HYCOM/u
    HYCOM/v
    HYCOM/ssh
    HYCOM/sea_water_velocity
    IBCAO/z
    ERDATSSTAMDAY/sst
    ERDMWCHLA8DAY/chlorophyll
    GEBCO/z
    MB_DAS/zeta
    MB_DAS/temp
    MB_DAS/salt
    MB_DAS/u
    MB_DAS/v
    MB_DAS/sea_water_velocity
    SNAP_PRC_CRU/precipitation
    RAPID_REFRESH_UV10M/U-component_of_wind
    RAPID_REFRESH_UV10M/V-component_of_wind
    RAPID_REFRESH_UV10M/wind
    SNAP_A1B/precipitationA1B
    SNAP_A1B/airtemperatureA1B
    SNAP_A2/precipitationA2
    SNAP_A2/airtemperatureA2
    SNAP_B1/precipitationB1
    SNAP_B1/airtemperatureB1
    SNAP_TAVE_CRU/air_temperature
    WRF_MPH/GLW
    WRF_MPH/Q2
    WRF_MPH/RAINC
    WRF_MPH/RAINNC
    WRF_MPH/SST
    WRF_MPH/SWDOWN
    WRF_MPH/T2
    WRF_MPH/U10
    WRF_MPH/V10
    WRF_MPH/XLAT
    WRF_MPH/XLONG
    WRF_MPH/wind
    ShelikofStraits_CookInlet_DEM/mask
    ShelikofStraits_CookInlet_DEM/dx
    ShelikofStraits_CookInlet_DEM/dy
    ShelikofStraits_CookInlet_DEM/DEM
    NDFD_Significant_height_of_wind_waves/Significant_height_of_wind_waves
    ERDMWCHLAMDAY/chlorophyll
    ERDMWCHLA1DAY/chlorophyll
    NCOM_SOCAL/surf_atm_press
    NCOM_SOCAL/water_u
    NCOM_SOCAL/water_v
    NCOM_SOCAL/water_temp
    NCOM_SOCAL/salinity
    NCOM_SOCAL/sea_water_velocity
    NOAA_CSDL_ROMS/zeta
    NOAA_CSDL_ROMS/u
    NOAA_CSDL_ROMS/v
    NOAA_CSDL_ROMS/sea_water_velocity
    NCEP_SKIN_TEMP/skt
    WAVE_2/U-component_of_wind
    WAVE_2/Significant_height_of_swell_waves
    WAVE_2/Significant_height_of_wind_waves
    WAVE_2/Direction_of_swell_waves
    WAVE_2/Mean_period_of_swell_waves
    WAVE_2/Mean_period_of_wind_waves
    WAVE_2/Significant_height_of_combined_wind_waves_and_swell
    WAVE_2/Direction_of_wind_waves
    WAVE_2/Primary_wave_direction
    WAVE_2/V-component_of_wind
    WAVE_2/Primary_wave_mean_period
    WAVE_2/wind
    COAMPS_4KM_AGG_AIR_TEMP/air_temperature
    WRF_D01/T2
    WRF_D01/U10
    WRF_D01/V10
    WRF_D01/SNOW
    WRF_D01/SNOWH
    WRF_D01/SST
    WRF_D01/TSK
    WRF_D01/RAINNC
    WRF_D01/SNOWNC
    WRF_D01/TMN
    WRF_D01/wind
    WRF_D02/T2
    WRF_D02/U10
    WRF_D02/V10
    WRF_D02/SNOW
    WRF_D02/SNOWH
    WRF_D02/SST
    WRF_D02/TSK
    WRF_D02/RAINNC
    WRF_D02/SNOWNC
    WRF_D02/TMN
    WRF_D02/wind
    COAMPS_4KM_10M_WIND/u_component_wind_true_direction_all_geometries
    COAMPS_4KM_10M_WIND/v_component_wind_true_direction_all_geometries
    COAMPS_4KM_10M_WIND/wind
    COAMPS_4KM_2M_AIR_TEMP/air_temperature
    COAMPS_4KM_GRND_SEA_TEMP/temperature_of_ground_or_sea
    COAMPS_4KM_AGG_WIND/u_component_wind_true_direction_all_geometries
    COAMPS_4KM_AGG_WIND/v_component_wind_true_direction_all_geometries
    COAMPS_4KM_AGG_WIND/wind
    NDFD_Minimum_Temperature/Minimum_temperature
    PWS_L0_FCST/zeta
    PWS_L0_FCST/temp
    PWS_L0_FCST/salt
    PWS_L0_FCST/u
    PWS_L0_FCST/v
    PWS_L0_FCST/sea_water_velocity
    PWS_L1_FCST/zeta
    PWS_L1_FCST/temp
    PWS_L1_FCST/salt
    PWS_L1_FCST/u
    PWS_L1_FCST/v
    PWS_L1_FCST/sea_water_velocity
    CORDC/u
    CORDC/v
    CORDC/sea_water_velocity
    CORDC_USWC_500m/u
    CORDC_USWC_500m/v
    CORDC_USWC_500m/sea_water_velocity
    CORDC_USWC_6km/u
    CORDC_USWC_6km/v
    CORDC_USWC_6km/sea_water_velocity
    CORDC_USWC_2km/u
    CORDC_USWC_2km/v
    CORDC_USWC_2km/sea_water_velocity
    CORDC_USWC_1km/u
    CORDC_USWC_1km/v
    CORDC_USWC_1km/sea_water_velocity
    CORDC_USEGC_6km/u
    CORDC_USEGC_6km/v
    CORDC_USEGC_6km/sea_water_velocity
    CORDC_USEGC_2km/u
    CORDC_USEGC_2km/v
    CORDC_USEGC_2km/sea_water_velocity
    CORDC_USEGC_1km/u
    CORDC_USEGC_1km/v
    CORDC_USEGC_1km/sea_water_velocity
    TAMU_SWAN_PWS/Hs
    TAMU_SWAN_PWS/Tp
    TAMU_SWAN_PWS/Dp
    NSIDC_SEA_ICE_CON/latitude
    NSIDC_SEA_ICE_CON/longitude
    NSIDC_SEA_ICE_CON/Sea_Ice_Concentration
    MASIE/sea_ice
    PWS_L2_FCST/zeta
    PWS_L2_FCST/temp
    PWS_L2_FCST/salt
    PWS_L2_FCST/u
    PWS_L2_FCST/v
    PWS_L2_FCST/sea_water_velocity
    NDFD_Maximum_Temperature/Maximum_temperature
    NDFD_Total_Snowfall/Total_snowfall
    COAMPS_MBAY_3KM_WIND_10M/u_component_wind_true_direction_all_geometries
    COAMPS_MBAY_3KM_WIND_10M/v_component_wind_true_direction_all_geometries
    COAMPS_MBAY_3KM_WIND_10M/wind
    NDFD_Total_Precipitation/Total_precipitation
    MB_FCST/zeta
    MB_FCST/temp
    MB_FCST/salt
    MB_FCST/u
    MB_FCST/v
    MB_FCST/sea_water_velocity
    COAMPS_3KM_AGG_WIND/u_component_wind_true_direction_all_geometries
    COAMPS_3KM_AGG_WIND/v_component_wind_true_direction_all_geometries
    COAMPS_3KM_AGG_WIND/wind
    COAMPS_3KM_AGG_AIR_TEMP/air_temperature
    NDFD_Aggregate/Wind_direction_from_which_blowing
    NDFD_Aggregate/Wind_speed
    NDFD_Aggregate/Temperature_tendency_by_all_radiation
    NDFD_Aggregate/Relative_humidity
    NDFD_Aggregate/Total_cloud_cover
    NDFD_Aggregate/Dew_point_temperature
    NDFD_Aggregate/Temperature
    NDFD_Aggregate/eastward_wind
    NDFD_Aggregate/northward_wind
    NDFD_Aggregate/wind
    RAPID_REFRESH_SKIN_TEMP/Temperature
    RAPID_REFRESH_ACC_TOTAL_PRCP/Total_precipitation
    G1_SST/analysed_sst
    NDFD_Wind_Speed_Gust/Wind_speed_gust
    PWS_DAS/zeta
    PWS_DAS/temp
    PWS_DAS/salt
    PWS_DAS/u
    PWS_DAS/v
    PWS_DAS/sea_water_velocity
    CA_FCST/zeta
    CA_FCST/temp
    CA_FCST/salt
    CA_FCST/u
    CA_FCST/v
    CA_FCST/sea_water_velocity
    NAM_12_CONUS/Temperature_surface
    NAM_12_CONUS/Total_cloud_cover
    NAM_12_CONUS/Total_precipitation
    NAM_12_CONUS/Relative_humidity_height_above_ground
    NAM_12_CONUS/V-component_of_wind
    NAM_12_CONUS/U-component_of_wind
    NAM_12_CONUS/wind
    MUR/sea_ice_fraction
    UCSC/v
    UCSC/zeta
    UCSC/shflux
    UCSC/vbar
    UCSC/temp
    UCSC/salt
    UCSC/mask_v
    UCSC/u
    UCSC/mask_u
    UCSC/ubar
    UCSC/sea_water_velocity
    UCSC/viswv
    COAMPS_MBAY_3KM_AIR_TEMP/air_temperature
    SCB_DAS/zeta
    SCB_DAS/temp
    SCB_DAS/salt
    SCB_DAS/u
    SCB_DAS/v
    SCB_DAS/sea_water_velocity
    COAMPS_MBAY_3KM_GRND_SEA_TEMP/temperature_of_ground_or_sea
    PMEL_CCCMA1/sea_water_temperature
    PMEL_CCCMA1/small_phytoplankton_concentration
    PMEL_CCCMA1/large_phytoplankton_concentration
    PMEL_CCCMA1/large_microzooplankton_concentration
    PMEL_CCCMA1/small_coastal_copepod_concentration
    PMEL_CCCMA1/neocalanus_concentration
    PMEL_CCCMA1/offshore_neocalanus_concentration
    PMEL_CCCMA1/euphausiids_concentration
    PMEL_CCCMA1/detritus_concentration
    PMEL_CCCMA1/u_current
    PMEL_CCCMA1/v_current
    PMEL_CCCMA1/benthos_concentration
    PMEL_CCCMA1/ice_phytoplankton_concentration
    PMEL_CCCMA1/sea_ice_area_fraction
    PMEL_CCCMA1/current_velocity
    PMEL_CFSR/sea_water_temperature
    PMEL_CFSR/small_phytoplankton_concentration
    PMEL_CFSR/large_phytoplankton_concentration
    PMEL_CFSR/large_microzooplankton_concentration
    PMEL_CFSR/small_coastal_copepod_concentration
    PMEL_CFSR/neocalanus_concentration
    PMEL_CFSR/offshore_neocalanus_concentration
    PMEL_CFSR/euphausiids_concentration
    PMEL_CFSR/detritus_concentration
    PMEL_CFSR/u_current
    PMEL_CFSR/v_current
    PMEL_CFSR/benthos_concentration
    PMEL_CFSR/ice_phytoplankton_concentration
    PMEL_CFSR/sea_ice_area_fraction
    PMEL_CFSR/current_velocity
    PMEL_CORE/sea_water_temperature
    PMEL_CORE/small_phytoplankton_concentration
    PMEL_CORE/large_phytoplankton_concentration
    PMEL_CORE/large_microzooplankton_concentration
    PMEL_CORE/small_coastal_copepod_concentration
    PMEL_CORE/neocalanus_concentration
    PMEL_CORE/offshore_neocalanus_concentration
    PMEL_CORE/euphausiids_concentration
    PMEL_CORE/detritus_concentration
    PMEL_CORE/u_current
    PMEL_CORE/v_current
    PMEL_CORE/benthos_concentration
    PMEL_CORE/ice_phytoplankton_concentration
    PMEL_CORE/sea_ice_area_fraction
    PMEL_CORE/current_velocity
    PMEL_ECHOG/sea_water_temperature
    PMEL_ECHOG/small_phytoplankton_concentration
    PMEL_ECHOG/large_phytoplankton_concentration
    PMEL_ECHOG/large_microzooplankton_concentration
    PMEL_ECHOG/small_coastal_copepod_concentration
    PMEL_ECHOG/neocalanus_concentration
    PMEL_ECHOG/offshore_neocalanus_concentration
    PMEL_ECHOG/euphausiids_concentration
    PMEL_ECHOG/detritus_concentration
    PMEL_ECHOG/u_current
    PMEL_ECHOG/v_current
    PMEL_ECHOG/benthos_concentration
    PMEL_ECHOG/ice_phytoplankton_concentration
    PMEL_ECHOG/sea_ice_area_fraction
    PMEL_ECHOG/current_velocity
    PMEL_FORECAST/sea_water_temperature
    PMEL_FORECAST/small_phytoplankton_concentration
    PMEL_FORECAST/large_phytoplankton_concentration
    PMEL_FORECAST/large_microzooplankton_concentration
    PMEL_FORECAST/small_coastal_copepod_concentration
    PMEL_FORECAST/neocalanus_concentration
    PMEL_FORECAST/offshore_neocalanus_concentration
    PMEL_FORECAST/euphausiids_concentration
    PMEL_FORECAST/detritus_concentration
    PMEL_FORECAST/u_current
    PMEL_FORECAST/v_current
    PMEL_FORECAST/benthos_concentration
    PMEL_FORECAST/ice_phytoplankton_concentration
    PMEL_FORECAST/sea_ice_area_fraction
    PMEL_FORECAST/current_velocity
    PMEL_MIROC/sea_water_temperature
    PMEL_MIROC/small_phytoplankton_concentration
    PMEL_MIROC/large_phytoplankton_concentration
    PMEL_MIROC/large_microzooplankton_concentration
    PMEL_MIROC/small_coastal_copepod_concentration
    PMEL_MIROC/neocalanus_concentration
    PMEL_MIROC/offshore_neocalanus_concentration
    PMEL_MIROC/euphausiids_concentration
    PMEL_MIROC/detritus_concentration
    PMEL_MIROC/u_current
    PMEL_MIROC/v_current
    PMEL_MIROC/benthos_concentration
    PMEL_MIROC/ice_phytoplankton_concentration
    PMEL_MIROC/sea_ice_area_fraction
    PMEL_MIROC/current_velocity
    SNAP_JOHN_WALSH_SEA_ICE/ACCESS-1_sea_ice_concentration
    SNAP_JOHN_WALSH_SEA_ICE/CESM-CAM5_sea_ice_concentration
    SNAP_JOHN_WALSH_SEA_ICE/CMCC-CM_sea_ice_concentration
    SNAP_JOHN_WALSH_SEA_ICE/HAD-GEM2-AO_sea_ice_concentration
    SNAP_JOHN_WALSH_SEA_ICE/MIROC-5_sea_ice_concentration
    SNAP_JOHN_WALSH_HISTORICAL/GFDL-CM3_air_temperature
    SNAP_JOHN_WALSH_HISTORICAL/IPSL-CM5A-LR_air_temperature
    SNAP_JOHN_WALSH_HISTORICAL/MRI-CGCM3_air_temperature
    SNAP_JOHN_WALSH_HISTORICAL/GFDL-CM3_u_near_surface_wind
    SNAP_JOHN_WALSH_HISTORICAL/IPSL-CM5A-LR_u_near_surface_wind
    SNAP_JOHN_WALSH_HISTORICAL/MRI-CGCM3_u_near_surface_wind
    SNAP_JOHN_WALSH_HISTORICAL/GFDL-CM3_v_near_surface_wind
    SNAP_JOHN_WALSH_HISTORICAL/IPSL-CM5A-LR_v_near_surface_wind
    SNAP_JOHN_WALSH_HISTORICAL/MRI-CGCM3_v_near_surface_wind
    SNAP_JOHN_WALSH_HISTORICAL/wind-gfdl_cm3
    SNAP_JOHN_WALSH_HISTORICAL/wind-ipsl_cm5a_lr
    SNAP_JOHN_WALSH_HISTORICAL/wind-mri-cgcm3
    SNAP_JOHN_WALSH_RCP60/GFDL-CM3_air_temperature
    SNAP_JOHN_WALSH_RCP60/IPSL-CM5A-LR_air_temperature
    SNAP_JOHN_WALSH_RCP60/MRI-CGCM3_air_temperature
    SNAP_JOHN_WALSH_RCP60/GFDL-CM3_u_near_surface_wind
    SNAP_JOHN_WALSH_RCP60/IPSL-CM5A-LR_u_near_surface_wind
    SNAP_JOHN_WALSH_RCP60/MRI-CGCM3_u_near_surface_wind
    SNAP_JOHN_WALSH_RCP60/GFDL-CM3_v_near_surface_wind
    SNAP_JOHN_WALSH_RCP60/IPSL-CM5A-LR_v_near_surface_wind
    SNAP_JOHN_WALSH_RCP60/MRI-CGCM3_v_near_surface_wind
    SNAP_JOHN_WALSH_RCP60/wind-gfdl_cm3
    SNAP_JOHN_WALSH_RCP60/wind-ipsl_cm5a_lr
    SNAP_JOHN_WALSH_RCP60/wind-mri-cgcm3
    SNAP_JOHN_WALSH_RCP85/GFDL-CM3_air_temperature
    SNAP_JOHN_WALSH_RCP85/IPSL-CM5A-LR_air_temperature
    SNAP_JOHN_WALSH_RCP85/MRI-CGCM3_air_temperature
    SNAP_JOHN_WALSH_RCP85/GFDL-CM3_u_near_surface_wind
    SNAP_JOHN_WALSH_RCP85/IPSL-CM5A-LR_u_near_surface_wind
    SNAP_JOHN_WALSH_RCP85/MRI-CGCM3_u_near_surface_wind
    SNAP_JOHN_WALSH_RCP85/GFDL-CM3_v_near_surface_wind
    SNAP_JOHN_WALSH_RCP85/IPSL-CM5A-LR_v_near_surface_wind
    SNAP_JOHN_WALSH_RCP85/MRI-CGCM3_v_near_surface_wind
    SNAP_JOHN_WALSH_RCP85/wind-gfdl_cm3
    SNAP_JOHN_WALSH_RCP85/wind-ipsl_cm5a_lr
    SNAP_JOHN_WALSH_RCP85/wind-mri-cgcm3
    JPL_BERING_HINDCAST/aice
    JPL_BERING_HINDCAST/hice
    JPL_BERING_HINDCAST/u
    JPL_BERING_HINDCAST/uice
    JPL_BERING_HINDCAST/v
    JPL_BERING_HINDCAST/vice
    JPL_BERING_HINDCAST/zeta
    JPL_BERING_HINDCAST/dd
    JPL_BERING_HINDCAST/ddsi
    JPL_BERING_HINDCAST/nh4
    JPL_BERING_HINDCAST/no3
    JPL_BERING_HINDCAST/ox
    JPL_BERING_HINDCAST/po4
    JPL_BERING_HINDCAST/s1
    JPL_BERING_HINDCAST/s2
    JPL_BERING_HINDCAST/salt
    JPL_BERING_HINDCAST/sio4
    JPL_BERING_HINDCAST/talk
    JPL_BERING_HINDCAST/tco2
    JPL_BERING_HINDCAST/zz1
    JPL_BERING_HINDCAST/zz2
    JPL_BERING_HINDCAST/sea_water_velocity
    JPL_BERING_HINDCAST/ice_velocity
    ARDEM/z
    BERING_SEA_SEABIRD/allspp
    BERING_SEA_SEABIRD/alte
    BERING_SEA_SEABIRD/amwi
    BERING_SEA_SEABIRD/anmu
    BERING_SEA_SEABIRD/arte
    BERING_SEA_SEABIRD/bago
    BERING_SEA_SEABIRD/bfal
    BERING_SEA_SEABIRD/bhgu
    BERING_SEA_SEABIRD/blbr
    BERING_SEA_SEABIRD/blgu
    BERING_SEA_SEABIRD/blki
    BERING_SEA_SEABIRD/blsc
    BERING_SEA_SEABIRD/bogu
    BERING_SEA_SEABIRD/buff
    BERING_SEA_SEABIRD/bush
    BERING_SEA_SEABIRD/caau
    BERING_SEA_SEABIRD/cacg
    BERING_SEA_SEABIRD/canv
    BERING_SEA_SEABIRD/coei
    BERING_SEA_SEABIRD/cogo
    BERING_SEA_SEABIRD/colo
    BERING_SEA_SEABIRD/come
    BERING_SEA_SEABIRD/comu
    BERING_SEA_SEABIRD/cope
    BERING_SEA_SEABIRD/cote
    BERING_SEA_SEABIRD/crau
    BERING_SEA_SEABIRD/dcco
    BERING_SEA_SEABIRD/dove
    BERING_SEA_SEABIRD/emgo
    BERING_SEA_SEABIRD/ffsh
    BERING_SEA_SEABIRD/ftsp
    BERING_SEA_SEABIRD/gadw
    BERING_SEA_SEABIRD/glgu
    BERING_SEA_SEABIRD/grsc
    BERING_SEA_SEABIRD/gwgu
    BERING_SEA_SEABIRD/gwte
    BERING_SEA_SEABIRD/hadu
    BERING_SEA_SEABIRD/hegu
    BERING_SEA_SEABIRD/hogr
    BERING_SEA_SEABIRD/hopu
    BERING_SEA_SEABIRD/ivgu
    BERING_SEA_SEABIRD/kiei
    BERING_SEA_SEABIRD/kimu
    BERING_SEA_SEABIRD/laal
    BERING_SEA_SEABIRD/leau
    BERING_SEA_SEABIRD/lesc
    BERING_SEA_SEABIRD/lesp
    BERING_SEA_SEABIRD/ltdu
    BERING_SEA_SEABIRD/ltja
    BERING_SEA_SEABIRD/mall
    BERING_SEA_SEABIRD/mamu
    BERING_SEA_SEABIRD/megu
    BERING_SEA_SEABIRD/mope
    BERING_SEA_SEABIRD/mupe
    BERING_SEA_SEABIRD/nofu
    BERING_SEA_SEABIRD/nopi
    BERING_SEA_SEABIRD/paau
    BERING_SEA_SEABIRD/paja
    BERING_SEA_SEABIRD/palo
    BERING_SEA_SEABIRD/peco
    BERING_SEA_SEABIRD/pfsh
    BERING_SEA_SEABIRD/pigu
    BERING_SEA_SEABIRD/poja
    BERING_SEA_SEABIRD/rbme
    BERING_SEA_SEABIRD/reph
    BERING_SEA_SEABIRD/rfco
    BERING_SEA_SEABIRD/rhau
    BERING_SEA_SEABIRD/rlki
    BERING_SEA_SEABIRD/rngr
    BERING_SEA_SEABIRD/rnph
    BERING_SEA_SEABIRD/rogu
    BERING_SEA_SEABIRD/rtlo
    BERING_SEA_SEABIRD/sagu
    BERING_SEA_SEABIRD/sbgu
    BERING_SEA_SEABIRD/sksh
    BERING_SEA_SEABIRD/sope
    BERING_SEA_SEABIRD/spei
    BERING_SEA_SEABIRD/spsk
    BERING_SEA_SEABIRD/stal
    BERING_SEA_SEABIRD/stei
    BERING_SEA_SEABIRD/stpe
    BERING_SEA_SEABIRD/susc
    BERING_SEA_SEABIRD/swsp
    BERING_SEA_SEABIRD/tbmu
    BERING_SEA_SEABIRD/thgu
    BERING_SEA_SEABIRD/tupu
    BERING_SEA_SEABIRD/tusw
    BERING_SEA_SEABIRD/unds
    BERING_SEA_SEABIRD/whau
    BERING_SEA_SEABIRD/wwsc
    BERING_SEA_SEABIRD/yblo
    GRACE/lwe_thickness_of_soil_moisture_content
    MAURER/wind_speed
    MAURER/lwe_thickness_of_precipitation_amount
    MAURER/air_temperature_average
    MAURER/air_temperature_maximum
    MAURER/air_temperature_minimum
    Aquarius_V3_scat_wind_speed_Daily/scat_wind_speed
    Aquarius_V3_scat_wind_speed_Weekly/scat_wind_speed
    Aquarius_V3_scat_wind_speed_Monthly/scat_wind_speed
    Aquarius_V3_SSS_Daily/SSS
    Aquarius_V3_SSS_Weekly/SSS
    Aquarius_V3_SSS_Monthly/SSS
    ci_bathy_20090101/Band1
    ai_bathy_20090101/Band1
    MBON_FKNMS/seascape
    MBON_MBNMS/seascape
    cgoa_bathy_20090101/Band1
    norton_bathy_20090101/Band1
    usgs_cmg_bb_backscatter1m/Band1
    usgs_cmg_vs_backscatter_1m/Band1
    usgs_cmg_klein_2011-013_1m/Band1
    usgs_cmg_bh_1mbs/Band1
    usgs_cmg_ccb_klein_bs_1m/Band1
    usgs_cmg_ccb_swath_bs_1m/Band1
    usgs_cmg_dh_usgs_backscatter1m/Band1
    usgs_cmg_dh_noaa_backscatter1m/Band1
    usgs_cmg_mb_backgs10m/Band1
    usgs_cmg_ss_mos1m/Band1
    usgs_cmg_klein_bs1m/Band1
    usgs_cmg_reson_bs5m/Band1
    usgs_cmg_bbvs_group/Band1
    usgs_cmg_massbay_group/Band1
    secoora_skio_hfradar/u
    secoora_skio_hfradar/uacc
    secoora_skio_hfradar/v
    secoora_skio_hfradar/vacc
    secoora_skio_hfradar/sea_water_velocity
    secoora_skio_hfradar/sea_water_velocity_accuracy
    secoora_long_bay_hfradar/u
    secoora_long_bay_hfradar/uacc
    secoora_long_bay_hfradar/v
    secoora_long_bay_hfradar/vacc
    secoora_long_bay_hfradar/sea_water_velocity
    secoora_long_bay_hfradar/sea_water_velocity_accuracy
    secoora_tampa_bay_wera_hfradar/u
    secoora_tampa_bay_wera_hfradar/uacc
    secoora_tampa_bay_wera_hfradar/v
    secoora_tampa_bay_wera_hfradar/vacc
    secoora_tampa_bay_wera_hfradar/sea_water_velocity
    secoora_tampa_bay_wera_hfradar/sea_water_velocity_accuracy
    secoora_tampa_bay_codar_hfradar/u
    secoora_tampa_bay_codar_hfradar/v
    secoora_tampa_bay_codar_hfradar/sea_water_velocity
    MARACOOS_NYHOPS_RIVERSONDE/depth
    MARACOOS_NYHOPS_RIVERSONDE/airt
    MARACOOS_NYHOPS_RIVERSONDE/cld
    MARACOOS_NYHOPS_RIVERSONDE/elev
    MARACOOS_NYHOPS_RIVERSONDE/patm
    MARACOOS_NYHOPS_RIVERSONDE/rhum
    MARACOOS_NYHOPS_RIVERSONDE/swobs
    MARACOOS_NYHOPS_RIVERSONDE/wd
    MARACOOS_NYHOPS_RIVERSONDE/wh
    MARACOOS_NYHOPS_RIVERSONDE/wp
    MARACOOS_NYHOPS_RIVERSONDE/wu
    MARACOOS_NYHOPS_RIVERSONDE/wv
    MARACOOS_NYHOPS_RIVERSONDE/salt
    MARACOOS_NYHOPS_RIVERSONDE/temp
    MARACOOS_NYHOPS_RIVERSONDE/u
    MARACOOS_NYHOPS_RIVERSONDE/v
    MARACOOS_NYHOPS_RIVERSONDE/wind
    MARACOOS_NYHOPS_NYBIGHT/depth
    MARACOOS_NYHOPS_NYBIGHT/airt
    MARACOOS_NYHOPS_NYBIGHT/cld
    MARACOOS_NYHOPS_NYBIGHT/elev
    MARACOOS_NYHOPS_NYBIGHT/patm
    MARACOOS_NYHOPS_NYBIGHT/rhum
    MARACOOS_NYHOPS_NYBIGHT/swobs
    MARACOOS_NYHOPS_NYBIGHT/wd
    MARACOOS_NYHOPS_NYBIGHT/wh
    MARACOOS_NYHOPS_NYBIGHT/wp
    MARACOOS_NYHOPS_NYBIGHT/wu
    MARACOOS_NYHOPS_NYBIGHT/wv
    MARACOOS_NYHOPS_NYBIGHT/salt
    MARACOOS_NYHOPS_NYBIGHT/temp
    MARACOOS_NYHOPS_NYBIGHT/u
    MARACOOS_NYHOPS_NYBIGHT/v
    MARACOOS_NYHOPS_NYBIGHT/wind
    MARACOOS_NYHOPS_NYBIGHTAPEX/depth
    MARACOOS_NYHOPS_NYBIGHTAPEX/airt
    MARACOOS_NYHOPS_NYBIGHTAPEX/cld
    MARACOOS_NYHOPS_NYBIGHTAPEX/elev
    MARACOOS_NYHOPS_NYBIGHTAPEX/patm
    MARACOOS_NYHOPS_NYBIGHTAPEX/rhum
    MARACOOS_NYHOPS_NYBIGHTAPEX/swobs
    MARACOOS_NYHOPS_NYBIGHTAPEX/wd
    MARACOOS_NYHOPS_NYBIGHTAPEX/wh
    MARACOOS_NYHOPS_NYBIGHTAPEX/wp
    MARACOOS_NYHOPS_NYBIGHTAPEX/wu
    MARACOOS_NYHOPS_NYBIGHTAPEX/wv
    MARACOOS_NYHOPS_NYBIGHTAPEX/salt
    MARACOOS_NYHOPS_NYBIGHTAPEX/temp
    MARACOOS_NYHOPS_NYBIGHTAPEX/u
    MARACOOS_NYHOPS_NYBIGHTAPEX/v
    MARACOOS_NYHOPS_NYBIGHTAPEX/wind
    MARACOOS_NYHOPS_RARITANBAY/depth
    MARACOOS_NYHOPS_RARITANBAY/airt
    MARACOOS_NYHOPS_RARITANBAY/cld
    MARACOOS_NYHOPS_RARITANBAY/elev
    MARACOOS_NYHOPS_RARITANBAY/patm
    MARACOOS_NYHOPS_RARITANBAY/rhum
    MARACOOS_NYHOPS_RARITANBAY/swobs
    MARACOOS_NYHOPS_RARITANBAY/wd
    MARACOOS_NYHOPS_RARITANBAY/wh
    MARACOOS_NYHOPS_RARITANBAY/wp
    MARACOOS_NYHOPS_RARITANBAY/wu
    MARACOOS_NYHOPS_RARITANBAY/wv
    MARACOOS_NYHOPS_RARITANBAY/salt
    MARACOOS_NYHOPS_RARITANBAY/temp
    MARACOOS_NYHOPS_RARITANBAY/u
    MARACOOS_NYHOPS_RARITANBAY/v
    MARACOOS_NYHOPS_RARITANBAY/wind
    MARACOOS_ESPRESSO1/v
    MARACOOS_ESPRESSO1/angle
    MARACOOS_ESPRESSO1/f
    MARACOOS_ESPRESSO1/h
    MARACOOS_ESPRESSO1/mask_rho
    MARACOOS_ESPRESSO1/pm
    MARACOOS_ESPRESSO1/pn
    MARACOOS_ESPRESSO1/mask_psi
    MARACOOS_ESPRESSO1/shflux
    MARACOOS_ESPRESSO1/swrad
    MARACOOS_ESPRESSO1/zeta
    MARACOOS_ESPRESSO1/DV_avg1
    MARACOOS_ESPRESSO1/DV_avg2
    MARACOOS_ESPRESSO1/svstr
    MARACOOS_ESPRESSO1/vbar
    MARACOOS_ESPRESSO1/salt
    MARACOOS_ESPRESSO1/temp
    MARACOOS_ESPRESSO1/urot
    MARACOOS_ESPRESSO1/vrot
    MARACOOS_ESPRESSO1/mask_v
    MARACOOS_ESPRESSO1/u
    MARACOOS_ESPRESSO1/AKs
    MARACOOS_ESPRESSO1/AKt
    MARACOOS_ESPRESSO1/AKv
    MARACOOS_ESPRESSO1/w
    MARACOOS_ESPRESSO1/mask_u
    MARACOOS_ESPRESSO1/DU_avg1
    MARACOOS_ESPRESSO1/DU_avg2
    MARACOOS_ESPRESSO1/sustr
    MARACOOS_ESPRESSO1/ubar
    MARACOOS_ESPRESSO1/sea_water_velocity
    MARACOOS_ESPRESSO2/angle
    MARACOOS_ESPRESSO2/f
    MARACOOS_ESPRESSO2/h
    MARACOOS_ESPRESSO2/mask_rho
    MARACOOS_ESPRESSO2/pm
    MARACOOS_ESPRESSO2/pn
    MARACOOS_ESPRESSO2/mask_psi
    MARACOOS_ESPRESSO2/v
    SECOORA_NCSU_SABGOM/u
    SECOORA_NCSU_SABGOM/angle
    SECOORA_NCSU_SABGOM/f
    SECOORA_NCSU_SABGOM/h
    SECOORA_NCSU_SABGOM/mask_rho
    SECOORA_NCSU_SABGOM/pm
    SECOORA_NCSU_SABGOM/pn
    SECOORA_NCSU_SABGOM/zeta
    SECOORA_NCSU_SABGOM/v
    SECOORA_NCSU_SABGOM/mask_psi
    SECOORA_NCSU_SABGOM/ubar
    SECOORA_NCSU_SABGOM/mask_v
    SECOORA_NCSU_SABGOM/NH4
    SECOORA_NCSU_SABGOM/NO3
    SECOORA_NCSU_SABGOM/chlorophyll
    SECOORA_NCSU_SABGOM/phytoplankton
    SECOORA_NCSU_SABGOM/salt
    SECOORA_NCSU_SABGOM/temp
    SECOORA_NCSU_SABGOM/zooplankton
    SECOORA_NCSU_SABGOM/urot
    SECOORA_NCSU_SABGOM/vrot
    SECOORA_NCSU_SABGOM/w
    SECOORA_NCSU_SABGOM/mask_u
    SECOORA_NCSU_SABGOM/vbar
    SECOORA_NCSU_SABGOM/sea_water_velocity
    SECOORA_NCSU_USEAST/u
    SECOORA_NCSU_USEAST/bustr
    SECOORA_NCSU_USEAST/sustr
    SECOORA_NCSU_USEAST/v
    SECOORA_NCSU_USEAST/ubar
    SECOORA_NCSU_USEAST/bvstr
    SECOORA_NCSU_USEAST/svstr
    SECOORA_NCSU_USEAST/salt
    SECOORA_NCSU_USEAST/temp
    SECOORA_NCSU_USEAST/urot
    SECOORA_NCSU_USEAST/vrot
    SECOORA_NCSU_USEAST/w
    SECOORA_NCSU_USEAST/mask_u
    SECOORA_NCSU_USEAST/angle
    SECOORA_NCSU_USEAST/f
    SECOORA_NCSU_USEAST/h
    SECOORA_NCSU_USEAST/mask_rho
    SECOORA_NCSU_USEAST/pm
    SECOORA_NCSU_USEAST/pn
    SECOORA_NCSU_USEAST/Dwave
    SECOORA_NCSU_USEAST/Hwave
    SECOORA_NCSU_USEAST/Lwave
    SECOORA_NCSU_USEAST/evaporation
    SECOORA_NCSU_USEAST/latent
    SECOORA_NCSU_USEAST/lwrad
    SECOORA_NCSU_USEAST/rain
    SECOORA_NCSU_USEAST/sensible
    SECOORA_NCSU_USEAST/shflux
    SECOORA_NCSU_USEAST/ssflux
    SECOORA_NCSU_USEAST/swrad
    SECOORA_NCSU_USEAST/zeta
    SECOORA_NCSU_USEAST/mask_psi
    SECOORA_NCSU_USEAST/mask_v
    SECOORA_NCSU_USEAST/vbar
    SECOORA_NCSU_USEAST/sea_water_velocity
    CIDA_STAGE4_PRECIP/Total_precipitation_surface_1_Hour_Accumulation
    HIOMAS/dxt
    HIOMAS/dyt
    HIOMAS/kmt
    HIOMAS/kmu
    HIOMAS/so
    HIOMAS/to
    HIOMAS/uo
    HIOMAS/vo
    HIOMAS/aiday
    HIOMAS/hiday
    HIOMAS/snowday
    HIOMAS/ssh
    HIOMAS/uiday
    HIOMAS/viday
    HIOMAS/sea_water_velocity
    HIOMAS/sea_ice_velocity
    GINA_UAF_BARROW_SEAICE/bs

</pre>
</div>
Getting the first one from the service list for our example.

<div class="prompt input_prompt">
In&nbsp;[18]:
</div>

```python
layer = list(service.contents.keys())[0]

wms = service.contents[layer]

lon = (wms.boundingBox[0] + wms.boundingBox[2]) / 2.
lat = (wms.boundingBox[1] + wms.boundingBox[3]) / 2.
```

<div class="prompt input_prompt">
In&nbsp;[19]:
</div>

```python
import folium

m = folium.Map(location=[lat, lon], zoom_start=3)

folium.WmsTileLayer(name='{} at {}'.format(wms.title,
                                           wms.defaulttimeposition),
                    url=url,
                    layers=layer,
                    format='image/png').add_to(m)

folium.LayerControl().add_to(m)

m
```




<div style="width:100%;"><div style="position:relative;width:100%;height:0;padding-bottom:60%;"><iframe src="data:text/html;base64,CiAgICAgICAgPCFET0NUWVBFIGh0bWw+CiAgICAgICAgPGhlYWQ+CiAgICAgICAgICAgIAogICAgICAgIAogICAgICAgICAgICA8bWV0YSBodHRwLWVxdWl2PSJjb250ZW50LXR5cGUiIGNvbnRlbnQ9InRleHQvaHRtbDsgY2hhcnNldD1VVEYtOCIgLz4KICAgICAgICAKICAgICAgICAgICAgCiAgICAgICAgCiAgICAgICAgICAgIDxzY3JpcHQgc3JjPSJodHRwczovL2NkbmpzLmNsb3VkZmxhcmUuY29tL2FqYXgvbGlicy9sZWFmbGV0LzAuNy4zL2xlYWZsZXQuanMiPjwvc2NyaXB0PgogICAgICAgIAogICAgICAgIAogICAgICAgIAogICAgICAgICAgICAKICAgICAgICAKICAgICAgICAgICAgPHNjcmlwdCBzcmM9Imh0dHBzOi8vYWpheC5nb29nbGVhcGlzLmNvbS9hamF4L2xpYnMvanF1ZXJ5LzEuMTEuMS9qcXVlcnkubWluLmpzIj48L3NjcmlwdD4KICAgICAgICAKICAgICAgICAKICAgICAgICAKICAgICAgICAgICAgCiAgICAgICAgCiAgICAgICAgICAgIDxzY3JpcHQgc3JjPSJodHRwczovL21heGNkbi5ib290c3RyYXBjZG4uY29tL2Jvb3RzdHJhcC8zLjIuMC9qcy9ib290c3RyYXAubWluLmpzIj48L3NjcmlwdD4KICAgICAgICAKICAgICAgICAKICAgICAgICAKICAgICAgICAgICAgCiAgICAgICAgCiAgICAgICAgICAgIDxzY3JpcHQgc3JjPSJodHRwczovL2NkbmpzLmNsb3VkZmxhcmUuY29tL2FqYXgvbGlicy9MZWFmbGV0LmF3ZXNvbWUtbWFya2Vycy8yLjAuMi9sZWFmbGV0LmF3ZXNvbWUtbWFya2Vycy5taW4uanMiPjwvc2NyaXB0PgogICAgICAgIAogICAgICAgIAogICAgICAgIAogICAgICAgICAgICAKICAgICAgICAKICAgICAgICAgICAgPHNjcmlwdCBzcmM9Imh0dHBzOi8vY2RuanMuY2xvdWRmbGFyZS5jb20vYWpheC9saWJzL2xlYWZsZXQubWFya2VyY2x1c3Rlci8wLjQuMC9sZWFmbGV0Lm1hcmtlcmNsdXN0ZXItc3JjLmpzIj48L3NjcmlwdD4KICAgICAgICAKICAgICAgICAKICAgICAgICAKICAgICAgICAgICAgCiAgICAgICAgCiAgICAgICAgICAgIDxzY3JpcHQgc3JjPSJodHRwczovL2NkbmpzLmNsb3VkZmxhcmUuY29tL2FqYXgvbGlicy9sZWFmbGV0Lm1hcmtlcmNsdXN0ZXIvMC40LjAvbGVhZmxldC5tYXJrZXJjbHVzdGVyLmpzIj48L3NjcmlwdD4KICAgICAgICAKICAgICAgICAKICAgICAgICAKICAgICAgICAgICAgCiAgICAgICAgCiAgICAgICAgICAgIDxsaW5rIHJlbD0ic3R5bGVzaGVldCIgaHJlZj0iaHR0cHM6Ly9jZG5qcy5jbG91ZGZsYXJlLmNvbS9hamF4L2xpYnMvbGVhZmxldC8wLjcuMy9sZWFmbGV0LmNzcyIgLz4KICAgICAgICAKICAgICAgICAKICAgICAgICAKICAgICAgICAgICAgCiAgICAgICAgCiAgICAgICAgICAgIDxsaW5rIHJlbD0ic3R5bGVzaGVldCIgaHJlZj0iaHR0cHM6Ly9tYXhjZG4uYm9vdHN0cmFwY2RuLmNvbS9ib290c3RyYXAvMy4yLjAvY3NzL2Jvb3RzdHJhcC5taW4uY3NzIiAvPgogICAgICAgIAogICAgICAgIAogICAgICAgIAogICAgICAgICAgICAKICAgICAgICAKICAgICAgICAgICAgPGxpbmsgcmVsPSJzdHlsZXNoZWV0IiBocmVmPSJodHRwczovL21heGNkbi5ib290c3RyYXBjZG4uY29tL2Jvb3RzdHJhcC8zLjIuMC9jc3MvYm9vdHN0cmFwLXRoZW1lLm1pbi5jc3MiIC8+CiAgICAgICAgCiAgICAgICAgCiAgICAgICAgCiAgICAgICAgICAgIAogICAgICAgIAogICAgICAgICAgICA8bGluayByZWw9InN0eWxlc2hlZXQiIGhyZWY9Imh0dHBzOi8vbWF4Y2RuLmJvb3RzdHJhcGNkbi5jb20vZm9udC1hd2Vzb21lLzQuMS4wL2Nzcy9mb250LWF3ZXNvbWUubWluLmNzcyIgLz4KICAgICAgICAKICAgICAgICAKICAgICAgICAKICAgICAgICAgICAgCiAgICAgICAgCiAgICAgICAgICAgIDxsaW5rIHJlbD0ic3R5bGVzaGVldCIgaHJlZj0iaHR0cHM6Ly9jZG5qcy5jbG91ZGZsYXJlLmNvbS9hamF4L2xpYnMvTGVhZmxldC5hd2Vzb21lLW1hcmtlcnMvMi4wLjIvbGVhZmxldC5hd2Vzb21lLW1hcmtlcnMuY3NzIiAvPgogICAgICAgIAogICAgICAgIAogICAgICAgIAogICAgICAgICAgICAKICAgICAgICAKICAgICAgICAgICAgPGxpbmsgcmVsPSJzdHlsZXNoZWV0IiBocmVmPSJodHRwczovL2NkbmpzLmNsb3VkZmxhcmUuY29tL2FqYXgvbGlicy9sZWFmbGV0Lm1hcmtlcmNsdXN0ZXIvMC40LjAvTWFya2VyQ2x1c3Rlci5EZWZhdWx0LmNzcyIgLz4KICAgICAgICAKICAgICAgICAKICAgICAgICAKICAgICAgICAgICAgCiAgICAgICAgCiAgICAgICAgICAgIDxsaW5rIHJlbD0ic3R5bGVzaGVldCIgaHJlZj0iaHR0cHM6Ly9jZG5qcy5jbG91ZGZsYXJlLmNvbS9hamF4L2xpYnMvbGVhZmxldC5tYXJrZXJjbHVzdGVyLzAuNC4wL01hcmtlckNsdXN0ZXIuY3NzIiAvPgogICAgICAgIAogICAgICAgIAogICAgICAgIAogICAgICAgICAgICAKICAgICAgICAKICAgICAgICAgICAgPGxpbmsgcmVsPSJzdHlsZXNoZWV0IiBocmVmPSJodHRwczovL3Jhdy5naXRodWJ1c2VyY29udGVudC5jb20vcHl0aG9uLXZpc3VhbGl6YXRpb24vZm9saXVtL21hc3Rlci9mb2xpdW0vdGVtcGxhdGVzL2xlYWZsZXQuYXdlc29tZS5yb3RhdGUuY3NzIiAvPgogICAgICAgIAogICAgICAgIAogICAgICAgIAogICAgICAgICAgICAKICAgICAgICAgICAgPHN0eWxlPgoKICAgICAgICAgICAgaHRtbCwgYm9keSB7CiAgICAgICAgICAgICAgICB3aWR0aDogMTAwJTsKICAgICAgICAgICAgICAgIGhlaWdodDogMTAwJTsKICAgICAgICAgICAgICAgIG1hcmdpbjogMDsKICAgICAgICAgICAgICAgIHBhZGRpbmc6IDA7CiAgICAgICAgICAgICAgICB9CgogICAgICAgICAgICAjbWFwIHsKICAgICAgICAgICAgICAgIHBvc2l0aW9uOmFic29sdXRlOwogICAgICAgICAgICAgICAgdG9wOjA7CiAgICAgICAgICAgICAgICBib3R0b206MDsKICAgICAgICAgICAgICAgIHJpZ2h0OjA7CiAgICAgICAgICAgICAgICBsZWZ0OjA7CiAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgIDwvc3R5bGU+CiAgICAgICAgICAgIAogICAgICAgIAogICAgICAgICAgICAKICAgICAgICAgICAgPHN0eWxlPiAjbWFwX2JjOTFjZTlkMGMwZjQxZGU4NDViNjZlZjA0MGViZDMyIHsKICAgICAgICAgICAgICAgIHBvc2l0aW9uIDogcmVsYXRpdmU7CiAgICAgICAgICAgICAgICB3aWR0aCA6IDEwMC4wJTsKICAgICAgICAgICAgICAgIGhlaWdodDogMTAwLjAlOwogICAgICAgICAgICAgICAgbGVmdDogMC4wJTsKICAgICAgICAgICAgICAgIHRvcDogMC4wJTsKICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgPC9zdHlsZT4KICAgICAgICAKICAgICAgICAKICAgICAgICAKICAgICAgICA8L2hlYWQ+CiAgICAgICAgPGJvZHk+CiAgICAgICAgICAgIAogICAgICAgIAogICAgICAgICAgICAKICAgICAgICAgICAgPGRpdiBjbGFzcz0iZm9saXVtLW1hcCIgaWQ9Im1hcF9iYzkxY2U5ZDBjMGY0MWRlODQ1YjY2ZWYwNDBlYmQzMiIgPjwvZGl2PgogICAgICAgIAogICAgICAgIAogICAgICAgIAogICAgICAgIDwvYm9keT4KICAgICAgICA8c2NyaXB0PgogICAgICAgICAgICAKICAgICAgICAKICAgICAgICAgICAgCgogICAgICAgICAgICB2YXIgc291dGhXZXN0ID0gTC5sYXRMbmcoLTkwLCAtMTgwKTsKICAgICAgICAgICAgdmFyIG5vcnRoRWFzdCA9IEwubGF0TG5nKDkwLCAxODApOwogICAgICAgICAgICB2YXIgYm91bmRzID0gTC5sYXRMbmdCb3VuZHMoc291dGhXZXN0LCBub3J0aEVhc3QpOwoKICAgICAgICAgICAgdmFyIG1hcF9iYzkxY2U5ZDBjMGY0MWRlODQ1YjY2ZWYwNDBlYmQzMiA9IEwubWFwKCdtYXBfYmM5MWNlOWQwYzBmNDFkZTg0NWI2NmVmMDQwZWJkMzInLCB7CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBjZW50ZXI6WzUyLjI0MjkyMzM4NDI5NzIsLTEzNi4xMTE5NDYzNjI5ODI3Nl0sCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICB6b29tOiAzLAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgbWF4Qm91bmRzOiBib3VuZHMsCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBsYXllcnM6IFtdLAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgY3JzOiBMLkNSUy5FUFNHMzg1NwogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIH0pOwogICAgICAgICAgICAKICAgICAgICAKICAgICAgICAKICAgICAgICAgICAgCiAgICAgICAgICAgIHZhciB0aWxlX2xheWVyX2ZhYmY2N2Y5MGM2NTQ2N2M4ZTlkZDI0NWVmZTFiNDM2ID0gTC50aWxlTGF5ZXIoCiAgICAgICAgICAgICAgICAnaHR0cHM6Ly97c30udGlsZS5vcGVuc3RyZWV0bWFwLm9yZy97en0ve3h9L3t5fS5wbmcnLAogICAgICAgICAgICAgICAgewogICAgICAgICAgICAgICAgICAgIG1heFpvb206IDE4LAogICAgICAgICAgICAgICAgICAgIG1pblpvb206IDEsCiAgICAgICAgICAgICAgICAgICAgYXR0cmlidXRpb246ICdEYXRhIGJ5IDxhIGhyZWY9Imh0dHA6Ly9vcGVuc3RyZWV0bWFwLm9yZyI+T3BlblN0cmVldE1hcDwvYT4sIHVuZGVyIDxhIGhyZWY9Imh0dHA6Ly93d3cub3BlbnN0cmVldG1hcC5vcmcvY29weXJpZ2h0Ij5PRGJMPC9hPi4nLAogICAgICAgICAgICAgICAgICAgIGRldGVjdFJldGluYTogZmFsc2UKICAgICAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgICAgICApLmFkZFRvKG1hcF9iYzkxY2U5ZDBjMGY0MWRlODQ1YjY2ZWYwNDBlYmQzMik7CgogICAgICAgIAogICAgICAgIAogICAgICAgICAgICAKICAgICAgICAgICAgdmFyIG1hY3JvX2VsZW1lbnRfOGJhMjdjM2EwOGUyNDAyNTg1NTc4MTk0M2ZkNmE3YWEgPSBMLnRpbGVMYXllci53bXMoCiAgICAgICAgICAgICAgICAnaHR0cDovL3BkeC5heGlvbWFsYXNrYS5jb20vbmNXTVMvd21zJywKICAgICAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgICAgICBsYXllcnM6ICdOREZEXzIwMTZfVG90YWxfU25vd2ZhbGwvVG90YWxfc25vd2ZhbGwnLAogICAgICAgICAgICAgICAgICAgIHN0eWxlczogJycsCiAgICAgICAgICAgICAgICAgICAgZm9ybWF0OiAnaW1hZ2UvcG5nJywKICAgICAgICAgICAgICAgICAgICB0cmFuc3BhcmVudDogdHJ1ZSwKICAgICAgICAgICAgICAgICAgICB2ZXJzaW9uOiAnMS4xLjEnLAogICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgICkuYWRkVG8obWFwX2JjOTFjZTlkMGMwZjQxZGU4NDViNjZlZjA0MGViZDMyKTsKCiAgICAgICAgCiAgICAgICAgCiAgICAgICAgICAgIAogICAgICAgICAgICB2YXIgbGF5ZXJfY29udHJvbF8zMGViMmUyOTU3YjY0ZjJjYjY4ZjVjYmZjODJmMGViZSA9IHsKICAgICAgICAgICAgICAgIGJhc2VfbGF5ZXJzIDogeyAib3BlbnN0cmVldG1hcCIgOiB0aWxlX2xheWVyX2ZhYmY2N2Y5MGM2NTQ2N2M4ZTlkZDI0NWVmZTFiNDM2LCB9LAogICAgICAgICAgICAgICAgb3ZlcmxheXMgOiB7ICJ0aGlja25lc3Nfb2Zfc25vd2ZhbGxfYW1vdW50IGF0IDIwMTYtMDktMTRUMTg6MDA6MDAuMDAwWiIgOiBtYWNyb19lbGVtZW50XzhiYTI3YzNhMDhlMjQwMjU4NTU3ODE5NDNmZDZhN2FhLCB9CiAgICAgICAgICAgICAgICB9OwogICAgICAgICAgICBMLmNvbnRyb2wubGF5ZXJzKAogICAgICAgICAgICAgICAgbGF5ZXJfY29udHJvbF8zMGViMmUyOTU3YjY0ZjJjYjY4ZjVjYmZjODJmMGViZS5iYXNlX2xheWVycywKICAgICAgICAgICAgICAgIGxheWVyX2NvbnRyb2xfMzBlYjJlMjk1N2I2NGYyY2I2OGY1Y2JmYzgyZjBlYmUub3ZlcmxheXMKICAgICAgICAgICAgICAgICkuYWRkVG8obWFwX2JjOTFjZTlkMGMwZjQxZGU4NDViNjZlZjA0MGViZDMyKTsKICAgICAgICAKICAgICAgICAKICAgICAgICAKICAgICAgICA8L3NjcmlwdD4KICAgICAgICA=" style="position:absolute;width:100%;height:100%;left:0;top:0;"></iframe></div></div>


