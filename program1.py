# Индексы Dst, Ae, Al, Bx, By, Bz, Vsw, Dsw, Tsw, Kp, Ap, F107, Lalfa
import spaceweather as sw
import pandas as pd
import datetime

# Создаем список дат за два года от апреля 2022 до апреля 2024
start_date = datetime.datetime(2022, 4, 1)
end_date = datetime.datetime(2024, 4, 1)

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
    data_all_years.rename(columns={'B_x': 'Bx'}, inplace=True)
    data_all_years.rename(columns={'B_y_GSM': 'By'}, inplace=True)
    data_all_years.rename(columns={'B_z_GSM': 'Bz'}, inplace=True)
    data_all_years.rename(columns={'v_plasma': 'Vsw'}, inplace=True)
    data_all_years.rename(columns={'n_p': 'Dsw'}, inplace=True)
    data_all_years.rename(columns={'T_p': 'Tsw'}, inplace=True)
    data_all_years.rename(columns={'f107_adj': 'F107'}, inplace=True)
    data_all_years.rename(columns={'Lya': 'Lalfa'}, inplace=True)

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

    return data_all_years


print(get_data(start_date, end_date))

# data_all_years.to_pickle('Data.pkl')

# import pickle
# data = pickle.load(open('Data.pkl', 'rb'))
# print(data)