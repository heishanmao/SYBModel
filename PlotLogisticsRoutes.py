#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 27/10/2021 8:07 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : PlotLogisticsRoutes.py
# @Software: PyCharm
# @Notes   :Plot the results figs with matplotlib and GeoPandas
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib as mpl
import os
root = os.path.abspath('.')  # 'D:\\OneDrive - University of Tennessee\\Scripts\\SYBModel'

def Coords(data, index):
    X = data.iloc[index, 1].to_numpy()
    Y = data.iloc[index, 2].to_numpy()
    return np.vstack((X,Y)).T

def num2color(values, cmap):
    """number to color"""
    norm = mpl.colors.Normalize(vmin=np.min(values), vmax=np.max(values))
    cmap = mpl.cm.get_cmap(cmap)
    return [cmap(norm(val)) for val in values]

def LogisticsFigure(CountryToStream, CountryToRail, StreamToExport, RailToExport, ExportToImport, Domestic_Price, Global_Price, Supply_Country, Total_Exported, FileName):
    ##adding coordinate for each loctaion
    LocCountryEle = pd.read_csv('.\GCAM_Data\Outputs\ProductionByCountry1.0.csv', usecols=['Name', 'LON', 'LAT'])
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
        # setting
    fig = plt.figure(dpi=300,figsize=(18, 9))
    parameters = {'axes.labelsize': 25,
                  'axes.titlesize': 30,
                  'xtick.labelsize': 25,
                  'ytick.labelsize': 25,
                  'legend.fontsize': 20,
                  }
    plt.rcParams.update(parameters)

        # plotting
    for i in range(len(S_Country_River)):
        plt.plot([S_Country_River[i][0],E_Country_River[i][0]], [S_Country_River[i][1],E_Country_River[i][1]], color='#F05E1C',linestyle='-')

    for i in range(len(S_Country_Rail)):
        plt.plot([S_Country_Rail[i][0], E_Country_Rail[i][0]], [S_Country_Rail[i][1], E_Country_Rail[i][1]], color='#FFB11B',linestyle='-')

    for i in range(len(S_River_Export)):
        plt.plot([S_River_Export[i][0], E_River_Export[i][0]], [S_River_Export[i][1], E_River_Export[i][1]], color='#F05E1C',linewidth=2)
        #plt.annotate(r'1112', xy=(E_River_Export[i][0], E_River_Export[i][1]), textcoords='offset points')

    for i in range(len(S_Rail_Export)):
        plt.plot([S_Rail_Export[i][0], E_Rail_Export[i][0]], [S_Rail_Export[i][1], E_Rail_Export[i][1]], color='#FFB11B',linewidth=2)

    # color based on production
    colors = num2color(Supply_Country, "Greens")

    plt.scatter(LocCountryEle['LON'].to_numpy(), LocCountryEle['LAT'].to_numpy(), label='Country Elevators', color='#7bb207',s=30, zorder=5)
    #plt.scatter(LocCountryEle['LON'].to_numpy(), LocCountryEle['LAT'].to_numpy(), label='Country Elevators', color=colors,s=30, zorder=5)
    plt.scatter(LocRiverEle['X'].to_numpy(),LocRiverEle['Y'].to_numpy(), label='River Elevators', color='#F05E1C', s=50, zorder=5)
    plt.scatter(LocShuttleEle['X'].to_numpy(),LocShuttleEle['Y'].to_numpy(), label='Rail Elevators', color='#FFB11B', s=50, zorder=5)
    plt.scatter(LocExports['X'].to_numpy(),LocExports['Y'].to_numpy(), label='Export Terminals', color='#006284', s=80, zorder=5)

    # # annotation
    # for e in range(LocExports.shape[0]):
    #     plt.text(LocExports.iloc[e,1]-5, LocExports.iloc[e,2]-2, LocExports.iloc[e,0], size=20)

    ## mapping layer
    ax = fig.gca()
    USA = gpd.read_file('./Shapefiles/cb_2018_us_state_20m.shp')
    # States = USA.STUSPS.tolist()
    Outside = ['AK', 'HI', 'PR']
    States = [state for state in USA.STUSPS.tolist() if state not in Outside]
    # USA.plot()
    USA[USA['STUSPS'].isin(States)].boundary.plot(ax=ax, color='#828282', zorder=-1)


    ## fig setting
    plt.legend()
    # plt.rcParams["figure.figsize"] = (100, 50)
    plt.xlabel("LONGITUDE")
    plt.ylabel("LATITUDE")
    #plt.title(r'$p^D:$'+str(round(Domestic_Price,2)) + ' $p^G:$'+ str(round(Global_Price,2)) + ' Supply:'+ str(int(Total_Supply_Country)) + ' Exported:' + str(int(Total_Exported)))
    Exported_Rate = round((Total_Exported / sum(Supply_Country)) * 100, 2)
    plt.title(r'$p^D:$'+str(round(Domestic_Price,2)) + ' $p^G:$'+ str(round(Global_Price,2)) + ' Exported: '+ str(Exported_Rate)+'%')

    # ax.set_axis_off()  #hide the axis
    plt.savefig(root + '\Exp\/' + FileName + '.png', dpi=300)
    plt.show()
