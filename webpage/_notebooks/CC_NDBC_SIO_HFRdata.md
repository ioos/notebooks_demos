---
layout: notebook
title: ""
---


## HF Radar Compliance Checker Script

### Purpose:
Run the compliance checker on NDBC and SIO HF radar data to compare the metadata
compliance.

Written by: JAB

<div class="prompt input_prompt">
In&nbsp;[1]:
</div>

```python
from compliance_checker.runner import ComplianceChecker, CheckSuite

# Load all available checker classes.
check_suite = CheckSuite()
check_suite.load_all_available_checkers()
```

### URLs to the east coast and Gulf of Mexico 1 km resolution HF Radar data

<div class="prompt input_prompt">
In&nbsp;[2]:
</div>

```python
NDBC_HFR = 'http://sdf.ndbc.noaa.gov/thredds/dodsC/hfradar_usegc_1km'
SIO_HFR = 'http://hfrnet.ucsd.edu/thredds/dodsC/HFRNet/USEGC/1km/hourly/RTV'
```

### NDBC

<div class="prompt input_prompt">
In&nbsp;[3]:
</div>

```python
from IPython.display import HTML, display

output_filename = 'NDBC_HFR.html'
kw = dict(checker_names=['cf', 'acdd'],
          verbose=True,
          criteria='normal',
          output_format='html')

ret_val, err = ComplianceChecker.run_checker(NDBC_HFR, output_filename=output_filename, **kw)


with open(output_filename) as f:
    display(HTML(f.read()))
```


<!doctype html>
<html>
  <head>
    <meta charset="UTF-8">
    <meta name="description" content="IOOS Compliance Checker Results">
    <title>Compliance Checker</title>
    <link rel="stylesheet" type="text/css" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css">
    <link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/font-awesome/4.3.0/css/font-awesome.min.css">
    <script type="text/javascript" src="https://code.jquery.com/jquery-2.1.4.min.js"></script>
    <script type="text/javascript" src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>
    <style>
.navbar-custom {
  background-color: #c6d4e1;
  border-size: 0px;
  margin-bottom: 0px;
  border-radius: 0px;
}

.navbar-custom .navbar-img-brand {
  float: left;
}

.navbar-custom .navbar-img-brand img {
  height: 47px;
}

.navbar-custom .navbar-brand {
  color: #565c61;
}
.navbar-custom .navbar-brand:hover,
.navbar-custom .navbar-brand:focus {
  color: #3e4246;
  background-color: transparent;
}
.navbar-custom .navbar-text {
  color: #565c61;
}
.navbar-custom .navbar-nav > li > a {
  color: #565c61;
}
.navbar-custom .navbar-nav > li > a:hover,
.navbar-custom .navbar-nav > li > a:focus {
  color: #333333;
  background-color: transparent;
}
.navbar-custom .navbar-nav > .active > a,
.navbar-custom .navbar-nav > .active > a:hover,
.navbar-custom .navbar-nav > .active > a:focus {
  color: #333333;
  background-color: #b0c4d6;
}
.navbar-custom .navbar-nav > .disabled > a,
.navbar-custom .navbar-nav > .disabled > a:hover,
.navbar-custom .navbar-nav > .disabled > a:focus {
  color: #cccccc;
  background-color: transparent;
}
.navbar-custom .navbar-toggle {
  border-color: #dddddd;
}
.navbar-custom .navbar-toggle:hover,
.navbar-custom .navbar-toggle:focus {
  background-color: #dddddd;
}
.navbar-custom .navbar-toggle .icon-bar {
  background-color: #cccccc;
}
.navbar-custom .navbar-collapse,
.navbar-custom .navbar-form {
  border-color: #afc2d5;
}
.navbar-custom .navbar-nav > .dropdown > a:hover .caret,
.navbar-custom .navbar-nav > .dropdown > a:focus .caret {
  border-top-color: #333333;
  border-bottom-color: #333333;
}
.navbar-custom .navbar-nav > .open > a,
.navbar-custom .navbar-nav > .open > a:hover,
.navbar-custom .navbar-nav > .open > a:focus {
  background-color: #b0c4d6;
  color: #333333;
}
.navbar-custom .navbar-nav > .open > a .caret,
.navbar-custom .navbar-nav > .open > a:hover .caret,
.navbar-custom .navbar-nav > .open > a:focus .caret {
  border-top-color: #333333;
  border-bottom-color: #333333;
}
.navbar-custom .navbar-nav > .dropdown > a .caret {
  border-top-color: #565c61;
  border-bottom-color: #565c61;
}
@media (max-width: 767) {
  .navbar-custom .navbar-nav .open .dropdown-menu > li > a {
    color: #565c61;
  }
  .navbar-custom .navbar-nav .open .dropdown-menu > li > a:hover,
  .navbar-custom .navbar-nav .open .dropdown-menu > li > a:focus {
    color: #333333;
    background-color: transparent;
  }
  .navbar-custom .navbar-nav .open .dropdown-menu > .active > a,
  .navbar-custom .navbar-nav .open .dropdown-menu > .active > a:hover,
  .navbar-custom .navbar-nav .open .dropdown-menu > .active > a:focus {
    color: #333333;
    background-color: #b0c4d6;
  }
  .navbar-custom .navbar-nav .open .dropdown-menu > .disabled > a,
  .navbar-custom .navbar-nav .open .dropdown-menu > .disabled > a:hover,
  .navbar-custom .navbar-nav .open .dropdown-menu > .disabled > a:focus {
    color: #cccccc;
    background-color: transparent;
  }
}
.navbar-custom .navbar-link {
  color: #565c61;
}
.navbar-custom .navbar-link:hover {
  color: #333333;
}

