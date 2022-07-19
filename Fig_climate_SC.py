#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 16/07/2022 9:53 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : Fig_climate_SC.py
# @Software: PyCharm
# @Notes   :

import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import seaborn as sns
sns.color_palette()

def merge_all():
    pjt = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
    data = pd.DataFrame()
    for snr in ['SSP1', 'SSP2', 'SSP3', 'SSP4', 'SSP5']:
        for yr in ['2020', '2025', '2030', '2035', '2040', '2045', '2050']:
            data0 = pd.read_csv(os.path.join(pjt, 'Exps-ssps2', '{}/all_rates_{}.csv'.format(snr, yr)))
            data = pd.concat([data, data0])

    data.to_csv(os.path.join(pjt, 'Exps-ssps2', 'all_merged.csv'), index=False)



class climateSC():
    def __init__(self, years, scenario, filename):
        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
        self.subregions = ['MissppRN', 'OhioR', 'MissouriR', 'NelsonR', 'GreatLakes', 'ArkWhtRedR']
        self.scenario = scenario
        self.years = years
        self.filename = filename

        self.data = pd.read_csv(self.root + '/GCAM_full/' + self.filename + '.csv').query('subregion in @self.subregions and scenario in @self.scenario')
        self.data = self.data.loc[:,self.years[0]:self.years[-1]].sum(axis=0).to_numpy()


class GRBResults():
    def __init__(self, rate, scenario):
        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
        self.GRB = pd.read_csv(os.path.join(self.root, 'Exps-ssps', 'all_merged.csv'))
        self.Years = ['2020', '2025', '2030', '2035', '2040', '2045', '2050']
        self.scenario = scenario
        self.rate = rate

        #self.GRB.query('Rates == @self.rate and Scenario == @self.label', inplace=True)

        self.Y = self.GRB.query('Rates == @self.rate and Scenario == @self.scenario')



def plot(ax, x, y, label, title):

    ax.plot(x, y, label=label)
    #ax.legend(loc='best')
    #ax.set_title(title, fontweight='bold')
    ax.set_xlabel(title, fontweight='bold', fontsize=12)
    ax.set_facecolor('#faf8ed')

def plot_b(ax, x, y, label, title):

    if label == 'SSP4':
        y = y /1e4

    ax.bar(x, y, label=label)
    ax.legend(loc='best')
    ax.set_title(title)

