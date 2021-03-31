# Using the `xtractomatic` R package to track Pacific Blue Marlin

The `xtractomatic` package can be used to subset data from remote servers. From the [GitHub README](https://github.com/rmendels/xtractomatic):

    xtractomatic is an R package developed to subset and extract satellite and other oceanographic related data from a remote server. The program can extract data for a moving point in time along a user-supplied set of longitude, latitude and time points; in a 3D bounding box; or within a polygon (through time). The xtractomatic functions were originally developed for the marine biology tagging community, to match up environmental data available from satellites (sea-surface temperature, sea-surface chlorophyll, sea-surface height, sea-surface salinity, vector winds) to track data from various tagged animals or shiptracks

There are routines to extract data from a `lon`, `lat`, `time` track (like a drifter or glider trajectory), a 3D bounding box, or within a polygon. For this example let us use the built-in dataset for the tagged blue marlin fish in the Pacific Ocean (`Marlintag38606`).

library('xtractomatic')

str(Marlintag38606)

This is a "track-like" data set of the tagged marlin with `lon`, `lat`, `time` arrays.

tagData <- Marlintag38606
xpos <- tagData$lon
ypos <- tagData$lat
tpos <- tagData$date

Now we can extract, for example, SeaWiFS chlorophyll 8 day composite(`swchla8day`) data around the recorded tags to see if the marlin follow areas of high productivity to presumably find food.

Note the that `xlen=0.2` and `ylen=0.2` is the bounding latitude/longitude box (in decimal degrees) for finding the data around the desired positions

swchl <- xtracto(xpos, ypos, tpos, 'swchla8day', xlen=0.2, ylen=0.2)

str(swchl)

Now we can use the `maps` and `ggplot2` packages to plot the results.

library('ggplot2')
library('maps')
library('mapdata')

# Combine the two data-frames.
alldata <- cbind(tagData, swchl)

# Adjust the longitudes to be (-180, 180).
alldata$lon <- alldata$lon - 360

# R does not have plotting support for NA so we need to a variable for it.
alldata$missing <- is.na(alldata$mean) * 1

# Map limits.
ylim <- c(15, 30)
xlim <- c(-160, -105)

# Get outline data for map.
w <- map_data('worldHires', ylim=ylim, xlim=xlim)

z <- ggplot(alldata, aes(x=lon, y=lat)) +
     geom_point(aes(colour=mean, shape=factor(missing)), size=2.0) +
     scale_shape_manual(values=c(19, 1))

z + geom_polygon(data=w, aes(x=long, y=lat, group=group), fill='grey80') +
    theme_bw() +
    scale_colour_gradient(low='#56B1F7', high='#132B43',
                          limits=c(0.0, 0.32),
                          expression(paste(Mean~chla~values~(mu~g~l^-1)))) +
    coord_fixed(1.3, xlim=xlim, ylim=ylim) +
    ggtitle('Mean chla values at marlin tag locations')

We can do the same for topography data. Let's use the `ETOPO360` dataset to display the depth at the tag locations.

ylim <- c(15, 30)
xlim <- c(-160, -105)
topo <- xtracto(tagData$lon, tagData$lat, tagData$date, 'ETOPO360', 0.1, 0.1)

ylim <- c(15, 30)
xlim <- c(-160, -105)
alldata <- cbind(tagData, topo)
alldata$lon <- alldata$lon - 360

z <- ggplot(alldata, aes(x=lon, y=lat)) +
     geom_point(aes(colour=mean), size=2.0) +
     scale_shape_manual(values=c(19, 1))

z + geom_polygon(data=w,
                 aes(x=long, y=lat, group=group),
                 fill='grey80') +
    theme_bw() +
    scale_colour_gradient('Depth (m)') +
    coord_fixed(1.3, xlim=xlim, ylim=ylim) +
    ggtitle('Bathymetry at marlin tag locations')

For more information and example on the other routines see the full example from the documentation at [https://cran.r-project.org/web/packages/xtractomatic/vignettes/Usingxtractomatic.html](https://cran.r-project.org/web/packages/xtractomatic/vignettes/Usingxtractomatic.html)


PS: note that R and all the `xtractomatic` dependencies are already included in the [IOOS conda environment](http://ioos.github.io/notebooks_demos/other_resources/).