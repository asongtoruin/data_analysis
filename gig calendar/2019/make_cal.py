import calmap
from matplotlib.colors import ListedColormap
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import pandas as pd


plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = 'Gilroy'

# Set up colours
bg_colour = '#11151C'
# zero_colour = '#212D40'
zero_colour = '#364156'
sep_colour = '#7D4E57'
highlight_colour = '#D66853'
cm = ListedColormap(['white', highlight_colour])

df = pd.read_csv('2019 gigs.csv', parse_dates=['Start', 'End']).assign(Count=1)

# Convert to midnight for each day
df['Start Day'] = df['Start'].dt.normalize()
df['End Day'] = (df['End'] - pd.Timedelta(hours=1)).dt.normalize()

df = pd.concat([
    pd.DataFrame(
        {'Day': pd.date_range(row['Start Day'], row['End Day'], freq='1D'),
         'Event': row['Event'],
         'Location': row['Location'],
         'Count': row['Count']}, columns=['Day', 'Event', 'Location', 'Count']
    ) for i, row in df.iterrows()
], ignore_index=True)

df.set_index('Day', inplace=True)
print(df)

fig, ax = plt.subplots(figsize=(15, 10))

calmap.yearplot(
    df['Count'], year=2019, ax=ax, how=None, vmin=0, vmax=1,
    monthseparator=True, separatorwidth=2,
    fillcolor=zero_colour, linecolor=bg_colour, cmap=cm, separatorcolor=sep_colour
)

ax.tick_params(axis='both', colors=highlight_colour)
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=15)

title = ax.set_title('2019 Gig Calendar', fontweight='bold', color=highlight_colour, size=40)

title.set_path_effects([pe.Stroke(linewidth=1.5, foreground=zero_colour),
                        pe.Normal()])

# Set colours
ax.set_facecolor(bg_colour)

plt.savefig('2019-Gig-Calendar.png', bbox_inches='tight', facecolor=bg_colour)