if __name__=="__main__":

    #merge_all()
    #
    Scenarios = ['SSP1', 'SSP2', 'SSP3', 'SSP4', 'SSP5']
    # Years = ['1990', '2005', '2010', '2015', '2020', '2025', '2030', '2035', '2040', '2045', '2050', '2055', '2060', '2065', '2070', '2075', '2080', '2085', '2090', '2095', '2100']
    Years = ['2020', '2025', '2030', '2035', '2040', '2045', '2050']
    title = ['(a). Irrigation', '(b). Fertilizer', '(c). GHG Emissions', '(d). Land', '(e). The global mean temperature','(f). Total production', '(g). Operation cost']

    file_list = ['2_water.csv', '2_N2.csv', '2_emission.csv', '20220421_GCAM_totalarea.csv']

    #rates = ['1_10_1_1', '1_1_0.5_1', '1_1_1_1', '1_1_1_10', '10_1_1_1']
    rates = '1_1_1_1'
    rate_legs = ['S1', 'S2', 'S0', 'S3', 'S4']

    fig = plt.figure(figsize=(10, 10), facecolor='#faf8ed', constrained_layout=True)
    gs = fig.add_gridspec(4, 2)

    for i, f in enumerate(file_list):
        ax = fig.add_subplot(gs[i, 0])
        for s, scenario in enumerate(Scenarios):
            CSC = climateSC(Years, scenario, f[:-4])
            plot(ax, Years, CSC.data, label=scenario, title=title[i])

    ######################################################################################################################
    ax = fig.add_subplot(gs[0:2, 1])
    ax.set_facecolor('#faf8ed')
    temp = pd.read_excel(os.path.join(os.path.dirname(__file__), 'GCAM_full', 'global_mean_temperature.xlsx'))

    temp = temp.query('scenario in @Scenarios')[[2020,2025,2030,2035,2040,2045,2050]]

    ax = temp.T.plot(kind ='line', ax=ax, legend=False)
    ax.title.set_fontweight('bold')
    ax.set_xlabel(title[4], fontweight='bold', fontsize=12)
    ax.legend(Scenarios, loc='best', facecolor='#faf8ed')

    # ######################################################################################################################
    #
    # ax = fig.add_subplot(gs[2, 1])
    # res = pd.DataFrame(index = Years)
    # for j, sc in enumerate(Scenarios):
    #     GRB = GRBResults(rates, sc)
    #     Y = GRB.Y['Revenue_Total'].to_numpy()
    #     res[sc] = Y
    #
    # res.plot(kind='line', ax=ax, legend=True, title=rates)
    # #
    # ax = fig.add_subplot(gs[3, 1])
    # res = pd.DataFrame(index = Years)
    # for j, sc in  enumerate(Scenarios):
    #     GRB = GRBResults(rates, sc)
    #     Y = GRB.Y['Cost_Total'].to_numpy()
    #     res[sc] = Y
    #
    # res.plot(kind='line', ax=ax, legend=True, title=rates)
    # #
    # ax = fig.add_subplot(gs[4, 1])
    # res = pd.DataFrame(index = Years)
    # for j, sc in  enumerate(Scenarios):
    #     GRB = GRBResults(rates, sc)
    #     Y = GRB.Y['Cost_Total'].to_numpy()
    #     res[sc] = Y
    #
    # res.plot(kind='line', ax=ax, legend=True, title=rates)
    ######################################################################################################################
    f = '20220421_gcam_production.csv'
    ax = fig.add_subplot(gs[2, 1])
    for s, scenario in enumerate(Scenarios):
        CSC = climateSC(Years, scenario, f[:-4])
        plot(ax, Years, CSC.data, label=scenario, title=title[5])


    ######################################################################################################################
    rates = ['1_10_1_1', '1_1_0.5_1', '1_1_1_1', '1_1_1_10', '10_1_1_1']
    sc = 'SSP4'

    ax = fig.add_subplot(gs[3, 1])
    res = pd.DataFrame(index = Years)
    for j, rate in enumerate(rates):
        GRB = GRBResults(rate, sc)
        Y = GRB.Y['Cost_Total'].to_numpy()
        res[rate] = Y
    res.iloc[:, 3] = res.iloc[:, 3] / 3.7
    res.iloc[:, 4] = res.iloc[:, 4] / 1.9
    res.plot(kind='line', ax=ax, legend=False)
    ax.set_facecolor('#faf8ed')
    ax.set_xlabel(title[6], fontweight='bold', fontsize=12)
    #ax.title.set_fontweight('bold')

    plt.show()
    fig.savefig('./Figs/Fig_climate.pdf', dpi=600, bbox_inches="tight")

    ######################################################################################################################
    # Scenarios = ['SSP1', 'SSP2', 'SSP3', 'SSP4', 'SSP5']
    # # Years = ['1990', '2005', '2010', '2015', '2020', '2025', '2030', '2035', '2040', '2045', '2050', '2055', '2060', '2065', '2070', '2075', '2080', '2085', '2090', '2095', '2100']
    # Years = ['2020', '2025', '2030', '2035', '2040', '2045', '2050']
    # rates = ['1_10_1_1', '1_1_0.5_1', '1_1_1_1', '1_1_1_10', '10_1_1_1']
    # rate = '1_1_1_1'
    #
    # fig = plt.figure(figsize=(10, 10), facecolor='#faf8ed', constrained_layout=True)
    # gs = fig.add_gridspec(8, 4)
    #
    # for i in range(3,32):
    #     row = i // 4
    #     col = i % 4
    #     ax = fig.add_subplot(gs[row, col])
    #     res = pd.DataFrame(index = Years)
    #     for j, sc in enumerate(Scenarios):
    #         #if j != 3:
    #         GRB = GRBResults(rate, sc)
    #         Y = GRB.Y.iloc[:, i].to_numpy()
    #         res[sc] = Y
    #
    #     res.plot(kind='line', ax=ax, legend=False, title=GRB.Y.columns[i])
    #
    # plt.show()


    ######################################################################################################################
    # # Cost_Structor and revenue Structor
    # rate = '1_1_1_1'
    # Scenarios = ['SSP1', 'SSP2', 'SSP3', 'SSP4', 'SSP5']
    # Years = ['2020', '2025', '2030', '2035', '2040', '2045', '2050']
    #
    # fig = plt.figure(figsize=(10, 10), facecolor='#faf8ed', constrained_layout=True)
    # gs = fig.add_gridspec(5, 1)
    #
    # costs = ['Cost_Operation', 'Cost_Holding', 'Cost_Facility', 'Cost_Barges', 'Cost_Rails', 'Cost_BExport', 'Cost_SExport', 'Cost_Oceans']
    #
    # # ax = fig.add_subplot(gs[0, 0])
    # # res = pd.DataFrame(index=Years)
    #
    # b = []
    # for s, snr in enumerate(Scenarios):
    #     G = GRBResults(rate, snr)
    #     data = G.GRB.query('Rates == @rate and Scenario == @snr')[costs]
    #     Summary = data.sum(axis=1)
    #
    #     for i, c in enumerate(costs):
    #         data[c] = data[c] / Summary
    #
    #     data.reset_index(drop=True, inplace=True)
    #     #data['x'] = yer-2.5+(s+1)/2
    #     b.append(data)
    #
    # #ax = fig.add_subplot(gs[1, 0])
    # for i in range(len(Scenarios)):
    #     ax = fig.add_subplot(gs[i, 0])
    #     b[i].plot(kind='bar', stacked=True, ax=ax, legend=False, title='Costs')
    # plt.show()
    #
    # ax.bar(b[0][cost], bottom=b[0].iloc[:, j-1], label=cost)
    #
    #
    # a= 1
    #
    # y = b[0].loc[:, costs[i]]
    # ax.bar(Years, y, label=y .name)
    # plt.show()
    # a=1
    #
    # res[costs] = GRB.Y[costs].to_numpy()
    #
    # a=1

