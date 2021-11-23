from bs4 import BeautifulSoup
import requests
from datetime import datetime
from datetime import timedelta
from datetime import date


class WeatherCenter:
    def retrieve_max_T_and_rain_amount(self, days_ago=None, day=None, month=None, year=None):
        if days_ago is None:
            self.url = f'https://www.wetterzentrale.de/weatherdata_de.php?station=3379' \
                       f'&jaar={year}&maand={month}&dag={day}'
        else:
            self.date = datetime.today() - timedelta(days=days_ago)
            self.url = f'https://www.wetterzentrale.de/weatherdata_de.php?station=3379' \
                       f'&jaar={self.date.year}&maand={self.date.month}&dag={self.date.day}'
        self.website = requests.get(self.url)
        self.soup = BeautifulSoup(self.website.content, 'html.parser')
        self.table = self.soup.find(attrs={'class': 'col-md-6'})
        self.bs = self.table.find_all('b')
        self.max_T = float(self.bs[0].get_text())
        self.rain_amount = float(self.bs[-3].get_text())



        return self.max_T, self.rain_amount
