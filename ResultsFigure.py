#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 27/10/2021 8:07 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : ResultsFigure.py
# @Software: PyCharm
# @Notes   :Plot the results figs with matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def Coords(data, index):
    X = data.iloc[index, 1].to_numpy()
    Y = data.iloc[index, 2].to_numpy()
    return np.vstack((X,Y)).T

def ResultsFigure(CountryToStream, CountryToRail, StreamToExport, RailToExport, ExportToImport, Domestic_Price, Global_Price):
    ##adding coordinate for each loctaion
    LocCountryEle = pd.read_csv('.\GCAM_Data\Outputs\ProductionByCountry_2020_IRR_lo.csv', usecols=['Name', 'LON', 'LAT'])
    LocRiverEle= pd.read_csv(".\Scripts\LargerRiverElevators.csv", usecols=['Name','X','Y'])
    LocShuttleEle = pd.read_csv(".\Scripts\Shuttle tarins and ports.csv", usecols=['Name','X','Y'])
    LocExports = pd.read_csv(".\Scripts\ExportTerminals.csv", usecols=['Name','X','Y'])

    ## return non-zero routes
    X_Country_River, Y_Country_River = np.nonzero(CountryToStream.values)
    X_Country_Rail, Y_Country_Rail = np.nonzero(CountryToRail.values)
    X_Stream_Export, Y_Stream_Export = np.nonzero(StreamToExport.values)
    X_Rail_Export, Y_Rail_Export = np.nonzero(RailToExport.values)
    X_Export_Import, Y_Export_Import = np.nonzero(ExportToImport.values)

    # check out start and end coords for pair of point
    S_Country_River = Coords(LocCountryEle, X_Country_River)
    E_Country_River = Coords(LocRiverEle, Y_Country_River)
    S_Country_Rail = Coords(LocCountryEle, X_Country_Rail)
    E_Country_Rail = Coords(LocShuttleEle, Y_Country_Rail)

    S_River_Export = Coords(LocRiverEle, X_Stream_Export)
    E_River_Export = Coords(LocExports, Y_Stream_Export)
    S_Rail_Export = Coords(LocShuttleEle, X_Rail_Export)
    E_Rail_Export = Coords(LocExports, Y_Rail_Export)

    ## plot
    plt.figure(dpi=600)

    parameters = {'axes.labelsize': 25,
                  'xtick.labelsize': 25,
                  'ytick.labelsize': 25,
                  'legend.fontsize': 20,
                  }
    plt.rcParams.update(parameters)
    plt.figure(figsize=(13, 10))

    for i in range(len(S_Country_River)):
        plt.plot([S_Country_River[i][0],E_Country_River[i][0]], [S_Country_River[i][1],E_Country_River[i][1]], color='#97CE68',linestyle='-')

    for i in range(len(S_Country_Rail)):
        plt.plot([S_Country_Rail[i][0], E_Country_Rail[i][0]], [S_Country_Rail[i][1], E_Country_Rail[i][1]], color='#b2c000',linestyle='-')

    for i in range(len(S_River_Export)):
        plt.plot([S_River_Export[i][0], E_River_Export[i][0]], [S_River_Export[i][1], E_River_Export[i][1]], color='#d52b15',linewidth=4)
        #plt.annotate(r'1112', xy=(E_River_Export[i][0], E_River_Export[i][1]), textcoords='offset points')

    for i in range(len(S_Rail_Export)):
        plt.plot([S_Rail_Export[i][0], E_Rail_Export[i][0]], [S_Rail_Export[i][1], E_Rail_Export[i][1]], color='#2a93d4',linewidth=2)

    plt.scatter(LocCountryEle['LON'].to_numpy(), LocCountryEle['LAT'].to_numpy(), label='Country Elevators', color='#b2de81',s=80)
    plt.scatter(LocRiverEle['X'].to_numpy(),LocRiverEle['Y'].to_numpy(), label='River Elevators', color='#d52b15', s=100)
    plt.scatter(LocShuttleEle['X'].to_numpy(),LocShuttleEle['Y'].to_numpy(), label='Rail Elevators', color='#2a93d4', s=100)
    plt.scatter(LocExports['X'].to_numpy(),LocExports['Y'].to_numpy(), label='Export Terminals', color='#feb545', s=120)

    plt.legend()
    # plt.rcParams["figure.figsize"] = (100, 50)
    plt.xlabel("LONGITUDE")  # x轴上的名字
    plt.ylabel("LATITUDE")  # y轴上的名字
    plt.show()