from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


cur_dir = Path(__file__).parent
data_dir = cur_dir / 'Data'
graph_dir = cur_dir / 'Graphs'
graph_dir.mkdir(exist_ok=True)

# Set up font
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = 'Noway Round'
plt.rcParams['font.weight'] = 'regular'

df = pd.read_csv(data_dir / 'Tier Seasons.csv')

# Get the outsiders
outsiders = df[df['Highest Level'].ne(1)]

# Set up colours
light_blue = '#89D2DC'
dark_blue = '#101d42'

# First, plot the outsiders
fig, ax = plt.subplots(figsize=(12, 10), facecolor=dark_blue)

top_ten = outsiders.groupby('Team')\
                   .agg({'Total Seasons': 'first'})\
                   .nlargest(11, 'Total Seasons')

teams = top_ten.index
seasons = top_ten['Total Seasons']

rects = ax.barh(y=teams, width=seasons, fc=light_blue)

for name, rect in zip(teams, rects):
    ax.text(
        x=rect.get_x(), y=rect.get_y()+rect.get_height()/2,
        s='  ' + name,
        ha='left', va='center',
        size=25, weight='regular', c=dark_blue
    )

    ax.text(
        x=rect.get_width(), y=rect.get_y()+rect.get_height()/2,
        s=f'{rect.get_width()}  ',
        ha='right', va='center',
        size=25, weight='regular', c=dark_blue
    )

ax.margins(x=0, y=0)

ax.invert_yaxis()
ax.set_axis_off()

plt.suptitle('Outsiders', weight='bold', size=80, c=light_blue, y=1.08)
ax.set_title(
    'Teams with the most seasons in the English (men\'s) Football\nLeague who have never played in the top flight.',
    c=light_blue, weight='regular', size=25, y=1.02, loc='left'
)

ax.annotate(
    s='Accurate up to 2019-2020 season using data from rsssf.com\n'
      'For more information, visit ruszkow.ski/graphs/2020-06-28-football-league-seasons', 
    xy=(0, -0.08), xycoords='axes fraction',
    c=light_blue, weight='regular', size=14
)

plt.savefig(
    graph_dir / 'outsiders.png', bbox_inches='tight', facecolor='#101d42', 
    pad_inches=.2, dpi=200
)
plt.close()


# Now get the top number of seasons in the second tier
nearly = outsiders[outsiders['Numeric Level'].eq(2)]\
                  .sort_values(by='Seasons', ascending=False)\
                  .nlargest(11, 'Seasons')

fig, ax = plt.subplots(figsize=(12, 10), facecolor=dark_blue)

# "Gainsborough Trinity" is too long to fit in the bar. Shorten.
teams = nearly['Team'].str.replace('Gainsborough Trinity', 'Gainsborough')
seasons = nearly['Seasons']

rects = ax.barh(y=teams, width=seasons, fc=light_blue)

for name, rect in zip(teams, rects):
    ax.text(
        x=rect.get_x(), y=rect.get_y()+rect.get_height()/2,
        s='  ' + name,
        ha='left', va='center',
        size=25, weight='regular', c=dark_blue
    )

    ax.text(
        x=rect.get_width(), y=rect.get_y()+rect.get_height()/2,
        s=f'{rect.get_width()}  ',
        ha='right', va='center',
        size=25, weight='regular', c=dark_blue
    )

ax.margins(x=0, y=0)

ax.invert_yaxis()
ax.set_axis_off()

ax.set_facecolor('#101D42')

plt.suptitle('Nearly Men', weight='bold', size=80, c=light_blue, y=1.09)
ax.set_title(
    'Teams with the most seasons in the second tier of English\n(men\'s) football who have never played in the top flight.',
    c=light_blue, weight='regular', size=25, y=1.02, loc='left'
)

ax.annotate(
    s='Accurate up to 2019-2020 season using data from rsssf.com\n'
      'For more information, visit ruszkow.ski/graphs/2020-06-28-football-league-seasons', 
    xy=(0, -0.08), xycoords='axes fraction',
    c=light_blue, weight='regular', size=14
)

plt.savefig(
    graph_dir / 'nearly.png', bbox_inches='tight', facecolor='#101d42', 
    pad_inches=.2, dpi=200
)
