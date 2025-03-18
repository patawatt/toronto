import glob
import pandas as pd
import sqlite3

# Read textfile from Toronto Airport weather station and slice out columns for date, and sunrise, sunset times
suntime = pd.read_fwf('daylight/sun.txt', skiprows=16, widths=[6, 16, 5, 7, 7])
suntime = suntime.iloc[:-1, [0, 2, 4]]
suntime.columns = ['date', 'sunrise', 'sunset']

# change format of times to python date-time format, set as dataframe index
suntime['date'] = pd.to_datetime(suntime['date'] + ', 2018').dt.date
suntime.set_index(pd.DatetimeIndex(suntime['date']), inplace=True)
suntime.sunrise = suntime.index + pd.to_timedelta(suntime.sunrise + ':00', unit='h')
suntime.sunset = suntime.index + pd.to_timedelta(suntime.sunset + ':00', unit='h')
# drop redundant date column
suntime = suntime.drop(['date'], axis=1)
suntime.sort_index(inplace=True)
final = suntime.copy()

# iterate through list of datalogger .csv files in data directory
files = glob.glob('data/*.csv')

for j in range(len(files)):
    df = pd.read_csv(files[j], skiprows=14)

    # add temperature data for each address as new column to df
    df = df.rename(columns={'Date/Time': 'dt', 'Value': files[j][5:-12]})
    df.set_index(pd.DatetimeIndex(df['dt']), inplace=True)
    # keep only data in 2018
    df = df.loc[df.index.year == 2018, :]
    df.dt = pd.DatetimeIndex(df['dt'])
    df.sort_index()

    # create lists of sunrise and sunset timestamps
    sunrises = []
    sunsets = []
    for i in range(len(df)):
        sunrises.append(suntime.loc[str(df.iloc[i, 0].date())]['sunrise'])
        sunsets.append(suntime.loc[str(df.iloc[i, 0].date())]['sunset'])

    # add sunset and sunrise lists as columns to df with single address
    df['sunrise'] = sunrises
    df['sunset'] = sunsets
    # create new column that describes which times are day and not using true/false
    df['day'] = (df['sunrise'] <= df['dt']) & (df['dt'] < df['sunset'])

    # create individual dataframes for measurements during day and night
    day = df[df['day']].drop(['day'], axis=1)
    night = df[~df['day']].drop(['day'], axis=1)

    # take daily means of day temperature and night temperature by resampling
    d_d_av = day.resample('D').mean()
    n_d_av = night.resample('D').mean()

    # merge the day and night dataframes together so daily averages can be compared side by side
    frames = [d_d_av, n_d_av]
    merge = pd.merge(frames[0], frames[1], how='inner', left_index=True,
                     right_index=True, suffixes=('_d', '_n'))
    merge2 = pd.merge(final, merge, how='inner', left_index=True,
                      right_index=True)

    final = merge2

# remove sunset and sunrise times as no longer needed.
final = final.drop(['sunrise', 'sunset'], axis=1)

# SAVE TO EXCEL
final.to_excel("day_night_temp_daily_AV.xlsx")

# resample at weekly intervals
wfinal = final.resample('W').mean()
wfinal.to_excel("day_night_temp_weekly_AV.xlsx")

# resample at monthly intervals
mfinal = final.resample('M').mean()
mfinal.to_excel("day_night_temp_monthly_AV.xlsx")

# export to sql database
conn = sqlite3.connect('daily_temperature_averages.db')
c = conn.cursor()
c.execute('CREATE TABLE TEMPS(date, temp)')
conn.commit()
final.to_sql('TEMPS', conn, if_exists= 'replace', index=False)

c.execute('''
SELECT * FROM TEMPS
''')

for row in c.fetchall():
    print(row)
