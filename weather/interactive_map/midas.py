#!/usr/bin/env python
# -*- coding: utf-8 -*-
from calendar import month_abbr

import matplotlib.patheffects as mpe
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
sns.set(
    style='white', context='talk',
    rc={'axes.facecolor': (0, 0, 0, 0)}
)


class MidasData:
    def __init__(self, csv_file):
        self.data = pd.read_csv(
            csv_file, skiprows=280, parse_dates=['ob_time'],
            dayfirst=True, skipfooter=1
        )

        self.data['Hour'] = self.data['ob_time'].dt.hour

        # Get the month name and average temperature
        self.data['Month'] = pd.Categorical(
            self.data['ob_time'].dt.strftime('%b'), categories=month_abbr[1:],
            ordered=True
        )

    def monthly_ridge_plot(self, hue, value, title, hue_label, x_label,
                           attribution, output_path, value_format='{}',
                           palette='plasma', background_colour='whitesmoke',
                           hspace=-.4, bottom_space=.12,
                           facet_params=None, shape_params=None,
                           outline_params=None):

        _fp = facet_params.copy() if facet_params else dict()
        _sp = shape_params.copy() if shape_params else dict()
        _op = outline_params.copy() if outline_params else dict()

        g = sns.FacetGrid(
            self.data, row='Month', hue=hue, palette=palette, **_fp
        )

        g.map(
            sns.kdeplot, value, clip_on=False, shade=True, alpha=1, lw=0, **_sp
        )
        if 'lw' not in _op.keys():
            _op['lw'] = 3

        g.map(
            sns.kdeplot, value, clip_on=False, color=background_colour, **_op
        )

        # Add the baseline lines
        g.map(plt.axhline, y=0, lw=_op['lw'], clip_on=False)

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
                1, .2, value_format.format(float(label)), fontweight='bold',
                color=color, ha='right', va='center', transform=ax.transAxes,
                path_effects=[mpe.withStroke(linewidth=5, foreground='white')]
            )

        g.map(label, 'Month')

        # Set the subplots to overlap and add space for the attribution
        g.fig.subplots_adjust(hspace=hspace, bottom=bottom_space)

        # Remove axes details that don't play well with overlap
        g.set_titles('')
        g.set(yticks=[])
        g.despine(bottom=True, left=True)

        mid = (plt.gcf().subplotpars.right + plt.gcf().subplotpars.left) / 2

        plt.suptitle(
            title, fontweight='bold',
            va='center', x=mid
        )

        # Add the headers for the labels
        first_ax = g.axes.flatten()[0]
        last_ax = g.axes.flatten()[-1]

        first_ax.text(
            0, .6, 'Month', fontweight='bold', color='k',
            ha='left', va='baseline', transform=first_ax.transAxes,
        )
        first_ax.text(
            1, .6, hue_label, fontweight='bold', color='k',
            ha='right', va='baseline', transform=first_ax.transAxes,
        )

        # Add an x label
        last_ax.set_xlabel(x_label)

        plt.text(
            plt.gcf().subplotpars.left, 0, attribution,
            fontsize='xx-small', style='italic', ha='left', va='baseline',
            alpha=.5,
            transform=plt.gcf().transFigure
        )

        # remember to set facecolor so it actually saves it out
        plt.savefig(
            output_path, bbox_inches='tight', facecolor=background_colour
        )

        plt.close()
