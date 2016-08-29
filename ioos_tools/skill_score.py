from __future__ import absolute_import, division, print_function

import numpy as np
import numpy.ma as ma
from pandas import DataFrame

__all__ = ['both_valid',
           'mean_bias',
           'median_bias',
           'rmse',
           'r2',
           'apply_skill',
           'low_pass']


def both_valid(x, y):
    """
    Returns a mask where both series are valid.

    Examples
    --------
    >>> import numpy as np
    >>> x = [np.NaN, 1, 2, 3, 4, 5]
    >>> y = [0, 1, np.NaN, 3, 4, 5]
    >>> both_valid(x, y)
    array([False,  True, False,  True,  True,  True], dtype=bool)

    """
    mask_x = np.isnan(x)
    mask_y = np.isnan(y)
    return np.logical_and(~mask_x, ~mask_y)


def mean_bias(obs, model):
    from sklearn.metrics import mean_absolute_error
    return mean_absolute_error(obs, model)


def median_bias(obs, model):
    from sklearn.metrics import median_absolute_error
    return median_absolute_error(obs, model)


def rmse(obs, model):
    """
    Compute root mean square between the observed data (`obs`) and the modeled
    data (`model`).
    >>> obs = [3, -0.5, 2, 7]
    >>> model = [2.5, 0.0, 2, 8]
    >>> rmse(obs, model)
    0.61237243569579447
    >>> obs = [[0.5, 1],[-1, 1],[7, -6]]
    >>> model = [[0, 2],[-1, 2],[8, -5]]
    >>> rmse(obs, model)
    0.84162541153017323

    """
    from sklearn.metrics import mean_squared_error
    return np.sqrt(mean_squared_error(obs, model))


def r2(x, y):
    from sklearn.metrics import r2_score
    return r2_score(x, y)


def apply_skill(dfs, function, remove_mean=True, filter_tides=False):
    skills = dict()
    for station, df in dfs.iteritems():
        if filter_tides:
            df = df.apply(low_pass)
        skill = dict()
        obs = df.pop('OBS_DATA')
        if obs.isnull().all():
            # No observations.
            skills.update({station: np.NaN})
            continue
        for model, y in df.iteritems():
            # No models.
            if y.isnull().all():
                skills.update({station: np.NaN})
                continue
            mask = both_valid(obs, y)
            x, y = obs[mask], y[mask]
            if remove_mean:
                x, y = x-x.mean(), y-y.mean()
            if x.size:
                ret = function(x, y)
            else:
                ret = np.NaN
            skill.update({model: ret})
        skills.update({station: skill})
    return DataFrame.from_dict(skills)


def low_pass(series, window_size=193, T=40, dt=360):
    """
    This function applies a lanczos filter on a pandas time-series and
    returns the low pass data series.

    series : Pandas series
    window_size : Size of the filter windows (default is 96+1+96).
    T : Period of the filter. (The default of 40 hours filter should
        get rid of all tides.)
    dt : time_delta in seconds.  Default is 360 (6 minutes).

    """
    from oceans import lanc
    T *= 60*60.  # To seconds.
    freq = dt/T

    mask = np.isnan(series)
    avg = series.mean()
    series = series - avg
    series.interpolate(inplace=True)

    wt = lanc(window_size, freq)
    low = np.convolve(wt, series, mode='same')
    low = ma.masked_array(low, mask)
    return low+avg


if __name__ == '__main__':
    import doctest
    doctest.testmod()
