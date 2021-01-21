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
With Anaconda you can create environments that use any Python version (e.g. Python 2.7 or Python 3.6),
so install the latest Python 3.x and if find out later you need a Python 2.7 environment,
you can create one.
Windows users also need to choose between 32-bit (old Windows XP) or 64-bit (modern Windows) versions.

### Windows

Run the installer
Choose *Just Me* (not *All Users*),
and choose a Install Location owned by you.
The default `%USERPROFILE%\AppData\Local\Continuum\Miniconda3` is fine,
but kind of long,
so if you have created some shorter directory like `c:\programs` that you own,
you might choose `c:\programs\Miniconda3`.

On the "Advanced Installation Options" screen,
leave the boxes checked if you want Miniconda 3 to be your default python.
If you are going to be switching from Python 2 to Python 3 or perhaps some other Python distribution,
it's best uncheck the boxes and use the `Anaconda Command Prompt` or `Anaconda Navigator` (see below for instructions) to start Anaconda.

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

Download the [environment.yml](https://raw.githubusercontent.com/ioos/notebooks_demos/master/.binder/environment.yml),
or the [environment-python_and_r.yml](https://raw.githubusercontent.com/ioos/notebooks_demos/master/.binder/environment-python_and_r.yml) for a bigger environment with the R packages,
by right clicking with the mouse and choosing `save as...`,
or, on `OS X` and `Linux`, use these commands to download:

```bash
url=https://raw.githubusercontent.com/ioos/notebooks_demos/master/environment.yml
curl $url -o environment.yml
```

Then from the directory where you saved the file above,
type the following commands in the terminal or Windows command prompt:

```bash
conda config --add channels conda-forge --force
conda update --yes --all
conda env create --quiet --file environment.yml
```

The last line actually creates the IOOS environment,
and since lots of packages are downloaded,
you should go get a coffee.

Once the environment is done building, you can activate it by typing:

```bash
activate IOOS  # Windows
source activate IOOS  # OS X and Linux
```

## Exiting the IOOS environment

If you want to leave the IOOS environment and return to the root environment,
you can type

```bash
deactivate  # Windows
source deactivate  # OS X and Linux
```

# If Miniconda is not your default python environment...

If you choose not to add Miniconda Python Distribution to your `~/.bashrc` or Windows path,
you must remember to activate the IOOS environment every time,
by typing in a command prompt

```
export PATH=$HOME/miniconda3/bin:$PATH && source activate IOOS  # OS X and Linux
```

Windows users can navigate to the Anaconda Command Prompt (e.g. Start Menu=>Anaconda3 on Windows 7) and type `activate IOOS`.

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
