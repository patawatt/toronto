import glob
import pandas as pd
import numpy as np
# import scipy as sp

def make_df(filename):
    """
    This function takes a file name, creates a DataFrame for the temperature data in that frame,
    and rounds the timestamp to the nearest hour.
    """

    # read file to DataFrame, rename value column to match address of data-logger
    df = pd.read_csv(filename, skiprows=14)
    df = df.rename(columns={'Date/Time': 'dt', 'Value': filename[5:-12]})

    # Round to nearest hour (all measurements taken at 1 or 2 minutes past the every even hour).
    df.dt = pd.DatetimeIndex(df['dt'])
    df['dt'] = df['dt'].dt.round('H')
    df.set_index(df['dt'], inplace=True)

    # keep only data in 2018
    df = df.loc[df.index.year == 2018, :]
    df.sort_index()

    return df

def degday(mean_temp, threshold):
    """
    Calculates the growing degree day above a certain threshold for individual days.
    """
    if pd.notnull(mean_temp):
        return max(0.0, (mean_temp - threshold))
    else:
        return None


# create list of datalogger .csv files in data directory
files = glob.glob('data/*.csv')

# make first DataFrame from first site
df1 = make_df(files[0])

# iterate through files, make data frame for each address
for j in range(1, len(files)):
    df2 = make_df(files[j])

    # merge the new DataFrames to the original data frame
    df1 = pd.merge(df1, df2.iloc[:, 2], how='outer', left_index=True, right_index=True)

sites = [x[5:-12] for x in files]

# make date and dt columns.  date column is needed for df.groupby function to calculate daily mean temps.
df1['date'] = df1['dt'].dt.date
df1['time']= df1['dt'].dt.time
df1 = df1.drop(['dt', 'Unit'], axis=1)

# get mean temperature for each day (calculated from all 12 measurements).
mean_temps = df1.groupby(['date']).mean()

# vectorize degreeday function so that it works on arrays and not just single values
vdegday = np.vectorize(degday)

# list of threshold temperatures, starting at 0 increasing to 10 degrees C by intervals of 0.5 (21 temps total).
threshold_temps = np.linspace(0.0, 10.0, 21.0)

# create a list of 21 arrays, calculating daily heat units (HU) (non-cumulative), using 21 different threshold temps.
dailyHUs = {}
for threshold in threshold_temps:
    # use vectorized degree day function to get array of daily heat units.
    dailyHUs[threshold] = vdegday(mean_temps, threshold)

# create lists for different start days, Jan 1, March 9, 19, 29, April 8, 18
start_days = [0, 67, 77, 87, 97, 107, 117]

ff = pd.read_csv('data/flower/Redbud_flowering_data_forPatrick.csv')
ff = ff.loc[:, ['Address','GDD_FF']]

first_flower = dict.fromkeys(sites)
for key in first_flower:
    cell = ff.loc[ff['Address'] == key]['GDD_FF'].item()
    if pd.notnull(cell):
        first_flower[key] = int(cell)
    else:
        first_flower[key] = None


latest_flower = max(first_flower.values())

thresholds = {}
for key, array in dailyHUs.items():
    curr = pd.DataFrame(array)

    # create multiple DataFrames with different start points, but same threshold temp, accumulate temperature data
    start_points = {}
    for start in start_days:
        start_points[start] = curr.iloc[start:latest_flower].cumsum()

    # add list of DataFrames with same threshold temperature to list of threshold temperatures
    thresholds[key] = start_points

# convert day of year integer to yyyy-mm-dd format
dts = pd.Series((np.asarray(2018, dtype='datetime64[Y]')-1970)
                +(np.asarray(start_days, dtype='timedelta64[D]'))).dt.strftime('%b%-d')
# note lower case b for month abbrieviation, B for full month name.

headers = []
for temp in threshold_temps:
    for day in dts:
        headers.append(str(day) + "_" + str(temp) + "C")

rows = {}
for i in range(len(sites)):

    curr_ff = first_flower[sites[i]]-1
    rows[sites[i]] = []

    for j in range(len(threshold_temps)):

        for k in range(len(start_days)):
            rows[sites[i]].append(thresholds[threshold_temps[j]][start_days[k]].loc[curr_ff, i])


ddff = pd.DataFrame.from_dict(rows, orient='index', columns=headers)
# ddff.to_excel("gdd_ff_7startdays.xlsx")
# subset = ddff[['Jan1_0.0C', 'Mar9_0.0C', 'Apr28_0.0C', 'ff']]
# subset.to_excel("gdd_dec7.xlsx")

remove = pd.read_csv('data/flower/remove.csv')
ddff.drop(remove['Address'].values.tolist(), inplace=True)

df_ff = pd.DataFrame.from_dict(first_flower, orient='index', columns=['ff'])
ddff['ff'] = df_ff['ff']
corr_matrix = ddff.corr()

final_corr = corr_matrix['ff']

#family = binomial
#link = logit

from sklearn.linear_model import LogisticRegression
import statsmodels.api as sm
import matplotlib.pyplot as plt
xs = ddff['Jan1_0.0C'].to_list()
xs.sort()
ys = list(np.arange(1, len(xs)+1)/float(len(xs)))
fig1, ax1 = plt.subplots()
ax1.plot(xs, ys)
# logit = sm.Logit(ys, xs).fit()

pred_input = np.linspace(min(xs), max(xs),10)
# predictions = logit.predict(pred_input)
# ax1.plot(pred_input, predictions)

binom = sm.GLM(ys, xs, family=sm.families.Binomial())

print(binom_results.summary)
print(binom_results.params)
print(binom_results.pvalues)
print(binom_results.model.endog_names)
predictions = binom_results.predict()

# instantiate the model (using the default parameters)
# logreg = LogisticRegression()
#
#
# # fit the model with data
# logreg.fit(xs, ys)

# relative log likelihoods, aic
# glm_binom = sm.GLM(xs, ys,family=sm.families.Binomial())
# res = glm_binom.fit()
# print(res.summary())