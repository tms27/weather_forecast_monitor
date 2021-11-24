from weather_center import  WeatherCenter
import pandas as pd
import os.path
from datetime import date
from datetime import timedelta
import calendar

class AccuracyMonitor:
    def __init__(self, website, filename):
        self.filename = filename
        self.df_website = website.data()
        self.today = date.today()
        self.weather_center = WeatherCenter()
        self.days_until_updated = 1  # number of days until the data of a day is published
        self.column_names = ['Day', 'Month', 'Year', 'max Temp.', 'Amount of Rain']
        self.month_str_to_int = {month: index for index, month in enumerate(calendar.month_name) if month}

        # retrieve new data from weather center and save to dataframe and file
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

    def avg_max_T_deviation(self, forecasted_day, sequence=None, absolute_value=True):
        self.deviations = []
        if 'not given' in set(self.df_website[f"max Temp. {forecasted_day}"]):
            raise ValueError(f"Quantity is not forecasted by the website on day {forecasted_day}")
        for self.index, self.row_website in self.df_website.iterrows():
            self.date_of_forecast = date(self.row_website['Year'], self.month_str_to_int[self.row_website['Month']], self.row_website['Day'])
            self.date_forecasted = self.date_of_forecast + timedelta(days=forecasted_day)
            self.row = self.df[(self.df.Day == self.date_forecasted.day)
                               & (self.df.Month == self.date_forecasted.month)
                               & (self.df.Year == self.date_forecasted.year)]
            if self.row.empty:
                continue
            self.deviation = self.row_website.at[f"max Temp. {forecasted_day}"] - self.row.at[self.row.index[0], 'max Temp.']
            if absolute_value:
                self.deviation = abs(self.deviation)
            self.deviations.append(self.deviation)
        self.deviation_avg = sum(self.deviations) / len(self.deviations)
        print(self.deviations)
        print(self.deviation_avg)

    def avg_max_T_deviation_rel(self):
        pass


