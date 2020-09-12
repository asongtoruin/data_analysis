from itertools import combinations

import matplotlib.pyplot as plt
import matplotlib.colors as colours
import pandas as pd
import seaborn as sns

# Set up mpl parameters
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = 'Noway Round'
plt.rcParams['font.weight'] = 'regular'

fc = 'white'
plt.rcParams['text.color'] = fc
plt.rcParams['axes.labelcolor'] = fc
plt.rcParams['xtick.color'] = fc
plt.rcParams['ytick.color'] = fc

bg = '#172727'
plt.rcParams['figure.facecolor'] = bg
plt.rcParams['axes.facecolor'] = bg
plt.rcParams['savefig.facecolor'] = bg

# Read in data and add columns
df = pd.read_csv(
    'download mainstage headliners.csv', parse_dates=['Date'], dayfirst=True
)
df['Weekday'] = df['Date'].dt.day_name()
df['Year'] = df['Date'].dt.year

df['Appearance Number'] = df.groupby('Headliner').cumcount() + 1

# Get a matrix of weekday by year
matrix = df.pivot_table(
    index='Year', columns='Weekday', values='Appearance Number'
)
# Add in 2020 as it'll be missing
matrix = matrix.reindex(range(matrix.index.min(), matrix.index.max()+1))

# Do the same for band names - this will give us our labels
labels = df.pivot_table(
    index='Year', columns='Weekday', values='Headliner', 
    aggfunc=lambda x: ''.join(x)
)
labels = labels.reindex(range(labels.index.min(), labels.index.max()+1))

# Set up our colour map
cmap = colours.LinearSegmentedColormap.from_list(
    'repeaters', colors=['#8DAB7F', '#2274A5', '#ED7D3A', '#EF2D56'], N=4
)

# Draw the heatmap
fig, ax = plt.subplots(figsize=(7, 6), facecolor='white')
sns.heatmap(matrix, ax=ax, cmap=cmap, lw=.5, annot=labels, fmt='', linecolor=bg)

# Clear axis labels, move days to the top and remove tick marks
ax.set_ylabel('')
ax.set_xlabel('')
ax.xaxis.tick_top()
ax.tick_params(length=0)

# Set up central labels for the colour bar
cbar = ax.collections[0].colorbar
cbar.set_ticks([])
for i, y in enumerate([1.375, 2.125, 2.875, 3.625]):
    cbar.ax.text(x=2.5, y=y, s=i+1, ha='center', va='center', weight='bold')

cbar.ax.tick_params(length=0)
cbar.set_label('Appearance Number (as headliner)', weight='regular')

# Set title and spacing
fig.suptitle(
    'Download Festival Main Stage Headliners', 
    style='normal', weight='heavy', size=20
)
fig.subplots_adjust(right=1.07, left=.08, bottom=.05)

# Add in site reference
source_text='''Source: ruszkow.ski/graphs/2020-09-12-download-headliners'''
ax.annotate(
    s=source_text, 
    xy=(0, .01), xycoords=('axes points', 'figure fraction'), 
    ha='left', va='bottom', size=10
)

# Save it
plt.savefig('Download Headliners.png')
