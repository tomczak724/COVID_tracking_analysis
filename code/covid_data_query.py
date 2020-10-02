
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

DATES = pandas.date_range(start='2020-03-01', end=datetime.datetime.now(), freq='1D')


def main():

    ###  query data from USA up to present day
    choice_run_dl_us = input('\nDownload latest data for USA? [y/N] ')
    if choice_run_dl_us.lower() in ['yes', 'y']:
        for d in DATES:

            ###  checking it state directory exists, create one if not
            dir_us = os.path.join(utils.DATA_PATH, 'us')
            if not os.path.exists(dir_us):
                os.mkdir(dir_us)

            ###  checking if data file for this day exists, query if not
            fname = '%s.json' % d.strftime('%Y%m%d')
            if not os.path.exists('%s/%s' % (dir_us, fname)):
                sys.stdout.write('\rDownloading %s data for USA' % d.strftime('%Y-%m-%d'))
                cmd = 'curl -O --silent %s/v1/us/%s' % (utils.URL_API, fname)
                subprocess.call(cmd, shell=True)
                os.rename(fname, '%s/%s' % (dir_us, fname))
        print('')


    ###  query data from all states up to present day
    choice_run_dl_states = input('\nDownload latest data for states? [y/N] ')
    if choice_run_dl_states.lower() in ['yes', 'y']:

        ###  checking it state directory exists, create one if not
        dir_states = os.path.join(utils.DATA_PATH, 'states')
        if not os.path.exists(dir_states):
            os.mkdir(dir_states)

        for d in DATES:

            for s in utils.INFO_STATES:

                ###  checking it state directory exists, create one if not
                dir_state = os.path.join(utils.DATA_PATH, 'states', s['state'])
                if not os.path.exists(dir_state):
                    os.mkdir(dir_state)

                ###  checking if data file for this day exists, query if not
                fname = '%s.json' % d.strftime('%Y%m%d')
                if not os.path.exists('%s/%s' % (dir_state, fname)):
                    sys.stdout.write('\rDownloading %s data for state %s' % (d.strftime('%Y-%m-%d'), s['state']))
                    cmd = 'curl -O --silent %s/v1/states/%s/%s' % (utils.URL_API, s['state'].lower(), fname)
                    subprocess.call(cmd, shell=True)
                    os.rename(fname, '%s/%s' % (dir_state, fname))
        print('')



if __name__ == '__main__':
    main()

