from calendar import month_abbr

import pandas as pd
import seaborn as sns
import matplotlib.patheffects as mpe
import matplotlib.pyplot as plt

BACKGROUND_COLOUR = 'whitesmoke'
SOURCE = (
    'Data Source - Met Office (2019): MIDAS Open: UK daily weather observation '
    'data, v201901. Centre for Environmental Data Analysis, 01 March 2019.\n'
    'Data taken from Edinburgh Royal Botanic Garden station.'
)


sns.set(
    style='white', context='talk', 
    rc={'axes.facecolor': (0, 0, 0, 0), 'figure.facecolor':BACKGROUND_COLOUR}
)

df = pd.read_csv(
    r'midas-open_uk-hourly-weather-obs_dv-201901_midlothian-in-lothian-region_00253_edinburgh-royal-botanic-garden-no-2_qcv-1_2017.csv', 
    skiprows=280, parse_dates=['ob_time'], dayfirst=True, skipfooter=1
)

# Filter to daytime hours
df['Hour'] = df['ob_time'].dt.hour
df = df[df['Hour'].between(7, 18)]

# Get the month name and average temperature
df['Month'] = pd.Categorical(
    df['ob_time'].dt.strftime('%b'), categories=month_abbr[1:], ordered=True
)
df['Mean Temp'] = df.groupby('Month')['air_temperature'].transform('mean')

# Initialize the FacetGrid, use the mean temp to determine hue
g = sns.FacetGrid(
    df, row='Month', hue='Mean Temp', aspect=14, height=.8, palette='plasma'
)

# Draw the densities in a few steps
g.map(
    sns.kdeplot, 'air_temperature', clip_on=False,
    shade=True, alpha=1, lw=0, bw=.4
)
g.map(
    sns.kdeplot, 'air_temperature', clip_on=False, color=BACKGROUND_COLOUR,
    lw=3, bw=.4
)

# Add the baseline lines
g.map(plt.axhline, y=0, lw=2, clip_on=False)


# Define and use a simple function to label the plot in axes coordinates
def label(x, color, label):
    # 'Label' in this instance passes the hue value
    ax = plt.gca()
    ax.text(
        0, .2, x.iloc[0], fontweight='bold', color=color,
        ha='left', va='center', transform=ax.transAxes,
        path_effects=[mpe.withStroke(linewidth=5, foreground='white')]
    )
    ax.text(
        1, .2, u'{:.2f}\u00b0'.format(float(label)), fontweight='bold',
        color=color, ha='right', va='center', transform=ax.transAxes,
        path_effects=[mpe.withStroke(linewidth=5, foreground='white')]
    )


g.map(label, 'Month')

# Set the subplots to overlap and add space for the attribution
g.fig.subplots_adjust(hspace=-.4, bottom=.12)

# Remove axes details that don't play well with overlap
g.set_titles('')
g.set(yticks=[])
g.despine(bottom=True, left=True)

mid = (plt.gcf().subplotpars.right + plt.gcf().subplotpars.left)/2

plt.suptitle(
    '2017 Edinburgh Daytime Temperatures\n(7am-7pm)', fontweight='bold',
    va='center', x=mid
)

# Add the headers for the labels
first_ax = g.axes.flatten()[0]
last_ax = g.axes.flatten()[-1]

first_ax.text(
    1, .6, 'Mean', fontweight='bold', color='k',
    ha='right', va='baseline', transform=first_ax.transAxes,
)
first_ax.text(
    0, .6, 'Month', fontweight='bold', color='k',
    ha='left', va='baseline', transform=first_ax.transAxes,
)

# Add an x label
last_ax.set_xlabel(u'Temperature (\u00b0C)')

plt.text(
    plt.gcf().subplotpars.left, 0, SOURCE,
    fontsize='xx-small', style='italic', ha='left', va='baseline',
    alpha=.5,
    transform=plt.gcf().transFigure
)

# remember to restate facecolor so it actually saves it out
plt.savefig(
    'edinburgh-2017-temperatures.png', bbox_inches='tight',
    facecolor=BACKGROUND_COLOUR
)

