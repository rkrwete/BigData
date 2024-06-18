import pandas as pd
import datetime

import get_data as gd
import compare_data as cd
import analysis_data_gaps as adg
import linear_regression as lr

# data = pd.read_pickle('data/final_inds.pkl')

# start_date = datetime.datetime(1970, 1, 1)
# end_date = datetime.datetime(2022, 6, 30)

start_date = datetime.datetime(2009, 1, 1)
end_date = datetime.datetime(2020, 1, 1)

initial_data = gd.get_data(start_date, end_date)
initial_data = gd.transform_data(initial_data)

# Сравнение данных 22 года с данными 24
# compare_1hour_data = cd.compare_data(data[0], initial_data[0])
# compare_3hour_data = cd.compare_data(data[1], initial_data[1])
# compare_24hour_data = cd.compare_data(data[2], initial_data[2])
# print(compare_1hour_data, compare_3hour_data, compare_24hour_data)

# Анализ пропусков
# data = adg.analysis_data_gaps(initial_data, initial_data[2], 'f107', 999)
# print(data)

# Востановление Bz из dst
print(lr.linear_regression(initial_data[0].dst, initial_data[0].bz))
