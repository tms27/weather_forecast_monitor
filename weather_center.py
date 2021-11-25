from bs4 import BeautifulSoup
import requests
from datetime import datetime
from datetime import timedelta
from datetime import date


class WeatherCenter:
    @staticmethod
    def retrieve_max_T_and_rain_amount(day=None, month=None, year=None, days_ago=None):
        # method retrieves actual weather data from wetterzentrale.de of a certain date or a certain number of days ago
        if days_ago is None:
            url = f'https://www.wetterzentrale.de/weatherdata_de.php?station=3379' \
                  f'&jaar={year}&maand={month}&dag={day}'
            target_date = date(year, month, day)
        else:
            target_date = datetime.today() - timedelta(days=days_ago)
            url = f'https://www.wetterzentrale.de/weatherdata_de.php?station=3379' \
                  f'&jaar={target_date.year}&maand={target_date.month}&dag={target_date.day}'
        website = requests.get(url)
        soup = BeautifulSoup(website.content, 'html.parser')
        table = soup.find(attrs={'class': 'col-md-6'})
        bs = table.find_all('b')
        try:
            max_T = float(bs[0].get_text())
            rain_amount = float(bs[-3].get_text())
            return max_T, rain_amount
        except ValueError:
            print(f"Data from wetterzentrale.de for {target_date.day}/{target_date.month}/{target_date.year} not yet available")
            return None, None
