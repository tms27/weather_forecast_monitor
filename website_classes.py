from bs4 import BeautifulSoup
import requests
import os.path
import re
import pandas as pd
from datetime import datetime

class Website:
    def __init__(self, url, temperature_excess_chars, rain_chance_excess_chars, forecasted_days, data_filename):
        self.url = url
        self.temperature_excess_chars = temperature_excess_chars
        self.rain_chance_excess_chars = rain_chance_excess_chars
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





    def retrieve_temperatures(self):  # saves list of maximum temperature of today and coming days in temperatures_float
        self.website = requests.get(self.url)
        self.soup = BeautifulSoup(self.website.content, 'html.parser')
        self.temperatures_str = self.retrieve_temperatures_str(self.soup)
        for self.temperature_str in self.temperatures_str:
            self.temperatures_float.append(float(self.temperature_str[:-1 * self.temperature_excess_chars]))


        self.rain_chances_str = self.retrieve_rain_chances_str(self.soup)
        for self.rain_chance_str in self.rain_chances_str:
            self.rain_chances_float.append(float(self.rain_chance_str[:-1 * self.rain_chance_excess_chars]))
        print(self.rain_chances_float)

    def retrieve_temperatures_str(self, soup):
        pass  # is defined individually for every website due to differences in the structures of the websites

    def retrieve_rain_chances_str(self, soup):
        pass

    def update_csv_file(self):
        # retrieve date
        self.today = datetime.today()
        self.day = self.today.day
        self.month = self.today.strftime("%B")
        self.year = self.today.year

        # retrieve data from website
        self.retrieve_temperatures()

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
            self.rainChance_temp = self.rainChance_nonzero.get_text()
            self.rainChance_str = self.rainChance_temp[5:-3]
            try:
                self.temp = float(self.rainChance_str[:-1])
            except ValueError:
                self.rainChance_str= '5%'
            self.rainChances_str[self.index] = self.rainChance_str
        return self.rainChances_str




class Wetter_com (Website):

    def retrieve_temperatures_str(self, soup):
        self.temp = soup.find_all(attrs={'class': 'temp-max'})
        return [self.temperature.get_text() for self.temperature in self.temp]

    def retrieve_rain_chances_str(self, soup):
        #self.weather_grid = soup.find(attrs={'class': 'weather-grid'})
        self.dds = soup.find_all('dd')
        '''
        self.rain_chances = []
        self.rain_amount = []
        self.sun_hours = []
        self.reaL_feel = []
        for self.value in self.dds:
            self.value_str = self.value.get_text()
            if '%' in self.value_str:
                self.percent_index = self.value_str.find('%')
                self.first_digit_index =
                self.rain_chances.append(self.value_str)
                if "l" in self.value_str:
                    self.rain_amount.append(self.value_str)
            elif 'h' in self.value_str:
                self.sun_hours.append(self.value_str)
            elif 'gefühlt' in self.value_str:
                self.reaL_feel.append(self.value_str)
            else:
                print("Unexpected string in weather_com retrieve_rain_chances_str")
        
        '''
        #self.dds = map(str,self.dds)
        #print(self.dds)
        self.dds_str_list = map(str, self.dds)
        self.dds_str = ' '.join(self.dds_str_list)
        #print(re.findall('\d\d %|\d %',self.dds_str))
        return re.findall('\d\d %|\d %',self.dds_str)
        #self.temp = self.weather_grid.find('dd')
        #print(self.temp)



class Proplanta_de(Website):

    def retrieve_temperatures(self):  # method of superclass needs to be overwritten because forecast is spread across mutliple urls
        self.url_memory = self.url
        for self.url in self.url_memory:
            Website.retrieve_temperatures(self)
        self.url = self.url_memory

    def retrieve_temperatures_str(self, soup):
        self.rows = soup.find('tr', id='TMAX')
        self.temp = self.rows.find_all(attrs={'class': 'SCHRIFT_FORMULAR_WERTE_MITTE'})
        return [self.temperature.get_text() for self.temperature in self.temp]