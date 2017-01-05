---
title: Installing the IOOS conda environment
layout: single
---

For IOOS python users we recommend the free
[Miniconda](http://conda.pydata.org/miniconda.html) Python distribution,
a lightweight version of the [Anaconda Scientific Python Distribution](https://store.continuum.io/cshop/anaconda/).
While the full Anaconda distribution will also work,
it's faster to install Miniconda,
and you install only the packages you need.
If for some reason you decide later that you want the full Anaconda distribution,
you can install it by typing `conda install anaconda` using miniconda.

## Install

Download and install the appropriate Miniconda installer from [http://conda.pydata.org/miniconda.html](http://conda.pydata.org/miniconda.html).
With Anaconda you can create environments that use any Python version (e.g. Python 2.7 or Python 3.x).
You should install the latest Python 3.x,
and if find out later you need a Python 2.7 environment,
you can create one.
Windows users also need to choose between 32-bit (old Windows XP) or 64-bit (modern Windows) versions.

### Windows

Run the installer.
Choose *Just myself* instead *All users* so `miniconda` is installed in your user `namespace`.
Also, make sure both boxes that sets Miniconda as your default Python,
and add it to the path are checked!

**ASIDE 0:** If have a personal laptop it is fine to use *All users* instead.

**ASIDE 1:** If you are using ArcGIS,
or any other Python distribution,
you should **uncheck** the boxes in the install script so that Anaconda is **not** made your default Python,
nor added to your path.
You then need to activate `conda` by opening a command prompt terminal and typing:

```
C:\Miniconda3\Scripts\activate
conda install console_shortcut
```

which will give you a "Anaconda Prompt" you can use in the future to type `conda` commands.
(Look in "Start Menu=>All Programs=>Anaconda3)

### Linux/OS X

Copy-and-paste this:

```shell
if [[ $(uname) == "Darwin" ]]; then
  url=https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
elif [[ $(uname) == "Linux" ]]; then
  url=https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
fi
curl $url -o miniconda.sh
bash miniconda.sh -b
export PATH=$HOME/miniconda3/bin:$PATH
```

We also recommend to add the following line to your `~/.bashrc` file to make Miniconda the Python found first than the system Python:

```
export PATH=$HOME/miniconda3/bin:$PATH
```

## Create the IOOS Anaconda environment

Download the [environment.yml](https://raw.githubusercontent.com/ioos/notebooks_demos/master/environment.yml) file by right clicking with the mouse and choosing `save as...`,
or, on `OS X` and `Linux`, use these commands to download:

```bash
url=https://raw.githubusercontent.com/ioos/notebooks_demos/master/environment.yml
curl $url -o environment.yml
```

From the directory where you saved the file above,
type the following commands in the terminal or Windows command prompt:

```bash
conda config --add channels conda-forge --force
conda update --yes --all
conda env create --quiet --file environment.yml
```

The first two, adding an extra channel and updating, are optional but recommended.
(Lots of packages get downloaded here! This step will take a while...)

Once it's done building the environment,
you can activate the environment by typing:

```bash
activate IOOS3  # Windows
source activate IOOS3  # OSX and Linux
```

**ASIDE 2:** This file is just a list of Python packages that will be installed in a new `conda` virtual environment named `IOOS3`.
You can edit the file to add/remove software,
and/or rename the environment name if you need more environments for different tasks.

**ASIDE 3:** The default `Python` chosen for the environment is `3.5`.
If you need Python 2.7 download [environment-python-2.yml](https://raw.githubusercontent.com/ioos/notebooks_demos/master/environment-python-2.yml) instead,
and replace `environment.yml` for `environment-python-2.yml` in the instructions above to create an `IOOS2` environment.
Note that you will need to substitute `IOOS3` for `IOOS2`.
BTW, one can create both envs and use the Jupyter notebook kernel menu to switch between them.

## Exiting the IOOS environment

If you want to leave the IOOS environment and return to the root environment,
you can type

```bash
deactivate  # Windows
source deactivate  # OSX and Linux
```

# If Miniconda is not your default python environment...

If you choose not to add Miniconda Python Distribution to your `~.bashrc` or Windows path,
you must remember to activate the IOOS environment every time,
by typing in a command prompt

```
C:\Miniconda3\Scripts\activate IOOS3  # Windows
export PATH=$HOME/miniconda3/bin:$PATH && source activate IOOS3  # OSX and Linux
```

On all systems, to start the Jupyter notebook, just type:

```
jupyter notebook
```

# Why we use and recommend Anaconda

Anaconda users can just `conda install`,
which installs not only binary packages for their platform,
but the binary libraries they depend on.
So it's easier than `pip install` and, thanks to binary relocation,
more powerful than python wheels.
System-level installation of libraries and admin privileges are not required.
Check out [Travis Oliphant's blog piece](http://technicaldiscovery.blogspot.com/2013/12/why-i-promote-conda.html) for more info.

# How to get help

* Raise an issue [here](https://github.com/ioos/notebooks_demos/issues)
* Please get help on the [IOOS-tech Google Group](https://groups.google.com/forum/?hl=en#!forum/ioos_tech)
