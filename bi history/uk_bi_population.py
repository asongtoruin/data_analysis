from datetime import datetime
from pathlib import Path

import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image


CURRENT_DIR = Path(__file__).resolve().parent

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = 'Bariol Serif'
plt.rcParams['font.weight'] = 'regular'
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150

# Set up colour maps
flag_map = LinearSegmentedColormap.from_list(
    name='bi_flag', colors=['#D60270', '#9B4F96', '#0038A8'], N=256
)
pink_map = LinearSegmentedColormap.from_list(
    name='bi_pink', colors=['#000000', '#D60270', '#ffffff'], N=256
)

# Choose a dark pink variant for our text, and a light pink for our background
bg_color = pink_map(0.95)
sup_text_color = pink_map(0.1)

logo = Image.open(CURRENT_DIR / 'bh_logo.jfif')

SMALL_SIZE = 100
small_logo = logo.resize((SMALL_SIZE, SMALL_SIZE))


total_pop = pd.read_excel(
    CURRENT_DIR / 'sexualorientation2018final05032020124027.xls', 
    sheet_name=2, skiprows=3, header=[0,1], nrows=24
)
total_pop.columns = ['_'.join(c) for c in total_pop.columns]

total_pop.rename(
    columns={
        total_pop.columns[0]: 'Year', 
        total_pop.columns[1]: 'Reported Sexual Identity'
    }, 
    inplace=True
)

total_pop['Year'] = total_pop['Year'].ffill().astype(int)
# Population given in thousands
total_pop['Total Population'] = (
    total_pop['Male_Estimate'] + total_pop['Female_Estimate']
) * 1000

bi_pop = total_pop[total_pop['Reported Sexual Identity'].eq('Bisexual')]

age_pop = pd.read_excel(
    CURRENT_DIR / 'sexualorientation2018final05032020124027.xls', 
    sheet_name=3, skiprows=3, header=[0,1], nrows=24
)
age_pop.columns = ['_'.join(c) for c in age_pop.columns]

age_pop.rename(
    columns={
        age_pop.columns[0]: 'Year', age_pop.columns[1]: 'Reported Sexual Identity'}
    , 
    inplace=True
    )

age_pop['Year'] = age_pop['Year'].ffill().astype(int)

bi_ages = age_pop[age_pop['Reported Sexual Identity'].eq('Bisexual')]\
                 .melt(id_vars=['Year', 'Reported Sexual Identity'], 
                       var_name='Age Group', value_name='Population')

# Filter to just the population estimates
bi_ages = bi_ages[bi_ages['Age Group'].str.contains('Estimate')]

# Get just the age group out
bi_ages['Age Group'] = bi_ages['Age Group'].str.split('_', expand=True).loc[:,0]

# Again - population in thousands
bi_ages['Population'] *= 1000

# Get latest year
bi_latest = bi_ages[bi_ages['Year'].eq(bi_ages['Year'].max())]

# Add extra description to the first group
bi_latest['Age Group']  = bi_latest['Age Group'].replace({'16-24': '16-24 years old'})

output_folder = CURRENT_DIR / 'Graphs'
output_folder.mkdir(exist_ok=True)

# First, plot the yearly totals
fig, ax = plt.subplots(figsize=(8,8))

years = bi_pop['Year']
num_years = len(years)

props = np.arange(0, 1+1/num_years, 1/num_years)

population = bi_pop['Total Population']

rects = ax.bar(x=years, height=population, color=flag_map(props))

# Add labels
for year, r in zip(years, rects):
    bar_mid = r.get_x() + r.get_width()/2
    height = r.get_height()
    ax.annotate(
        s=year, xy=(bar_mid, 0), 
        ha='center', va='baseline', 
        xytext=(0, 10), textcoords='offset points', 
        c='white', weight='bold', size=22
    )

    ax.annotate(
        s=f'{height/1000:.0f}k', xy=(bar_mid, height), 
        ha='center', va='baseline', 
        xytext=(0, 10), textcoords='offset points', 
        c=r.get_facecolor(), weight='bold', size=22
    )

ax.axis('off')
ax.margins(x=0)

fig.set_facecolor(bg_color)
fig.subplots_adjust(left=0.05, right=0.95, bottom=0.1, top=0.75)

fig.suptitle(
    'Estimated UK\nBisexual Population', size=45, c=sup_text_color, 
    style='italic', y=0.95, va='top', fontname='Salome'
)

source_text='''Source: ons.gov.uk/peoplepopulationandcommunity/culturalidentity/sexuality/datasets/sexualidentityuk
Released 2020-03-06, retrieved 2020-07-01. Estimates considered "reasonably precise".'''

ax.annotate(
    s=source_text, 
    xy=(0, .05), xycoords=('axes points', 'figure fraction'), 
    ha='left', va='bottom',
    size=10, c=sup_text_color, weight='bold'
)

# Add in the logo
fig.figimage(small_logo, xo=0, yo=fig.bbox.ymax-SMALL_SIZE)

plt.savefig(output_folder / 'total population.png', dpi=150, facecolor=bg_color)

# Now do our population by year
fig, ax = plt.subplots(figsize=(8,8))

age_groups = bi_latest['Age Group']
num_years = len(years)

props = np.arange(0, 1+1/num_years, 1/num_years)

population = bi_latest['Population']

rects = ax.barh(y=age_groups, width=population, color=flag_map(props))

for grp, r in zip(age_groups, rects):
    bar_mid = r.get_y() + r.get_height()/2
    width = r.get_width()
    ax.annotate(
        s=grp, xy=(0, bar_mid), 
        ha='left', va='center', 
        xytext=(10, 0), textcoords='offset points', 
        c='white', weight='bold', size=20
    )

    ax.annotate(
            s=f'{width/1000:.0f}k', xy=(width, bar_mid), 
            ha='left', va='center', 
            xytext=(10, 0), textcoords='offset points', 
            c=r.get_facecolor(), weight='bold', size=20
        )

ax.axis('off')
ax.margins(x=0, y=0)

fig.set_facecolor(bg_color)
fig.subplots_adjust(left=0.05, right=0.85, bottom=0.1, top=0.75)

fig.suptitle('2018 Estimated UK\nBisexual Population', fontname='Salome', size=45, c=sup_text_color, style='italic', y=0.95, va='top')


source_text='''Source: ons.gov.uk/peoplepopulationandcommunity/culturalidentity/sexuality/datasets/sexualidentityuk
Released 2020-03-06, retrieved 2020-07-01. Estimates considered "acceptable" or higher'''

ax.annotate(
    s=source_text, 
    xy=(0, .05), xycoords=('axes points', 'figure fraction'), ha='left', va='bottom',
    size=10, c=sup_text_color, weight='bold'
)

ax.invert_yaxis()

fig.figimage(small_logo, xo=0, yo=fig.bbox.ymax-SMALL_SIZE)

plt.savefig(output_folder / f'2018 age groups.png', dpi=150, facecolor=bg_color)
