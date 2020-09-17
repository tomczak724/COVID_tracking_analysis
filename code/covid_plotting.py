
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


def main():

    ###  plot summary of data for USA
    choice_run_us_summary = input('\nPlot data summary for USA? [y/N] ')
    if choice_run_us_summary.lower() in ['yes', 'y']:
        return plot_usa_summary()


    ###  plot summary of data for state
    choice_run_ma_summary = input('Plot data summary for Massachusetts? [y/N] ')
    if choice_run_ma_summary.lower() in ['yes', 'y']:
        return plot_state_summary('ma')


    ###  plot example 1 of Benford breakdown
    choice_run_benford_breakdown_1 = input('Plot example 1 Benford analysis? [y/N] ')
    if choice_run_benford_breakdown_1.lower() in ['yes', 'y']:
        df_us = utils.load_df_us()
        return plot_benford_breakdown(df_us, column='positive', data_label='cumulative # cases', legend_title='Data for USA')


    ###  plot example 2 of Benford breakdown
    choice_run_benford_breakdown_2 = input('Plot example 2 Benford analysis? [y/N] ')
    if choice_run_benford_breakdown_2.lower() in ['yes', 'y']:
        df_ma = utils.load_df_state('ma')
        return plot_benford_breakdown(df_ma, column='deathIncrease', data_label='# deaths per day', legend_title='Data for Massachusetts')






def plot_usa_summary(days_smooth=7):
    '''
    Generates a summary plot of positive cases and deaths for the USA
    '''

    df = utils.load_df_us()

    fig, (ax1, ax2) = pyplot.subplots(ncols=2, figsize=(10.5, 5), sharex=True)
    fig.subplots_adjust(left=0.08, top=0.91, right=0.98, bottom=0.15, wspace=0.2)

    ax1.set_title('# New Cases per day in USA', size=16)
    ax2.set_title('# Deaths per day in USA', size=16)

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


def plot_benford_breakdown(df_input, column='positiveIncrease', data_label='# new cases per day', legend_title=''):
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

    ###  initializing figure
    fig, ax = pyplot.subplots()
    ax.set_xlabel('Leading Digit', size=14)
    ax.set_ylabel('Fraction of total', size=14)

    ax.grid(color='gray', lw=1, ls=':')

    ax.errorbar(range(1,10), counts/counts.sum(), yerr=counts**0.5/counts.sum(), ls='-', marker='o', ms=9, color='g', mfc='none', mec='g', mew=2, ecolor='g', elinewidth=2, capsize=0, label=data_label)

    ax.plot(range(1,10), utils.benford_probabilities(), ls='-', lw=3, dashes=[4,1], color='r', label="Benford's Law")

    legend = ax.legend(loc='upper right', title=legend_title, fontsize=11)
    pyplot.setp(legend.get_title(), fontsize=12)

    return fig



if __name__ == '__main__':
    main()

