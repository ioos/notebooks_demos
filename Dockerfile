FROM andrewosh/binder-base

MAINTAINER Filipe Fernandes <ocefpaf@gmail.com>

USER main

# Update conda.
RUN conda update conda --yes
ADD environment.yml environment.yml
RUN conda-env create environment.yml

RUN /bin/bash -c "source activate IOOS3 && ipython kernel install --user"
