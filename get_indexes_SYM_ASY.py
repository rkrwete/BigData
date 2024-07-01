import os
import pandas as pd

def get_indexes_SYM_ASY():
    directory = "SYM_ASY"
    files = os.listdir(directory)

    data_frames = []

    for file in files:
        df = pd.read_csv(directory + '/' + file, delim_whitespace=True, header=None)
        data_frames.append(df)
        df = pd.concat(data_frames, ignore_index=True)
        df.columns = ['year', 'day_of_year', 'hour', 'minute', 'SYM_D', 'SYM_H', 'ASY_D', 'ASY_H']
        df = df[df['minute'] == 0]
        df['datetime'] = pd.to_datetime(df['year'] * 1000 + df['day_of_year'], format='%Y%j') + pd.to_timedelta(df['hour'], unit='h')
        df.set_index('datetime', inplace=True)
        df = df[['SYM_D', 'SYM_H', 'ASY_D', 'ASY_H']]
        df.to_csv('SYM_ASY.csv')

get_indexes_SYM_ASY()