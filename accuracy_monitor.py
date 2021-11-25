from weather_center import WeatherCenter
import pandas as pd
import os.path
from datetime import date
from datetime import timedelta
import calendar
import warnings
warnings.filterwarnings("error")

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
                    if None in self.new_data:
                        break
                    self.new_row = [self.date.day, self.date.month, self.date.year, *self.new_data]
                    self.new_row_df = pd.DataFrame(data=[self.new_row], columns=self.column_names)
                    self.df = self.df.append(self.new_row_df, ignore_index=True)
                self.df.to_csv(self.filename, index=False)

    def avg_max_T_deviation(self, forecasted_day=3, sequence=False, absolute_value=True, relative=False):
        return self.avg_deviation("max Temp.", forecasted_day, sequence, absolute_value, relative)

    def avg_rain_amount_deviation(self, forecasted_day=3, sequence=False, absolute_value=True, relative=False):
        return self.avg_deviation("Amount of Rain", forecasted_day, sequence, absolute_value, relative)

    def avg_deviation(self, quantity_name, forecasted_day=3, sequence=False, absolute_value=True, relative=False):
        self.deviations = []
        if 'not given' in set(self.df_website[f"{quantity_name} {forecasted_day}"]):
            raise ValueError(f"Quantity is not forecasted by the website on day {forecasted_day}")

        # calculate deviations from actual value
        for self.index, self.row_website in self.df_website.iterrows():
            self.date_of_forecast = date(self.row_website['Year'], self.month_str_to_int[self.row_website['Month']], self.row_website['Day'])
            self.date_forecasted = self.date_of_forecast + timedelta(days=forecasted_day)
            self.row = self.df[(self.df.Day == self.date_forecasted.day)
                               & (self.df.Month == self.date_forecasted.month)
                               & (self.df.Year == self.date_forecasted.year)]
            if self.row.empty:  # continue if actual value is not yet available
                continue
            self.deviation = self.row_website.at[f"{quantity_name} {forecasted_day}"] - self.row.at[self.row.index[0], quantity_name]
            if relative:
                try:
                    self.deviation /= self.row.at[self.row.index[0], quantity_name]
                except RuntimeWarning:
                    if quantity_name == "max. Temp":
                        self.deviation /= self.row.at[self.row.index[0], quantity_name] + 0.1
                    else:
                        self.deviation = 3.0
            if absolute_value:
                self.deviation = abs(self.deviation)
            self.deviations.append(self.deviation)

        # calculate average deviation
        if sequence is False:
            return sum(self.deviations) / len(self.deviations)
        else:
            self.avg_seq = []
            for self.i in range(1, len(self.deviations)+1):
                self.avg_seq.append(sum(self.deviations[:self.i]) / self.i)
            if (sequence in range(1, len(self.deviations)+1)) & sequence is not True:
                return self.avg_seq[-1 * sequence:]
            else:
                return self.avg_seq
