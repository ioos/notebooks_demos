from __future__ import absolute_import, division, print_function

import numpy as np
import pandas as pd
import numpy.ma as ma
from pandas.tseries.frequencies import to_offset


"""
Basic QA/QC tools.

"""


def has_time_gaps(times, freq):
    """
    Check for gaps in a series time-stamp `times`. The `freq` can be a string
    or a pandas offset object.  Note the `freq` cannot be an ambiguous offset
    (like week, months, etc), in those case reduce it to the smallest
    unambiguous unit (i.e.: 1 month -> 30 days).

    Example
    -------
    >>> import numpy as np
    >>> from pandas import date_range
    >>> times = date_range('1980-01-19', periods=48, freq='1H')
    >>> has_time_gaps(times, freq='6min')
    True
    >>> has_time_gaps(times, freq='1H')
    False

    """
    freq = to_offset(freq)
    if hasattr(freq, 'delta'):
        times = pd.DatetimeIndex(times)
    else:
        raise ValueError('Cannot interpret freq {!r} delta'.format(freq))
    return (np.diff(times) > freq.delta.to_timedelta64()).any()


def is_monotonically_increasing(series):
    """
    Check if a given list or array is monotonically increasing.

    Examples
    --------
    >>> from pandas import date_range
    >>> times = date_range('1980-01-19', periods=10)
    >>> all(is_monotonically_increasing(times))
    True
    >>> import numpy as np
    >>> all(is_monotonically_increasing(np.r_[times[-2:-1], times]))
    False
    """
    return [x < y for x, y in zip(series, series[1:])]


def is_flatline(series, reps=10, eps=None):
    """
    Check for consecutively repeated values (`reps`) in `series` within a
    tolerance `eps`.

    Examples
    --------
    >>> series = np.r_[np.random.rand(10), [10]*15, np.random.rand(10)]
    >>> is_flatline(series, reps=10)
    array([False, False, False, False, False, False, False, False, False,
           False,  True,  True,  True,  True,  True,  True,  True,  True,
            True,  True,  True,  True,  True,  True,  True, False, False,
           False, False, False, False, False, False, False, False], dtype=bool)

    """
    series = np.asanyarray(series)

    if not eps:
        eps = np.finfo(float).eps

    if reps < 2:
        reps = 2

    mask = np.zeros_like(series, dtype='bool')

    flatline = 1
    for k, current in enumerate(series):
        if np.abs(series[k-1] - current) < eps:
            flatline += 1
        else:
            if flatline >= reps:
                mask[k-flatline:k] = True
            flatline = 1
    return mask


def is_spike(series, window_size=3, threshold=3, scale=True):
    """
    Flags spikes in an array-like object using a median filter of `window_size`
    and a `threshold` for the median difference.  If `scale=False` the
    differences are not scale by the data standard deviation and the masking
    is "aggressive."

    Examples
    --------
    >>> from pandas import pd.Series, date_range
    >>> series = [33.43, 33.45, 34.45, 90.0, 35.67, 34.9, 43.5, 34.6, 33.7]
    >>> series = pd.Series(series, index=date_range('1980-01-19',
    ...                    periods=len(series)))
    >>> series[is_spike(series, window_size=3, threshold=3, scale=False)]
    1980-01-22    90.0
    1980-01-25    43.5
    dtype: float64
    >>> series[is_spike(series, window_size=3, threshold=3, scale=True)]
    1980-01-22    90.0
    Freq: D, dtype: float64

    """
    # bfill+ffil needs a series and won't affect the median.
    series = pd.Series(series)
    roll = series.rolling(window=window_size, center=True)
    medians = roll.median().fillna(method='bfill').fillna(method='ffill')
    difference = np.abs(series - medians).values
    if scale:
        return difference > (threshold*difference.std())
    return difference > threshold


