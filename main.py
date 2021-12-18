import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from website_classes import *
from accuracy_monitor import AccuracyMonitor

links = {
    'wetter.de': 'https://www.wetter.de/deutschland/wetter-muenchen-18225562.html?q=m%C3%BCnchen',
    'wetter.com': 'https://www.wetter.com/wetter_aktuell/wettervorhersage/16_tagesvorhersage/deutschland/muenchen/DE0006515.html',
    'proplanta.de day 1-4': 'https://www.proplanta.de/Agrar-Wetter/M%FCnchen-AgrarWetter.html',
    'proplanta.de day 5-7': 'https://www.proplanta.de/Agrar-Wetter/profi-wetter.php?SITEID=60&PLZ=M%FCnchen&STADT=M%FCnchen&WETTERaufrufen=stadt&Wtp=&SUCHE=Agrarwetter&wT=4',
    'proplanta.de day 8-11': 'https://www.proplanta.de/Agrar-Wetter/profi-wetter.php?SITEID=60&PLZ=M%FCnchen&STADT=M%FCnchen&WETTERaufrufen=stadt&Wtp=&SUCHE=Agrarwetter&wT=7',
    'proplanta.de day 12-14': 'https://www.proplanta.de/Agrar-Wetter/profi-wetter.php?SITEID=60&PLZ=M%FCnchen&STADT=M%FCnchen&WETTERaufrufen=stadt&Wtp=&SUCHE=Agrarwetter&wT=11',
    'wetterzentrale.de': 'https://www.wetterzentrale.de/weatherdata_de.php?station=3379'
}


# Create objects of websites from which the weather forecasts are retrieved
wetter_de = Wetter_de(url=links['wetter.de'],
                      forecasted_days=14,
                      data_filename='wetter_de.csv')

wetter_com = Wetter_com(url=links['wetter.com'],
                        forecasted_days=16,
                        data_filename='wetter_com.csv')

proplanta_de = Proplanta_de(url=[links['proplanta.de day 1-4'],
                                 links['proplanta.de day 5-7'],
                                 links['proplanta.de day 8-11'],
                                 links['proplanta.de day 12-14']],
                            forecasted_days=14,
                            data_filename='proplanta_de.csv')

forecast_websites = [wetter_de, wetter_com, proplanta_de]

# create a monitor object for each website
wetter_com_monitor = AccuracyMonitor(wetter_com, 'wetter.com', 'wetter_com_acc_log.csv', links['wetterzentrale.de'])
wetter_de_monitor = AccuracyMonitor(wetter_de, 'wetter.de', 'wetter_de_acc_log.csv', links['wetterzentrale.de'])
proplanta_de_monitor = AccuracyMonitor(proplanta_de, 'proplanta.de', 'proplanta_de_acc_log.csv', links['wetterzentrale.de'])
accuracy_monitors = [wetter_de_monitor, wetter_com_monitor, proplanta_de_monitor]

# retrieve weather forecast
for website in forecast_websites:
    website.update_csv_file()


# set plotting style
plt.style.use('seaborn-colorblind')

# plot course of average deviation of maximum temperature
fig1, ax1 = plt.subplots()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
for monitor in accuracy_monitors:
    avg_deviations, dates_forecasted = monitor.avg_max_T_deviation(5, sequence=True, absolute_value=True, relative=False)
    ax1.plot(dates_forecasted, avg_deviations, label=monitor.name)
ax1.xaxis.set_major_locator(mdates.DayLocator(interval=math.ceil(len(dates_forecasted) / 7)))
fig1.autofmt_xdate()
ax1.set_ylabel('average absolute deviation in °C')
ax1.set_title('Accuracy of T$_{\mathrm{max}}$ projection five days in advance ')
ax1.legend()

# plot deviation of maximum temperature from real value
fig2, ax2 = plt.subplots()
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
for monitor in accuracy_monitors:
    deviations, dates_forecasted = monitor.deviations("max Temp.", forecasted_day=1, absolute_value=False, relative=False)
    actual_values = monitor.actual_values("max Temp.", dates_forecasted)
    forecasted_values = [x + y for x, y in zip(actual_values, deviations)]
    ax2.plot(dates_forecasted, forecasted_values, '--', label=monitor.name)
