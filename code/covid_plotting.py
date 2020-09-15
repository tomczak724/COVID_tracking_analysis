
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


def plot_benford_breakdown(df_input, column='positiveIncrease'):
    '''
    Description
    -----------
        Generates a plot showing the fraction of entries of `column`
        in `df_input` that begin with each leading digit of (1-9)

    Parameters
    ----------
        df_input : pandas.DataFrame
            Dataframe containing the data (duh)

        column : str
            Name of column to analyze
    '''

    if column not in df_input.columns:
        raise IOError('Column "%s" not found in input dataframe' % column)

    ###  ignoring values of 0 and NaN
    df_input = df_input.query('%s!=0' % column).dropna(subset=[column])

    ###  extracting leading digits
    leading_digits = df_input[column].apply(lambda val: int(str(val)[0])).values

    ###  counting frequencies
    counts = numpy.array([(leading_digits==i).sum() for i in range(1,10)])


    fig, ax = pyplot.subplots()
    ax.set_xlabel('Leading Digit', size=14)
    ax.set_ylabel('Fraction of total', size=14)

    ax.grid(color='gray', lw=1, ls=':')

    ax.errorbar(range(1,10), counts/counts.sum(), yerr=counts**0.5/counts.sum(), ls='-', marker='o', ms=9, color='g', mfc='none', mec='g', mew=2, ecolor='g', elinewidth=2, capsize=0)

    ax.plot(range(1,10), utils.benford_probabilities(), ls='-', lw=3, dashes=[4,1], color='r', label="Benford's Law")

    return fig








