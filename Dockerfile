FROM andrewosh/binder-base

MAINTAINER Filipe Fernandes <ocefpaf@gmail.com>

USER root

USER main

# Update conda.
RUN conda update conda --yes

ADD requirements.txt requirements.txt

RUN conda config --add channels conda-forge --force
RUN conda config --add channels defaults --force
RUN conda config --add channels ioos --force

RUN conda install --yes --file requirements.txt

RUN conda info
RUN conda list
