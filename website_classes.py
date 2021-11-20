from bs4 import BeautifulSoup
import requests
import os.path
import pandas as pd
from datetime import datetime

class Website:
    def __init__(self, url, temperature_excess_chars, forecasted_days, data_filename):
        self.url = url
        self.temperature_excess_chars = temperature_excess_chars
        self.temperatures_float = []
        self.forecasted_days = forecasted_days
        self.data_filename = data_filename

        # create names of columns in .csv file
        self.column_names = ['Day', 'Month', 'Year']
        self.temperature_columns = ['max Temp. ' + str(i) for i in range(self.forecasted_days)]
        self.column_names.extend(self.temperature_columns)
        '''
        if os.path.isfile(self.data_filename) is False:
            self.column_names = ['Day', 'Month', 'Year']
            self.temperature_columns = ['max Temp. ' + str(i) for i in range(self.forecasted_days)]
            self.column_names.extend(self.temperature_columns)
            self.df = pd.DataFrame(columns=self.column_names)
            self.df.to_csv(self.data_filename)
            #with open(data_filename, 'w') as file:
        '''


    def retrieve_temperatures(self):  # saves list of maximum temperature of today and coming days in temperatures_float
        self.website = requests.get(self.url)
        self.soup = BeautifulSoup(self.website.content, 'html.parser')
        self.temperatures_str = self.retrieve_temperatures_str(self.soup)
        for self.temperature in self.temperatures_str:
            self.temperature_str = self.temperature.get_text()
            self.temperatures_float.append(float(self.temperature_str[:-1 * self.temperature_excess_chars]))

    def retrieve_temperatures_str(self, soup):
        pass  # is defined individually for every website due to differences in the structures of the websites

    def update_csv_file(self):
        # retrieve date
        self.today = datetime.today()
        self.day = self.today.day
        self.month = self.today.strftime("%B")
        self.year = self.today.year

        # retrieve data from website
        self.retrieve_temperatures()

        # write data to file
        self.new_data = [self.day, self.month, self.year, *self.temperatures_float]
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
        return soup.find_all(attrs={'class': 'meteogram-slot__temperature'})

class Wetter_com (Website):

    def retrieve_temperatures_str(self, soup):
        return soup.find_all(attrs={'class': 'temp-max'})

class Proplanta_de(Website):

    def retrieve_temperatures(self):  # method of superclass needs to be overwritten because forecast is spread across mutliple urls
        self.url_memory = self.url
        for self.url in self.url_memory:
            Website.retrieve_temperatures(self)
        self.url = self.url_memory

    def retrieve_temperatures_str(self, soup):
        self.rows = soup.find('tr', id='TMAX')
        return self.rows.find_all(attrs={'class': 'SCHRIFT_FORMULAR_WERTE_MITTE'})