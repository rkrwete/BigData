# Файл с функиями получения и подготовки данных

import spaceweather as sw
import pandas as pd
import numpy as np

# Функция для выгрузки данных за период
def get_data(start_date, end_date):
    # Сформировать массив годов
    start_year = int(start_date.year)
    end_year = int(end_date.year)
    years = []
    while start_year <= end_year:
        years.append(start_year)
        start_year += 1 

    data_all_years = pd.DataFrame()
    for year in years:
        data_year = sw.omnie_hourly(int(year), cache=True)
        data_all_years = pd.concat([data_all_years, data_year], ignore_index=True)

    # Выбор необходимых индексов
    data_all_years = data_all_years[[
        'year', 'doy', 'hour', 'Dst', 'AE', 'AL', 'B_x', 'B_y_GSM', 'B_z_GSM', 
        'v_plasma', 'n_p', 'T_p', 'Kp', 'Ap', 'f107_adj', 'Lya'
    ]]

    # Преобразование столбцов year, doy, hour во временные метки
    timestamp = data_all_years['year']  * 1000 + data_all_years['doy']
    data_all_years['date'] = pd.to_datetime(timestamp, format='%Y%j', errors='coerce')
    
    data_all_years['month'] = data_all_years['date'].dt.month
    data_all_years['day'] = data_all_years['date'].dt.day
    data_time = data_all_years[['year', 'day', 'month', 'hour']]
    data_time = pd.to_datetime(data_time, format='%Y %j %m %H', utc=True)
    data_all_years['data-time'] = data_time.dt.strftime('%Y-%m-%d %H:%M:%S')

    # Удалить ненужные столбцы
    data_all_years = data_all_years.drop(columns=['date'])
    data_all_years = data_all_years.drop(columns=['doy'])
    data_all_years = data_all_years.drop(columns=['year'])
    data_all_years = data_all_years.drop(columns=['day'])
    data_all_years = data_all_years.drop(columns=['month'])
    data_all_years = data_all_years.drop(columns=['hour'])

    # Переименовать столбцы
    data_all_years.rename(columns={'Dst': 'dst'}, inplace=True)
    data_all_years.rename(columns={'AE': 'ae'}, inplace=True)
    data_all_years.rename(columns={'AL': 'al'}, inplace=True)
    data_all_years.rename(columns={'Kp': 'kp'}, inplace=True)
    data_all_years.rename(columns={'Ap': 'ap'}, inplace=True)
    data_all_years.rename(columns={'B_x': 'bx'}, inplace=True)
    data_all_years.rename(columns={'B_y_GSM': 'by'}, inplace=True)
    data_all_years.rename(columns={'B_z_GSM': 'bz'}, inplace=True)
    data_all_years.rename(columns={'v_plasma': 'vsw'}, inplace=True)
    data_all_years.rename(columns={'n_p': 'dsw'}, inplace=True)
    data_all_years.rename(columns={'T_p': 'tsw'}, inplace=True)
    data_all_years.rename(columns={'f107_adj': 'f107'}, inplace=True)
    data_all_years.rename(columns={'Lya': 'lalfa'}, inplace=True)

    # Переупорядочить столбцы, чтобы 'data-time' был первым
    columnOrder = ['data-time'] + [column for column in data_all_years if column != 'data-time']
    data_all_years = data_all_years[columnOrder]

    # Cрез по нужному периоду
    data_all_years['data-time'] = pd.to_datetime(data_all_years['data-time'])
    data_all_years = data_all_years[
        (data_all_years['data-time'] >= start_date) & 
        (data_all_years['data-time'] <= end_date)
    ]
    
    # Обновить индексы
    data_all_years.reset_index(drop=True, inplace=True)
    data_all_years.set_index('data-time', inplace=True, drop=True)
    data_all_years.index.name = None

    data_all_years['kp'] = data_all_years['kp'] * 10
    data_all_years['lalfa'] = data_all_years['lalfa'] * 612

    return data_all_years

# Функция преобразования данных в три dataframe
def transform_data(dataframe):
    result = []

    dataframe0 = dataframe[[
        'dst', 'ae', 'al', 'bx', 'by', 'bz', 'vsw', 'dsw', 'tsw'
    ]]
    result.append(dataframe0)
    del dataframe0

    dataframe1 = dataframe[['kp', 'ap']]
    dataframe1 = dataframe1.resample('3h').mean()
    dataframe1 = dataframe1.map(lambda x: round(x))
    result.append(dataframe1)
    

    dataframe2 = dataframe[['lalfa', 'f107']]
    dataframe2 = dataframe2.resample('24h').mean()
    dataframe2['f107av'] = dataframe2['f107'].rolling(window=81, min_periods=1, center=True).mean()
    dataframe2['f107av'] = dataframe2['f107av'].round(1)
    dataframe2['skp'] = dataframe1['kp'].resample('D').sum()
    dataframe2['apm'] = dataframe1['ap'].resample('D').mean()
    dataframe2['apm'] = dataframe2['apm'].astype (int)
    dataframe2['skp'] = dataframe2['skp'].astype (int)

    result.append(dataframe2)

    del dataframe1
    del dataframe2

    return result
