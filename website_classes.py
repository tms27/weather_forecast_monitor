from bs4 import BeautifulSoup
import requests

class Website:
    def __init__(self, url, temperature_excess_chars):
        self.url = url
        self.temperature_excess_chars = temperature_excess_chars
        self.temperatures_float = []

    def retrieve_temperatures(self):  # saves list of maximum temperature of today and coming days in temperatures_float
        self.website = requests.get(self.url)
        self.soup = BeautifulSoup(self.website.content, 'html.parser')
        self.temperatures_str = self.retrieve_temperatures_str(self.soup)
        for self.temperature in self.temperatures_str:
            self.temperature_str = self.temperature.get_text()
            self.temperatures_float.append(float(self.temperature_str[:-1 * self.temperature_excess_chars]))

    def retrieve_temperatures_str(self, soup):
        pass  # is defined individually for every website due to differences in the structures of the websites

class Wetter_de (Website):

    def retrieve_temperatures_str(self, soup):
        return soup.find_all(attrs={'class': 'meteogram-slot__temperature'})

class Wetter_com (Website):

    def retrieve_temperatures_str(self, soup):
        return soup.find_all(attrs={'class': 'temp-max'})

class Proplanta(Website):

    def retrieve_temperatures(self):  # method of superclass needs to be overwritten because forecast is spread across mutliple urls
        self.url_memory = self.url
        for self.url in self.url_memory:
            Website.retrieve_temperatures(self)
        self.url = self.url_memory

    def retrieve_temperatures_str(self, soup):
        self.rows = soup.find('tr', id='TMAX')
        return self.rows.find_all(attrs={'class': 'SCHRIFT_FORMULAR_WERTE_MITTE'})