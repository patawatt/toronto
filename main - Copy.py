import glob
import pandas as pd
import numpy as np


def dtstr(self):
    hour = self.time().hour
    minute = self.time().minute
    if hour < 10:
        hour = '0' + str(hour)
    else:
        hour = str(hour)
    if minute < 10:
        minute = '0' + str(minute)
    else:
        minute = str(minute)
    return str(self.date()) + ' ' + hour + '-' + minute

# glob.glob('data*.csv') - returns List[str]
# pd.read_csv(f) - returns pd.DataFrame()
# for f in glob.glob() - returns a List[DataFrames]
# pd.concat() - returns one pd.DataFrame()

files = glob.glob('data/*.csv')
df = pd.read_csv(files[0], skiprows=14)
# why was this here?
df = df.rename(columns={'Date/Time': 'dt', 'Value': files[0][5:-12]})
df.set_index(pd.DatetimeIndex(df['dt']), inplace=True)
df = df.loc[df.index.year == 2018, :]
# df = df.drop(['dt'], axis=1)
df.dt = pd.DatetimeIndex(df['dt'])

# df.index = pd.MultiIndex.from_arrays([df.date, df.time], names=['Date', 'Time'])
# df = df.drop(['date', 'time', 'year', 'Date/Time'], axis=1)
#
# df.sort_index(inplace=True)
df.sort_index()

suntime = pd.read_fwf('daylight/sun.txt', skiprows=16, widths=[6, 16, 5, 7, 7])
suntime = suntime.iloc[:-1, [0, 2, 4]]
suntime.columns = ['date', 'sunrise', 'sunset']
suntime['date'] = pd.to_datetime(suntime['date'] + ', 2018').dt.date
# suntime['date'] = pd.to_datetime(suntime['date'] + ', 2018').dt.date
suntime.set_index(pd.DatetimeIndex(suntime['date']), inplace=True)

suntime.sunrise = suntime.index + pd.to_timedelta(suntime.sunrise + ':00', unit='h')
suntime.sunset = suntime.index + pd.to_timedelta(suntime.sunset + ':00', unit='h')
# suntime['sunrise'] = pd.to_datetime(suntime['date'].date() + ', 2018').dt.date

# suntime.index = suntime['date']
suntime = suntime.drop(['date'], axis=1)
suntime.sort_index(inplace=True)
#
# first = 0
# for date, new_df in df.groupby(level=0):
#
#     # print(suntime[str(date)])
#     if first == 0:
#         print(type(date))
#         print(str(date))
#         print(df[str(date)])
#         first +=1
#
# first = 0
#
# for date, new_df in suntime.groupby(level=0):
#     if first == 0:
#         print(type(date))
#         print(str(date))
#         first +=1

# add check that key exists, or loop through df instead.
# for date in df.index:
#     # print(type(date))
#     # print(type(pd.to_datetime(date)))
#     # print(df[date])
#     # print(suntime.loc[str(date.date())])
#
#     # good April 25th
#     # print(suntime.loc[date.date()])
#     # print(suntime.loc[date.date()]['sunrise'])
#
#     sunrise = suntime.loc[date.date()]['sunrise']
#     sunset = suntime.loc[date.date()]['sunset']
    # if date < sunrise or date >= sunset:
    #     df[date]['Day/Night'] = 'N'
    # else:
    #     df[date]['Day/Night'] = 'D'

    # df['Day/Night'] = np.where(sunrise > df['dt'], 'Day', 'Night')
    # df['Day/Night'] = df.apply(lambda index: label_race(index), axis=1)



# def nord(index, sunrise, sunset):
#     if index < sunrise or index >= sunset:

# possible approaches
# loop through each hour, assign day or night to new columns
# add sunrise and sunset columns to df, then use pandas comparisons to assign to new third column
# break dataframe into list of dataframes for individual days, use np.where for each day, then recombine all the dataframes.
sunrises = []
sunsets = []
for i in range(len(df)):
    # print(df[i][:])
    sunrises.append(suntime.loc[str(df.iloc[i, 0].date())]['sunrise'])
    sunsets.append(suntime.loc[str(df.iloc[i, 0].date())]['sunset'])

df['sunrise'] = sunrises
df['sunset'] = sunsets
df['day'] = (df['sunrise'] <= df['dt']) & (df['dt'] < df['sunset'])

df_avg = df.resample('D').mean()

day = df[df['day']].drop(['day'], axis=1)
night = df[~df['day']].drop(['day'], axis=1)

d_avg = day.resample('D').mean()
n_avg = day.resample('D').mean()
