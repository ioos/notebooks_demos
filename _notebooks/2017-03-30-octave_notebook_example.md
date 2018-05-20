---
title: "A Matlab notebook primer"
layout: notebook

---
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

<div class="prompt input_prompt">
In&nbsp;[1]:
</div>

```octave
x = [1, 2, 3]
y = [1; 2; 3]

z = x*y
```
<div class="output_area"><div class="prompt"></div>
<pre>
    x =
    
       1   2   3
    
    y =
    
       1
       2
       3
    
    z =  14

</pre>
</div>
And a simple plot.

<div class="prompt input_prompt">
In&nbsp;[2]:
</div>

```octave
x = linspace(0, 2*pi, 100);
y = sin(x);

plot(x, y)
```


![png](data:image/png;base64,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
)


To demonstrate the Matlab/Octave notebook we will use a well known toolbox for tidal analysis [`t_tide`](https://www.eoas.ubc.ca/~rich/).
First we need to add it to the path.

<div class="prompt input_prompt">
In&nbsp;[3]:
</div>

```octave
addpath(genpath('t_tide_v1.3beta'))
```

If you are running this on `octave` you need to load the `signal` package.
This step is not necessary on `Matlab`.

<div class="prompt input_prompt">
In&nbsp;[4]:
</div>

```octave
pkg load signal;
```

`t_demo` is a built-in script that contains a short example of capabilities of tidal analysis toolbox.

<div class="prompt input_prompt">
In&nbsp;[5]:
</div>

```octave
t_demo
```
<div class="output_area"><div class="prompt"></div>
<pre>
    + echo ('on')
    + ## Load the example.
    + load ('t_example')
    warning: load: file found in load path
    + ## Define inference parameters.
    + infername = ['P1'; 'K2'];
    + inferfrom = ['K1'; 'S2'];
    + infamp = [.33093; .27215];
    + infphase = [-7.07; -22.40];
    + ## The call (see t_demo code for details).
    
    + ## hourly data
    
    + ## start time is datestr(tuk_time(1))
    
    + ## Latitude of obs
    
    + ## Add a shallow-water constituent 
    
    + ## coloured boostrap CI
    + [tidestruc, pout] = t_tide (tuk_elev, 'interval', 1, 'start', tuk_time (1), 'latitude', 69 + 27 / 60, 'inference', infername, inferfrom, infamp, infphase, 'shallow', 'M10', 'error', 'linear', 'synthesis', 1);
    warning: /home/filipe/IOOS/notebooks_demos/notebooks/t_tide_v1.3beta/t_tide.m: possible Matlab-style short-circuit operator at line 443, column 18
    warning: /home/filipe/IOOS/notebooks_demos/notebooks/t_tide_v1.3beta/t_tide.m: possible Matlab-style short-circuit operator at line 637, column 19
    warning: load: file found in load path
       number of standard constituents used: 35
       Forced fit to M10
       Inference of P1   using K1  
       Inference of K2   using S2  
       Points used: 1510 of 1584
       percent of var residual after lsqfit/var original: 74.18 %
    warning: /home/filipe/IOOS/notebooks_demos/notebooks/t_tide_v1.3beta/t_vuf.m: possible Matlab-style short-circuit operator at line 68, column 22
    warning: load: file found in load path
       Greenwich phase computed with nodal corrections applied to amplitude 
     and phase relative to center time
       Do inference corrections
       Using linearized error estimates
       Generating prediction with nodal corrections, SNR is 1.000000
    warning: /home/filipe/IOOS/notebooks_demos/notebooks/t_tide_v1.3beta/t_predic.m: possible Matlab-style short-circuit operator at line 66, column 34
    warning: /home/filipe/IOOS/notebooks_demos/notebooks/t_tide_v1.3beta/t_predic.m: possible Matlab-style short-circuit operator at line 173, column 18
    warning: isstr is obsolete and will be removed from a future version of Octave, please use ischar instead
    warning: load: file found in load path
    warning: load: file found in load path
       percent of var residual after synthesis/var original: 78.42 %
    -----------------------------------
    date: 29-Mar-2017
    nobs = 1584,  ngood = 1510,  record length (days) = 66.00
    start time: 06-Jul-1975 01:00:00
    rayleigh criterion = 1.0
    Greenwich phase computed with nodal corrections applied to amplitude \n and phase relative to center time
    
    x0= 1.98, x trend= 0
    
    var(x)= 0.82196   var(xp)= 0.17966   var(xres)= 0.64461
    percent var predicted/var original= 21.9 %
    
         tidal amplitude and phase with 95% CI estimates
    
    tide   freq       amp     amp_err    pha    pha_err     snr
     MM   0.0015122    0.2121    0.521   263.34   140.72     0.17
     MSF  0.0028219    0.1561    0.521   133.80   191.29     0.09
     ALP1 0.0343966    0.0152    0.035   334.95   143.54     0.19
     2Q1  0.0357064    0.0246    0.035    82.69    89.79     0.48
     Q1   0.0372185    0.0158    0.035    65.74   140.51      0.2
    *O1   0.0387307    0.0764    0.035    74.23    29.21      4.7
     NO1  0.0402686    0.0290    0.035   238.14    53.29     0.67
    *P1   0.0415526    0.0465    0.035    71.88    43.41      1.7
    *K1   0.0417807    0.1405    0.035    64.81    15.24       16
     J1   0.0432929    0.0253    0.035     7.32    86.65     0.51
    *OO1  0.0448308    0.0531    0.035   235.75    43.75      2.3
     UPS1 0.0463430    0.0298    0.035    91.73    87.12     0.71
     EPS2 0.0761773    0.0211    0.025   184.59    66.90      0.7
    *MU2  0.0776895    0.0419    0.025    83.23    33.79      2.8
    *N2   0.0789992    0.0838    0.025    44.52    16.86       11
    *M2   0.0805114    0.4904    0.025    77.70     2.89  3.8e+02
     L2   0.0820236    0.0213    0.025    35.22    82.98     0.71
    *S2   0.0833333    0.2197    0.025   126.72     6.58       76
    *K2   0.0835615    0.0598    0.025   149.12    28.01      5.6
     ETA2 0.0850736    0.0071    0.025   246.05   244.76     0.08
    *MO3  0.1192421    0.0148    0.010   234.97    40.62      2.3
    *M3   0.1207671    0.0123    0.010   261.57    44.22      1.6
     MK3  0.1222921    0.0049    0.010   331.60   117.53     0.25
     SK3  0.1251141    0.0023    0.010   237.69   252.59    0.057
    *MN4  0.1595106    0.0092    0.009   256.47    52.74      1.1
    *M4   0.1610228    0.0126    0.009   291.78    38.58        2
     SN4  0.1623326    0.0083    0.009   270.85    59.58     0.89
     MS4  0.1638447    0.0010    0.009   339.35   479.33    0.014
     S4   0.1666667    0.0047    0.009   299.56   108.15     0.28
     2MK5 0.2028035    0.0013    0.005   310.10   214.09    0.073
     2SK5 0.2084474    0.0045    0.005   104.00    62.55     0.94
     2MN6 0.2400221    0.0035    0.007   271.24   101.52     0.28
     M6   0.2415342    0.0017    0.007   158.88   207.26    0.067
     2MS6 0.2443561    0.0056    0.007   306.10    65.10     0.71
     2SM6 0.2471781    0.0023    0.007   298.92   165.13     0.12
    *3MK7 0.2833149    0.0086    0.004   212.25    29.47      3.7
     M8   0.3220456    0.0030    0.003    42.43    56.78     0.86
     M10  0.4025570    0.0009    0.003   198.23   195.47     0.07
    + ## Use SNR=1 for synthesis. 
    + echo ('off')
    warning: get: allowing linewi to match line property linewidth
    error: get: ambiguous text property name vertical; possible matches:
    
    verticalalignment      verticalalignmentmode
    
    error: called from:
    error:   /usr/share/octave/3.8.2/m/plot/appearance/text.m at line 152, column 17
    error:   /home/filipe/IOOS/notebooks_demos/notebooks/t_tide_v1.3beta/t_demo.m at line 57, column 1

</pre>
</div>

![png](data:image/png;base64,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
3+17/nw6f/7u3PbAfYsepOl0OjtN397bfnc6HU3iAKNR6vWO+u58wH0KFKThcJjnParP/eRTRK1W
K1+zuOv7J5PJeDxutVrxz9RxL/k6tIVeOlGW97jhKRBEoCBtbGzsukx+Mpl0u92UUr/f3xukfJou
pbTvxQv1VXYppRsplWUZ/xr8NdXrpbTgID3EDU9pmtkrIdfAeDyu/2SP/7d7oCDtNXuw7oEXcvYr
X/GbKLStrfTBB8veCNbDSy+l0ejobzm4RPmXZ77se9nbcrDGvjE2/t8CR2C8EjdZ6HbTN7+5uMWv
xiAsmEEwAimljz76aNmbcIDQQaqj8gAvplu3bh325qweVU4GIaVkEOoR2N5O29vrs3u0y+3bt5e9
CQcIdMhuMBjk8EwmkzydeVEU/X6/1Wo9wCG7Y8eOeWMsQLp7xv3ixYvL3pADBApSZ89NVjY2NvLf
NQ9wPcLt27f/44c/fPqdd559/vlDPoe0s5MefTQdPz59//rOndROOz/5n7OP/NYT7ZM7O6ldHvtZ
6+rVQ1vj1auT489dvnz6iSdSSqk89rP//vfpT66klHZSWR76udnpNO3spJRS+ej1VjFJrVba2VnE
GbjJ5O6K/u8/W8eOpatXU1kuaF2funr1N+6bsHPYAziZpPffT3fupHb703UtbPSyQ38G+8gviCb9
YTeZpEP88Vwd+RzSzZs3l70hB3ikqqplb8NCnDt37o233/7dW7dSShe+9rWfnzp1KIv9sytX/vL9
91NKdx555JXqn4Zp49vp+99P304pXUivvpoubKThm+nlv3jllYdf1x9Mpxffeuvso+OdO2fzVzbS
8J/Tn3+SHn81XTh3evC9F1+89xJm38U1j8uXv3P9+gt5Rf/w+F/9/OmnX7h+/R+//OV/ef75B34W
+3r77Qs3bhQppU4aXEqbKaV/++IX/+SDDxaxrul0ejali2+99csTJ/7m3LmU0tevXfvWu+/+9PTp
Awdwfq//6EcnPvkkpfSvzz33p7/4xc3HH1/c6KWUrl37+rvvfuv06Z+++OL35vn++30lZN+5fPmF
69df/+pX33n22fvfxljyCPzdj3986ubN737jG/+1ThfapZQ+/vjjmzdvXrly5cMPP1z2ttxT1WDt
dnXyZHXmTHXt2qEtc3u7euqpvNit3+u3nrz197//t799/Fenfuej95784+KZj7tn3qja7cNZ140b
VVF0z7xx8mR14kT1zDNV98wbZ5748Pix/9958o+qbvdw1jKj261OnaqeevLO1pder9rtamurarWq
N99c0IpOP/2rN0/9dXXmTNVuV5cuVUWxiHVVVVVdu1YVxWcj9t57v/HpoWi3qy98oTpzpvrBD6qi
qNrtqtutWq1qe/sw13LXIp7BPrrdqigO88dn6Zr3jJqlsXtIAKyW0FfZAbA+BAmAEAQJgBAECYAQ
GhukNXxr+ho+5V3mGYHGj9Kcg9DscWj2s5vTKg5CoDfGHqJ7z1vRSPM85b0TfDTJPCPQ7/eLoshv
Sdk77X0DzPkySHffl7O2g5BSmk6nm5ubnU5nbX8cevlG+ykF+p2w7OvOF2Jra2vXB40351Pe3t7e
Xsw7Y5ZunhGon3t34W/hWY77euWv+SBsbW2t+Y9DwBdAM/eQDmXeitWyhk95l3lGIP8ZmHcTj2iz
jtacL4PxeDwcDhu5e5TmG4TxeNzsn5R5BqHVag0Gg+l0WhRFkBdDY88hwb7G4/FkMmlqkOZUlmW3
2x2NRsvekKUZjUZr/hpIKXW73U6n0+1248zN0cwgPcy8FStq36fc+HPXs+YZgVyjIH8MLsL8L4MG
T6A8zyCUZTkajfLr4ai370is6C+EZh6ye5h5K1bUvk/55ZdfLori0qVL+dO9E3w0yYEjMB6Pe71e
WZZ5Uud6WJpkzpdBq9XKB2qWtJmLNc8gtNvtyWQyHA6bGuZ5BiH/OEyn0zi/Jxt7L7sHnrdide19
yus2CEYgzTcI+fqrBg+LV0JazVdCY4MEwGpp5jkkAFaOIAEQgiABEIIgARCCIAEQgiABEIIgARCC
INF8w+Gw1+v1er3Vuk9MvpXAnN88Go02Nzd3fTHPQXDY2wWLIkg03Hg8znfS3NjYyDfLyXcwm06n
s7f5ync2m31gfa+z+t+UUv3B3kflBU4mk103Lc0bkN8kP51O6/+tv/h5BoPB7G33ZpdTb1K9tHa7
3Wq1dq19Y2NjMBjMPVSwZILE2plOp71eL+895Pva5ZnKptNpv9+f/WAymdS7HfW8dvUHux6VUur3
+7lPs1/JCamXPBwO8z0uDwzS7P/uWk5KaXNzM+/91P9VJ7b+Hlgtzby5KtTKsmy1WrNzDbTb7dFo
VN9eNu9S5H8nd3U6nXyDr10T55RlmYOUf/XPPqooinpemfrr9XydeSH5e/KiZj/eV32Hsb3LKcuy
LMu8rny72LyHNLt2WDmCxLprtVqdTme2DXlXIwfg83Zi9j7qwLXkDzqdTj6MduAN1/dddb2c2fkF
4twcEx6GINFw+TBar9criqLT6eQjbPkr7Xa73W6XZZlnZGi1WqPRqNvtlmVZH3yrf+/n/x2Px/n8
zd5H1Web0t1zPEVRDIfDwWBQFEXeJyuKoo7HgRWpv2Hf5Uyn0zzdZ0opz7Y3u/bGz4hKI7nbN6R0
d+6yvXs8vV5va2srf5wbM8+j7v09/X6/PiR4D/nIW32wcddyZjdsziVAcPaQIKWU9p0VJu8k1Xsb
e8Mzz1wys9+TzzbltBz4wHa7PXvUbnY5uzbs8+TzZ/deC8RhDwmAEFz2DUAIggRACIIEQAiCBEAI
ggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiC
BEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIE
QAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRA
CIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAI
ggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiC
BEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIE
QAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRA
CIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAI
ggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiC
BEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIE
QAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRA
CIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAI
ggRACIIEQAiCBEAIggRACIIEQAiCBH3Y7DoAAABQSURBVEAIggRACIIEQAiCBEAIggRACIIEQAiC
BEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIggRACIIEQAiCBEAIvwZFaHTJ
tofwhQAAAABJRU5ErkJggg==
)

<br>
Right click and choose Save link as... to
[download](https://raw.githubusercontent.com/ioos/notebooks_demos/master/notebooks/2017-03-30-octave_notebook_example.ipynb)
this notebook, or click [here](https://beta.mybinder.org/v2/gh/ioos/notebooks_demos/master?filepath=notebooks/2017-03-30-octave_notebook_example.ipynb) to run a live instance of this notebook.