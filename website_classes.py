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
        self.forecasted_days = forecasted_days
        self.data_filename = data_filename

        # create names of columns in .csv file
        self.column_names = ['Day', 'Month', 'Year']
        self.temperature_columns = [f"max Temp. {i}" for i in range(self.forecasted_days)]
        self.column_names.extend(self.temperature_columns)
        self.rain_chance_columns = [f"Chance of Rain {i}" for i in range(self.forecasted_days)]
        self.column_names.extend(self.rain_chance_columns)

    def retrieve_data(self):  # saves list of maximum temperature of today and coming days in temperatures_float
        self.website = requests.get(self.url)
        self.soup = BeautifulSoup(self.website.content, 'html.parser')

        # retrieve maximum temperatures
        self.temperatures_str = self.retrieve_temperatures_str(self.soup)
        for self.temperature_str in self.temperatures_str:
            self.temperatures_float.append(float(re.findall('-\d\d|-\d|\d\d|\d', self.temperature_str)[0]))

        # retrieve likelihoods of rain
        self.rain_chances_str = self.retrieve_rain_chances_str(self.soup)
        for self.rain_chance_str in self.rain_chances_str:
            if 'not given' in self.rain_chance_str:
                self.rain_chances_float.append(self.rain_chance_str)
            else:
                self.rain_chances_float.append(float(re.findall('\d\d\d|\d\d|\d', self.rain_chance_str)[0]))

    def retrieve_temperatures_str(self, soup):
        pass  # is defined individually for every website due to differences in the structures of the websites

    def retrieve_rain_chances_str(self, soup):
        pass  # is defined individually for every website due to differences in the structures of the websites

    def update_csv_file(self):
        # retrieve date
        self.today = datetime.today()
        self.day = self.today.day
        self.month = self.today.strftime("%B")
        self.year = self.today.year

        # retrieve data from website
        self.retrieve_data()

        # write data to file
        self.new_data = [self.day, self.month, self.year, *self.temperatures_float, *self.rain_chances_float]
        if os.path.isfile(self.data_filename) is False:
            self.df = pd.DataFrame(data=[self.new_data], columns=self.column_names)
            self.df.to_csv(self.data_filename, index=False)
        else:
            self.df_new_data = pd.DataFrame(data=[self.new_data], columns=self.column_names)
            self.df = pd.read_csv(self.data_filename)
            # check if data for today already exists. If Yes, update data in respective row
            if ((self.df['Day'] == self.day) & (self.df['Month'] == self.month) & (self.df['Year'] == self.year)).any():
                self.index = self.df[(self.df['Day'] == self.day) & (self.df['Month'] == self.month) & (self.df['Year'] == self.year)].index.tolist()
                self.df.iloc[self.index[0], :] = self.df_new_data.iloc[0, :]
            else:
                self.df = self.df.append(self.df_new_data, ignore_index=True)

            self.df.to_csv(self.data_filename, index=False)


class Wetter_de (Website):

    def retrieve_temperatures_str(self, soup):
        #return soup.find_all(attrs={'class': 'meteogram-slot__temperature'})
        self.temp = soup.find_all(attrs={'class': 'meteogram-slot__temperature'})
        return [self.temperature.get_text() for self.temperature in self.temp]

    def retrieve_rain_chances_str(self, soup):
        # find out on which days the chance of rain is not zero
        self.rainAmountclasses = soup.find_all(attrs={'class': 'meteogram-slot__rainAmount'})
        self.rainAmountclasses= map(str, self.rainAmountclasses)
        self.rain_true_false= []
        for self.rainAmountclass_str in self.rainAmountclasses:
            if "height:0%" in self.rainAmountclass_str:
                self.rain_true_false.append(False)
            else:
                self.rain_true_false.append(True)
        self.rainChance_nonzero_indices = [i for i, x in enumerate(self.rain_true_false) if x is True]

        # retrieve non-zero rain chances and insert them at the right place in the list
        self.rainChances_str = ['0%'] * self.forecasted_days
        self.rainChances_nonzero = soup.find_all(attrs={'class': 'meteogram-slot__rainChance'})
        for self.index, self.rainChance_nonzero in zip(self.rainChance_nonzero_indices, self.rainChances_nonzero):
            self.rainChance_text = self.rainChance_nonzero.get_text()
            self.rainChance_str = re.findall('\d\d\d%|\d\d%|\d%', self.rainChance_text)[0]
            self.rainChances_str[self.index] = self.rainChance_str
        return self.rainChances_str


