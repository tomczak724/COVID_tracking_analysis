
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

DATA_PATH = os.path.join('..', 'data')
if not os.path.exists(DATA_PATH):
    os.mkdir(DATA_PATH)

URL_API = 'https://api.covidtracking.com'
URL_GITHUB = 'https://github.com/tomczak724'

###  downloading meta data for states
fname_info_states = '../data/info_states.json'
if not os.path.exists(fname_info_states):
    cmd = 'curl -O --silent https://api.covidtracking.com/v1/states/info.json'
    subprocess.call(cmd, shell=True)
    os.rename('info.json', fname_info_states)

DF_POPULATION = pandas.read_csv('../data/populations.csv')
DF_AREA = pandas.read_csv('../data/areas.csv')
DF_ELECTION_RESULTS_2016 = pandas.read_csv('../data/election_results_2016.csv')

INFO_STATES = json.load(open(fname_info_states, 'r'))
DF_INFO_STATES = pandas.DataFrame(INFO_STATES)


###  adding population data from Wikipedia (https://en.wikipedia.org/wiki/List_of_states_and_territories_of_the_United_States_by_population)
DF_INFO_STATES = pandas.merge(DF_INFO_STATES, DF_POPULATION, on='name')

###  adding land area data from Wikipedia (https://en.wikipedia.org/wiki/List_of_U.S._states_and_territories_by_area)
DF_INFO_STATES = pandas.merge(DF_INFO_STATES, DF_AREA, on='name')



def get_rate_per_100k(data, name):
    '''
    Description
    -----------
        Returns the per-capita (100k population) rate of the 
        input data for the specified state / territory / USA

    Parameters
    ----------
        data : array-like
            Data to normalize (e.g. deaths)

        name : str
            Either "US" or name of state
    '''

    if name.upper() in ('US' 'USA'):
        pop = DF_POPULATION['population_20190701'].sum()

    elif name.upper() in tuple(DF_INFO_STATES['state']):
        pop = DF_INFO_STATES.query('state=="%s"'%name.upper()).iloc[0]['population_20190701']

    elif name.capitalize() in tuple(DF_INFO_STATES['name']):
        pop = DF_INFO_STATES.query('name=="%s"'%name.capitalize()).iloc[0]['population_20190701']

    else:
        raise IOError('Unknown name provided: %s' % name)

    death_per_100k = data * 10.**5 / pop

    return death_per_100k


def get_election2016_dem_ratio():
    '''
    Description
    -----------
        Returns the fraction of the popular vote of the 2016 USA presidential election that
        went to the Democratic party. Intended to approximate Dem. / Rep. "lean"

    Source
    ------
        https://en.wikipedia.org/wiki/2016_United_States_presidential_election
    '''

    DF_ELECTION_RESULTS_2016['dem_ratio'] = DF_ELECTION_RESULTS_2016['votes_dem'] / (DF_ELECTION_RESULTS_2016['votes_dem'] + DF_ELECTION_RESULTS_2016['votes_rep'])

    ###  normalizing results to range (0-1)
    DF_ELECTION_RESULTS_2016['dem_ratio'] -= 0.5
    ii_lo = DF_ELECTION_RESULTS_2016['dem_ratio'] < 0
    ii_hi = DF_ELECTION_RESULTS_2016['dem_ratio'] >= 0
    DF_ELECTION_RESULTS_2016.loc[ii_lo, 'dem_ratio'] /= -DF_ELECTION_RESULTS_2016['dem_ratio'].min()
    DF_ELECTION_RESULTS_2016.loc[ii_hi, 'dem_ratio'] /= DF_ELECTION_RESULTS_2016['dem_ratio'].max()
    DF_ELECTION_RESULTS_2016['dem_ratio'] /= 2
    DF_ELECTION_RESULTS_2016['dem_ratio'] += 0.5

    return DF_ELECTION_RESULTS_2016[['state', 'dem_ratio']]


def benford_probabilities(n=10):
    '''
    Returns the Benford probabilities for each leading digit of the given base
    '''
    return numpy.log(1 + 1 / numpy.arange(1, n)) / numpy.log(n)
    

