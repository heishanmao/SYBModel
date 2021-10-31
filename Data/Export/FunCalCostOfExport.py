# Author: Scott
# Date: 2021-10-30 15:18:45
# LastEditTime: 2021-10-30 15:18:46
# LastEditors: Scott Zheng
# Description: Calculate Trans Cost form Country elevators to its Facility, River, and Rail elevators.
#             Inputs: '.\DistanceExportToImport.csv'
#             Outputs:'..\Cost\CostExportToImport.csv'
#
#
# FilePath: .\Data\CalculateCostOfRiver&Rail.py

import pandas as pd
import numpy as np
import time


def CalCostOfExport(pathIn, pathOut, LimitExport):
    Distance = pd.read_csv(pathIn + 'DistanceExportToImport.csv', index_col=0)
    Distance['min_val'] = Distance.min(axis=1)
    OMax = Distance['min_val'].max()
    OMin = Distance['min_val'].min()

    def NormalizateData(OriginData, NMin, NMax, OMax, OMin):
        N = NMin + ((NMax - NMin) / (OMax - OMin)) * (OriginData - OMin)
        return ("%.2f" % N)

    ## 1. write Cost from Export to Import
    Cost = Distance.copy()
    Cost = Cost.drop('min_val', axis=1)
    for i in range(Cost.shape[0]):
        for j in range(Cost.shape[1]):
            Cost.iloc[i, j] = NormalizateData(Cost.iloc[i, j], LimitExport[0], LimitExport[1], OMax, OMin)
    Cost.to_csv(pathOut + 'CostExportToImport.csv')

    localtime = time.asctime(time.localtime(time.time()))
    print(localtime + '  Successfully write out to CostExportToImport.csv')



