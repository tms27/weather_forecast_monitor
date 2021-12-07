from datetime import datetime
from website_classes import *
from weather_center import WeatherCenter
from accuracy_monitor import AccuracyMonitor
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import math

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



# Create objects of websites from which the weather forecasts are retrieved
wetter_de = Wetter_de(url='https://www.wetter.de/deutschland/wetter-muenchen-18225562.html?q=m%C3%BCnchen',
                      forecasted_days=14,
                      data_filename='wetter_de.csv')


wetter_com = Wetter_com(url='https://www.wetter.com/wetter_aktuell/wettervorhersage/16_tagesvorhersage/deutschland/muenchen/DE0006515.html',
                        forecasted_days=16,
                        data_filename='wetter_com.csv')


proplanta_de = Proplanta_de(url=['https://www.proplanta.de/Agrar-Wetter/M%FCnchen-AgrarWetter.html',
                               'https://www.proplanta.de/Agrar-Wetter/profi-wetter.php?SITEID=60&PLZ=M%FCnchen&STADT=M%FCnchen&WETTERaufrufen=stadt&Wtp=&SUCHE=Agrarwetter&wT=4',
                               'https://www.proplanta.de/Agrar-Wetter/profi-wetter.php?SITEID=60&PLZ=M%FCnchen&STADT=M%FCnchen&WETTERaufrufen=stadt&Wtp=&SUCHE=Agrarwetter&wT=7',
                               'https://www.proplanta.de/Agrar-Wetter/profi-wetter.php?SITEID=60&PLZ=M%FCnchen&STADT=M%FCnchen&WETTERaufrufen=stadt&Wtp=&SUCHE=Agrarwetter&wT=11'],
                            forecasted_days=14,
                            data_filename='proplanta_de.csv')

forecast_websites = [wetter_de, wetter_com, proplanta_de]
#forecast_websites = [proplanta_de]
#website = requests.get('https://www.proplanta.de/Agrar-Wetter/M%FCnchen-AgrarWetter.html')
#soup = BeautifulSoup(website.content, 'html.parser')
#print(proplanta_de.retrieve_rain_chances_str(soup))
#print(soup)
#a = proplanta_de.retrieve_rain_amounts_str(soup)
#print(a)
#print(AccuracyMonitor.retrieve_max_T_and_rain_amount(days_ago=5))

wetter_com_monitor = AccuracyMonitor(wetter_com, 'wetter.com', 'wetter_com_acc_log.csv')
wetter_de_monitor = AccuracyMonitor(wetter_de, 'wetter.de', 'wetter_de_acc_log.csv')
proplanta_de_monitor = AccuracyMonitor(proplanta_de, 'proplanta.de', 'proplanta_de_acc_log.csv')
accuracy_monitors = [wetter_de_monitor, wetter_com_monitor, proplanta_de_monitor]
#a = wetter_com_monitor.avg_max_T_deviation(1, sequence=True, absolute_value=False, relative=False)
#print(a)
#a = wetter_com_monitor.avg_rain_amount_deviation(1, sequence=2, absolute_value=True, relative=False)
#print(a)

# plot course of average deviation of maximum temperature
'''
fig1, ax1 = plt.subplots()
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
for monitor in accuracy_monitors:
    avg_deviations, dates_forecasted = monitor.avg_max_T_deviation(1, sequence=True, absolute_value=True, relative=False)
    plt.plot(dates_forecasted, avg_deviations, label=monitor.name)
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=math.ceil(len(dates_forecasted) / 7)))
plt.gcf().autofmt_xdate()
plt.ylabel('average absolute deviation in °C')
plt.title('Accuracy of T$_{\mathrm{max}}$ projection five days in advance ')
plt.gca().legend()


# plot deviation of maximum temperature
fig2, ax2 = plt.subplots()
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
for monitor in accuracy_monitors:
    avg_deviations, dates_forecasted = monitor.avg_max_T_deviation(1, sequence=True, absolute_value=True, relative=False)
    plt.plot(dates_forecasted, avg_deviations, label=monitor.name)
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=math.ceil(len(dates_forecasted) / 7)))
plt.gcf().autofmt_xdate()
plt.ylabel('average absolute deviation in °C')
plt.title('Accuracy of T$_{\mathrm{max}}$ projection five days in advance ')
plt.gca().legend()
plt.show()
'''
temp, dates = wetter_com_monitor.deviation('max Temp.')
print(wetter_com_monitor.actual_values('max Temp.', dates))

# plot course of average deviation of rain amount

# plot deviation of rain amount



# retrieve weather forecast
#for website in forecast_websites:
#    website.update_csv_file()





