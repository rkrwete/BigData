import os
import time
import requests
import pandas as pd 
from PIL import Image
from io import BytesIO
from datetime import datetime, timedelta
from .graph_processing import GraphProcessing


class GetDataFromGrarts:
    """ Класс используется для загрузки графиков и объединения их данных в один DataFrame """
    
    def __init__(self):
        self.start_day = datetime.strptime('20200101', '%Y%m%d')
        self.url = 'https://wdc.kugi.kyoto-u.ac.jp/ae_realtime/'
        self.folder_name = 'charts'
        self.current_directory = os.path.dirname(os.path.abspath(__file__))

    def start(self, round='none'):
        """ Метод запускает обработку загруженных изображений 
        
        Parameters 
        ----------
        round:
            параметр округления ('1H' - почасовое округление)
        """
        result = pd.DataFrame()

        current_date = datetime.now()
        date_iterator = self.start_day

        while date_iterator < current_date:
            formatted_month = date_iterator.strftime('%Y%m')
            formatted_day = date_iterator.strftime('%Y%m%d')
            file_path = os.path.join(self.current_directory, self.folder_name, f"rtae_{formatted_day}.png")

            if os.path.exists(file_path):
                data_from_img = GraphProcessing(file_path).start() 
                data_from_img = self.__preprocessing_dataframe(data_from_img, formatted_day)

                result = pd.concat([result, data_from_img], ignore_index=False) 

            date_iterator += timedelta(days=1)

        if (round == '1H'):
            result = result.resample('H').mean()
            print(result)

    def downloads(self):
        """ Метод запускает загрузку изображений """
        self.__check_folder()
        current_date = datetime.now()
        date_iterator = self.start_day

        while date_iterator < current_date:
            formatted_month = date_iterator.strftime('%Y%m')
            formatted_day = date_iterator.strftime('%Y%m%d')
            file_path = os.path.join(self.current_directory, self.folder_name, f"rtae_{formatted_day}.png")

            url = self.__get_url(formatted_month, formatted_day)
            self.__save_img(url, formatted_day)

            date_iterator += timedelta(days=1)

    def __preprocessing_dataframe(self, dataframe, day):
        """ Предобработка dataframe """
        data_from_img = dataframe.iloc[:-1]
        time_offsets = pd.to_timedelta(data_from_img.index)
        data_from_img.index = pd.to_datetime(day) + time_offsets

        return data_from_img

    def __check_folder(self):
        """ Проверка наличия папки """
        folder_path = os.path.join(self.current_directory, self.folder_name)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    def __get_url(self, month, day):
        """ Получение url 
        
        Parameters 
        ----------
        month:
            месяц
        day:
            день
        """
        return f"{self.url}{month}/rtae_{day}.png"
    
    def __save_img(self, url, day):
        """ Загрузка и сохранение файла 
        
        Parameters 
        ----------
        url:
            url 
        day:
            день
        """
        file_path = os.path.join(self.current_directory, self.folder_name, f"rtae_{day}.png")

        if not os.path.exists(file_path):
            attempts = 5
            for attempt in range(attempts):
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()  # поднять исключение для недействительных ответов

                    image = Image.open(BytesIO(response.content))
                    image.save(file_path)
                    print(f"Сохранено: {file_path}")
                    break  
                except requests.exceptions.RequestException as e:
                    print(f"Ошибка загрузки (попытка {attempt + 1}/{attempts}): {e}")
                    if attempt == attempts - 1: 
                        return  
                    time.sleep(5)  
                except Exception as e:
                    print(f"Ошибка при сохранении файла: {e}")
                    return  


# test = GetDataFromGrarts().start()
# test = GetDataFromGrarts().downloads()
