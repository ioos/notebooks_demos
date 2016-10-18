---
layout: notebook
title: ""
---


<img style='float: left' width="150px" src="http://bostonlightswim.org/wp/wp-
content/uploads/2011/08/BLS-front_4-color.jpg">
<br><br>

## [The Boston Light Swim](http://bostonlightswim.org/)

### Sea Surface Temperature time-series model skill

### Load configuration

<div class="prompt input_prompt">
In&nbsp;[1]:
</div>

```python
import os
import sys
import warnings

ioos_tools_path = os.path.join(os.path.pardir, os.path.pardir)
sys.path.append(ioos_tools_path)

# Suppresing warnings for a "pretty output."
# Remove this line to debug any possible issues.
warnings.simplefilter("ignore")
```

<div class="prompt input_prompt">
In&nbsp;[2]:
</div>

```python
from ioos_tools.ioos import parse_config

config = parse_config('config.yaml')

save_dir = os.path.join(os.path.abspath(config['run_name']))
```

### Skill 1: Model Bias (or Mean Bias)

The bias skill compares the model mean temperature against the observations.
It is possible to introduce a Mean Bias in the model due to a mismatch of the
boundary forcing and the model interior.

$$ \text{MB} = \mathbf{\overline{m}} - \mathbf{\overline{o}}$$

<div class="prompt input_prompt">
In&nbsp;[3]:
</div>

```python
from ioos_tools.ioos import stations_keys


def rename_cols(df, config):
    cols = stations_keys(config, key='station_name')
    return df.rename(columns=cols)
```

<div class="prompt input_prompt">
In&nbsp;[4]:
</div>

```python
from ioos_tools.ioos import to_html, save_html, load_ncs
from ioos_tools.skill_score import mean_bias, apply_skill

dfs = load_ncs(config)

df = apply_skill(dfs, mean_bias, remove_mean=False, filter_tides=False)
skill_score = dict(mean_bias=df.to_dict())

# Filter out stations with no valid comparison.
df.dropna(how='all', axis=1, inplace=True)
df = df.applymap('{:.2f}'.format).replace('nan', '--')

# Pretty HTML table.
df = rename_cols(df, config)
html = to_html(df.T)
fname = os.path.join(save_dir, 'mean_bias.html')
save_html(fname, html)
html
```




<style>.info {
    background-color:#fcf8e3;
    border-color:#faebcc;
    border-left:5px solid #8a6d3b;
    padding:.5em;
    color:#8a6d3b
}

.success {
    background-color:#d9edf7;
    border-color:#bce8f1;
    border-left:5px solid #31708f;
    padding:.5em;
    color:#31708f
}

.error {
    background-color:#f2dede;
    border-color:#ebccd1;
    border-left:5px solid #a94442;
    padding:.5em;
    color:#a94442
}

.warning {
    background-color:#fcf8e3;
    border-color:#faebcc;
    border-left:5px solid #8a6d3b;
    padding:.5em;
    color:#8a6d3b
}

.text-shadow {
    text-shadow:0 1px 0 #ccc,0 2px 0 #c9c9c9,0 3px 0 #bbb,0 4px 0 #b9b9b9,0 5px 0 #aaa,0 6px 1px rgba(0,0,0,.1)
}

.datagrid table {
    border-collapse:collapse;
    text-align:left;
    width:65%
}

.datagrid td {
    border-collapse:collapse;
    text-align:right;
}

.datagrid {
    font:normal 12px/150% Arial,Helvetica,sans-serif;
    background:#fff;
    overflow:hidden;
    border:1px solid #069;
    -webkit-border-radius:3px;
    -moz-border-radius:3px;
    border-radius:3px
}

.datagrid table td,.datagrid table th {
    padding:3px 10px
}

