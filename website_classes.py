from bs4 import BeautifulSoup
import requests
import os.path
import re
import pandas as pd
from datetime import datetime


class Website:
    def __init__(self, url, forecasted_days, data_filename):
        self.url = url
        self.temperatures_float = []
        self.rain_chances_float = []
        self.rain_amounts_float = []
        self.forecasted_days = forecasted_days
        self.data_filename = data_filename

        # create names of columns in .csv file
        self.column_names = ['Day', 'Month', 'Year']
        temperature_columns = [f"max Temp. {i}" for i in range(self.forecasted_days)]
        self.column_names.extend(temperature_columns)
        rain_chance_columns = [f"Chance of Rain {i}" for i in range(self.forecasted_days)]
        self.column_names.extend(rain_chance_columns)
        rain_amount_columns = [f"Amount of Rain {i}" for i in range(self.forecasted_days)]
        self.column_names.extend(rain_amount_columns)

    def retrieve_data(self):
        website = requests.get(self.url)
        soup = BeautifulSoup(website.content, 'html.parser')

        # retrieve maximum temperatures
        temperatures_str = self.retrieve_temperatures_str(soup)
        for temperature_str in temperatures_str:
            self.temperatures_float.append(float(re.findall('-\d\d|-\d|\d\d|\d', temperature_str)[0]))

        # retrieve likelihoods of rain
        rain_chances_str = self.retrieve_rain_chances_str(soup)
        for rain_chance_str in rain_chances_str:
            if 'not given' in rain_chance_str:
                self.rain_chances_float.append(rain_chance_str)
            else:
                self.rain_chances_float.append(float(re.findall('\d\d\d|\d\d|\d', rain_chance_str)[0]))

        # retrieve rain amount
        rain_amounts_str = self.retrieve_rain_amounts_str(soup)
        for rain_amount_str in rain_amounts_str:
            if 'not given' in rain_amount_str:
                self.rain_amounts_float.append(rain_amount_str)
            else:
                self.rain_amounts_float.append(float(re.findall('\d\d.\d|\d.\d|\d', rain_amount_str)[0]))

    def retrieve_temperatures_str(self, soup):
        pass  # is defined individually for every website due to differences in the structures of the websites

    def retrieve_rain_chances_str(self, soup):
        pass  # is defined individually for every website due to differences in the structures of the websites

    def retrieve_rain_amounts_str(self, soup):
        pass  # is defined individually for every website due to differences in the structures of the websites

    def update_csv_file(self):
        # retrieve date
        today = datetime.today()
        day = today.day
        month = today.strftime("%B")
        year = today.year

        # retrieve data from website
        self.retrieve_data()

        # write data to file
        new_data = [day, month, year,
                    *self.temperatures_float,
                    *self.rain_chances_float,
                    *self.rain_amounts_float]
        if os.path.isfile(self.data_filename) is False:
            df = pd.DataFrame(data=[new_data], columns=self.column_names)
            df.to_csv(self.data_filename, index=False)
        else:
            df_new_data = pd.DataFrame(data=[new_data], columns=self.column_names)
            df = pd.read_csv(self.data_filename)
            # check if data for today already exists. If Yes, update data in respective row
            if ((df['Day'] == day) & (df['Month'] == month) & (df['Year'] == year)).any():
                index = df[(df['Day'] == day) & (df['Month'] == month) & (df['Year'] == year)].index.tolist()
                df.iloc[index[0], :] = df_new_data.iloc[0, :]
            else:
                df = df.append(df_new_data, ignore_index=True)

            df.to_csv(self.data_filename, index=False)

    def data(self):
        return pd.read_csv(self.data_filename)

class Wetter_de (Website):

    def retrieve_temperatures_str(self, soup):
        temp = soup.find_all(attrs={'class': 'meteogram-slot__temperature'})
        return [temperature.get_text() for temperature in temp]

    def retrieve_rain_chances_str(self, soup):
        # find out on which days the chance of rain is not zero
        rain_amount_classes = soup.find_all(attrs={'class': 'meteogram-slot__rainAmount'})
        rain_amount_classes = map(str, rain_amount_classes)
        rain_true_false = []
        for rain_amount_class_str in rain_amount_classes:
            if "height:0%" in rain_amount_class_str:
                rain_true_false.append(False)
            else:
                rain_true_false.append(True)
        rainchance_nonzero_indices = [i for i, x in enumerate(rain_true_false) if x is True]

        # retrieve non-zero rain chances and insert them at the right place in the list
        rain_chances_str = ['0%'] * self.forecasted_days
        rain_chances_nonzero = soup.find_all(attrs={'class': 'meteogram-slot__rainChance'})
        for index, rain_chance_nonzero in zip(rainchance_nonzero_indices, rain_chances_nonzero):
            rain_chance_text = rain_chance_nonzero.get_text()
            rain_chance_str = re.findall('\d\d\d%|\d\d%|\d%', rain_chance_text)[0]
            rain_chances_str[index] = rain_chance_str
        return rain_chances_str

    def retrieve_rain_amounts_str(self, soup):
        return ["not given"] * self.forecasted_days