.bad-score {
  color: #D70834;
}

thead .tname {
  width: 60%;
}
thead .tpriority {
  width: 20%;
}

thead .tscore {
  width: 20%;
}

thead .cname {
  width: 25%;
}

thead .cpriority {
  width: 5%;
}

thead .ccorrection {
  width: 70%;
}

.table-collapse {
  display: inline;
  font-size: 18px;
  font-weight: bold;
}

.table-collapse a{
  color: #333;
}

.table-collapse a:hover {
  color: #777;
  text-decoration: none;
}

.failures {
  display: inline;
}

.label-as-badge {
  border-radius: 1em;
}
    </style>

  </head>
  <body>
  <header>
      <nav class="navbar navbar-custom">
        <div class="container">
          <div class="navbar-header">
            <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#nb-collapse">
              <span class="icon-bar"></span>
              <span class="icon-bar"></span>
              <span class="icon-bar"></span>
            </button>
            <a class="navbar-img-brand" href="http://ioos.noaa.gov/">
              <img src="http://catalog.ioos.us/static/img/ioos.png" alt="IOOS Catalog" />
            </a>
            <div class="navbar-brand">
              Compliance Checker
            </div>
          </div>
      </nav>
    </header>

    <div class="container">
      <div class="row">
        <div class="col-md-12">
          <div class="page-header">
            <h3>Your dataset scored 83 out of 91 points</h3>
            <p>During the cf check</p>
            <p>For dataset http://sdf.ndbc.noaa.gov/thredds/dodsC/hfradar_usegc_1km</p>
          </div>
        </div>
        <div class="col-md-12">
          <h4>
            Scoring Breakdown:
          </h4>
        </div>
        <div class="col-md-12">
          <div class="table-collapse">
            <a data-target="high-priority-table" href="#">High Priority <i class="glyphicon glyphicon-collapse-up"></i></a>
          </div>
          <div class="failures">
            | <span class="label label-danger label-as-badge">3</span>
          </div>
          <div class="high-priority-table collapse in">
            <table class="table">
              <thead>
                <tr>
                  <th class="tname">Name</th>
                  <th class="tscore">Score</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                <td>§2.2 Valid netCDF data types</td>
                  <td>12/12</td>
                </tr>
                <tr>
                <td>§2.3 Legal variable names</td>
                  <td>12/12</td>
                </tr>
                <tr>
                <td>§2.4 Unique dimensions</td>
                  <td>12/12</td>
                </tr>
                <tr class="bad-score">
                <td>§2.6.1 Global Attribute Conventions includes CF-1.6</td>
                  <td>0/1</td>
                </tr>
                <tr>
                <td>§2.6.2 Convention Attributes</td>
                  <td>5/5</td>
                </tr>
                <tr class="bad-score">
                <td>§3.1 Variables contain valid CF Units</td>
                  <td>0/1</td>
                </tr>
                <tr>
                <td>§3.1 Variables contain valid units for the standard_name</td>
                  <td>6/6</td>
                </tr>
                <tr>
                <td>§3.3 Standard Names</td>
                  <td>7/7</td>
                </tr>
                <tr>
                <td>§3.4 Ancillary Variables</td>
                  <td>2/2</td>
                </tr>
                <tr>
                <td>§4 Coordinate Variable latitude contains valid attributes</td>
                  <td>2/2</td>
                </tr>
                <tr>
                <td>§4 Coordinate Variable longitude contains valid attributes</td>
                  <td>2/2</td>
                </tr>
                <tr class="bad-score">
                <td>§4.4 Time coordinate variable and attributes</td>
                  <td>0/1</td>
                </tr>
                </tbody>
            </table>
          </div> <!-- .high-priority-table -->
        </div> <!-- .col-md-12 -->
        <div class="col-md-12">
          <div class="table-collapse">
            <a data-target="medium-priority-table" href="#">Medium Priority <i class="glyphicon glyphicon-collapse-up"></i></a>
          </div>
          <div class="failures">
            | <span class="label label-danger label-as-badge">1</span>
          </div>
          <div class="medium-priority-table collapse in">
            <table class="table">
              <thead>
                <tr>
                  <th class="tname">Name</th>
                  <th class="tscore">Score</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                <td>§4 Coordinate Variables</td>
                  <td>3/3</td>
                </tr>
                <tr>
                <td>§4.1 Coordinates representing latitude</td>
                  <td>6/6</td>
                </tr>
                <tr>
                <td>§4.1 Coordinates representing longitude</td>
                  <td>6/6</td>
                </tr>
                <tr class="bad-score">
                <td>§5.1 Geophysical variables contain valid dimensions</td>
                  <td>0/5</td>
                </tr>
                <tr>
                <td>§8.1 Packed Data</td>
                  <td>8/8</td>
                </tr>
                </tbody>
            </table>
          </div> <!-- .medium-priority-table -->
        </div> <!-- .col-md-12 -->
        <div class="col-md-12">
          <div class="table-collapse">
            <a data-target="low-priority-table" href="#">Low Priority <i class="glyphicon glyphicon-collapse-up"></i></a>
          </div>
          <div class="low-priority-table collapse in">
            <table class="table">
              <thead>
                <tr>
                  <th class="tname">Name</th>
                  <th class="tscore">Score</th>
                </tr>
              </thead>
              <tbody>
                </tbody>
            </table>
          </div>
        </div> <!-- .col-md-12 -->
        <div class="col-md-12">
          <h4>Corrective Actions</h4>
          <table class="table">
            <thead>
              <tr>
                <th class="cname">Name</td>
                <th class="cpriority">Priority</td>
                <th class="ccorrection">Corrective action</td>
              </tr>
            </thead>
            <tbody>
            <tr>
                  <td>§2.6.1 Global Attribute Conventions includes CF-1.6</td>
                  <td>3</td>
                  <td>Conventions field is not "CF-1.6"</td>
                </tr>
              <tr>
                  <td>§3.1 Variables contain valid CF Units</td>
                  <td>3</td>
                  <td>unknown units type (None) for procParams</td>
                </tr>
              <tr>
                  <td>§4.4 Time coordinate variable and attributes</td>
                  <td>3</td>
                  <td>time does not have units</td>
                </tr>
              <tr>
                  <td>§5.1 Geophysical variables contain valid dimensions</td>
                  <td>2</td>
                  <td>The time dimension for the variable time does not have an associated coordinate variable, but is a Lat/Lon/Time/Height dimension.</td>
                </tr>
              <tr>
                  <td>§5.1 Geophysical variables contain valid dimensions</td>
                  <td>2</td>
                  <td>The time dimension for the variable u does not have an associated coordinate variable, but is a Lat/Lon/Time/Height dimension.</td>
                </tr>
              <tr>
                  <td>§5.1 Geophysical variables contain valid dimensions</td>
                  <td>2</td>
                  <td>The time dimension for the variable v does not have an associated coordinate variable, but is a Lat/Lon/Time/Height dimension.</td>
                </tr>
              <tr>
                  <td>§5.1 Geophysical variables contain valid dimensions</td>
                  <td>2</td>
                  <td>The time dimension for the variable DOPx does not have an associated coordinate variable, but is a Lat/Lon/Time/Height dimension.</td>
                </tr>
              <tr>
                  <td>§5.1 Geophysical variables contain valid dimensions</td>
                  <td>2</td>
                  <td>The time dimension for the variable DOPy does not have an associated coordinate variable, but is a Lat/Lon/Time/Height dimension.</td>
                </tr>
              </tbody>
          </table>
        </div> <!-- .col-md-12 -->
      </div> <!-- .row -->
    </div> <!-- .container -->
    <script type="text/javascript">
