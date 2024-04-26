# Функции сравнение двух датафреймов (часового, трехчасового, суточного)

import pandas as pd
import numpy as np

def compare_data(dataframe1, dataframe2):
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
