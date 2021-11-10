#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 09/11/2021 11:22 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : FunCalCostOfCountry2.py
# @Software: PyCharm
# @Notes   : Update the function to calculate costs of truck by distance
# @Inputs  : 'CountryToLargerDistance.csv'
#            'CountryToRailDistance.csv'
# @Outputs : Cost files

import pandas as pd
import numpy as np
import time

import os
path = os.path.abspath('..')
pathIn = path + '\Country/'
pathOut = path + "\Cost/"

def TruckCost(distance):
    # assumed 25 metric ton pre truck
    # Units:   $/metric ton
    if distance <= 25:
        cost = 4.8 / 25 * distance
    elif distance <= 100:
        cost = 3.64 / 25 * distance
    else: # greater than 100
        cost = 3.54 / 25 * distance
    return cost

## Truck to River
DisToRiver = pd.read_csv(pathIn + 'CountryToRiverDistance.csv', index_col=0)
CostToRiver = DisToRiver.applymap(TruckCost)
    # write to csv file
CostToRiver.to_csv(pathOut + 'CostToStreamByTruck.csv')
localtime = time.asctime(time.localtime(time.time()))
print(localtime + '  Successfully write out to CostToStreamByTruck.csv')

## Truck to Rail
DisToRail = pd.read_csv(pathIn + 'CountryToRailDistance.csv', index_col=0)
CostToRail= DisToRail.applymap(TruckCost)
    # write to csv file
CostToRail.to_csv(pathOut + 'CostToRailByTruck.csv')
localtime = time.asctime(time.localtime(time.time()))
print(localtime + '  Successfully write out to CostToRailByTruck.csv')

## Truck to its facility
CostToFacility = CostToRiver.min(axis=1)
CostToFacility.name = 'Facility'
CostToFacility.to_csv(pathOut + 'CostToFacility.csv')
localtime = time.asctime(time.localtime(time.time()))
print(localtime + '  Successfully write out to CostToFacility.csv')

