# Индексы Dst, Ae, Al, Bx, By, Bz, Vsw, Dsw, Tsw, Kp, Ap, F107, Lalfa
import spaceweather as sw
import pandas as pd
import datetime

# Создаем список дат за два года от апреля 2022 до апреля 2024
startDate = datetime.datetime(2022, 4, 1)
endDate = datetime.datetime(2024, 4, 1)

# Функция для выгрузки данных за период
def getData(startDate, endDate):
    # Сформировать массив годов
    startYear = int(startDate.year)
    endYear = int(endDate.year)
    years = []
    while startYear <= endYear:
        years.append(startYear)
        startYear += 1 

    dataAllYear = pd.DataFrame()
    for year in years:
        dataYear = sw.omnie_hourly(int(year), cache=True)
        dataAllYear = pd.concat([dataAllYear, dataYear], ignore_index=True)

    # Выбор необходимых индексов
    dataAllYear = dataAllYear[['year', 'doy', 'hour', 'Dst', 'AE', 'AL', 'B_x', 'B_y_GSE', 'B_z_GSE',  'v_plasma', 'n_p', 'T_p', 'Kp', 'Ap', 'f107_adj', 'Lya']]

    # Преобразование столбцов year, doy, hour во временные метки
    dataAllYear['date'] = pd.to_datetime(dataAllYear['year'] * 1000 + dataAllYear['doy'], format='%Y%j', errors='coerce')
    dataAllYear['month'] = dataAllYear['date'].dt.month
    dataAllYear['day'] = dataAllYear['date'].dt.day
    dataAllYear['timestamp'] = pd.to_datetime(dataAllYear[['year', 'day', 'month', 'hour']], format='%Y %j %m %H', utc=True).dt.strftime('%Y-%m-%d %H:%M:%S')

    # Удалить ненужные столбцы
    dataAllYear = dataAllYear.drop(columns=['date'])
    dataAllYear = dataAllYear.drop(columns=['doy'])
    dataAllYear = dataAllYear.drop(columns=['year'])
    dataAllYear = dataAllYear.drop(columns=['day'])
    dataAllYear = dataAllYear.drop(columns=['month'])
    dataAllYear = dataAllYear.drop(columns=['hour'])

    # Переупорядочить столбцы, чтобы 'timestamp' был первым
    columnOrder = ['timestamp'] + [column for column in dataAllYear if column != 'timestamp']
    dataAllYear = dataAllYear[columnOrder]
    
    # Cрез по нужному периоду
    dataAllYear['timestamp'] = pd.to_datetime(dataAllYear['timestamp'])
    dataAllYear = dataAllYear[(dataAllYear['timestamp'] >= startDate) & (dataAllYear['timestamp'] <= endDate)]
    
    # Обновить индексы
    dataAllYear.reset_index(drop=True, inplace=True)

    return dataAllYear





print(getData(startDate, endDate))

# dataAllYear.to_pickle('Data.pkl')

# import pickle
# data = pickle.load(open('Data.pkl', 'rb'))
# print(data)