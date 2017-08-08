# -*- coding: utf-8 -*-

import cStringIO
from contextlib import closing

import matplotlib
matplotlib.use('Agg') # force matplotlib not to use x-window as backend
import matplotlib.pyplot as plt

from matplotlib.dates import MinuteLocator, DateFormatter, AutoDateFormatter, AutoDateLocator
from matplotlib.ticker import FormatStrFormatter

def draw_chart(x, y, size, format="png", dpi=80, color="#000080", xlim=None):
    from matplotlib.dates import DayLocator, HourLocator, AutoDateFormatter
    from matplotlib import ticker
    import pylab as pl
    f = plt.figure()
    ax = f.add_axes([0, 0, 1, 1])
    if xlim:
        ax.set_xlim(xlim[0], xlim[1])
    else:
        ax.set_xlim(x[0], x[-1])
    ax.plot(x, y)
    formatter = AutoDateFormatter(HourLocator())
    formatter.scaled[(1/24.)] = "%H:%M"
    ax.xaxis.grid(True, which="major")
    ax.yaxis.grid(True, which="major")
    ax.xaxis.set_major_locator(HourLocator())
    ax.xaxis.set_major_formatter(formatter)
    res = cStringIO.StringIO()
    w_inches = size[0] / dpi
    h_inches = size[1] / dpi
    if h_inches <= 0 or w_inches <= 0:
        raise Exception("chart size not allowed!")
    f.autofmt_xdate()
    f.set_size_inches(w_inches, h_inches)
    f.savefig(res, format=format, dpi=dpi, bbox_inches="tight")
    return res.getvalue()

def draw_list(x, y, size=(750, 200), dpi=80, xlim=None, ylim=None, autodt=False):

    fig = plt.figure(figsize=(size[0] / dpi, size[1] / dpi))

    ax = fig.add_subplot(1, 1, 1)

    if len(y) > 2:
        ax.plot(x, y[3], color='silver')
    ax.plot(x, y[1], color='gray')

    if len(y) > 2:
        ax.plot(x, y[2], color='green')
    ax.plot(x, y[0], color='blue')

    ax.grid(True, axis='y')

    # xlim
    if xlim is not None:
        ax.set_xlim(*xlim)

    # ylim
    try:
        y0 = [i for i in y[0] if i is not None]
        if not y0:
            raise ValueError

        ylim_max = max(y0)
        ylim_min = min(y0)

        y1 = [i for i in y[1] if i is not None]
        if y1:
            ylim_max = max(ylim_max, max(y1))
            ylim_min = min(ylim_min, min(y1))

        if len(y) > 2:
            y2 = [i for i in y[2] if i is not None]
            if y2:
                ylim_max = max(ylim_max, max(y2))
                ylim_min = min(ylim_min, min(y2))

            y3 = [i for i in y[3] if i is not None]
            if y3:
                ylim_max = max(ylim_max, max(y3))
                ylim_min = min(ylim_min, min(y3))

    except Exception, e:
        ylim_min, ylim_max = (0, 5)

    else:
        ylim_min, ylim_max = (int(round(ylim_min * 0.95)), int(round(ylim_max / 0.95)))

    if ylim is not None:
        if ylim[0] is not None:
            ylim_min = ylim[0]
        if ylim[1] is not None:
            ylim_max = ylim[1]

    ax.set_ylim(ylim_min if ylim_min > 0 else 0 , ylim_max if ylim_max > 5 else 5)

    if autodt:
        locator = AutoDateLocator()
        formatter = AutoDateFormatter(locator)
        formatter.scaled[(1.)] = '%Y-%m-%d'
        formatter.scaled[(1./24.)] = '%H:%M'
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
    else:
        ax.xaxis.set_major_locator(MinuteLocator(byminute=range(0, 60, 15)))
        ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))

    ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))

    for tick in ax.xaxis.get_major_ticks():
        tick.label1.set_size(9)
    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_size(9)

    with closing(cStringIO.StringIO()) as f:
        fig.savefig(f, bbox_inches='tight')
        plt.close()
        return f.getvalue()
