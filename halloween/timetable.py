from datetime import datetime

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
import matplotlib.ticker as mtick
import pandas as pd


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

# Set up durations and start times
durations = pd.DataFrame([
    {'Film': 'Halloween', 'Length': 91, 'Start': datetime(year=2020, month=10, day=31, hour=11, minute=30)},
    {'Film': 'Ginger Snaps', 'Length': 108, 'Start': datetime(year=2020, month=10, day=31, hour=20, minute=30)},
    {'Film': 'Don\'t Breathe', 'Length': 89, 'Start': datetime(year=2020, month=10, day=31, hour=18, minute=0)},
    {'Film': 'Scream', 'Length': 112, 'Start': datetime(year=2020, month=10, day=31, hour=14, minute=0)},
])

durations['End'] = durations['Start'] + pd.to_timedelta(durations['Length'], unit='m')
durations['Start_Minute'] = durations['Start'].dt.hour * 60 + durations['Start'].dt.minute
durations['x'] = durations['Start'].dt.weekday

# Draw plot
fig, ax = plt.subplots(figsize=(6,10))

boxes = []

for i, row in durations.iterrows():
    start = row['Start_Minute']
    duration = row['Length']
    
    label = f'{row["Film"]}\n({row["Start"].strftime("%H:%M")} - {row["End"].strftime("%H:%M")})'
    
    rect = Rectangle(xy=(0, start), width=1, height=duration)
    ax.annotate(
        text=label, xy=(0.5, start+duration/2), 
        ha='center', va='center', weight='bold', size=16
    )
    boxes.append(rect)

# Set up and draw the boxes
pc = PatchCollection(
    boxes, facecolor='#eb6123', alpha=1, edgecolor='k', zorder=2, lw=2
)
ax.add_collection(pc)

# Set up hourly labels for y axis
ax.yaxis.set_major_formatter(
    mtick.FuncFormatter(lambda x, pos: f'{int(x/60):02.0f}:{x%60:02.0f}')
)
ax.yaxis.set_major_locator(mtick.MultipleLocator(60))

# Gridline faff etc
ax.set_ylim(60*11-1, 60*22.5)
ax.set_xlim(-0.05, 1.05)
ax.grid(axis='y', ls='--', zorder=1, lw=2, alpha=.75)
ax.tick_params(
    axis='x', which='both',
    bottom=False, top=False, labelbottom=False
)
ax.tick_params(which='both', length=0)

for side in ('left', 'right', 'top', 'bottom'):
    ax.spines[side].set_visible(False)


# Use spooky font for the title    
font = fm.FontProperties(fname='GROOVYGH.TTF')
plt.suptitle('Spooky Island', weight='bold', size=60, fontproperties=font)

# Time top to bottom
ax.invert_yaxis()

# Add in site reference
source_text = (
    'Source: ruszkow.ski/graphs/2020-11-03-halloween-timetable'
)
ax.annotate(
    text=source_text, 
    xy=(-25, -15), xycoords=('axes points', 'axes points'), 
    ha='left', va='bottom', size='small'
)

# Save out
plt.savefig('Spooky Island Timetable.png', bbox_inches='tight')
