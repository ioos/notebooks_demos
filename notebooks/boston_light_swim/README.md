# Boston light swim

Sea Surface Temperature forecast for the Boston Light Swim


## How to run the notebook

Download the latest version `conda` version

```bash
url=http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh
wget $url -O miniconda.sh
chmod +x miniconda.sh
./miniconda.sh -b
```

Add Miniconda to path and update

```bash
export PATH=/$HOME/miniconda/bin:$PATH
conda update --yes conda
```

Add the conda-forge channel
```bash
conda config --add channels conda-forge
```

Create a virtual environment and update

```bash
ENV_NAME=ioos
wget https://raw.githubusercontent.com/ocefpaf/boston_light_swim/master/requirements.txt
conda create --yes -n $ENV_NAME --file requirements.txt python=2.7
source activate $ENV_NAME
```
