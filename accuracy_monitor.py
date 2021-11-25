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
            new_data = list(self.weather_center.retrieve_max_T_and_rain_amount(days_ago=self.days_until_updated))
            target_date = self.today - timedelta(days=self.days_until_updated)
            self.df = pd.DataFrame(data=[[target_date.day, target_date.month, target_date.year, *new_data]],
                                   columns=self.column_names)
            self.df.to_csv(self.filename, index=False)
        else:
            self.df = pd.read_csv(self.filename)
            last_date = date(self.df['Year'].max(), self.df['Month'].max(), self.df['Day'].max())
            time_difference = self.today - last_date
            days_elapsed = time_difference.days
            if int(days_elapsed) > self.days_until_updated:
                for i in range(days_elapsed-1, self.days_until_updated-1, -1):
                    target_date = self.today - timedelta(days=i)
                    new_data = list(self.weather_center.retrieve_max_T_and_rain_amount(days_ago=i))
                    if None in new_data:
                        break
                    new_row = [target_date.day, target_date.month, target_date.year, *new_data]
                    new_row_df = pd.DataFrame(data=[new_row], columns=self.column_names)
                    self.df = self.df.append(new_row_df, ignore_index=True)
                self.df.to_csv(self.filename, index=False)

    def avg_max_T_deviation(self, forecasted_day=3, sequence=False, absolute_value=True, relative=False):
        return self.avg_deviation("max Temp.", forecasted_day, sequence, absolute_value, relative)

    def avg_rain_amount_deviation(self, forecasted_day=3, sequence=False, absolute_value=True, relative=False):
        return self.avg_deviation("Amount of Rain", forecasted_day, sequence, absolute_value, relative)

    def avg_deviation(self, quantity_name, forecasted_day=3, sequence=False, absolute_value=True, relative=False):
        if 'not given' in set(self.df_website[f"{quantity_name} {forecasted_day}"]):
            raise ValueError(f"Quantity is not forecasted by the website on day {forecasted_day}")

        # calculate deviations from actual value
        deviations = []
        for index, row_website in self.df_website.iterrows():
            date_of_forecast = date(row_website['Year'], self.month_str_to_int[row_website['Month']], row_website['Day'])
            date_forecasted = date_of_forecast + timedelta(days=forecasted_day)
            row = self.df[(self.df.Day == date_forecasted.day)
                          & (self.df.Month == date_forecasted.month)
                          & (self.df.Year == date_forecasted.year)]
            if row.empty:  # continue if actual value is not yet available
                continue
            deviation = row_website.at[f"{quantity_name} {forecasted_day}"] - row.at[row.index[0], quantity_name]
            if relative:
                try:
                    deviation /= row.at[row.index[0], quantity_name]
                except RuntimeWarning:
                    if quantity_name == "max. Temp":
                        deviation /= row.at[row.index[0], quantity_name] + 0.1
                    else:
                        deviation = 3.0
            if absolute_value:
                deviation = abs(deviation)
            deviations.append(deviation)

        # calculate average deviation
        if sequence is False:
            return sum(deviations) / len(deviations)
        else:
            avg_seq = []
            for i in range(1, len(deviations)+1):
                avg_seq.append(sum(deviations[:i]) / i)
            if (sequence in range(1, len(deviations)+1)) & sequence is not True:
                return avg_seq[-1 * sequence:]
            else:
                return avg_seq
