import spaceweather as sw
import pandas as pd
import numpy as np

class GetData:
    """ Класс для получения и предобработки данных """

    def get_data(self, start_date, end_date):
        """ Получение данных и формирование их в dataframe
        
        Parameters 
        ----------
        start_date
            дата начала периода
        end_date
            дата окончания периода
        """
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

        # Присоединение индексов SYM, ASY
        df_SYM_ASY = pd.read_csv('data/SYM_ASY.csv')
        df_SYM_ASY.set_index('datetime', inplace=True)

        data_all_years.index = pd.to_datetime(data_all_years.index)
        df_SYM_ASY.index = pd.to_datetime(df_SYM_ASY.index)

        df_SYM_ASY = df_SYM_ASY[
            (df_SYM_ASY.index >= start_date) & 
            (df_SYM_ASY.index <= end_date)
        ]

        data_all_years = data_all_years[~data_all_years.index.duplicated(keep='first')]
        df_SYM_ASY = df_SYM_ASY[~df_SYM_ASY.index.duplicated(keep='first')]

        data_all_years = data_all_years.join(df_SYM_ASY, how='outer')

        return data_all_years
    
    def transform_data(self, dataframe):
        """ Преобразования данных в три dataframe
        
        Parameters 
        ----------
        dataframe
            исходный dataframe
        """
        result = []

        dataframe0 = dataframe[[
            'dst', 'ae', 'al', 'bx', 'by', 'bz', 'vsw', 'dsw', 'tsw', 'SYM_D', 'SYM_H', 'ASY_D', 'ASY_H'
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
    
    def compare_data(self, dataframe1, dataframe2):
        """ Функции сравнение двух датафреймов 
        Parameters 
        ----------
        dataframe1
            датафрейм 1
        dataframe2
            датафрейм 2
        """

        result = pd.DataFrame(columns=[
            'column', 'status', 'inx_first_diff', 'first_diff', 
            'inx_max_val', 'max_val', 'inx_min_val', 'min_val', 'std'
        ])

        difference = dataframe1 - dataframe2

        # Перебор столбцов
        for column in dataframe1.columns:
            status = ''
            # Проверка на наличие столбцов
            if column not in dataframe2.columns:
                status = 'NAN'
            else:
                status = 'OK'
                # Получение max, min, std
                max_inx = difference[column].idxmax()
                max_val = difference[column].max()
                min_inx = difference[column].idxmin()
                min_val = difference[column].min()
                std = np.std(difference[column])

                # Поиск первого расхождения
                inx_first_diff = None
                for index, val in difference[column].items():
                    if val != 0 and inx_first_diff is None:
                        inx_first_diff = index
                        first_diff = val
                        break
            
                if max_val == 0 and min_val == 0:
                    status = 'Нет изменений'

            # Запись результатов в новый датафрейм
            result.loc[len(result)] = {
                'column': column,
                'status': status,
                'inx_first_diff': inx_first_diff, 
                'first_diff': first_diff,
                'inx_max_val': max_inx,
                'max_val': max_val,
                'inx_min_val': min_inx,
                'min_val': min_val,
                'std': std
            }

        return result