$(document).ready(function() {
    $('.high-priority-table').collapse({toggle: false});
    $('.table-collapse').click(function(e) {
      e.preventDefault();
      console.log("Collapse this table");
      $('.' + $(e.target).data('target')).collapse('toggle');
      var glyph = $(e.target).find('.glyphicon');
      if(glyph.hasClass('glyphicon-collapse-up')) {
        glyph.removeClass('glyphicon-collapse-up');
        glyph.addClass('glyphicon-collapse-down');
      } else {
        glyph.removeClass('glyphicon-collapse-down');
        glyph.addClass('glyphicon-collapse-up');
      }
    });
});
    </script>
  </body>
</html>


### Scripps

<div class="prompt input_prompt">
In&nbsp;[4]:
</div>

```python
output_filename = 'SIO_HFR.html'
ret_val, err = ComplianceChecker.run_checker(SIO_HFR, output_filename=output_filename, **kw)

with open(output_filename) as f:
    display(HTML(f.read()))
```


<!doctype html>
<html>
  <head>
    <meta charset="UTF-8">
    <meta name="description" content="IOOS Compliance Checker Results">
    <title>Compliance Checker</title>
    <link rel="stylesheet" type="text/css" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css">
    <link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/font-awesome/4.3.0/css/font-awesome.min.css">
    <script type="text/javascript" src="https://code.jquery.com/jquery-2.1.4.min.js"></script>
    <script type="text/javascript" src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>
    <style>