def load_df_us(remove_negative_cases_deaths=True):
    '''
    Description
    -----------
        Loads all time series data for the USA
    '''

    ###  grabbing file names
    fnames = glob.glob(os.path.join(DATA_PATH, 'us', '*json'))

    ###  loading and parsing data
    data = [json.load(open(f, 'r')) for f in fnames]
    df_data = pandas.DataFrame(data).dropna(subset=['date'])

    df_data['date'] = pandas.DatetimeIndex(df_data['date'].apply(lambda x: '%s-%s-%s' % (str(x)[0:4], str(x)[4:6], str(x)[6:8])))
    #df_data['dateChecked'] = pandas.DatetimeIndex(df_data['dateChecked'])
    #df_data['lastModified'] = pandas.DatetimeIndex(df_data['lastModified'])

    df_data = df_data.sort_values(by=['date']).reset_index(drop=True)

    if remove_negative_cases_deaths == True:
        for col in ['positive', 'negative', 'death', 'positiveIncrease', 'negativeIncrease', 'deathIncrease']:
            ii_neg = df_data[col] < 0
            df_data.loc[ii_neg, col] = numpy.nan

    ###  adding column for death per 100k
    df_data['death_per_100k'] = get_rate_per_100k(df_data['death'], 'US')

    return df_data


def load_df_state(state, remove_negative_cases_deaths=True):
    '''
    Description
    -----------
        Loads all time series data for the given state

    Parameters
    ----------
        state : str
            Name of state to load, choose from:

            AK, AL, AR, AS, AZ, CA, CO, CT, DC, DE, FL, GA, GU, HI, IA, ID, IL, IN, KS, 
            KY, LA, MA, MD, ME, MI, MN, MO, MP, MS, MT, NC, ND, NE, NH, NJ, NM, NV, NY, 
            OH, OK, OR, PA, PR, RI, SC, SD, TN, TX, UT, VA, VI, VT, WA, WI, WV, WY
    '''

    ###  checking if valid state name provided
    if os.path.join(DATA_PATH, 'states', state.upper()) not in glob.glob(os.path.join(DATA_PATH, 'states%s*'%os.sep)):
        raise IOError('invalid state name provided')

    ###  grabbing file names
    fnames = glob.glob(os.path.join(DATA_PATH, 'states', state.upper(), '*json'))

    ###  loading and parsing data
    data = [json.load(open(f, 'r')) for f in fnames]
    df_data = pandas.DataFrame(data).dropna(subset=['date'])

    df_data['date'] = pandas.DatetimeIndex(df_data['date'].apply(lambda x: '%s-%s-%s' % (str(x)[0:4], str(x)[4:6], str(x)[6:8])))
    #df_data['dateModified'] = pandas.DatetimeIndex(df_data['dateModified'])
    #df_data['lastUpdateEt'] = pandas.DatetimeIndex(df_data['lastUpdateEt'])
    #df_data['dateChecked'] = pandas.DatetimeIndex(df_data['dateChecked'])

    df_data = df_data.sort_values(by=['date']).reset_index(drop=True)

    if remove_negative_cases_deaths == True:
        for col in ['positive', 'negative', 'death', 'positiveIncrease', 'negativeIncrease', 'deathIncrease']:
            ii_neg = df_data[col] < 0
            df_data.loc[ii_neg, col] = numpy.nan

    ###  adding column for death per 100k
    df_data['death_per_100k'] = get_rate_per_100k(df_data['death'], state)

    return df_data


def load_df_all_states(remove_negative_cases_deaths=True, verbose=True):
    '''
    Description
    -----------
        Loads all time series data for all states into one dataframe
    '''

    list_df_states = []
    for idx, state in DF_INFO_STATES.iterrows():
        if verbose == True:
            sys.stdout.write('\rLOADING DATA FOR %s (%i%%)' % (state['state'], 100.*(idx+1)/len(INFO_STATES)))

        list_df_states.append(load_df_state(state['state'], remove_negative_cases_deaths=remove_negative_cases_deaths))

    if verbose == True:
        print('')

    df_all_states = pandas.concat(list_df_states).reset_index(drop=True)
    return df_all_states





###  adding USA presidentaial 2016 popular vote results
DF_INFO_STATES = pandas.merge(DF_INFO_STATES, get_election2016_dem_ratio(), on='state')


###  adding deaths per 100k population
add_death_per_100k = input('\nCalculate deaths per 100k for all states? [y/N] ')
if add_death_per_100k.lower() in ('y', 'yes'):
    for idx, row in DF_INFO_STATES.iterrows():
        sys.stdout.write('\rCalculating for %s (%i%%)' % (row['state'], (idx+1.)*100/len(DF_INFO_STATES)))
        df = load_df_state(row['state'])
        DF_INFO_STATES.loc[idx, 'death_per_100k'] = df.iloc[-1]['death_per_100k']
    print('')

