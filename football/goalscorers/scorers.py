#!/usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import pandas as pd
from pywaffle import Waffle
import matplotlib.font_manager as font_manager


# Update font list
# font_manager._rebuild()

# plt.rcParams['font.family'] = 'sans-serif'
# plt.rcParams['font.sans-serif'] = 'Mexcellent'
plt.rcParams['savefig.facecolor'] = 'k'
plt.rcParams['text.color'] = 'w'

df = pd.read_csv('goalscorers.csv')

mex_3d = font_manager.FontProperties(
    fname='mexcellent_3D.otf', size=34
)
mex_reg = font_manager.FontProperties(
    fname='mexcellent_rg.otf', size=12
)

scorers_dict = dict()
num_players = 8

for i, scorer in df.head(num_players).iterrows():
    # scorers_dict[(num_players, 1, i+1)] = dict(
    scorers_dict[num_players*100 + 10 + i+1] = dict(
        {
            'values': [scorer['Goals']],
            'title': {
                'label': f'{scorer["Name"]} - {scorer["Goals"]} Goals ({scorer["Career"]})',
                'loc': 'left',
                'fontproperties': mex_reg
            }
        }
    )

fig = plt.figure(
    FigureClass=Waffle,
    plots=scorers_dict,
    rows=5,
    colors='w',
    figsize=(11.2, 7.5),
    icons='futbol',
    icon_size=6,
    facecolor='k',
)

plt.suptitle(
    'All-Time Top Scorers in\nEnglish League Football',
    ha='center', fontproperties=mex_3d,
    x=(fig.subplotpars.left+fig.subplotpars.right)/2, y=1.15
)

SOURCE = 'Source: http://www.rsssf.com/tablese/engtops-allt.html, as of 2019-10-29'
plt.text(
    fig.subplotpars.left*.55, 0, SOURCE,
    fontsize='x-small', style='italic', ha='left', va='baseline',
    alpha=.8,
    transform=plt.gcf().transFigure
)

plt.subplots_adjust(bottom=0.02)
plt.savefig('england-scorers.png', bbox_inches='tight', dpi=150)