def threshold_series(series, vmin=None, vmax=None):
    """
    Threshold an series by flagging with NaN values below `vmin` and above
    `vmax`.

    Examples
    --------
    >>> series = [0.1, 20, 30, 35.5, 34.9, 43.5, 34.6, 40]
    >>> threshold_series(series, vmin=30, vmax=40)
    masked_array(data = [-- -- 30.0 35.5 34.9 -- 34.6 40.0],
                 mask = [ True  True False False False  True False False],
           fill_value = 1e+20)
    <BLANKLINE>
    >>> from pandas import pd.Series, date_range
    >>> series = pd.Series(series, index=date_range('1980-01-19',
    ...                    periods=len(series)))
    >>> threshold_series(series, vmin=30, vmax=40)
    1980-01-19     NaN
    1980-01-20     NaN
    1980-01-21    30.0
    1980-01-22    35.5
    1980-01-23    34.9
    1980-01-24     NaN
    1980-01-25    34.6
    1980-01-26    40.0
    Freq: D, dtype: float64

    """
    if not vmin:
        vmin = min(series)
    if not vmax:
        vmax = max(series)

    masked = ma.masked_outside(series, vmin, vmax)
    if masked.mask.any():
        if isinstance(series, pd.Series):
            series[masked.mask] = np.NaN
            return series
    return masked


def filter_spikes(series, window_size=3, threshold=3, scale=True):
    """
    Filter an array-like object using a median filter and a `threshold`
    for the median difference.

    Examples
    --------
    >>> from pandas import pd.Series, date_range
    >>> series = [33.43, 33.45, 34.45, 90.0, 35.67, 34.9, 43.5, 34.6, 33.7]
    >>> series = pd.Series(series, index=date_range('1980-01-19',
    ...                    periods=len(series)))
    >>> filter_spikes(series)
    1980-01-19    33.43
    1980-01-20    33.45
    1980-01-21    34.45
    1980-01-22      NaN
    1980-01-23    35.67
    1980-01-24    34.90
    1980-01-25    43.50
    1980-01-26    34.60
    1980-01-27    33.70
    Freq: D, dtype: float64

    """
    outlier_idx = is_spike(series, window_size=window_size,
                           threshold=threshold, scale=scale)
    if not isinstance(series, pd.Series):
        series = np.asanyarray(series)
    series[outlier_idx] = np.NaN
    return series


def _high_pass(data, alpha=0.5):
    """
    Runs a high pass RC filter over the given data.

    Parameters
    ----------
    data : array_like

    alpha : float
            Smoothing factor between 0.0 (exclusive) and 1.0 (inclusive).
            A lower value means more filtering.  A value of 1.0 equals no
            filtering. Defaults is 0.5.

    Returns
    -------
    hpf : array_like
          Filtered data.

    Based on http://en.wikipedia.org/wiki/High-pass_filter

    """
    mean = data.mean()
    data = data - mean
    hpf = data.copy()
    for k in range(1, len(data)):
        hpf[k] = alpha * hpf[k-1] + alpha * (data[k] - data[k-1])
    return hpf + mean


def tukey53H(series, k=1.5):
    """
    Flags suspicious spikes values in `series` using Tukey 53H criteria.

    References
    ----------
    .. [1] Goring, Derek G., and Vladimir I. Nikora. "Despiking acoustic
    Doppler velocimeter data." Journal of Hydraulic Engineering 128.1 (2002):
    117-126.  http://dx.doi.org/10.1061/(ASCE)0733-9429(2002)128:1(117)

    Examples
    --------
    >>> from pandas import pd.Series, date_range
    >>> series = [33.43, 33.45, 34.45, 90.0, 35.67, 34.9, 43.5, 34.6, 33.7]
    >>> series = pd.Series(series, index=date_range('1980-01-19',
    ...                    periods=len(series)))
    >>> series[tukey53H(series, k=1.5)]
    1980-01-22    90.0
    Freq: D, dtype: float64

    """
    series = np.asanyarray(series)

    series = _high_pass(series, 0.99)
    series = series - series.mean()

    N = len(series)
    stddev = series.std()

    u1 = np.zeros_like(series)
    for n in range(N-4):
        if series[n:n+5].any():
            u1[n+2] = np.median(series[n:n+5])

    u2 = np.zeros_like(series)
    for n in range(N-2):
        if u1[n:n+3].any():
            u2[n+1] = np.median(u1[n:n+3])

    u3 = np.zeros_like(series)
    u3[1:-1] = 0.25*(u2[:-2] + 2*u2[1:-1] + u2[2:])

    delta = np.abs(series-u3)

    return delta > k*stddev

if __name__ == '__main__':
    import doctest
    doctest.testmod()