ax2.plot(dates_forecasted, actual_values, label="actual values")
ax2.xaxis.set_major_locator(mdates.DayLocator(interval=math.ceil(len(dates_forecasted) / 7)))
fig2.autofmt_xdate()
ax2.set_ylabel('T in °C')
ax2.set_title('Projection of  T$_{\mathrm{max}}$ the next day vs actual value')
handles, labels = ax2.get_legend_handles_labels()
ax2.legend([handles[-1], *handles[:-1]], [labels[-1], *labels[:-1]])

# plot average deviation of maximum temperature dependent on days in advance
fig3, ax3 = plt.subplots()
range_forecasted_days = range(1, 14)
for monitor in accuracy_monitors:
    avg_deviations = []
    for forecasted_day in range_forecasted_days:
        avg_deviation = monitor.avg_max_T_deviation(forecasted_day, sequence=False, absolute_value=True, relative=False)
        avg_deviations.append(avg_deviation)
    ax3.plot(range_forecasted_days, avg_deviations, label=monitor.name)
ax3.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax3.set_ylabel('Average deviation from T$_{\mathrm{max, real}}$ in °C')
ax3.set_xlabel('Number of days ahead')
ax3.set_title('Accuracy of T$_{\mathrm{max}}$ projection')
ax3.legend()
ax3.set_ylim(0)
plt.show()


accuracy_monitors = [wetter_com_monitor, proplanta_de_monitor]
# plot course of average deviation of amount of rain
fig4, ax4 = plt.subplots()
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
for monitor in accuracy_monitors:
    avg_deviations, dates_forecasted = monitor.avg_rain_amount_deviation(5, sequence=True, absolute_value=True, relative=False)
    ax4.plot(dates_forecasted, avg_deviations, label=monitor.name)
ax4.xaxis.set_major_locator(mdates.DayLocator(interval=math.ceil(len(dates_forecasted) / 7)))
fig4.autofmt_xdate()
ax4.set_ylabel('Average absolute deviation in l/m$^{2}$')
ax4.set_title('Accuracy of amount of rain projection five days in advance ')
ax4.legend()

# plot projection of amount of rain the next day vs actual value
fig5, ax5 = plt.subplots()
ax5.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
for monitor in accuracy_monitors:
    deviations, dates_forecasted = monitor.deviations("Amount of Rain", forecasted_day=1, absolute_value=False, relative=False)
    actual_values = monitor.actual_values("Amount of Rain", dates_forecasted)
    forecasted_values = [x + y for x, y in zip(actual_values, deviations)]
    ax5.plot(dates_forecasted, forecasted_values, '--', label=monitor.name)
ax5.plot(dates_forecasted, actual_values, label="actual values")
ax5.xaxis.set_major_locator(mdates.DayLocator(interval=math.ceil(len(dates_forecasted) / 7)))
fig5.autofmt_xdate()
ax5.set_ylabel('Amount of rain in l/m$^{2}$')
ax5.set_title('Projection of amount of rain the next day vs actual value')
handles, labels = ax5.get_legend_handles_labels()
ax5.legend([handles[-1], *handles[:-1]], [labels[-1], *labels[:-1]])

# plot average deviation of amount of rain dependent on days in advance
fig6, ax6 = plt.subplots()
range_forecasted_days = range(1, 7)
for monitor in accuracy_monitors:
    avg_deviations = []
    for forecasted_day in range_forecasted_days:
        avg_deviation = monitor.avg_rain_amount_deviation(forecasted_day, sequence=False, absolute_value=True, relative=False)
        avg_deviations.append(avg_deviation)
    ax6.plot(range_forecasted_days, avg_deviations, label=monitor.name)
ax6.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax6.set_ylabel('Average deviation from real amount of rain in l/m$^{2}$')
ax6.set_xlabel('Number of days ahead')
ax6.set_title('Accuracy of amount of rain projection')
ax6.legend()
ax6.set_ylim(0)
