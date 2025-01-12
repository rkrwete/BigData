import datetime
import os
from get_data import GetData
from graphics_processing.graph_processing import GraphProcessing
from graphics_processing.get_charts import GetDataFromGrarts

# data = pd.read_pickle('data/final_inds.pkl')

# start_date = datetime.datetime(1981, 1, 1)
# end_date = datetime.datetime(1991, 5, 31)

# initial_data = GetData().get_data(start_date, end_date)
# initial_data = GetData().transform_data(initial_data)

# Сравнение данных 22 года с данными 24
# compare_1hour_data = GetData().compare_data(data[0], initial_data[0])
# compare_3hour_data = GetData().compare_data(data[1], initial_data[1])
# compare_24hour_data = GetData().compare_data(data[2], initial_data[2])
# print(compare_1hour_data, compare_3hour_data, compare_24hour_data)

# print(initial_data[0], initial_data[1], initial_data[2])


# current_path = os.path.dirname(os.path.abspath(__file__))

# current_path = os.path.join(current_path, 'graphics_processing', 'charts', 'rtae_20200131.png')
# print(current_path)
# data_from_image = GraphProcessing(current_path)
# print(data_from_image.start())
# test = GetDataFromGrarts().downloads()
# test = GetDataFromGrarts().start('1H')
# print(test)
