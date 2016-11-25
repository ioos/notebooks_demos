from __future__ import absolute_import, division, print_function

import numpy as np
import matplotlib.pyplot as plt


__all__ = ['TaylorDiagram']


class TaylorDiagram(object):
    """
    Taylor diagram: plot model standard deviation and correlation
    to reference (data) sample in a single-quadrant polar plot, with
    r=stddev and theta=arccos(correlation).

    Taylor diagram (Taylor, 2001) test implementation.

    http://www-pcmdi.llnl.gov/about/staff/Taylor/CV/Taylor_diagram_primer.htm
    https://gist.github.com/ycopin/3342888

    """

    def __init__(self, refstd, fig=None, rect=111, label='_'):
        """
        Set up Taylor diagram axes, i.e. single quadrant polar
        plot, using mpl_toolkits.axisartist.floating_axes. refstd is
        the reference standard deviation to be compared to.

        """

        from matplotlib.projections import PolarAxes
        from mpl_toolkits.axisartist import floating_axes
        from mpl_toolkits.axisartist import grid_finder

        self.refstd = refstd  # Reference standard deviation.

        tr = PolarAxes.PolarTransform()

        # Correlation labels.
        rlocs = np.concatenate((np.arange(10)/10., [0.95, 0.99]))
        tlocs = np.arccos(rlocs)  # Conversion to polar angles.
        gl1 = grid_finder.FixedLocator(tlocs)  # Positions.
        dict_formatter = dict(list(zip(tlocs, map(str, rlocs))))
        tf1 = grid_finder.DictFormatter(dict_formatter)

        # Standard deviation axis extent.
        self.smin = 0
        self.smax = 1.5*self.refstd

        extremes = (0,
                    np.pi/2,  # 1st quadrant.
                    self.smin,
                    self.smax)
        ghelper = floating_axes.GridHelperCurveLinear(tr,
                                                      extremes=extremes,
                                                      grid_locator1=gl1,
                                                      tick_formatter1=tf1)

        if fig is None:
            fig = plt.figure()

        ax = floating_axes.FloatingSubplot(fig, rect, grid_helper=ghelper)
        fig.add_subplot(ax)

        # Adjust axes.
        ax.axis["top"].set_axis_direction("bottom")  # "Angle axis".
        ax.axis["top"].toggle(ticklabels=True, label=True)
        ax.axis["top"].major_ticklabels.set_axis_direction("top")
        ax.axis["top"].label.set_axis_direction("top")
        ax.axis["top"].label.set_text("Correlation")

        ax.axis["left"].set_axis_direction("bottom")  # "X axis".
        ax.axis["left"].label.set_text("Standard deviation")

        ax.axis["right"].set_axis_direction("top")  # "Y axis".
        ax.axis["right"].toggle(ticklabels=True)
        ax.axis["right"].major_ticklabels.set_axis_direction("left")

        ax.axis["bottom"].set_visible(False)  # Useless.

        # Contours along standard deviations.
        ax.grid(False)

        self._ax = ax  # Graphical axes.
        self.ax = ax.get_aux_axes(tr)  # Polar coordinates.

        # Add reference point and stddev contour.
        l, = self.ax.plot([0], self.refstd, 'ko',
                          ls='', ms=10, label=label)
        t = np.linspace(0, np.pi/2)
        r = np.zeros_like(t) + self.refstd
        self.ax.plot(t, r, 'k--', label='_')

        # Collect sample points for latter use (e.g. legend).
        self.samplePoints = [l]

    def add_sample(self, stddev, corrcoef, *args, **kwargs):
        """
        Add sample (stddev, corrcoeff) to the Taylor diagram. args
        and kwargs are directly propagated to the Figure.plot
        command.

        """
        l, = self.ax.plot(np.arccos(corrcoef), stddev,
                          *args, **kwargs)  # (theta, radius).
        self.samplePoints.append(l)
        return l

    def add_contours(self, levels=5, **kwargs):
        """
        Add constant centered RMS difference contours.

        """
        rs, ts = np.meshgrid(np.linspace(self.smin, self.smax),
                             np.linspace(0, np.pi/2))
        # Compute centered RMS difference.
        rms = np.sqrt(self.refstd**2 + rs**2 - 2*self.refstd*rs*np.cos(ts))
        contours = self.ax.contour(ts, rs, rms, levels, **kwargs)
        return contours


if __name__ == '__main__':
    # Reference dataset.
    x = np.linspace(0, 4*np.pi, 100)
    data = np.sin(x)
    refstd = data.std(ddof=1)  # Reference standard deviation.

    # Models.
    m1 = data + 0.2*np.random.randn(len(x))  # Model 1.
    m2 = 0.8*data + 0.1*np.random.randn(len(x))  # Model 2.
    m3 = np.sin(x-np.pi/10)  # Model 3.

    # Compute stddev and correlation coefficient of models.
    samples = np.array([[m.std(ddof=1), np.corrcoef(data, m)[0, 1]]
                        for m in (m1, m2, m3)])

    fig = plt.figure(figsize=(10, 4))

    ax1 = fig.add_subplot(1, 2, 1, xlabel='X', ylabel='Y')
    # Taylor diagram.
    dia = TaylorDiagram(refstd, fig=fig, rect=122, label="Reference")

    colors = plt.matplotlib.cm.jet(np.linspace(0, 1, len(samples)))

    ax1.plot(x, data, 'ko', label='Data')
    for k, m in enumerate([m1, m2, m3]):
        ax1.plot(x, m, c=colors[k], label='Model %d' % (k+1))
    ax1.legend(numpoints=1, prop=dict(size='small'), loc='best')

    # Add samples to Taylor diagram.
    for k, (stddev, corrcoef) in enumerate(samples):
        dia.add_sample(stddev, corrcoef, marker='s', ls='', c=colors[k],
                       label="Model %d" % (k+1))

    # Add RMS contours, and label them.
    contours = dia.add_contours(colors='0.5')
    plt.clabel(contours, inline=1, fontsize=10)

    # Add a figure legend.
    fig.legend(dia.samplePoints,
               [p.get_label() for p in dia.samplePoints],
               numpoints=1, prop=dict(size='small'), loc='upper right')
    plt.show()