.navbar-custom {
  background-color: #c6d4e1;
  border-size: 0px;
  margin-bottom: 0px;
  border-radius: 0px;
}

.navbar-custom .navbar-img-brand {
  float: left;
}

.navbar-custom .navbar-img-brand img {
  height: 47px;
}

.navbar-custom .navbar-brand {
  color: #565c61;
}
.navbar-custom .navbar-brand:hover,
.navbar-custom .navbar-brand:focus {
  color: #3e4246;
  background-color: transparent;
}
.navbar-custom .navbar-text {
  color: #565c61;
}
.navbar-custom .navbar-nav > li > a {
  color: #565c61;
}
.navbar-custom .navbar-nav > li > a:hover,
.navbar-custom .navbar-nav > li > a:focus {
  color: #333333;
  background-color: transparent;
}
.navbar-custom .navbar-nav > .active > a,
.navbar-custom .navbar-nav > .active > a:hover,
.navbar-custom .navbar-nav > .active > a:focus {
  color: #333333;
  background-color: #b0c4d6;
}
.navbar-custom .navbar-nav > .disabled > a,
.navbar-custom .navbar-nav > .disabled > a:hover,
.navbar-custom .navbar-nav > .disabled > a:focus {
  color: #cccccc;
  background-color: transparent;
}
.navbar-custom .navbar-toggle {
  border-color: #dddddd;
}
.navbar-custom .navbar-toggle:hover,
.navbar-custom .navbar-toggle:focus {
  background-color: #dddddd;
}
.navbar-custom .navbar-toggle .icon-bar {
  background-color: #cccccc;
}
.navbar-custom .navbar-collapse,
.navbar-custom .navbar-form {
  border-color: #afc2d5;
}
.navbar-custom .navbar-nav > .dropdown > a:hover .caret,
.navbar-custom .navbar-nav > .dropdown > a:focus .caret {
  border-top-color: #333333;
  border-bottom-color: #333333;
}
.navbar-custom .navbar-nav > .open > a,
.navbar-custom .navbar-nav > .open > a:hover,
.navbar-custom .navbar-nav > .open > a:focus {
  background-color: #b0c4d6;
  color: #333333;
}
.navbar-custom .navbar-nav > .open > a .caret,
.navbar-custom .navbar-nav > .open > a:hover .caret,
.navbar-custom .navbar-nav > .open > a:focus .caret {
  border-top-color: #333333;
  border-bottom-color: #333333;
}
.navbar-custom .navbar-nav > .dropdown > a .caret {
  border-top-color: #565c61;
  border-bottom-color: #565c61;
}
@media (max-width: 767) {
  .navbar-custom .navbar-nav .open .dropdown-menu > li > a {
    color: #565c61;
  }
  .navbar-custom .navbar-nav .open .dropdown-menu > li > a:hover,
  .navbar-custom .navbar-nav .open .dropdown-menu > li > a:focus {
    color: #333333;
    background-color: transparent;
  }
  .navbar-custom .navbar-nav .open .dropdown-menu > .active > a,
  .navbar-custom .navbar-nav .open .dropdown-menu > .active > a:hover,
  .navbar-custom .navbar-nav .open .dropdown-menu > .active > a:focus {
    color: #333333;
    background-color: #b0c4d6;
  }
  .navbar-custom .navbar-nav .open .dropdown-menu > .disabled > a,
  .navbar-custom .navbar-nav .open .dropdown-menu > .disabled > a:hover,
  .navbar-custom .navbar-nav .open .dropdown-menu > .disabled > a:focus {
    color: #cccccc;
    background-color: transparent;
  }
}
.navbar-custom .navbar-link {
  color: #565c61;
}
.navbar-custom .navbar-link:hover {
  color: #333333;
}