.datagrid table thead th {
    background:-webkit-gradient(linear,left top,left bottom,color-stop(0.05,#069),color-stop(1,#00557F));
    background:-moz-linear-gradient(center top,#069 5%,#00557F 100%);
    filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#006699',endColorstr='#00557F');
    background-color:#069;
    color:#FFF;
    font-size:15px;
    font-weight:700;
    border-left:1px solid #0070A8
}

.datagrid table thead th:first-child {
    border:none
}

.datagrid table tbody td {
    color:#00496B;
    border-left:1px solid #E1EEF4;
    font-size:12px;
    font-weight:400
}

.datagrid table tbody .alt td {
    background:#E1EEF4;
    color:#00496B
}

.datagrid table tbody td:first-child {
    border-left:none
}

.datagrid table tbody tr:last-child td {
    border-bottom:none
}

.datagrid table tfoot td div {
    border-top:1px solid #069;
    background:#E1EEF4
}

.datagrid table tfoot td {
    padding:0;
    font-size:12px
}

.datagrid table tfoot td div {
    padding:2px
}

.datagrid table tfoot td ul {
    margin:0;
    padding:0;
    list-style:none;
    text-align:right
}

.datagrid table tfoot li {
    display:inline
}

.datagrid table tfoot li a {
    text-decoration:none;
    display:inline-block;
    padding:2px 8px;
    margin:1px;
    color:#FFF;
    border:1px solid #069;
    -webkit-border-radius:3px;
    -moz-border-radius:3px;
    border-radius:3px;
    background:-webkit-gradient(linear,left top,left bottom,color-stop(0.05,#069),color-stop(1,#00557F));
    background:-moz-linear-gradient(center top,#069 5%,#00557F 100%);
    filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#006699',endColorstr='#00557F');
    background-color:#069
}

.datagrid table tfoot ul.active,.datagrid table tfoot ul a:hover {
    text-decoration:none;
    border-color:#069;
    color:#FFF;
    background:none;
    background-color:#00557F
}

div.dhtmlx_window_active,div.dhx_modal_cover_dv {
    position:fixed!important
}
</style><div class="datagrid"><table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>G1_SST_GLOBAL</th>
      <th>NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST</th>
      <th>NECOFS_GOM3_FORECAST</th>
      <th>coawst_4_use_best</th>
      <th>global</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>BOSTON 16 NM East of Boston, MA</th>
      <td>-0.33</td>
      <td>-0.66</td>
      <td>-0.40</td>
      <td>-1.57</td>
      <td>-1.48</td>
    </tr>
    <tr>
      <th>Buoy A0102 - Mass. Bay/Stellwagen</th>
      <td>0.19</td>
      <td>-0.98</td>
      <td>-0.28</td>
      <td>-1.10</td>
      <td>-0.64</td>
    </tr>
    <tr>
      <th>Boston, MA</th>
      <td>-0.18</td>
      <td>-0.35</td>
      <td>-0.44</td>
      <td>-1.04</td>
      <td>--</td>
    </tr>
  </tbody>
</table></div>



### Skill 2: Central Root Mean Squared Error

Root Mean Squared Error of the deviations from the mean.

$$ \text{CRMS} = \sqrt{\left(\mathbf{m'} - \mathbf{o'}\right)^2}$$

where: $\mathbf{m'} = \mathbf{m} - \mathbf{\overline{m}}$ and $\mathbf{o'} =
\mathbf{o} - \mathbf{\overline{o}}$

<div class="prompt input_prompt">
In&nbsp;[5]:
</div>

```python
from ioos_tools.skill_score import rmse

dfs = load_ncs(config)

df = apply_skill(dfs, rmse, remove_mean=True, filter_tides=False)
skill_score['rmse'] = df.to_dict()

# Filter out stations with no valid comparison.
df.dropna(how='all', axis=1, inplace=True)
df = df.applymap('{:.2f}'.format).replace('nan', '--')

# Pretty HTML table.
df = rename_cols(df, config)
html = to_html(df.T)
fname = os.path.join(save_dir, 'rmse.html')
save_html(fname, html)
html
```




<style>.info {
    background-color:#fcf8e3;
    border-color:#faebcc;
    border-left:5px solid #8a6d3b;
    padding:.5em;
    color:#8a6d3b
}

.success {
    background-color:#d9edf7;
    border-color:#bce8f1;
    border-left:5px solid #31708f;
    padding:.5em;
    color:#31708f
}

.error {
    background-color:#f2dede;
    border-color:#ebccd1;
    border-left:5px solid #a94442;
    padding:.5em;
    color:#a94442
}

.warning {
    background-color:#fcf8e3;
    border-color:#faebcc;
    border-left:5px solid #8a6d3b;
    padding:.5em;
    color:#8a6d3b
}

.text-shadow {
    text-shadow:0 1px 0 #ccc,0 2px 0 #c9c9c9,0 3px 0 #bbb,0 4px 0 #b9b9b9,0 5px 0 #aaa,0 6px 1px rgba(0,0,0,.1)
}

.datagrid table {
    border-collapse:collapse;
    text-align:left;
    width:65%
}

.datagrid td {
    border-collapse:collapse;
    text-align:right;
}

.datagrid {
    font:normal 12px/150% Arial,Helvetica,sans-serif;
    background:#fff;
    overflow:hidden;
    border:1px solid #069;
    -webkit-border-radius:3px;
    -moz-border-radius:3px;
    border-radius:3px
}

.datagrid table td,.datagrid table th {
    padding:3px 10px
}

.datagrid table thead th {
    background:-webkit-gradient(linear,left top,left bottom,color-stop(0.05,#069),color-stop(1,#00557F));
    background:-moz-linear-gradient(center top,#069 5%,#00557F 100%);
    filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#006699',endColorstr='#00557F');
    background-color:#069;
    color:#FFF;
    font-size:15px;
    font-weight:700;
    border-left:1px solid #0070A8
}

.datagrid table thead th:first-child {
    border:none
}

.datagrid table tbody td {
    color:#00496B;
    border-left:1px solid #E1EEF4;
    font-size:12px;
    font-weight:400
}

.datagrid table tbody .alt td {
    background:#E1EEF4;
    color:#00496B
}

.datagrid table tbody td:first-child {
    border-left:none
}

.datagrid table tbody tr:last-child td {
    border-bottom:none
}

.datagrid table tfoot td div {
    border-top:1px solid #069;
    background:#E1EEF4
}

.datagrid table tfoot td {
    padding:0;
    font-size:12px
}

.datagrid table tfoot td div {
    padding:2px
}

.datagrid table tfoot td ul {
    margin:0;
    padding:0;
    list-style:none;
    text-align:right
}

.datagrid table tfoot li {
    display:inline
}

.datagrid table tfoot li a {
    text-decoration:none;
    display:inline-block;
    padding:2px 8px;
    margin:1px;
    color:#FFF;
    border:1px solid #069;
    -webkit-border-radius:3px;
    -moz-border-radius:3px;
    border-radius:3px;
    background:-webkit-gradient(linear,left top,left bottom,color-stop(0.05,#069),color-stop(1,#00557F));
    background:-moz-linear-gradient(center top,#069 5%,#00557F 100%);
    filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#006699',endColorstr='#00557F');
    background-color:#069
}

.datagrid table tfoot ul.active,.datagrid table tfoot ul a:hover {
    text-decoration:none;
    border-color:#069;
    color:#FFF;
    background:none;
    background-color:#00557F
}

div.dhtmlx_window_active,div.dhx_modal_cover_dv {
    position:fixed!important
}
</style><div class="datagrid"><table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>G1_SST_GLOBAL</th>
      <th>NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST</th>
      <th>NECOFS_GOM3_FORECAST</th>
      <th>coawst_4_use_best</th>
      <th>global</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>BOSTON 16 NM East of Boston, MA</th>
      <td>0.36</td>
      <td>0.60</td>
      <td>0.50</td>
      <td>0.47</td>
      <td>0.63</td>
    </tr>
    <tr>
      <th>Buoy A0102 - Mass. Bay/Stellwagen</th>
      <td>0.13</td>
      <td>0.66</td>
      <td>0.31</td>
      <td>0.34</td>
      <td>0.78</td>
    </tr>
    <tr>
      <th>Boston, MA</th>
      <td>0.10</td>
      <td>0.30</td>
      <td>0.41</td>
      <td>0.78</td>
      <td>--</td>
    </tr>
  </tbody>
</table></div>



### Skill 3: R$^2$
https://en.wikipedia.org/wiki/Coefficient_of_determination

<div class="prompt input_prompt">
In&nbsp;[6]:
</div>

```python
from ioos_tools.skill_score import r2

dfs = load_ncs(config)

df = apply_skill(dfs, r2, remove_mean=True, filter_tides=False)
skill_score['r2'] = df.to_dict()

# Filter out stations with no valid comparison.
df.dropna(how='all', axis=1, inplace=True)
df = df.applymap('{:.2f}'.format).replace('nan', '--')

# Pretty HTML table.
df = rename_cols(df, config)
html = to_html(df.T)
fname = os.path.join(save_dir, 'r2.html')
save_html(fname, html)
html
```




<style>.info {
    background-color:#fcf8e3;
    border-color:#faebcc;
    border-left:5px solid #8a6d3b;
    padding:.5em;
    color:#8a6d3b
}

.success {
    background-color:#d9edf7;
    border-color:#bce8f1;
    border-left:5px solid #31708f;
    padding:.5em;
    color:#31708f
}

.error {
    background-color:#f2dede;
    border-color:#ebccd1;
    border-left:5px solid #a94442;
    padding:.5em;
    color:#a94442
}

.warning {
    background-color:#fcf8e3;
    border-color:#faebcc;
    border-left:5px solid #8a6d3b;
    padding:.5em;
    color:#8a6d3b
}

.text-shadow {
    text-shadow:0 1px 0 #ccc,0 2px 0 #c9c9c9,0 3px 0 #bbb,0 4px 0 #b9b9b9,0 5px 0 #aaa,0 6px 1px rgba(0,0,0,.1)
}

.datagrid table {
    border-collapse:collapse;
    text-align:left;
    width:65%
}

.datagrid td {
    border-collapse:collapse;
    text-align:right;
}

.datagrid {
    font:normal 12px/150% Arial,Helvetica,sans-serif;
    background:#fff;
    overflow:hidden;
    border:1px solid #069;
    -webkit-border-radius:3px;
    -moz-border-radius:3px;
    border-radius:3px
}

.datagrid table td,.datagrid table th {
    padding:3px 10px
}

.datagrid table thead th {
    background:-webkit-gradient(linear,left top,left bottom,color-stop(0.05,#069),color-stop(1,#00557F));
    background:-moz-linear-gradient(center top,#069 5%,#00557F 100%);
    filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#006699',endColorstr='#00557F');
    background-color:#069;
    color:#FFF;
    font-size:15px;
    font-weight:700;
    border-left:1px solid #0070A8
}

.datagrid table thead th:first-child {
    border:none
}

.datagrid table tbody td {
    color:#00496B;
    border-left:1px solid #E1EEF4;
    font-size:12px;
    font-weight:400
}

.datagrid table tbody .alt td {
    background:#E1EEF4;
    color:#00496B
}

.datagrid table tbody td:first-child {
    border-left:none
}

.datagrid table tbody tr:last-child td {
    border-bottom:none
}

.datagrid table tfoot td div {
    border-top:1px solid #069;
    background:#E1EEF4
}

.datagrid table tfoot td {
    padding:0;
    font-size:12px
}

.datagrid table tfoot td div {
    padding:2px
}

.datagrid table tfoot td ul {
    margin:0;
    padding:0;
    list-style:none;
    text-align:right
}

.datagrid table tfoot li {
    display:inline
}

.datagrid table tfoot li a {
    text-decoration:none;
    display:inline-block;
    padding:2px 8px;
    margin:1px;
    color:#FFF;
    border:1px solid #069;
    -webkit-border-radius:3px;
    -moz-border-radius:3px;
    border-radius:3px;
    background:-webkit-gradient(linear,left top,left bottom,color-stop(0.05,#069),color-stop(1,#00557F));
    background:-moz-linear-gradient(center top,#069 5%,#00557F 100%);
    filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#006699',endColorstr='#00557F');
    background-color:#069
}

.datagrid table tfoot ul.active,.datagrid table tfoot ul a:hover {
    text-decoration:none;
    border-color:#069;
    color:#FFF;
    background:none;
    background-color:#00557F
}

div.dhtmlx_window_active,div.dhx_modal_cover_dv {
    position:fixed!important
}
</style><div class="datagrid"><table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>G1_SST_GLOBAL</th>
      <th>NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST</th>
      <th>NECOFS_GOM3_FORECAST</th>
      <th>coawst_4_use_best</th>
      <th>global</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>BOSTON 16 NM East of Boston, MA</th>
      <td>0.25</td>
      <td>-0.60</td>
      <td>-0.12</td>
      <td>0.48</td>
      <td>-1.74</td>
    </tr>
    <tr>
      <th>Buoy A0102 - Mass. Bay/Stellwagen</th>
      <td>0.94</td>
      <td>-1.92</td>
      <td>0.34</td>
      <td>0.66</td>
      <td>-1.70</td>
    </tr>
    <tr>
      <th>Boston, MA</th>
      <td>0.86</td>
      <td>-0.77</td>
      <td>-2.24</td>
      <td>-2.70</td>
      <td>--</td>
    </tr>
  </tbody>
</table></div>



<div class="prompt input_prompt">
In&nbsp;[7]:
</div>

```python
import json

fname = os.path.join(save_dir, 'skill_score.json')

# Stringfy keys for json.
for key in skill_score.keys():
    skill_score[key] = {str(k): v for k, v in skill_score[key].items()}

with open(fname, 'w') as f:
    f.write(json.dumps(skill_score))
```

### Normalized Taylor diagrams

The radius is model standard deviation error divided  by observations deviation,
azimuth is arc-cosine of cross correlation (R), and distance to point (1, 0) on
the
abscissa is Centered RMS.

<div class="prompt input_prompt">
In&nbsp;[8]:
</div>

```python
%matplotlib inline
import matplotlib.pyplot as plt
from ioos_tools.taylor_diagram import TaylorDiagram


def make_taylor(samples):
    fig = plt.figure(figsize=(9, 9))
    dia = TaylorDiagram(samples['std']['OBS_DATA'],
                        fig=fig,
                        label="Observation")
    # Add samples to Taylor diagram.
    samples.drop('OBS_DATA', inplace=True)
    for model, row in samples.iterrows():
        dia.add_sample(row['std'], row['corr'], marker='s', ls='',
                       label=model)
    # Add RMS contours, and label them.
    contours = dia.add_contours(colors='0.5')
    plt.clabel(contours, inline=1, fontsize=10)
    # Add a figure legend.
    kw = dict(prop=dict(size='small'), loc='upper right')
    fig.legend(dia.samplePoints,
               [p.get_label() for p in dia.samplePoints],
               numpoints=1, **kw)
    return fig
```

<div class="prompt input_prompt">
In&nbsp;[9]:
</div>

```python
import numpy as np
import pandas as pd

dfs = load_ncs(config)

# Bin and interpolate all series.
freq = '30min'
for station, df in list(dfs.iteritems()):
    df = df.resample(freq).interpolate().dropna(axis=1)
    if 'OBS_DATA' in df:
        samples = pd.DataFrame.from_dict(dict(std=df.std(),
                                              corr=df.corr()['OBS_DATA']))
    else:
        continue
    samples[samples < 0] = np.NaN
    samples.dropna(inplace=True)
    if len(samples) <= 2:  # 1 obs 1 model.
        continue
    fig = make_taylor(samples)
    fig.savefig(os.path.join(save_dir, '{}.png'.format(station)))
    plt.close(fig)
```
