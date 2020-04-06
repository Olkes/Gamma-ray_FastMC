import random
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import pyplot as pp
from scipy.stats import chisquare
import os
import re
import fnmatch
import pandas as pd

class style:
    def __init__(self, **kwargs):
        # parameters for plot style
        self.fig_width= kwargs.pop('figure_width',10)
        self.SPINE_COLOR = kwargs.pop('spine_color','grey')
        return

    def latexify(self,fig_height=None, columns=1):
        """Set up matplotlib's RC params for LaTeX plotting.
        Call this before plotting a figure.

        Parameters
        ----------
        fig_width : float, optional, inches
        fig_height : float,  optional, inches
        columns : {1, 2}
        """

        # code adapted from http://www.scipy.org/Cookbook/Matplotlib/LaTeX_Examples

        # Width and max height in inches for IEEE journals taken from
        # computer.org/cms/Computer.org/Journal%20templates/transactions_art_guide.pdf

        assert (columns in [1, 2])

        if self.fig_width is None:
            self.fig_width = 3.39 if columns == 1 else 6.9  # width in inches

        if fig_height is None:
            golden_mean = (np.sqrt(5) - 1.0) / 2.0  # Aesthetic ratio
            fig_height = self.fig_width * golden_mean  # height in inches

        MAX_HEIGHT_INCHES = 80.0
        if fig_height > MAX_HEIGHT_INCHES:
            print("WARNING: fig_height too large:" + fig_height +
                  "so will reduce to" + MAX_HEIGHT_INCHES + "inches.")
            fig_height = MAX_HEIGHT_INCHES

        params = {'backend': 'ps',
                  # 'text.latex.preamble': ['\usepackage{gensymb}'],
                  'axes.labelsize': 25,  # fontsize for x and y labels (was 10)
                  'axes.titlesize': 25,
                  'font.size': 25,  # was 10
                  'legend.fontsize': 25,  # was 10
                  'xtick.labelsize': 20,
                  'ytick.labelsize': 20,
                  'text.usetex': True,
                  'figure.figsize': [self.fig_width, fig_height],
                  'font.family': 'serif',
                  'errorbar.capsize': 3

        }

        matplotlib.rcParams.update(params)
        #matplotlib.style.use('classic')


    def format_axes(self,ax):
        for spine in ['top', 'right']:
            ax.spines[spine].set_color(self.SPINE_COLOR)
            ax.spines[spine].set_linewidth(0.8)

        for spine in ['left', 'bottom']:
            ax.spines[spine].set_color(self.SPINE_COLOR)
            ax.spines[spine].set_linewidth(0.8)

        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')

        for axis in [ax.xaxis, ax.yaxis]:
            axis.set_tick_params(direction='in', which='both', color=self.SPINE_COLOR)

        return ax

    def reorderLegend(self,ax=None, order=None, unique=False):
        if ax is None: ax = plt.gca()
        handles, labels = ax.get_legend_handles_labels()
        labels, handles = zip(
            *sorted(zip(labels, handles), key=lambda t: t[0]))  # sort both labels and handles by labels
        if order is not None:  # Sort according to a given list (not necessarily complete)
            keys = dict(zip(order, range(len(order))))
            labels, handles = zip(*sorted(zip(labels, handles), key=lambda t, keys=keys: keys.get(t[0], np.inf)))
        if unique:  labels, handles = zip(
            *unique_everseen(zip(labels, handles), key=labels))  # Keep only the first of each handle
        ax.legend(handles, labels,frameon=False)
        return (handles, labels)

    def unique_everseen(self,seq, key=None):
        seen = set()
        seen_add = seen.add
        return [x for x, k in zip(seq, key) if not (k in seen or seen_add(k))]