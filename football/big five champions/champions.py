from datetime import datetime
from pathlib import Path
import re
from urllib import request

from bs4 import BeautifulSoup
from matplotlib.patches import FancyBboxPatch
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
from PIL import Image
from PIL.ImageOps import colorize, grayscale


plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = 'Geomanist'
plt.rcParams['font.weight'] = 'regular'


def recolour_badge(team_name, black, white, base_folder=Path('Badges')):
    img_path = base_folder / f'{team_name}.png'
    if img_path.is_file():
        img = Image.open(img_path).convert('RGBA')
        r, g, b, a = img.split()

        grey = grayscale(img)

        res = colorize(grey, black, white)
        res.putalpha(a)

        return res


bg_col = '#343633'
colours = ['#f15025', '#ffc01e', '#6f8ab7', '#93e1d8', '#8E5572']


path_lookups = {
    'England': 'eng',
    'France': 'fran',
    'Germany': 'duit',
    'Italy': 'ital',
    'Spain': 'span',
}

colour_lookup = {c: col for c, col in zip(path_lookups.keys(), colours)}

patt = re.compile(
    '^(?P<Season>[\d\/]+)[\s\-\*]+(?:[DQT]\s)?(?P<Team>[A-Za-z][A-Za-z\s\.\-üéñ]+)'
)

results = []

for country, code in path_lookups.items():
    colour = colour_lookup[country]
    resp = request.urlopen(fr'http://www.rsssf.com/tables{code[0]}/{code}champ.html')
    soup = BeautifulSoup(resp.read(), features='html.parser')
    for section in soup.find_all('pre'):
        for line in section.text.splitlines():
            for match in patt.finditer(line):
                team_dict = match.groupdict()
                team_dict['Country'] = country
                team_dict['Colour'] = colour
                results.append(team_dict)
                break

df = pd.DataFrame.from_records(results)

# We get some extra lines accidentally. Filter them out
df = df[df['Season'].str.len().eq(4) | df['Season'].str.contains('/')]

# Make sure we have consistent marking of seasons
df['Season'] = np.where(
    df['Season'].str.contains('/'),
    df['Season'].str.split('/', expand=True)[0].astype(int) + 1,
    df['Season']
).astype(int)

df['Team'] = df['Team'].replace(
    {'FC': '', 'CF': '', 'Football Club': '', 'Association Sportive de': 'AS'}, 
    regex=True
)
df['Team'] = df['Team'].str.strip()
df['Team'] = df['Team'].replace(
    {'Internazionale': 'Inter Milan', 'Milan AC': 'AC Milan', 'Juventus': 'Juventus *'}
)


recent = df[df['Season'].ge(2000)]

counts = recent.groupby(['Country', 'Colour', 'Team'], as_index=False)\
               .agg({'Season': 'count'})\
               .rename(columns={'Season': 'Titles Won'})\
               .sort_values(by='Titles Won', ascending=False)

# Get the most frequent champions            
top_dogs = counts.head(15)


fig, ax = plt.subplots(figsize=(8, 12), facecolor=bg_col)

# Get and plot values
teams = top_dogs['Team']
titles = top_dogs['Titles Won']
colours = top_dogs['Colour']

bars = ax.barh(y=teams, width=titles, color=colours, height=0.90, zorder=2)

# Flip the y-axis so our most frequent winner is at the top
ax.invert_yaxis()

ax.set_facecolor(bg_col)

fig.subplots_adjust(left=0.05, right=0.95, bottom=0.08, top=0.85)
ax.margins(x=0, y=0.02)

# Shift by 0.1 so we fit in our rounded bars
ax.set_xlim(0.1, titles.max()+0.1)

# Draw the canvas so we can do image placement
fig.canvas.draw()
r = fig.canvas.get_renderer()

# Scale for team badges
im_scale = 0.85

for name, bar, colour in zip(teams, bars, colours):
    bb = bar.get_bbox()
    color = bar.get_facecolor()
    ec = bar.get_edgecolor()
    
    # Redraw bars rounded. Add .1 to the values so we overlap grid lines
    p_bbox = FancyBboxPatch(
        (bb.xmin+0.1, bb.ymin), abs(bb.width), abs(bb.height),
        boxstyle='round,pad=0,rounding_size=0.4',
        ec=ec, fc=color, zorder=2
    )
    
    # Remove the old bar and add the new bar
    bar.remove()
    new_bar = ax.add_patch(p_bbox)
    
    ext = new_bar.get_window_extent(r)
    logo_size = int(ext.height * im_scale)
    x = ext.x0
    y = ext.y0
    
    offset = (ext.height * (1-im_scale)) / 2
    
    # Add in the recoloured badge
    logo = recolour_badge(name.replace(' *', ''), black=bg_col, white=colour)
    if logo:
        fig.figimage(
            logo.resize((logo_size, logo_size), Image.ANTIALIAS), 
            xo=x+offset, yo=y+offset
        )
    
    # Try adding in the team name, with offset 
    text = ax.annotate(
        s=name, 
        xy=(bar.get_x()+0.1, bar.get_y() + bar.get_height()/2), 
        xytext=(logo_size + 4 * offset, 0), textcoords='offset pixels',
        va='center', color=bg_col, size=20
    )
    
    # Check if text overlaps bar - if so, move the annotation
    fig.canvas.draw()
    patch = text.get_window_extent()
    if patch.x1 > ext.x1:
        text.remove()
        text = ax.annotate(
            s=name, 
            xy=(bar.get_x() + bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2), 
            xytext=(offset*2, 0), textcoords='offset pixels',
            va='center', color=colour, size=20
        )
    

# Neaten the axis
ax.set_frame_on(False)
ax.tick_params(length=0)
ax.grid(axis='x', ls=':', c='white', alpha=.15, zorder=1, lw=3, dash_capstyle='round')
ax.yaxis.set_ticklabels([])
ax.xaxis.set_ticklabels(ax.xaxis.get_ticklabels(), c='white', size=13, alpha=.3)

# Titles and labels
fig.suptitle('Millennials', size=50, c='white', style='oblique', y=0.97, va='top', weight='heavy')

ax.set_title(
    'Most frequent title-winners in Europe\'s "big five" leagues\nsince the turn of the millennium', 
    c='white', weight='regular', size=20, y=1.2, loc='left', pad=12
)

ax.annotate(
    s=(
        'Accurate up to 2019-2020 season. Data courtesy of rsssf.com, badges courtesy of api-football.com\n'
        '* 04/05 title not awarded and 05/06 title awarded to Inter Milan as a result of Calciopoli\n'
        'For more information, visit ruszkow.ski/graphs/2020-07-30-big-five-champions'
    ), 
    xy=(0, -0.09), xycoords='axes fraction',
    c='white', weight='regular', size=12
)

plt.savefig('champions.png', facecolor=bg_col)
