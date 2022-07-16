#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 15/07/2022 8:59 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : Exp2.py
# @Software: PyCharm
# @Notes   :
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
sns.set(font_scale = 2)
import os
from matplotlib.gridspec import GridSpec
import numpy as np

root = './Exps/'

class AnalysisCost():

    def __init__(self, scenario, rate):
        self.root = 'D:\\OneDrive - University of Tennessee\\Scripts\\SYBModel\\'
        self.scenario = scenario
        self.rate = rate

        self.read_data()

    def read_data(self):
        self.Years = pd.read_csv(self.root + 'GCAM_full/20220421_gcam_production.csv')
        self.Years = self.Years.columns.values.tolist()[5:-1]  ## string

        self.data = pd.DataFrame()
        for year in self.Years:
            path = self.root + 'Exps/' + self.scenario + '/'
            data0 = pd.read_csv(path + 'all_rates_'+ year + '.csv').query('Rates == @self.rate')
            self.data = pd.concat([self.data, data0])
            self.data['Inventory'] = self.data['Total_production'] - self.data['Quantity_X_Facility'] - self.data['Quantity_X_Country_Stream'] - self.data['Quantity_X_Country_Rail']

    def create(self, ax, legs, axl=None, leg=False):
        data0 = self.data.query('Rates == @self.rate')
        data0 = data0[['Year', 'Inventory', 'Quantity_X_Facility', 'Quantity_X_Country_Rail', 'Quantity_X_Country_Stream']].set_index(
            'Year', drop=True)
        data0.loc['total'] = data0.apply(lambda x: x.sum())
        # data0.loc['perct'] = data0.loc['total'] / data0.loc['total'].sum()

        labels = ['Inventory', 'Local facility', 'Shuttle elevator', 'River elevator']
        colors = ['#287271', '#8ab07d', '#e9c46b', '#f3a261']

        wedges, tex, texts = ax.pie(data0.loc['total'],
               autopct=lambda p: f'{p:.0f}%' if p != 0 else '',
               textprops={'fontsize': 22, 'fontweight': 'bold'},
               pctdistance=0.7,
               colors=colors,
               startangle=90,
               # shadow = True,
               wedgeprops=dict(width=0.7),
               radius=1.3
               )

        # wedges, texts = ax.pie(data0.loc['total'], wedgeprops=dict(width=0.5), startangle=-40, colors=colors)
        # bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
        # kw = dict(arrowprops=dict(arrowstyle="-"),
        #           bbox=bbox_props, zorder=0, va="center")
        #
        # for i, p in enumerate(wedges):
        #     ang = (p.theta2 - p.theta1) / 2. + p.theta1
        #     y = np.sin(np.deg2rad(ang))
        #     x = np.cos(np.deg2rad(ang))
        #     horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        #     connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        #     kw["arrowprops"].update({"connectionstyle": connectionstyle})
        #     ax.annotate(labels[i], xy=(x, y), xytext=(1.35 * np.sign(x), 1.4 * y),
        #                 horizontalalignment=horizontalalignment, **kw)


        ax.annotate(legs, (-0.3, -0.2), color='#2a4652' ,fontweight='bold')
        # ax.set_title(legs, pad=30)

        if leg == True:
            axl.legend(handles=wedges, labels=labels,
                      loc="center",
                      ncol=4,
                      facecolor='#faf8ed',
                      edgecolor='#faf8ed',
                      # fontsize=12,
                      # labelcolor='#2a4652',
                      )
            axl.set_axis_off()  # hide the axis

    def __del__(self):
        pass

if __name__ == '__main__':
    scenario = 'SSP2'
    # rates = ['1_1_1_1', '1_10_1_1', '1_1_0.5_1', '1_1_1_10', '10_1_1_1']
    # legs = ['S0', 'S1', 'S2', 'S3', 'S4']


    fig = plt.figure(figsize=(8, 8), facecolor='#faf8ed')
    # fig.tight_layout()
    gs = GridSpec(2, 3, hspace=0.0, wspace=0.2, width_ratios=[1, 1, 1])
    # gs.update(left=0.55, right=0.98, hspace=0.05)

    ax = plt.subplot(gs[0, 0])
    AC = AnalysisCost(scenario, '1_10_1_1')
    AC.create(ax, 'S1')

    ax = plt.subplot(gs[0, 2])
    AC = AnalysisCost(scenario, '1_1_0.5_1')
    AC.create(ax, 'S2')

    ax = plt.subplot(gs[:, 1])
    AC = AnalysisCost(scenario, '1_1_1_1')
    AC.create(ax, 'S0', True)

    ax = plt.subplot(gs[1, 0])
    AC = AnalysisCost(scenario, '1_1_1_10')
    AC.create(ax, 'S3')

    ax = plt.subplot(gs[1, 2])
    AC = AnalysisCost(scenario, '10_1_1_1')
    AC.create(ax, 'S4')

    plt.show()