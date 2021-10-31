# Author: Scott
# Date: 2021-10-30 15:18:45
# LastEditTime: 2021-10-30 15:18:46
# LastEditors: Scott Zheng
# Description: Calculate Trans Cost form Country elevators to its Facility, River, and Rail elevators.
#             Inputs: 'DistanceRailToPorts.csv'
#                     'DistanceRiverToPorts.csv'
#             Outputs:'..\Cost\CostStreamToExport.csv'
#                     '..\Cost\CostRaiToExport.csv'
#
# FilePath: .\Data\CalculateCostOfRiver&Rail.py

import pandas as pd
import numpy as np
import time


def CalCostOfRiverRail(pathIn, pathOut, LimitRiver, LimitRail):
    River_Export_Distance = pd.read_csv(pathIn + 'DistanceRiverToPorts.csv', index_col=0)
    River_Export_Distance['min_val'] = River_Export_Distance.min(axis=1)
    Rail_Export_Distance = pd.read_csv(pathIn + 'DistanceRailToPorts.csv', index_col=0)
    Rail_Export_Distance['min_val'] = Rail_Export_Distance.min(axis=1)
    OMax_River = River_Export_Distance['min_val'].max()
    OMin_River = River_Export_Distance['min_val'].min()
    OMax_Rail = Rail_Export_Distance['min_val'].max()
    OMin_Rail = Rail_Export_Distance['min_val'].min()

    def NormalizateData(OriginData, NMin, NMax, OMax, OMin):
        N = NMin + ((NMax - NMin) / (OMax - OMin)) * (OriginData - OMin)
        return ("%.2f" % N)

    ## 1. write Cost from River to Exports
    Cost_River_Export = River_Export_Distance.copy()
    Cost_River_Export = Cost_River_Export.drop('min_val', axis=1)
    for i in range(Cost_River_Export.shape[0]):
        for j in range(Cost_River_Export.shape[1]):
            Cost_River_Export.iloc[i, j] = NormalizateData(Cost_River_Export.iloc[i, j], LimitRiver[0], LimitRiver[1], OMax_River, OMin_River)
    Cost_River_Export.to_csv(pathOut + 'CostStreamToExport.csv')
    localtime = time.asctime(time.localtime(time.time()))
    print(localtime + '  Successfully write out to CostStreamToExport.csv')

    ## 2. write Cost from Rail to Exports
    Cost_Rail_Export = Rail_Export_Distance.copy()
    Cost_Rail_Export = Cost_Rail_Export.drop('min_val', axis=1)
    for i in range(Cost_Rail_Export.shape[0]):
        for j in range(Cost_Rail_Export.shape[1]):
            Cost_Rail_Export.iloc[i, j] = NormalizateData(Cost_Rail_Export.iloc[i, j], LimitRail[0], LimitRail[1], OMax_Rail, OMin_Rail)
    Cost_Rail_Export.to_csv(pathOut + 'CostRaiToExport.csv')
    localtime = time.asctime(time.localtime(time.time()))
    print(localtime + '  Successfully write out to CostRaiToExport.csv')