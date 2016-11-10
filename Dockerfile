FROM andrewosh/binder-base

MAINTAINER Filipe Fernandes <ocefpaf@gmail.com>

USER root

# Update conda.
RUN conda update --all --yes

USER main1
ADD environment.yml environment.yml
RUN conda env create environment.yml
RUN source activate IOOS
