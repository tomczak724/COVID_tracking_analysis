
import os
import sys
import glob
import json
import numpy
import pandas
import datetime
import subprocess
import matplotlib
from matplotlib import pyplot

import covid_utils as utils



def plot_usa_summary(days_smooth=7):
    '''
    Generates a summary plot of positive cases and deaths for the USA
    '''

    df = utils.load_df_us()

    fig, (ax1, ax2) = pyplot.subplots(ncols=2, figsize=(10.5, 5), sharex=True)
    fig.subplots_adjust(left=0.08, top=0.91, right=0.98, bottom=0.15, wspace=0.2)

    ax1.set_title('# New Cases per day', size=16)
    ax2.set_title('# Deaths per day', size=16)

    dt = pandas.Timedelta('%iD'%days_smooth)

    ax1.plot(df['date']-dt/2., df['positiveIncrease'].rolling(days_smooth).mean(), lw=3, color='#135cd1')
    ax2.plot(df['date']-dt/2., df['deathIncrease'].rolling(days_smooth).mean(), lw=3, color='#d40f0f')


    ax1.grid(lw=1, color='gray', ls=':')
    ax2.grid(lw=1, color='gray', ls=':')

    ###  converting xlabel from date to month name
    fig.canvas.draw()
    x_dates = pandas.DatetimeIndex([x.get_text() for x in ax1.xaxis.get_ticklabels()])
    x_months = [month[0:3] for month in x_dates.month_name()]
    ax1.xaxis.set_ticklabels(x_months)

    ###  formatting y-axis of new-cases plot
    yticks = [ytick.get_text() for ytick in ax1.yaxis.get_ticklabels()]
    yticks_new = [ytick.replace('0000','0k') for ytick in yticks]
    ax1.yaxis.set_ticklabels(yticks_new)

    ###  references
    ref = '$\it Data \; from \; the \; COVID \; Tracking \; Project$\n%s' % utils.URL_API
    t = ax2.text(0.97, -0.09, ref, transform=ax2.transAxes, ha='right', va='top', size=10, color='#666666')

    return fig


def plot_state_summary(state, days_smooth=7, format_yaxis=True):
    '''
    Generates a summary plot of positive cases and deaths for the given state
    '''

    df = utils.load_df_state(state)

    fig, (ax1, ax2) = pyplot.subplots(ncols=2, figsize=(10.5, 5), sharex=True)
    fig.subplots_adjust(left=0.08, top=0.91, right=0.98, bottom=0.15, wspace=0.2)

    ax1.set_title('# New Cases per day in %s' % state.upper(), size=16)
    ax2.set_title('# Deaths per day in %s' % state.upper(), size=16)

    dt = pandas.Timedelta('%iD'%days_smooth)

    ax1.plot(df['date']-dt/2., df['positiveIncrease'].rolling(days_smooth).mean(), lw=3, color='#135cd1')
    ax2.plot(df['date']-dt/2., df['deathIncrease'].rolling(days_smooth).mean(), lw=3, color='#d40f0f')


    ax1.grid(lw=1, color='gray', ls=':')
    ax2.grid(lw=1, color='gray', ls=':')

    ###  converting xlabel from date to month name
    fig.canvas.draw()
    x_dates = pandas.DatetimeIndex([x.get_text() for x in ax1.xaxis.get_ticklabels()])
    x_months = [month[0:3] for month in x_dates.month_name()]
    ax1.xaxis.set_ticklabels(x_months)

    ###  formatting y-axis of new-cases plot
    if format_yaxis == True:
        yticks = [ytick.get_text() for ytick in ax1.yaxis.get_ticklabels()]
        yticks_new = [ytick.replace('0000','0k') for ytick in yticks]
        ax1.yaxis.set_ticklabels(yticks_new)

    ###  references
    ref = '$\it Data \; from \; the \; COVID \; Tracking \; Project$\n%s' % utils.URL_API
    t = ax2.text(0.97, -0.09, ref, transform=ax2.transAxes, ha='right', va='top', size=10, color='#666666')

    return fig


