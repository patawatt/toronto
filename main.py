import glob
import pandas as pd
import geopandas as gpd

suntime = pd.read_fwf('daylight/sun.txt', skiprows=16, widths=[6, 16, 5, 7, 7])
suntime = suntime.iloc[:-1, [0, 2, 4]]
suntime.columns = ['date', 'sunrise', 'sunset']
suntime['date'] = pd.to_datetime(suntime['date'] + ', 2018').dt.date
suntime.set_index(pd.DatetimeIndex(suntime['date']), inplace=True)

suntime.sunrise = suntime.index + pd.to_timedelta(suntime.sunrise + ':00',
                                                  unit='h')
suntime.sunset = suntime.index + pd.to_timedelta(suntime.sunset + ':00',
                                                 unit='h')

suntime = suntime.drop(['date'], axis=1)
suntime.sort_index(inplace=True)

files = glob.glob('data/*.csv')

final = suntime.copy()

# for j in range(len(files)):
for j in range(len(files)):
    df = pd.read_csv(files[j], skiprows=14)

    # concat now or after?
    # df = pd.read_csv(files[0], skiprows=14)

    df = df.rename(columns={'Date/Time': 'dt', 'Value': files[j][5:-12]})
    df.set_index(pd.DatetimeIndex(df['dt']), inplace=True)
    df = df.loc[df.index.year == 2018, :]
    df.dt = pd.DatetimeIndex(df['dt'])
    df.sort_index()

    sunrises = []
    sunsets = []
    for i in range(len(df)):
        sunrises.append(suntime.loc[str(df.iloc[i, 0].date())]['sunrise'])
        sunsets.append(suntime.loc[str(df.iloc[i, 0].date())]['sunset'])

    df['sunrise'] = sunrises
    df['sunset'] = sunsets
    df['day'] = (df['sunrise'] <= df['dt']) & (df['dt'] < df['sunset'])

    day = df[df['day']].drop(['day'], axis=1)
    night = df[~df['day']].drop(['day'], axis=1)

    d_d_av = day.resample('D').mean()
    n_d_av = night.resample('D').mean()

    frames = [d_d_av, n_d_av]
    merge = pd.merge(frames[0], frames[1], how='inner', left_index=True,
                     right_index=True, suffixes=('_d', '_n'))
    merge2 = pd.merge(final, merge, how='inner', left_index=True,
                      right_index=True)

    final = merge2


final = final.drop(['sunrise', 'sunset'], axis=1)
# SAVE TO EXCEL
# final.to_excel("day_night_temp_daily_AV.xlsx")
#
# wfinal = final.resample('W').mean()
# wfinal.to_excel("day_night_temp_weekly_AV.xlsx")
#
# mfinal = final.resample('M').mean()
# mfinal.to_excel("day_night_temp_monthly_AV.xlsx")

