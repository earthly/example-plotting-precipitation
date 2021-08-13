import math
import re
import os
import pandas
import datetime
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.pyplot as plt

# Our new date parser
def yyyymmdd_parser(s):
    return datetime.datetime.strptime(s, '%Y-%m-%d')

def get_data(weather_dir):
    p = re.compile('victoria-weather-[0-9]+.csv')
    data = []
    for filename in sorted(os.listdir(weather_dir)):
        if p.match(filename):
            path = os.path.join(weather_dir, filename)
            # We identify which column contains the date, along with the date parser to use.
            yearly_data = pandas.read_csv(path, parse_dates=['Date/Time'], date_parser=yyyymmdd_parser)
            data.append(yearly_data)
    return pandas.concat(data)

def get_days_since_jan1(date):
    return date.timetuple().tm_yday - 1

def split_data_by_year(weather):
    yearly_rainfall = []
    yearly_days_since_jan1 = []
    current_year = None
    by_year = []
    for i, row in weather.iterrows():
        date = row['Date/Time']
        rainfall = row['Total Precip (mm)']

        # 1cm snow = 10mm snow; 13mm of snow = 1mm of rain
        snowfall = row['Total Snow (cm)'] * 10.0 / 13.0
        rainfall += snowfall

        if current_year is None:
            current_year = date.year
        elif current_year != date.year:
            by_year.append((current_year, pandas.DataFrame({
                'days_since_jan1': yearly_days_since_jan1,
                'rainfall': yearly_rainfall,
                })))
            yearly_days_since_jan1 = []
            yearly_rainfall = []
            current_year = date.year

        yearly_rainfall.append(rainfall)
        yearly_days_since_jan1.append(get_days_since_jan1(date))

    if current_year is not None:
        by_year.append((current_year, pandas.DataFrame({
            'days_since_jan1': yearly_days_since_jan1,
            'rainfall': yearly_rainfall,
            })))

    return by_year

def get_total_rainfall(val):
    year, annual_data = val
    total_rainfall = annual_data['rainfall'].cumsum().to_list()[-1]
    return (total_rainfall, year)

def format_days_since_jan1(days, pos=None):
    date = datetime.date(2020, 1, 1) + datetime.timedelta(days)
    return date.strftime('%b')

if __name__ == '__main__':

    weather = get_data('data')
    weather['Total Precip (mm)'] = weather['Total Precip (mm)'].fillna(0)
    weather['Total Snow (cm)'] = weather['Total Snow (cm)'].fillna(0)
    rainfall_by_year = split_data_by_year(weather)

    fig = plt.figure(figsize=(10.0, 7.0), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])

    for year, annual_data in sorted(rainfall_by_year, key=get_total_rainfall, reverse=True):
        days_since_jan1 = annual_data['days_since_jan1'].to_list()
        rainfall = annual_data['rainfall'].cumsum().to_list()
        ax.plot(days_since_jan1, rainfall, label=year)

    # format x axis values as month names rather than days since jan 1st
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(format_days_since_jan1))

    # label the axes and title the plot
    ax.set_xlabel('calendar date')
    ax.set_ylabel('precipitation (mm)')
    ax.set_title('Victoria BC cumulative annual precipitation')
    ax.legend()

    # save the plot to disk
    fig.savefig('cumulative-annual-precipitation.png', bbox_inches='tight')
