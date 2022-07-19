#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 16/07/2022 3:17 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : Fig_climate_cost_anaylisis.py
# @Software: PyCharm
# @Notes   :

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import GCAM_full.GCAM_plot as Gplot
from matplotlib.gridspec import GridSpec

from matplotlib.colors import ListedColormap



if __name__ == "__main__":
    SMALL_SIZE = 11
    MEDIUM_SIZE = 11
    BIGGER_SIZE = 11

    plt.rc('font', size=SMALL_SIZE)  # controls default text sizes
    plt.rc('axes', titlesize=SMALL_SIZE)  # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)  # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

    scenario = 'SSP2'
    year = '2030'
    Rates = ['1_1_1_1', '1_10_1_1', '1_1_0.5_1', '1_1_1_10', '10_1_1_1']


    fig = plt.figure(figsize=(10, 10), facecolor='#faf8ed', constrained_layout=True)
    #fig.tight_layout()
    # gs = fig.add_gridspec(5, 2, height_ratios=(5,5), wspace=0.05, hspace=1)
    gs = fig.add_gridspec(5, 5)

    # gs0 = gs[0, 0].subgridspec(2, 1)
    # gs1 = gs[1, 0].subgridspec(2, 2)
    # gs2 = gs[2, 0].subgridspec(2, 2)
    # gs3 = gs[3, 0].subgridspec(2, 2)
    # gs4 = gs[4, 0].subgridspec(2, 2)

    ######################################################################################################################
    file_list = ['2_water.csv', '2_N2.csv', '2_emission.csv', '20220421_gcam_leafarea.csv', '20220421_gcam_production.csv']
    title = ['Water', 'Fertilizer', 'Emissions', 'Land', 'Production']
    colors =[
        ['#f0f9e8', '#ccebc5', '#a8ddb5', '#7bccc4', '#43a2ca', '#0868ac'],
        ['#feebe2', '#fcc5c0', '#fa9fb5', '#f768a1', '#c51b8a', '#7a0177'],
        ['#f6e8c3', '#dfc27d', '#d8b365', '#bf812d', '#a6611a', '#8c510a'],
        ['#ffffcc', '#d9f0a3', '#addd8e', '#78c679', '#31a354', '#006837'],
        ['#ffffb2', '#fed976', '#feb24c', '#fd8d3c', '#f03b20', '#bd0026'],
        ['#f0f9e8', '#ccebc5', '#a8ddb5', '#7bccc4', '#43a2ca', '#0868ac'],
    ]


    for i, f in enumerate(file_list):
        for j, scenario in enumerate(['SSP1', 'SSP2', 'SSP3', 'SSP4', 'SSP5']):
            if f == '2_water.csv':
                mgt_list = ['IRR']
            else:
                mgt_list = ['IRR', 'RFD']

            for m, mgt in enumerate(mgt_list):
                lev_list = ['hi', 'lo']
                for l, lev in enumerate(lev_list):
                    sub_gs = gs[i, j].subgridspec(len(lev_list), len(mgt_list))
                    ax = fig.add_subplot(sub_gs[l, m])

                    GCAM = Gplot.plot_map(f, scenario, year)
                    GCAM.create_single(ax, mgt, lev, cmap=ListedColormap(sns.color_palette(colors[i])))


    fig.show()




