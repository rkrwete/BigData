from PIL import Image
from datetime import datetime, timedelta
import os
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt

class GraphProcessing:
    """ Класс GraphProcessing используется для получения данных индекса AU из графиков

    Attributes
    ----------
    path_img: str
        полный путь до файла изображения
    """

    def __init__(self, path_img):
        self.path_img = path_img

    def start(self):
        """ Начинает работу класса """
        image_array = self.img_to_array()
        result = self.image_array_to_data(image_array)

        return result

    def img_to_array(self):
        """ Преобразует файл изображения в массив 
            Удаляет не нужные строки и столбцы из массива  
        """
        image = Image.open(self.path_img)
        print('Обработано'+ self.path_img)
        image_array = np.array(image)
        image_array[:, :, 0] = 0 
        image_array[:, :, 1] = 0
        image_array = image_array[27:198, 82:649]
        return image_array

    def __get_count_rows(self):
        """ Считает количество строк в массиве изображения """
        return len(self.img_to_array())
    
    def __get_count_columns(self):
        """ Считает количество столбцов в массиве изображения """
        return len(self.img_to_array()[0])
    
    def __get_array_values(self):
        """ Присвоение каждой строке значения индекса """
        max_value = 1000
        min_value = -2000
        count_rows = self.__get_count_rows()

        values = np.linspace(max_value, min_value, count_rows)
        values[57] = 0

        return values
    
    def __get_array_times(self):
        """ Присвоение каждому столбцу значения даты """
        times = []  
        start_time = datetime.strptime("00:00:00", "%H:%M:%S")
        second_in_day = 60 * 60 * 24
        count_columns = self.__get_count_columns()

        interval = second_in_day / (count_columns - 1)
        interval = timedelta(seconds=interval)

        for i in range(count_columns):
            time_str = start_time.strftime("%H:%M:%S")
            times.append(time_str)
            start_time += interval

        return times
    
    def image_array_to_data(self, image_array):
        """ Получение данных из массива изображения

        Parameters 
        ----------
        image_array
            массив изображения
        """
        times = self.__get_array_times()
        values = self.__get_array_values()
        result = pd.DataFrame(index=times, columns=['AU'])

        start_row = 57

        for key, column in enumerate(image_array[start_row]):
            column_index = key

            if column[2] <= 140:
                for row in range(56, -1, -1):
                    if image_array[row][column_index][2] >= 140:
                        result.at[times[key], "AU"] = values[row - 1]
                        break

        return result
    

current_path = os.path.dirname(os.path.abspath(__file__))
current_path = os.path.join(current_path, 'charts', 'rtae_20200109.png')
# p = GraphProcessing(current_path).start()
# print(p)
