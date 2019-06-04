import glob
import pandas as pd

# glob.glob('data*.csv') - returns List[str]
# pd.read_csv(f) - returns pd.DataFrame()
# for f in glob.glob() - returns a List[DataFrames]
# pd.concat() - returns one pd.DataFrame()

files = glob.glob('data/*.csv')
df = pd.read_csv(files[0], skiprows=14)
df.rename(index=str, columns={"Value": files[0][5:-12]})
df['Date/Time'] = pd.to_datetime(df['Date/Time'])
df['year'] = pd.DatetimeIndex(df['Date/Time']).year
df['date'] = pd.DatetimeIndex(df['Date/Time']).date
df['time'] = pd.DatetimeIndex(df['Date/Time']).time
df = df.loc[df['year'] == 2018, :]
df.index = pd.MultiIndex.from_arrays([df.date, df.time], names=['Date', 'Time'])
df = df.drop(['date', 'time', 'year', 'Date/Time'], axis=1)

df.sort_index(inplace=True)

suntime = pd.read_fwf('daylight/sun.txt', skiprows=16, widths=[6, 16, 5, 7, 7])
suntime = suntime.iloc[:-1, [0, 2, 4]]
suntime.columns = ['date', 'sunrise', 'sunset']
suntime['date'] = pd.to_datetime(suntime['date'] + ', 2018').dt.date
# df.set_index(pd.DatetimeIndex(df['date']), inplace=True)
suntime.index = suntime['date']
suntime = suntime.drop(['date'], axis=1)
suntime.sort_index(inplace=True)

first = 0
for date, new_df in df.groupby(level=0):

    # print(suntime[str(date)])
    if first == 0:
        print(type(date))
        print(str(date))
        print(df[str(date)])
        first +=1

first = 0

for date, new_df in suntime.groupby(level=0):
    if first == 0:
        print(type(date))
        print(str(date))
        first +=1


