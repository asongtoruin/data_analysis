from datetime import datetime, time
from pathlib import Path

import fitparse
import matplotlib.font_manager as fm
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import seaborn as sns


# Set up font and line colours
fc = '#d9e5c4'
plt.rcParams['text.color'] = fc
plt.rcParams['axes.labelcolor'] = fc
plt.rcParams['xtick.color'] = fc
plt.rcParams['ytick.color'] = fc

# Set up background colour
bg = '#23113b'
plt.rcParams['figure.facecolor'] = bg
plt.rcParams['axes.facecolor'] = bg
plt.rcParams['savefig.facecolor'] = bg

# Set up font
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = 'Geomanist'
plt.rcParams['font.weight'] = 'regular'


durations = pd.DataFrame([
    {'Film': 'Halloween', 'Length': 91, 'Start': datetime(year=2020, month=10, day=31, hour=11, minute=30)},
    {'Film': 'Ginger Snaps', 'Length': 108, 'Start': datetime(year=2020, month=10, day=31, hour=20, minute=30)},
    {'Film': 'Don\'t Breathe', 'Length': 89, 'Start': datetime(year=2020, month=10, day=31, hour=18, minute=0)},
    {'Film': 'Scream', 'Length': 112, 'Start': datetime(year=2020, month=10, day=31, hour=14, minute=0)},
])

# Add in a buffer for film start delays
durations['End'] = (
    durations['Start'] + pd.to_timedelta(durations['Length'] + 10, unit='m')
)

# Read inthe .FIT files
base = Path('2020-10-31')
records = []
for fit in base.glob('*.fit'):
    print(fit)
    fitfile = fitparse.FitFile(str(fit))

    # Garmin timestamps are weird, so this is some very specific faffing
    for f in fitfile.get_messages('monitoring'):
        for data in f:
            if data.name == 'timestamp':
                current_offset = int(datetime.timestamp(data.value)) - 631065600
        if any(data.name == 'heart_rate' for data in f):
            curr_dict = {data.name: data.value for data in f}
            curr_dict['timestamp_16'] = (
                current_offset 
                + ((curr_dict['timestamp_16'] - current_offset) & 0xffff)
            )
            
            records.append(curr_dict)


df = pd.DataFrame.from_records(records)
df['Datetime'] = (df['timestamp_16'] + 631065600).apply(datetime.fromtimestamp)
df.set_index('Datetime', inplace=True)

# Tag heart rate data with films
df['Film'] = None
for i, row in durations.iterrows():
    df.loc[
        df.between_time(row['Start'].time(), row['End'].time()).index, 'Film'
    ] = row['Film']

film_times = df.dropna().reset_index(drop=False)

# Draw the grid
plots = sns.FacetGrid(
    film_times, row='Film', sharex=False, sharey=True, aspect=4, height=2
)

# Draw the lines
plots.map(
    sns.lineplot, 'Datetime', 'heart_rate', 
    color='#eb6123', zorder=2, lw=3, solid_capstyle='round'
)
plots.set(xticks=[], xlabel='', ylabel='')
plots.set_titles("{row_name}", weight='regular', size=15)
plots.despine(left=True, bottom=True)

# Set up the title
mid = (plots.fig.subplotpars.right + plots.fig.subplotpars.left) / 2
font = fm.FontProperties(fname='GROOVYGH.TTF')
plots.fig.suptitle(
    'Adam\'s Movie Marathon Heart Rate', size=30, x=mid, fontproperties=font
)
plots.fig.subplots_adjust(top=0.88)

# We want to add in a label for when the delivery came
DELIVERY = datetime(year=2020, month=10, day=31, hour=14, minute=56)
hr = film_times[film_times['Datetime'].eq(DELIVERY)]['heart_rate'].iloc[0]

for ax in plots.axes.flatten():
    ax.tick_params(which='both', length=0)
    ax.grid(axis='y', alpha=.2, ls='--')
    
    start, end = ax.get_xlim()
    if start < mdates.date2num(DELIVERY) < end:
        ax.annotate(
            'Answering the door\nfor a parcel', xy=(DELIVERY, hr), 
            xytext=(-40, -10), textcoords='offset pixels', 
            va='center', ha='right', size=8, 
            bbox=dict(pad=0, fc='none', ec='none'),
            arrowprops=dict(
                arrowstyle="->", connectionstyle="arc3", color=fc, 
                relpos=(1, 0.5)
            ),
        )
    
# Add in site reference
source_text = (
    'Data extracted from Garmin Forerunner 45\n'
    'Source: ruszkow.ski/graphs/2020-11-03-halloween-heartrate'
)
ax.annotate(
    text=source_text, 
    xy=(18, 10), xycoords=('figure points', 'figure points'), 
    ha='left', va='bottom', size='small'
)

plt.savefig('heartbeats.png', bbox_inches='tight')
