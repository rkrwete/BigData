import os, re
import pandas as pd
import subprocess

from datetime import datetime, timedelta

# def get_indexes_SYM_ASY():
#     directory = "data/SYM_ASY"
#     files = os.listdir(directory)

#     data_frames = []

#     for file in files:
#         df = pd.read_csv(directory + '/' + file, delim_whitespace=True, header=None)
#         data_frames.append(df)
#         df = pd.concat(data_frames, ignore_index=True)
#         df.columns = ['year', 'day_of_year', 'hour', 'minute', 'SYM_D', 'SYM_H', 'ASY_D', 'ASY_H']
#         df = df[df['minute'] == 0]
#         df['datetime'] = pd.to_datetime(df['year'] * 1000 + df['day_of_year'], format='%Y%j') + pd.to_timedelta(df['hour'], unit='h')
#         df.set_index('datetime', inplace=True)
#         df = df[['SYM_D', 'SYM_H', 'ASY_D', 'ASY_H']]
#         df.to_csv('SYM_ASY.csv')

# get_indexes_SYM_ASY()

class SYM_ASY:
    """ Класс для получения и предобработки данных индексов SYM_ASY"""

    start_data = '1981.01.01'

    def get_end_date(self):
        """ Получение конечной даты """
        now = datetime.now()
        first_day_this_month = datetime(now.year, now.month, 1)
        last_day_previous_month = first_day_this_month - timedelta(days=1)
        return last_day_previous_month.strftime("%Y.%m.%d")
    
    def generate_date_ranges(self, start_data, end_date):
        """ Генерация массива дат с интервалом в год """
        start_date_obj = datetime.strptime(start_data, "%Y.%m.%d")
        end_date_obj = datetime.strptime(end_date, "%Y.%m.%d")
        ranges = []

        current_year = start_date_obj.year
        while current_year <= end_date_obj.year:
            current_start = datetime(current_year, 1, 1)
            current_end = datetime(current_year, 12, 31)

            if current_end > end_date_obj:
                current_end = end_date_obj

            if current_start >= start_date_obj and current_start <= end_date_obj:
                ranges.append((
                    current_start.strftime("%Y%m%d"),
                    current_end.strftime("%Y%m%d")
                ))

            current_year += 1

        return ranges

    def download(self):
        start_data = self.start_data
        end_date = self.get_end_date()

        date_ranges = self.generate_date_ranges(start_data, end_date)

        for start, end in date_ranges:
            self.request(start, end)
            print(f"Start: {start}, End: {end}")

    def request(self, start_date, end_date):
        url = "https://omniweb.gsfc.nasa.gov/cgi/nx1.cgi"
        data = {
            "activity": "retrieve",
            "res": "min",
            "spacecraft": "omni_min",
            "start_date": start_date,
            "end_date": end_date,
            "vars": ["40", "41", "42", "43"],
        }
        
        # Подготовка параметров для передачи в subprocess
        curl_command = [
            "curl", "-d",
            "&".join(f"{k}={v}" if not isinstance(v, list) else "&".join(f"{k}={item}" for item in v) for k, v in data.items()),
            url
        ]

        directory = "data/SYM_ASY"
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, f"SYM-ASY--{start_date}-{end_date}.txt")
        with open(file_path, "wb") as f:
            subprocess.run(curl_command, stdout=f)

    def create_result_file(self):
        directory = "data/SYM_ASY"
        files = os.listdir(directory)
        pattern = re.compile(r"SYM-ASY--\d{8}-\d{8}\.txt")
        filtered_files = [f for f in files if pattern.match(f)]

        if not filtered_files:
            print("Нет подходящих файлов")
            return

        data_frames = []
        for file in filtered_files:
            file_path = os.path.join(directory, file)
            print(f"Открытие файла: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                relevant_lines = lines[11:-17]
                data = [line.strip().split() for line in relevant_lines]
                df = pd.DataFrame(data, columns=['year', 'day_of_year', 'hour', 'minute', 'SYM_D', 'SYM_H', 'ASY_D', 'ASY_H'])

                df['year'] = df['year'].astype(int)
                df['day_of_year'] = df['day_of_year'].astype(int)
                df['hour'] = df['hour'].astype(int)
                df['minute'] = df['minute'].astype(int)
                df['SYM_D'] = df['SYM_D'].astype(float)
                df['SYM_H'] = df['SYM_H'].astype(float)
                df['ASY_D'] = df['ASY_D'].astype(float)
                df['ASY_H'] = df['ASY_H'].astype(float)

                df['datetime'] = df.apply(
                    lambda row: (datetime(int(row['year']), 1, 1) + timedelta(days=int(row['day_of_year']) - 1, hours=int(row['hour']), minutes=int(row['minute']))),
                    axis=1
                )
                df.drop(['year', 'day_of_year', 'hour', 'minute'], axis=1, inplace=True)
                df.set_index('datetime', inplace=True)
                hourly_avg = df.resample('h').mean()
                hourly_avg = hourly_avg.round(0).astype(int)

                data_frames.append(hourly_avg)

        final_df = pd.concat(data_frames)

        output_directory = "data"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            
        output_path = os.path.join(output_directory, "SYM_ASY.csv")
        final_df.to_csv(output_path)
        print(f"Данные успешно записаны в файл {output_path}")

sym_asy = SYM_ASY()
# sym_asy.download()
# sym_asy.create_result_file()