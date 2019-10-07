#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
sns.set_context('talk')


DEST_DIR = 'Yearly Totals'
if not os.path.isdir(DEST_DIR):
    os.mkdir(DEST_DIR)

SOURCE = (
    'Source (as of 2019-10-07): '
    'playsmartplaysafe.com/newsroom/reports/injury-data/'
)

frames = pd.read_excel('InjuryData.xlsx', sheet_name=None, header=[0, 1], index_col=0)
print(frames)

for injury, data in frames.items():
    totals = data.xs('Preseason + Regular Season', level=0, axis=1)\
                 .drop('Total', axis=1)

    fig, ax = plt.subplots(figsize=(16, 6))

    totals.plot.bar(
        stacked=True, color=['#013369', '#D50A0A'], ax=ax, zorder=2, width=.75,
        legend=False
    )
    for side in ('top', 'bottom', 'left', 'right'):
        ax.spines[side].set_visible(False)

    ax.grid(axis='y', ls='--', c='gainsboro', alpha=.5, zorder=1)

    ax.tick_params(which='both', length=0)
    ax.tick_params(axis='y', which='major', pad=3, colors='gainsboro')
    ax.tick_params(axis='x', which='major', pad=10)
    plt.xticks(rotation=0)
    plt.legend(bbox_to_anchor=(0.5, -0.1), loc='upper center', ncol=2)

    for p in ax.patches:
        size = int(p.get_height())
        text = ax.annotate(
            s=f'{size}',
            xy=(p.get_x() + p.get_width() / 2, p.get_y() + size / 2),
            ha='center', va='center', color='white', weight='bold'
        )

    mid = (fig.subplotpars.right + fig.subplotpars.left) / 2

    plt.suptitle(
        f'{injury} per Year (including preseason)', weight='bold', x=mid
    )
    plt.title(SOURCE, fontsize='xx-small')
    plt.savefig(os.path.join(DEST_DIR, f'{injury}.png'), bbox_inches='tight')
    plt.close('all')
