from bs4 import BeautifulSoup
import requests
from datetime import datetime
def weekdaylist_from_current_weekday(length_of_list = 7):
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    current_weekday = datetime.today().weekday()
    weekdays_ordered = weekdays[current_weekday:]  # start list of weekdays from current weekday
    weekdays_ordered.extend(weekdays[:current_weekday])
    weekdays_from_today = []
    j = 0
    for i in range(length_of_list):
        weekdays_from_today.append(weekdays_ordered[j])
        if j == 6:
            j = 0
        else:
            j += 1


    return weekdays_from_today
class Website:
    def __init__(self, url):
        self.url = url
    def retrieve_temperatures(self):
        #is defined individually for every website due to differences in the
        pass

class Wetter_de (Website):
    def retrieve_temperatures(self):  # saves list of maximum temperature of today and coming days in temperatures_float
        self.website = requests.get(self.url)
        self.soup = BeautifulSoup(self.website.content, 'html.parser')
        self.temperatures_str = self.soup.find_all(attrs={'class': 'meteogram-slot__temperature'})
        self.temperatures_float = []
        for self.temperature in self.temperatures_str:
            self.temperature_str = self.temperature.get_text()
            self.temperatures_float.append(float(self.temperature_str[:-1]))

class Wetter_com (Website):
    def retrieve_temperatures(self):  # saves list of maximum temperature of today and coming days in temperatures_float
        self.website = requests.get(self.url)
        self.soup = BeautifulSoup(self.website.content, 'html.parser')
        self.temperatures_str = self.soup.find_all(attrs={'class': 'temp-max'})
        self.temperatures_float = []
        for self.temperature in self.temperatures_str:
            self.temperature_str = self.temperature.get_text()
            self.temperatures_float.append(float(self.temperature_str[:-1]))

class Proplanta(Website):
    def retrieve_temperatures(self):  # saves list of maximum temperature of today and coming days in temperatures_float
        self.temperatures_float = []
        for self.url_i in self.url:
            self.website = requests.get(self.url_i)
            self.soup = BeautifulSoup(self.website.content, 'html.parser')
            self.rows = self.soup.find('tr', id='TMAX')
            self.temperatures_str = self.rows.find_all(attrs={'class': 'SCHRIFT_FORMULAR_WERTE_MITTE'})
            for self.temperature in self.temperatures_str:
                self.temperature_str = self.temperature.get_text()
                self.temperatures_float.append(float(self.temperature_str[:-3]))




wetter_de = Wetter_de(url='https://www.wetter.de/deutschland/wetter-muenchen-18225562.html?q=m%C3%BCnchen')
wetter_de.retrieve_temperatures()
print(wetter_de.temperatures_float)
wetter_com = Wetter_com(url='https://www.wetter.com/wetter_aktuell/wettervorhersage/16_tagesvorhersage/deutschland/muenchen/DE0006515.html')
wetter_com.retrieve_temperatures()
print(wetter_com.temperatures_float)
proplanta= Proplanta(url= ['https://www.proplanta.de/Agrar-Wetter/M%FCnchen-AgrarWetter.html',
                               'https://www.proplanta.de/Agrar-Wetter/profi-wetter.php?SITEID=60&PLZ=M%FCnchen&STADT=M%FCnchen&WETTERaufrufen=stadt&Wtp=&SUCHE=Agrarwetter&wT=4',
                               'https://www.proplanta.de/Agrar-Wetter/profi-wetter.php?SITEID=60&PLZ=M%FCnchen&STADT=M%FCnchen&WETTERaufrufen=stadt&Wtp=&SUCHE=Agrarwetter&wT=7',
                               'https://www.proplanta.de/Agrar-Wetter/profi-wetter.php?SITEID=60&PLZ=M%FCnchen&STADT=M%FCnchen&WETTERaufrufen=stadt&Wtp=&SUCHE=Agrarwetter&wT=11'])
proplanta.retrieve_temperatures()
print(proplanta.temperatures_float)



