from weather_center import  WeatherCenter
import pandas as pd
import os.path
from datetime import date
from datetime import timedelta


class AccuracyMonitor:
    def __init__(self, website, filename):
        self.filename = filename
        self.df_website = website.data()
        self.today = date.today()
        self.weather_center = WeatherCenter()
        self.days_until_updated = 3  # number of days until the data of a day is published
        self.column_names = ['Day', 'Month', 'Year', 'max Temp', 'Amount of Rain']

        if os.path.isfile(self.filename) is False:
            self.new_data = list(self.weather_center.retrieve_max_T_and_rain_amount(days_ago=self.days_until_updated))
            self.date = self.today - timedelta(days=self.days_until_updated)
            self.df = pd.DataFrame(data=[[self.date.day, self.date.month, self.date.year, *self.new_data]],
                                   columns=self.column_names)
            self.df.to_csv(self.filename, index=False)
        else:
            self.df = pd.read_csv(self.filename)
            self.last_date = date(self.df['Year'].max(), self.df['Month'].max(), self.df['Day'].max())
            self.timedelta = self.today - self.last_date
            self.days_elapsed = self.timedelta.days
            if int(self.days_elapsed) > self.days_until_updated:
                for self.i in range(self.days_elapsed-1, self.days_until_updated-1, -1):
                    self.date = self.today - timedelta(days=self.i)
                    self.new_data = list(self.weather_center.retrieve_max_T_and_rain_amount(days_ago=self.i))
                    self.new_row = [self.date.day, self.date.month, self.date.year, *self.new_data]
                    self.new_row_df = pd.DataFrame(data=[self.new_row], columns=self.column_names)
                    self.df = self.df.append(self.new_row_df, ignore_index=True)
                self.df.to_csv(self.filename, index=False)

    def max_T_deviation(self):
        pass





