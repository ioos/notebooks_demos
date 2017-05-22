FROM jupyter/minimal-notebook

MAINTAINER Filipe Fernandes <ocefpaf@gmail.com>

USER main

# Update conda.
RUN conda update conda --yes
ADD environment.yml environment.yml
RUN conda env create --file environment.yml --name IOOS

RUN /bin/bash -c "source activate IOOS && ipython kernel install --user"
