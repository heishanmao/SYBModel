#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 27/10/2021 8:07 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : Exp3_logistic_plot.py
# @Software: PyCharm
# @Notes   :Plot the results figs with matplotlib and GeoPandas
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib as mpl
import os
import seaborn as sns
sns.set(font_scale = 2)
from matplotlib.gridspec import GridSpec

class logistic_plot():
    def __init__(self, ax, scenario, year, rate, leg, legs=False):
        self.root = os.path.abspath('.')  # get the current directory 'D:\\OneDrive - University of Tennessee\\Scripts\\SYBModel'

        self._get_data(scenario, year, rate)

        self._load_loc()
        self._load_routes(scenario, year, rate)

        self._get_routes(ax, scenario, year, leg, legs)

    def _get_data(self,scenario, year, rate):
        self.data = pd.read_csv(self.root + '\Exps\\{}\\all_rates_{}.csv'.format(scenario,year)).query('Rates == @rate')
        self.total_production = self.data['Total_production'].values[0]
        self.china_demand = self.data['Demand'].values[0]

        self.OBJ_vaules = self.data['OBJ_vaules'].values[0]
        self.total_farmer = self.data['Cost_Farmers'].values[0]
        self.total_barge = self.data['Cost_Barges'].values[0]
        self.total_rail = self.data['Cost_Rails'].values[0]
        self.total_ocaen = self.data['Cost_Oceans'].values[0]


    def _load_loc(self):
        self.LocCountryEle = pd.read_csv(self.root + '\GCAM_Data\Outputs\ProductionByCountry.csv', usecols=['Name', 'LON', 'LAT'])
        self.LocRiverEle = pd.read_csv(self.root + "\Scripts\LargerRiverElevators.csv", usecols=['Name', 'X', 'Y'])
        self.LocShuttleEle = pd.read_csv(self.root + "\Scripts\Shuttle tarins and ports.csv", usecols=['Name', 'X', 'Y'])
        self.LocExports = pd.read_csv(self.root + "\Scripts\ExportTerminals.csv", usecols=['Ports', 'X', 'Y'])

    def _load_routes(self, scenario, year, rate):
        self.Matrix_X_Country_Stream = pd.read_csv(self.root + '\Exps\{}\\{}\\'.format(scenario, year, rate) + '2_ResultsOfCountryElevators_{}.csv'.format(rate), index_col=0, usecols=[x for x in range(0,11)])
        self.Matrix_X_Country_Rail = pd.read_csv(self.root + '\Exps\{}\\{}\\'.format(scenario, year, rate) + '2_ResultsOfCountryElevators_{}.csv'.format(rate), index_col=0, usecols=[x for x in range(11,17)])
        self.Matrix_X_Facility = pd.read_csv(self.root + '\Exps\{}\\{}\\'.format(scenario, year, rate) + '2_ResultsOfCountryElevators_{}.csv'.format(rate), usecols=['X_Facility'])
        #Matrix_ = pd.read_csv(self.root + '\Exps\{}\\{}\\'.format(scenario, year, rate) + '2_ResultsOfCountryElevators_{}.csv'.format(rate), index_col=0)

        self.Matrix_Y_Stream_Export = pd.read_csv(self.root + '\Exps\{}\\{}\\'.format(scenario, year, rate) + '3_ResultsOfRiverElevators_{}.csv'.format(rate), index_col=0)
        self.Matrix_Y_Rail_Export = pd.read_csv(self.root + '\Exps\{}\\{}\\'.format(scenario, year, rate) + '4_ResultsOfRailElevators_{}.csv'.format(rate), index_col=0)

        self.Matrix_Z_Export_Import =pd.read_csv(self.root + '\Exps\{}\\{}\\'.format(scenario, year, rate) + '5_ResultsOfExports_{}.csv'.format(rate), index_col=0)

    def _get_routes(self, ax, scenario, year, leg, legs):

        def Coords(data, index):
            X = data.iloc[index, 1].to_numpy()
            Y = data.iloc[index, 2].to_numpy()
            return np.vstack((X, Y)).T

        ## return non-zero number of facility - 1
        X_Country_River, Y_Country_River = np.nonzero(self.Matrix_X_Country_Stream.values)
        X_Country_Rail, Y_Country_Rail = np.nonzero(self.Matrix_X_Country_Rail.values)
        X_Stream_Export, Y_Stream_Export = np.nonzero(self.Matrix_Y_Stream_Export.values)
        X_Rail_Export, Y_Rail_Export = np.nonzero(self.Matrix_Y_Rail_Export.values)
        X_Export_Import, Y_Export_Import = np.nonzero(self.Matrix_Z_Export_Import.values)

        ## get the coordinates of the routes
        S_Country_River = Coords(self.LocCountryEle, X_Country_River)
        E_Country_River = Coords(self.LocRiverEle, Y_Country_River)
        S_Country_Rail = Coords(self.LocCountryEle, X_Country_Rail)
        E_Country_Rail = Coords(self.LocShuttleEle, Y_Country_Rail)

        S_River_Export = Coords(self.LocRiverEle, X_Stream_Export)
        E_River_Export = Coords(self.LocExports, Y_Stream_Export)
        S_Rail_Export = Coords(self.LocShuttleEle, X_Rail_Export)
        E_Rail_Export = Coords(self.LocExports, Y_Rail_Export)

        ## plot setting
        #fig, ax = plt.subplots(1, figsize=(16, 14))
        # self.fig, self.ax = plt.subplots()
        # parameters = {'axes.labelsize': 20,
        #               'axes.titlesize': 20,
        #               'xtick.labelsize': 20,
        #               'ytick.labelsize': 20,
        #               'legend.fontsize': 16,
        #               }
        # plt.rcParams.update(parameters)
        # plotting
        for i in range(len(S_Country_River)):
            ax.plot([S_Country_River[i][0], E_Country_River[i][0]], [S_Country_River[i][1], E_Country_River[i][1]],
                     color='#F05E1C', linestyle='-')

        for i in range(len(S_Country_Rail)):
            ax.plot([S_Country_Rail[i][0], E_Country_Rail[i][0]], [S_Country_Rail[i][1], E_Country_Rail[i][1]],
                     color='#FFB11B', linestyle='-')

        for i in range(len(S_River_Export)):
            ax.plot([S_River_Export[i][0], E_River_Export[i][0]], [S_River_Export[i][1], E_River_Export[i][1]],
                     color='#F05E1C', linewidth=2)
            # plt.annotate(r'1112', xy=(E_River_Export[i][0], E_River_Export[i][1]), textcoords='offset points')

        for i in range(len(S_Rail_Export)):
            ax.plot([S_Rail_Export[i][0], E_Rail_Export[i][0]], [S_Rail_Export[i][1], E_Rail_Export[i][1]],
                     color='#FFB11B', linewidth=2)

        ax.scatter(self.LocCountryEle['LON'].to_numpy(), self.LocCountryEle['LAT'].to_numpy(), label='Country elevators', color='#7bb207',
                    s=30, zorder=5)
        ax.scatter(self.LocRiverEle['X'].to_numpy(), self.LocRiverEle['Y'].to_numpy(), label='River elevators', color='#F05E1C', s=50,
                    zorder=5)
        ax.scatter(self.LocShuttleEle['X'].to_numpy(), self.LocShuttleEle['Y'].to_numpy(), label='Shuttle elevators', color='#FFB11B', s=50,
                    zorder=5)
        ax.scatter(self.LocExports['X'].to_numpy(), self.LocExports['Y'].to_numpy(), label='Export terminals', color='#006284', s=80,
                    zorder=5)

        for i in range(self.Matrix_Z_Export_Import.shape[0]):
            if self.LocExports.iloc[i, 1] <= -95:
                ax.annotate(self.LocExports.iloc[i, 0], xy=(self.LocExports.iloc[i, 1], self.LocExports.iloc[i, 2]),
                             xytext=(self.LocExports.iloc[i, 1] - 4, self.LocExports.iloc[i, 2] - 1.3), fontsize=30)
            else:
                ax.annotate(self.LocExports.iloc[i, 0], xy=(self.LocExports.iloc[i, 1], self.LocExports.iloc[i, 2]),
                             xytext=(self.LocExports.iloc[i, 1] - 1, self.LocExports.iloc[i, 2] - 1.3), fontsize=30)


        ## mapping base layer
        USA = gpd.read_file(self.root + '/Shapefiles/cb_2018_us_state_20m.shp')
        # States = USA.STUSPS.tolist()
        Outside = ['AK', 'HI', 'PR']
        States = [state for state in USA.STUSPS.tolist() if state not in Outside]
        # USA.plot()
        USA[USA['STUSPS'].isin(States)].boundary.plot(ax=ax, color='#828282', zorder=-1)

        ## fig setting
        if legs == True:
            ax.legend(loc='lower left', markerscale=2, facecolor='#faf8ed',fontsize=35, bbox_to_anchor=(1.01, 0.2),  labelcolor='#2a4652', edgecolor='#faf8ed')
            ax.text(-128, 35, '{}               \n\nTotal production: {:.2e}\nChina demand: {:.2e}'.format(str(year)+'-'+str(scenario),self.total_production, self.china_demand),
                    fontsize=45, color='#2a4652',
                    horizontalalignment='right',
                    verticalalignment='center')
        # plt.xlabel("LONGITUDE")
        # plt.ylabel("LATITUDE")
        #ax.set_title('{} Total Production: {:.2e}  Total China Demand: {:.2e}'.format(leg, self.total_production, self.china_demand))

        textstr = '\nTotal Costs: {:.2e}\nTruck Costs: {:.2e}\nBarge Costs: {:.2e}\nRail Costs: {:.2e}\nOcean Costs: {:.2e}'.format(self.OBJ_vaules, self.total_farmer, self.total_barge, self.total_rail, self.total_ocaen)
        ax.text(-107, 28, textstr, fontsize=38, verticalalignment='center', horizontalalignment='right', color='#2a4652')
        #ax.text(-126, 24, textstr, fontsize=38, verticalalignment='center', horizontalalignment='right', color='#2a4652',
                 #bbox=dict(facecolor='#faf8ed', edgecolor='#d6d6d6', boxstyle='round', alpha=0.8))
        #ax.annotate(textstr, xy=(-126, 24), color='#2a4652')
        ax.annotate('{}'.format(leg), xy=(-75, 27), color='#2a4652', fontsize=80)

        ax.set_axis_off()  # hide the axis
        ax.grid(False)
        # ax.get_xaxis().set_visible(False)
        # ax.get_yaxis().set_visible(False)
        ax.set_facecolor('#faf8ed')
        #fig.show()
        #plt.savefig(self.path + '/' + str(self.year) + '_' + self.model_name + '_' + self.scenario_text + '.pdf', dpi=600, bbox_inches="tight")
        #fig.savefig(self.root + '/Figs/{}_{}_{}.pdf'.format(scenario, year, leg) , bbox_inches="tight")
        #plt.close()

