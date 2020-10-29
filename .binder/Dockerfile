FROM pangeo/base-image:2020.06.03

# install rstudio-server
USER root
RUN apt-get update && \
    curl --silent -L --fail https://download2.rstudio.org/rstudio-server-1.1.419-amd64.deb > /tmp/rstudio.deb && \
    echo '24cd11f0405d8372b4168fc9956e0386 /tmp/rstudio.deb' | md5sum -c - && \
    apt-get install -y /tmp/rstudio.deb && \
    rm /tmp/rstudio.deb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
ENV PATH=$PATH:/usr/lib/rstudio-server/bin
USER $NB_USER

COPY CONDARC /tmp/.condarc
