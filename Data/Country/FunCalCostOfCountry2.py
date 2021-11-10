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
# @Outputs : '../Data/Cost/CostToStreamByTruck.csv'
# @Outputs : '../Data/Cost/CountryToRailDistance.csv'
# @Outputs : '../Data/Cost/CostToFacility.csv'

import pandas as pd
import time
import random

# import os
# path = os.path.abspath('..')
# pathIn = path + '\Country/'
# pathOut = path + "\Cost/"

def CalCostOfCountry(pathIn, pathOut):
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
    CostToFacility = pd.concat([CostToRiver.min(axis=1),CostToRail.min(axis=1)], axis=1).mean(axis=1)  # rate base both River and Rail
    CostToFacility = CostToFacility.map(lambda x: random.uniform(0.55, 1.55)*x) # randomly range
    CostToFacility.name = 'Facility'
        # write to csv file
    CostToFacility.to_csv(pathOut + 'CostToFacility.csv')
    localtime = time.asctime(time.localtime(time.time()))
    print(localtime + '  Successfully write out to CostToFacility.csv')