class Wetter_com (Website):

    def retrieve_temperatures_str(self, soup):
        temp = soup.find_all(attrs={'class': 'temp-max'})
        return [temperature.get_text() for temperature in temp]

    def retrieve_rain_chances_str(self, soup):
        dds = soup.find_all('dd')
        dds_str_list = map(str, dds)
        dds_str = ' '.join(dds_str_list)
        return re.findall('\d\d\d %|\d\d %|\d %', dds_str)

    def retrieve_rain_amounts_str(self, soup):
        dds = soup.find_all('dd')
        rain_amounts = []
        for content in dds:
            content_text = content.get_text()
            if '%' in content_text:
                rain_amount = re.findall('\d\d,\d l|\d,\d l', content_text)
                if rain_amount:
                    rain_amount = rain_amount[0].replace(',', '.')
                    rain_amounts.append(rain_amount)
                else:
                    rain_amounts.append('0.0 l')
        return rain_amounts

    def retrieve_real_feel(self):
        website = requests.get(self.url)
        soup = BeautifulSoup(website.content, 'html.parser')
        dds = soup.find_all('dd')
        dds_str_list = map(str, dds)
        dds_str = ' '.join(dds_str_list)
        real_feels_str = re.findall('-\d\d°|-\d°|\d\d°|\d°', dds_str)
        real_feels_str = real_feels_str[0::2]
        self.real_feels_float = [float(real_feel_str[:-1]) for real_feel_str in real_feels_str]
        return self.real_feels_float

class Proplanta_de(Website):

    def retrieve_data(self):  # method of superclass needs to be overwritten because forecast is spread across multiple urls
        url_memory = self.url
        for self.url in url_memory:
            Website.retrieve_data(self)
        self.url = url_memory

    def retrieve_temperatures_str(self, soup):
        rows = soup.find('tr', id='TMAX')
        temp = rows.find_all(attrs={'class': 'SCHRIFT_FORMULAR_WERTE_MITTE'})
        return [temperature.get_text() for temperature in temp]

    def retrieve_rain_chances_str(self, soup):
        # retrieve chance of rain during the  day
        rows = soup.find('tr', id='NW')  # returns None if nothing found
        if rows is None:
            num_of_days = len(self.retrieve_temperatures_str(soup))  # determine number of days forecasted by website
            return ['not given'] * num_of_days
        temp = rows.find_all(attrs={'class': 'SCHRIFT_FORMULAR_WERTE_MITTE'})
        rain_chances_day_str = [rain_chance.get_text() for rain_chance in temp]

        # retrieve chance of rain at night
        rows = soup.find('tr', id='NW_Nacht')
        temp = rows.find_all(attrs={'class': 'SCHRIFT_FORMULAR_WERTE_MITTE'})
        rain_chances_night_str = [rain_chance.get_text() for rain_chance in temp]

        # check if chance of rain at night or  day is higher and use the higher one for returned list
        rain_chances = []
        for rain_chance_day, rain_chance_night in zip(rain_chances_day_str, rain_chances_night_str):
            if float(rain_chance_day[:-2]) > float(rain_chance_night[:-2]):
                rain_chances.append(rain_chance_day)
            else:
                rain_chances.append(rain_chance_night)
        return rain_chances

    def retrieve_rain_amounts_str(self, soup):
        rows = soup.find('tr', id='NS_24H')  # returns None if nothing is found
        if rows is None:
            num_of_days = len(self.retrieve_temperatures_str(soup))  # determine number of forecasted days on website
            return ['not given'] * num_of_days
        temp = rows.find_all(attrs={'class': 'SCHRIFT_FORMULAR_WERTE_MITTE'})
        rain_amounts_str = [rain_amount.get_text().replace(',', '.') for rain_amount in temp]
        return rain_amounts_str


