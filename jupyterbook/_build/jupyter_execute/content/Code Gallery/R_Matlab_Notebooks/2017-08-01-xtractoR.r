library('xtractomatic')

str(Marlintag38606)

tagData <- Marlintag38606
xpos <- tagData$lon
ypos <- tagData$lat
tpos <- tagData$date

swchl <- xtracto(xpos, ypos, tpos, 'swchla8day', xlen=0.2, ylen=0.2)

str(swchl)

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
