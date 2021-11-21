# Author: Scott
# Date: 2021-10-30 15:18:45
# LastEditTime: 2021-11-14 15:18:46
# LastEditors: Scott Zheng
# Description: Calculate Trans Cost form Exports to Imports
#             Inputs: '.\DistanceExportToImport.csv'
#             Outputs:'..\Cost\CostExportToImport.csv'
#
#
# FilePath: .\Data\FunCalCostOfExport.py

import pandas as pd
import numpy as np
import time

# import os
# path = os.path.abspath('..')
# pathIn = path + '\Export/'
# pathOut = path + "\Cost/"

def CalCostOfExport(pathIn, pathOut):
    def BaseCost(types):
        # $ / mt of soybean
        if types == 'Gulf':
            cost = 44.5
        elif types == 'PNW':
            cost = 40.5
        elif types == 'EC':
            cost = 58.9
        else:
            cost = 88.75
        return cost

    # import data
    Distance = pd.read_csv(pathIn + 'DistanceExportToImport.csv', index_col=0)
    avgDis = Distance.iloc[:,:-1].mean(axis=1)

    # Base
    BaseCost = Distance['Coast'].map(BaseCost)
    BaseCost = BaseCost.div(avgDis, axis=0)
    # map unit * avg
    CostToImport = Distance.iloc[:,:-1].mul(BaseCost, axis=0)

    # output
    CostToImport.to_csv(pathOut + 'CostExportToImport.csv')
    localtime = time.asctime(time.localtime(time.time()))
    print(localtime + '  Successfully write out to CostExportToImport.csv')