if __name__ == '__main__':
    SMALL_SIZE = 38
    MEDIUM_SIZE = 38
    BIGGER_SIZE = 38

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
    Legs = ['S0', 'S1', 'S2', 'S3', 'S4']

    fig = plt.figure(figsize=(36, 32), facecolor='#faf8ed')
    #fig.tight_layout()
    gs = GridSpec(3, 2, hspace=0, wspace=0)
    gs.update(left=0, right=1, bottom=0, top=1)

    ax = plt.subplot(gs[0, 0])
    logistic_plot(ax, scenario, year, Rates[1], Legs[1])

    ax = plt.subplot(gs[0, 1])
    logistic_plot(ax, scenario, year, Rates[2], Legs[2])

    ax = plt.subplot(gs[1, :])
    logistic_plot(ax, scenario, year, Rates[0], Legs[0], True)

    ax = plt.subplot(gs[2, 0])
    logistic_plot(ax, scenario, year, Rates[3], Legs[3])

    ax = plt.subplot(gs[2, 1])
    logistic_plot(ax, scenario, year, Rates[4], Legs[4])

    fig.show()
    fig.savefig('./Figs/Fig_network.pdf', dpi=600, bbox_inches="tight")
    # for index, rate in enumerate(Rates):
    #     logistic_plot(ax, scenario, year, rate, Legs[index])

