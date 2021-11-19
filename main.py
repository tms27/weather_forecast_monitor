from bs4 import BeautifulSoup
import requests
from datetime import datetime
def weekdaylist_from_current_weekday():
    weekdays = ['Monday', 'Tuesday','Wednesday', 'Thursday', 'Friday','Saturday', 'Sunday']
    weekday = datetime.today().weekday()
    weekdays_from_today = weekdays[weekday:]
    weekdays_from_today.extend(weekdays[:weekday])
    return weekdays_from_today
class Website:
    def __init__(self, url):
        self.url = url

class Wetter_de (Website):
    def create_tempdict(self):
        self.wetter_de = requests.get(self.url)
        self.soup_wetter_de = BeautifulSoup(self.wetter_de.content, 'html.parser')
        self.temperatures_str = self.soup_wetter_de.find_all(attrs={'class': 'meteogram-slot__temperature'})
        self.temperatures_float = []
        for self.temperature in self.temperatures_str:
            self.temperature_str = self.temperature.get_text()
            self.temperatures_float.append(float(self.temperature_str[:-1]))
            print(self.temperatures_float)
            self.temperatures_wetter_de = dict(zip(weekdaylist_from_current_weekday(), self.temperatures_float[:6]))

wetter_de = Wetter_de(url ='https://www.wetter.de/deutschland/wetter-muenchen-18225562.html?q=m%C3%BCnchen')
wetter_de.create_tempdict()
print(wetter_de.temperatures_wetter_de)