class Wetter_com (Website):

    def retrieve_temperatures_str(self, soup):
        self.temp = soup.find_all(attrs={'class': 'temp-max'})
        return [self.temperature.get_text() for self.temperature in self.temp]

    def retrieve_rain_chances_str(self, soup):
        self.dds = soup.find_all('dd')
        self.dds_str_list = map(str, self.dds)
        self.dds_str = ' '.join(self.dds_str_list)
        return re.findall('\d\d\d %|\d\d %|\d %', self.dds_str)

    def retrieve_rain_amount_str(self, soup):
        self.dds = soup.find_all('dd')
        self.rain_amounts = []
        for self.content in self.dds:
            self.content_text = self.content.get_text()
            if '%' in self.content_text:
                self.rain_amount = re.findall('\d\d,\d l|\d,\d l', self.content_text)
                if self.rain_amount:
                    self.rain_amount = self.rain_amount[0].replace(',', '.')
                    self.rain_amounts.append(self.rain_amount)
                else:
                    self.rain_amounts.append('0.0 l')
        return self.rain_amounts

    def retrieve_real_feel(self):
        self.website = requests.get(self.url)
        self.soup = BeautifulSoup(self.website.content, 'html.parser')
        self.dds = self.soup.find_all('dd')
        self.dds_str_list = map(str, self.dds)
        self.dds_str = ' '.join(self.dds_str_list)
        print(self.dds_str)

class Proplanta_de(Website):

    def retrieve_data(self):  # method of superclass needs to be overwritten because forecast is spread across multiple urls
        self.url_memory = self.url
        for self.url in self.url_memory:
            Website.retrieve_data(self)
        self.url = self.url_memory

    def retrieve_temperatures_str(self, soup):
        self.rows = soup.find('tr', id='TMAX')
        self.temp = self.rows.find_all(attrs={'class': 'SCHRIFT_FORMULAR_WERTE_MITTE'})
        return [self.temperature.get_text() for self.temperature in self.temp]

    def retrieve_rain_chances_str(self, soup):
        # retrieve chance of rain during the  day
        self.rows = soup.find('tr', id='NW') # returns None if nothing found
        if self.rows is None:
            self.num_of_days = len(self.retrieve_temperatures_str(soup)) # determine number of forecasted days on website
            return ['not given'] * self.num_of_days
        self.temp = self.rows.find_all(attrs={'class': 'SCHRIFT_FORMULAR_WERTE_MITTE'})
        self.rain_chances_day_str = [self.rain_chance.get_text() for self.rain_chance in self.temp]
        #retrieve chance of rain at night
        self.rows = soup.find('tr', id='NW_Nacht')
        self.temp = self.rows.find_all(attrs={'class': 'SCHRIFT_FORMULAR_WERTE_MITTE'})
        self.rain_chances_night_str = [self.rain_chance.get_text() for self.rain_chance in self.temp]
        # check if chance of rain at night or during the day is higher and use the higher one for returned list
        self.rain_chances = []
        for self.rain_chance_day, self.rain_chance_night in zip(self.rain_chances_day_str, self.rain_chances_night_str):
            if float(self.rain_chance_day[:-2]) > float(self.rain_chance_night[:-2]):
                self.rain_chances.append(self.rain_chance_day)
            else:
                self.rain_chances.append(self.rain_chance_night)
        return self.rain_chances


