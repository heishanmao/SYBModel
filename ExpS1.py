#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 22/07/2022 6:54 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : ExpS1.py
# @Software: PyCharm
# @Notes   :
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style="white", palette='pastel')
sns.set(font_scale = 1)
import os
import numpy as np
from matplotlib.gridspec import GridSpec

#Rates = sameRate()
Rates = ['1_1_1_1','1_10_1_1','1_1_0.5_1','1_1_1_10','10_1_1_1']
Legs = ['S0','S1','S2','S3','S4']
Scenarios = ['SSP1', 'SSP2', 'SSP3', 'SSP4', 'SSP5']
Years = ['2020', '2025', '2030', '2035', '2040', '2045', '2050']
#Rates = ['5_5_5_5','5_10_5_5','5_5_0.5_5','5_5_5_10','10_5_5_5']
root = './Exps-ssps2/'

data = pd.DataFrame()
for scenario in Scenarios:
    for year in Years:
        path = root + scenario + '/'
        data0 = pd.read_csv(path + 'all_rates_'+ year + '.csv').query('Rates == @Rates')
        data0['Exported(%)'] =  data0['Quantity_Z_Export_Import'] / data0['Total_production']
        data = pd.concat([data,data0])
a=1
########################################################################################################################
# # Plotting
# fig = plt.figure(figsize=(15, 15), facecolor='#faf8ed', constrained_layout=True)
# gs = fig.add_gridspec(5, 3)
#
# for r, rate in enumerate(Rates):
#     # row = r // 2
#     # col = r % 2
#     ax = fig.add_subplot(gs[r, 0])
#     for scenario in Scenarios:
#         data1 = data.query('Rates == @rate and Scenario == @scenario')
#         ax.plot(data1['Year'], data1['OBJ_Values'], label=scenario)
#         #ax.legend(loc='best')
#
#     ax = fig.add_subplot(gs[r, 1])
#     for scenario in Scenarios:
#         data1 = data.query('Rates == @rate and Scenario == @scenario')
#         ax.plot(data1['Year'], data1['Revenue_Total'], label=scenario)
#         #ax.legend(loc='best')
#
#     ax = fig.add_subplot(gs[r, 2])
#     for scenario in Scenarios:
#         data1 = data.query('Rates == @rate and Scenario == @scenario')
#         ax.plot(data1['Year'], data1['Cost_Total'], label=scenario)
#         ax.legend(loc='best')
#
# plt.show()

########################################################################################################################

# fig = plt.figure(figsize=(15, 15), facecolor='#faf8ed', constrained_layout=True)
# gs = fig.add_gridspec(5, 3)
#
# for r, scenario in enumerate(Scenarios):
#     # row = r // 2
#     # col = r % 2
#     ax = fig.add_subplot(gs[r, 0])
#     for rate in Rates:
#         data1 = data.query('Rates == @rate and Scenario == @scenario')
#         ax.plot(data1['Year'], data1['OBJ_Values'], label=rate)
#         #ax.legend(loc='best')
#
#     ax = fig.add_subplot(gs[r, 1])
#     for rate in Rates:
#         data1 = data.query('Rates == @rate and Scenario == @scenario')
#         ax.plot(data1['Year'], data1['Revenue_Total'], label=rate)
#         #ax.legend(loc='best')
#
#     ax = fig.add_subplot(gs[r, 2])
#     for rate in Rates:
#         data1 = data.query('Rates == @rate and Scenario == @scenario')
#         ax.plot(data1['Year'], data1['Cost_Total'], label=rate)
#         ax.legend(loc='best')
#
# plt.show()

########################################################################################################################
# fig = plt.figure(figsize=(15, 15), constrained_layout=True)
# gs = fig.add_gridspec(6, 5)
#
# rate = Rates[2]
# for i in range(30):
#     row = i // 5
#     col = i % 5
#     ax = fig.add_subplot(gs[row, col])
#     for scenario in Scenarios:
#         data1 = data.query('Scenario == @scenario and Rates == @rate')
#         ax.plot(data1['Year'], data1.iloc[:, i+3], label=scenario)
#         ax.legend(loc='best')
#         ax.set_title(data1.iloc[:, i+3].name)
#         #ax.set_facecolor('#faf8ed')
#         ax.grid(False)

# plt.show()
# fig.savefig('./Figs/Fig_Sclimate.pdf', dpi=600, bbox_inches="tight")

########################################################################################################################

ssp4 = data.query('Scenario == "SSP3"')['Exported(%)'].mean()
ssp = ['SSP1', 'SSP2', 'SSP3', 'SSP5']
ssps = data.query('Scenario in @ssp')['Exported(%)'].mean()

a = ssp4/ssps
a=1