# A Matlab notebook primer

A common misconception is that `Jupyter` notebooks are for Python only.
We already showed how to use the
[`R` language](http://ioos.github.io/notebooks_demos/notebooks/2017-01-23-R-notebook/),
and now we are going to create a Matlab/Octave toolboxes notebook.

The IOOS conda
[environment](http://ioos.github.io/notebooks_demos/other_resources/)
installs [`oct2py`](https://github.com/ioos/notebooks_demos/blob/229dabe0e7dd207814b9cfb96e024d3138f19abf/environment.yml#L40), the dependency needed to run Matlab/Octave notebooks.
However, unlike `R` that can be installed with conda,
we cannot install Matlab or Octave with it.
This notebook relies on system installation of `octave` but it is possible to run the same on Matlab with very little modification.

Here are some basic Matlab-like array creation and `dot` multiplication.

x = [1, 2, 3]
y = [1; 2; 3]

z = x*y

And a simple plot.

x = linspace(0, 2*pi, 100);
y = sin(x);

plot(x, y)

To demonstrate the Matlab/Octave notebook we will use a well known toolbox for tidal analysis [`t_tide`](https://www.eoas.ubc.ca/~rich/).
First we need to add it to the path.

addpath(genpath('t_tide_v1.3beta'))

If you are running this on `octave` you need to load the `signal` package.
This step is not necessary on `Matlab`.

pkg load signal;

`t_demo` is a built-in script that contains a short example of capabilities of tidal analysis toolbox.

t_demo