.bad-score {
  color: #D70834;
}

thead .tname {
  width: 60%;
}
thead .tpriority {
  width: 20%;
}

thead .tscore {
  width: 20%;
}

thead .cname {
  width: 25%;
}

thead .cpriority {
  width: 5%;
}

thead .ccorrection {
  width: 70%;
}

.table-collapse {
  display: inline;
  font-size: 18px;
  font-weight: bold;
}

.table-collapse a{
  color: #333;
}

.table-collapse a:hover {
  color: #777;
  text-decoration: none;
}

.failures {
  display: inline;
}

.label-as-badge {
  border-radius: 1em;
}
    </style>

  </head>
  <body>
  <header>
      <nav class="navbar navbar-custom">
        <div class="container">
          <div class="navbar-header">
            <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#nb-collapse">
              <span class="icon-bar"></span>
              <span class="icon-bar"></span>
              <span class="icon-bar"></span>
            </button>
            <a class="navbar-img-brand" href="http://ioos.noaa.gov/">
              <img src="http://catalog.ioos.us/static/img/ioos.png" alt="IOOS Catalog" />
            </a>
            <div class="navbar-brand">
              Compliance Checker
            </div>
          </div>
      </nav>
    </header>

    <div class="container">
      <div class="row">
        <div class="col-md-12">
          <div class="page-header">
            <h3>Your dataset scored 122 out of 139 points</h3>
            <p>During the cf check</p>
            <p>For dataset http://hfrnet.ucsd.edu/thredds/dodsC/HFRNet/USEGC/1km/hourly/RTV</p>
          </div>
        </div>
        <div class="col-md-12">
          <h4>
            Scoring Breakdown:
          </h4>
        </div>
        <div class="col-md-12">
          <div class="table-collapse">
            <a data-target="high-priority-table" href="#">High Priority <i class="glyphicon glyphicon-collapse-up"></i></a>
          </div>
          <div class="failures">
            | <span class="label label-danger label-as-badge">4</span>
          </div>
          <div class="high-priority-table collapse in">
            <table class="table">
              <thead>
                <tr>
                  <th class="tname">Name</th>
                  <th class="tscore">Score</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                <td>§2.2 Valid netCDF data types</td>
                  <td>14/14</td>
                </tr>
                <tr>
                <td>§2.3 Legal variable names</td>
                  <td>14/14</td>
                </tr>
                <tr>
                <td>§2.4 Unique dimensions</td>
                  <td>14/14</td>
                </tr>
                <tr class="bad-score">
                <td>§2.6.1 Global Attribute Conventions includes CF-1.6</td>
                  <td>0/1</td>
                </tr>
                <tr>
                <td>§2.6.2 Convention Attributes</td>
                  <td>5/5</td>
                </tr>
                <tr class="bad-score">
                <td>§3.1 Variables contain valid CF Units</td>
                  <td>0/1</td>
                </tr>
                <tr class="bad-score">
                <td>§3.1 Variables contain valid units for the standard_name</td>
                  <td>7/9</td>
                </tr>
                <tr>
                <td>§3.3 Standard Names</td>
                  <td>9/9</td>
                </tr>
                <tr>
                <td>§3.4 Ancillary Variables</td>
                  <td>2/2</td>
                </tr>
                <tr>
                <td>§4 Coordinate Variable latitude contains valid attributes</td>
                  <td>2/2</td>
                </tr>
                <tr>
                <td>§4 Coordinate Variable longitude contains valid attributes</td>
                  <td>2/2</td>
                </tr>
                <tr>
                <td>§4.4 Time coordinate variable and attributes</td>
                  <td>6/6</td>
                </tr>
                <tr>
                <td>§5.2 Latitude and longitude coordinates of a horizontal grid</td>
                  <td>5/5</td>
                </tr>
                <tr class="bad-score">
                <td>§9.1 Feature Types are all the same</td>
                  <td>0/1</td>
                </tr>
                </tbody>
            </table>
          </div> <!-- .high-priority-table -->
        </div> <!-- .col-md-12 -->
        <div class="col-md-12">
          <div class="table-collapse">
            <a data-target="medium-priority-table" href="#">Medium Priority <i class="glyphicon glyphicon-collapse-up"></i></a>
          </div>
          <div class="failures">
            | <span class="label label-danger label-as-badge">3</span>
          </div>
          <div class="medium-priority-table collapse in">
            <table class="table">
              <thead>
                <tr>
                  <th class="tname">Name</th>
                  <th class="tscore">Score</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                <td>§4 Coordinate Variables</td>
                  <td>3/3</td>
                </tr>
                <tr>
                <td>§4.1 Coordinates representing latitude</td>
                  <td>6/6</td>
                </tr>
                <tr>
                <td>§4.1 Coordinates representing longitude</td>
                  <td>6/6</td>
                </tr>
                <tr>
                <td>§5.1 Geophysical variables contain valid dimensions</td>
                  <td>6/6</td>
                </tr>
                <tr class="bad-score">
                <td>§5.3 Is reduced horizontal grid</td>
                  <td>0/4</td>
                </tr>
                <tr>
                <td>§6.2 Alternative Coordinates</td>
                  <td>1/1</td>
                </tr>
                <tr>
                <td>§9.3.1 Orthogonal Multidimensional Array</td>
                  <td>14/14</td>
                </tr>
                <tr class="bad-score">
                <td>§9.4 featureType attribute</td>
                  <td>0/1</td>
                </tr>
                <tr class="bad-score">
                <td>§9.5 Discrete Geometry</td>
                  <td>2/9</td>
                </tr>
                <tr>
                <td>§9.6 Missing Data</td>
                  <td>4/4</td>
                </tr>
                </tbody>
            </table>
          </div> <!-- .medium-priority-table -->
        </div> <!-- .col-md-12 -->
        <div class="col-md-12">
          <div class="table-collapse">
            <a data-target="low-priority-table" href="#">Low Priority <i class="glyphicon glyphicon-collapse-up"></i></a>
          </div>
          <div class="low-priority-table collapse in">
            <table class="table">
              <thead>
                <tr>
                  <th class="tname">Name</th>
                  <th class="tscore">Score</th>
                </tr>
              </thead>
              <tbody>
                </tbody>
            </table>
          </div>
        </div> <!-- .col-md-12 -->
        <div class="col-md-12">
          <h4>Corrective Actions</h4>
          <table class="table">
            <thead>
              <tr>
                <th class="cname">Name</td>
                <th class="cpriority">Priority</td>
                <th class="ccorrection">Corrective action</td>
              </tr>
            </thead>
            <tbody>
            <tr>
                  <td>§2.6.1 Global Attribute Conventions includes CF-1.6</td>
                  <td>3</td>
                  <td>Conventions field is not "CF-1.6"</td>
                </tr>
              <tr>
                  <td>§3.1 Variables contain valid CF Units</td>
                  <td>3</td>
                  <td>unknown units type (None) for procParams</td>
                </tr>
              <tr>
                  <td>§3.1 Variables contain valid units for the standard_name</td>
                  <td>3</td>
                  <td>units are hours since 2012-01-01T00:00:00Z, standard_name units should be s</td>
                </tr>
              <tr>
                  <td>§3.1 Variables contain valid units for the standard_name</td>
                  <td>3</td>
                  <td>units are hours since 2012-01-01T00:00:00Z, standard_name units should be s</td>
                </tr>
              <tr>
                  <td>is_reduced_horizontal_grid</td>
                  <td>2</td>
                  <td>Coordinate  is not a proper variable</td>
                </tr>
              <tr>
                  <td>is_reduced_horizontal_grid</td>
                  <td>2</td>
                  <td>Coordinate  is not a proper variable</td>
                </tr>
              <tr>
                  <td>is_reduced_horizontal_grid</td>
                  <td>2</td>
                  <td>Coordinate  is not a proper variable</td>
                </tr>
              <tr>
                  <td>is_reduced_horizontal_grid</td>
                  <td>2</td>
                  <td>Coordinate  is not a proper variable</td>
                </tr>
              <tr>
                  <td>§9.1 Feature Types are all the same</td>
                  <td>3</td>
                  <td>At least one of the variables has a different feature type than the rest of the variables.</td>
                </tr>
              <tr>
                  <td>§9.1 Feature Types are all the same</td>
                  <td>3</td>
                  <td>procParams(nProcParam) site_lat(nSites) time_offset(time) u(time, lat, lon) site_code(nSites, maxStrlen64) site_netCode(nSites, maxStrlen64) v(time, lat, lon) site_lon(nSites) time_run(time)</td>
                </tr>
              <tr>
                  <td>§9.4 featureType attribute</td>
                  <td>2</td>
                  <td>The featureType is provided and is not from the featureType list.</td>
                </tr>
              <tr>
                  <td>dataset</td>
                  <td>2</td>
                  <td>The cf_role featureType is not properly defined.</td>
                </tr>
              <tr>
                  <td>check_coordinates</td>
                  <td>2</td>
                  <td>The variable procParams does not have associated coordinates</td>
                </tr>
              <tr>
                  <td>check_coordinates</td>
                  <td>2</td>
                  <td>The variable site_code does not have associated coordinates</td>
                </tr>
              <tr>
                  <td>check_coordinates</td>
                  <td>2</td>
                  <td>The variable site_lat does not have associated coordinates</td>
                </tr>
              <tr>
                  <td>check_coordinates</td>
                  <td>2</td>
                  <td>The variable site_lon does not have associated coordinates</td>
                </tr>
              <tr>
                  <td>check_coordinates</td>
                  <td>2</td>
                  <td>The variable site_netCode does not have associated coordinates</td>
                </tr>
              <tr>
                  <td>check_coordinates</td>
                  <td>2</td>
                  <td>The variable time_offset does not have associated coordinates</td>
                </tr>
              </tbody>
          </table>
        </div> <!-- .col-md-12 -->
      </div> <!-- .row -->
    </div> <!-- .container -->
    <script type="text/javascript">
$(document).ready(function() {
    $('.high-priority-table').collapse({toggle: false});
    $('.table-collapse').click(function(e) {
      e.preventDefault();
      console.log("Collapse this table");
      $('.' + $(e.target).data('target')).collapse('toggle');
      var glyph = $(e.target).find('.glyphicon');
      if(glyph.hasClass('glyphicon-collapse-up')) {
        glyph.removeClass('glyphicon-collapse-up');
        glyph.addClass('glyphicon-collapse-down');
      } else {
        glyph.removeClass('glyphicon-collapse-down');
        glyph.addClass('glyphicon-collapse-up');
      }
    });
});
    </script>
  </body>
</html>

