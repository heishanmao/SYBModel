# Author: Scott
# Date: 2021-10-30 15:18:45
# LastEditTime: 2021-10-30 15:18:46
# LastEditors: Scott Zheng
# Description: Calculate Trans Cost form River or Rail elevators to Export terminals.
# @Inputs  : 'DistanceRiverToPorts.csv'
#            'DistanceRailToPorts.csv'
# @Outputs : '../Data/Cost/CostStreamToExport.csv'
# @Outputs : '../Data/Cost/CostRaiToExport.csv'
# FilePath: ./Data/River&Rail/FunCalCostOfRiverRail2.py

import pandas as pd
import numpy as np
import time

import os
path = os.path.abspath('..')
pathIn = path + '\River&Rail/'
pathOut = path + "\Cost/"

Year = 2021
## Calculate River Cost
# 1976 traiff benchmark rate per ton
benchmarkRate = { 'TWC':6.19, 'MM':5.32, 'ILL':4.64, 'ST LOUIS':3.99,
                 'CINC':4.69, 'LOH':4.04, 'CAR-MEM':3.14}

# Dict_Routes
Dict_Routes = {'West River Transit':['ST LOUIS','CINC'],
              'Vision Transportation of Elk River | Big Lake | Rogers | Zimmerman':['TWC','MM','ST LOUIS','CINC'],
              'River Cities Public Transit':['ST LOUIS','CINC'],
              'Two Rivers Transportation':['ST LOUIS','CINC'],
              'Blue Rivers Public Transportation':['ST LOUIS','CINC'],
              'Transport 360, LLC.':['ST LOUIS','CINC'],
              'Five Rivers Transport, LLC':['ST LOUIS','CINC'],
              'East Side River Transportation Inc':['ST LOUIS','CINC'],
              'River City Transportation':['TWC','ST LOUIS','CINC'],
              'River Transportation Co':['CAR-MEM','LOH','CINC']}

# Import rates for all year
Weekly_BargeRate = pd.read_excel(pathIn + 'GTRFigure8Table9_2021.xlsx',sheet_name='Table 9_data', header =2, usecols ="A:H").iloc[2:,:]
Weekly_BargeRate['All Points'] = pd.DatetimeIndex(Weekly_BargeRate['All Points']).year
Weekly_BargeRate = Weekly_BargeRate.replace(0, np.nan)
Annualy_BargeRate = Weekly_BargeRate.groupby('All Points').mean(numeric_only=True) # weekly to annually

# Calculate Rates to New Orleans
BargeCost_NO = pd.Series(index=Dict_Routes.keys(), dtype='float64')
for key, value in Dict_Routes.items():
    Rate = 0
    for Routes in value:
        Rate = Rate + benchmarkRate[Routes] * Annualy_BargeRate.loc[Year, Routes] / 100
    BargeCost_NO.loc[key] = Rate

# Barge Cost
River_Export_Distance = pd.read_csv(pathIn + 'DistanceRiverToPorts.csv', index_col=0)
BargeCost = pd.DataFrame().reindex_like(River_Export_Distance)
BargeCost.loc[:,'New Orleans'] = BargeCost_NO
 # Calculate other exports based on the rate to New Orleans.
for col in range(1, len(River_Export_Distance.columns.tolist())):
    for row in range(River_Export_Distance.shape[0]):
        BargeCost.iloc[row,col] = BargeCost.iloc[row,0] * (River_Export_Distance.iloc[row,col]/River_Export_Distance.iloc[row,0] + 1 )

# output Barge Rate
BargeCost.to_csv(pathOut + 'CostStreamToExport.csv')
localtime = time.asctime(time.localtime(time.time()))
print(localtime + '  Successfully write out to CostStreamToExport.csv')





a1=1

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