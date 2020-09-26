from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd


# Set up font and line colours
fc = '#d9e5c4'
plt.rcParams['text.color'] = fc
plt.rcParams['axes.labelcolor'] = fc
plt.rcParams['xtick.color'] = fc
plt.rcParams['ytick.color'] = fc

# Set up background colour
bg = '#262e2f'
plt.rcParams['figure.facecolor'] = bg
plt.rcParams['axes.facecolor'] = bg
plt.rcParams['savefig.facecolor'] = bg

# Set up font
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = 'Geomanist'
plt.rcParams['font.weight'] = 'regular'

# Download tables
singles, albums = pd.read_html(
    r'https://www.officialcharts.com/artist/10292/biffy-clyro/'
)

# Combine into a single frame
all_releases = pd.concat([
    singles.assign(Type='Single'),
    albums.assign(Type='Album')
])

# Convert to proper datetimes, and drop rows that don't correspond to releases
all_releases['Date'] = pd.to_datetime(
    all_releases['Date'].str.replace(' ', ''), 
    errors='coerce', format='%d.%m.%Y'
)
all_releases = all_releases.dropna(subset=['Date'])

# Convert numeric values
for col in ('WoC', 'Peak Pos'):
    all_releases[col] = pd.to_numeric(all_releases[col])

# Get release title from combined title and artist string, convert to Title case
# with replacements
all_releases['Release'] = all_releases['Title, Artist'].str.split(
    ' BIFFY CLYRO'
).str[0].str.title().str.replace('Mtv', 'MTV').str.replace('Ost', 'OST')

# Ensure we're only plotting the first week of charting, but all the weeks in 
# the charts
all_releases = all_releases.groupby(['Release', 'Type'], as_index=False)\
                           .agg({'WoC': 'sum', 'Date': 'min', 'Peak Pos': 'min'})

# Use different marker for releases reaching number 1
all_releases['Marker'] = np.where(all_releases['Peak Pos'].eq(1), '*', 'o')

# Set up colours
c1 = '#6c8a88'
c2 = '#a3a137'

colours = {
    'Single': c1,
    'Album': c2,
}

# Set up the axes
fig, ax = plt.subplots(figsize=(13,5))

# Scaling factor for number of weeks
point_scale = 8

# Plot albums and singles separately
for release_type, data in all_releases.groupby('Type'):
    colour = colours[release_type]
    
    # Draw lines of lollipop
    ax.vlines(
        data['Date'], ymin=100, ymax=data['Peak Pos'], color=colour, 
        alpha=.5, lw=2, zorder=2
    )
    
    # Draw "heads"
    for marker, marker_data in data.groupby('Marker'):
        ax.scatter(
            marker_data['Date'], marker_data['Peak Pos'], 
            marker=marker, color=colour, s=marker_data['WoC']*point_scale, 
            zorder=3
        )
    
    # Add labels for albums
    if release_type == 'Album':
        for i, row in data.iterrows():
            ax.text(
                s=row['Release'], x=row['Date']+pd.Timedelta(30, unit='d'), 
                y=99, rotation=90, c=c2, ha='left', alpha=.75, va='bottom',
            )

# Neaten up the Y axis
ax.yaxis.set_major_locator(mtick.FixedLocator([1, 10, 20, 40, 60, 80, 100]))
ax.grid(axis='y', which='major', zorder=1, alpha=.4, ls=':', lw=1.5)
ax.invert_yaxis()
ax.tick_params(axis='y', length=0)
ax.set_ylim(bottom=100.5)

# Label the axes
ax.set_ylabel('Peak UK Chart Position')
ax.set_xlabel('First Week in Charts')

# Hide spines
for side in ('left', 'right', 'top', 'bottom'):
    ax.spines[side].set_visible(False)

# Set up a bit of padding for the x-axis
ax.set_xlim(
    left=all_releases['Date'].min() - pd.Timedelta(90, unit='d'),
    right=all_releases['Date'].max() + pd.Timedelta(90, unit='d')
)

# Add in the legend
legend_entries = [
    Line2D([0], [0], marker='o', color=fc, label='Charting release', markersize=8, lw=0),
    Line2D([0], [0], marker='*', color=fc, label='Number 1 release', markersize=8, lw=0),
    Patch(fc=c1, label='Single'),
    Patch(fc=c2, label='Album'),
]
ax.legend(
    # title='Scaled to Weeks In Chart',
    handles=legend_entries, ncol=2, edgecolor=fc, 
    loc='upper center', bbox_to_anchor=(0.5, -0.12)
)

# Add in site reference
source_text = (
    'Points scaled according to number of weeks in chart.\n'
    'Correct as of 2020-09-26.\n'
    'Source: ruszkow.ski/graphs/2020-09-26-biffy-clyro-chart-positions'
)
ax.annotate(
    s=source_text, 
    xy=(-20, .01), xycoords=('axes points', 'figure fraction'), 
    ha='left', va='bottom', size='small'
)

ax.set_title(
    'Biffy Clyro Chart Positions', size=50, weight='bold', style='italic'
)
plt.savefig('biffy-chart-positions.png', bbox_inches='tight')