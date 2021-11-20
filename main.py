from datetime import datetime
from website_classes import *

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

def DataFrame_column_descriptions(num_of_days):
    column_names = ['Day', 'Month', 'Year']
    temperature_columns = ['max Temp. ' + str(i) for i in range(num_of_days)]
    column_names.extend(temperature_columns)
    return column_names

wetter_de = Wetter_de(url='https://www.wetter.de/deutschland/wetter-muenchen-18225562.html?q=m%C3%BCnchen',
                      temperature_excess_chars=1)
wetter_de.retrieve_temperatures()
print(wetter_de.temperatures_float)

wetter_com = Wetter_com(url='https://www.wetter.com/wetter_aktuell/wettervorhersage/16_tagesvorhersage/deutschland/muenchen/DE0006515.html',
                        temperature_excess_chars=1)
wetter_com.retrieve_temperatures()
print(wetter_com.temperatures_float)

proplanta= Proplanta(url=['https://www.proplanta.de/Agrar-Wetter/M%FCnchen-AgrarWetter.html',
                               'https://www.proplanta.de/Agrar-Wetter/profi-wetter.php?SITEID=60&PLZ=M%FCnchen&STADT=M%FCnchen&WETTERaufrufen=stadt&Wtp=&SUCHE=Agrarwetter&wT=4',
                               'https://www.proplanta.de/Agrar-Wetter/profi-wetter.php?SITEID=60&PLZ=M%FCnchen&STADT=M%FCnchen&WETTERaufrufen=stadt&Wtp=&SUCHE=Agrarwetter&wT=7',
                               'https://www.proplanta.de/Agrar-Wetter/profi-wetter.php?SITEID=60&PLZ=M%FCnchen&STADT=M%FCnchen&WETTERaufrufen=stadt&Wtp=&SUCHE=Agrarwetter&wT=11'],
                     temperature_excess_chars=3)
proplanta.retrieve_temperatures()
print(proplanta.temperatures_float)



print(DataFrame_column_descriptions(10))



