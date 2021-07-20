#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/07/2021 3:22 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : GModel.py
# @Software: PyCharm
# @Notes   : GUROBI code for the SYBModel

from gurobipy import *

def Get_GuRoBi(Model_Name, Cost_Country_Stream, Cost_Country_Rail, Cost_Stream_Export, Cost_Rail_Export,
               Cost_Export_Improt_Stream, Cost_Export_Improt_Rail, Cost_Country_Facility, Alpha,
               Unit_Holding_Cost, Demand_China, Supply_Country, Last_Year_Inventory):
    # Parameters
    T = 1  # Do not change! period year

    # Dom_P =  200   # Domestic Soybean price
    Beta1 = 315.948
    Beta2 = 0
    Beta3 = -4.43476  # Regression coefficients

    # Glo_P =  400   # Global Soybean price
    Gamma1 = 117.09
    Gamma2 = 0
    Gamma3 = 5.6e-6  # Regression coefficients

    # Model
    model = Model(Model_Name)


if __name__ =='__main__':
    import pandas as pd
    import numpy as np

    # function parameters
    Model_Name = "Soybean_V13_July-19-2021"
    Year = 2019
    Alpha = 0.99

    # @Datasets
    # Country_Elevator to Stream_Elevator by Trucks  @(c, s)
    Cost_Country_Stream = pd.read_csv('.\Data\CostToStreamByTruck.csv', index_col=0).to_numpy()

    # Stream_Elevator to Export_Terminals by Barges @(s, e)
    Cost_Stream_Export = pd.read_csv('.\Data\CostByBarge.csv', index_col=0).to_numpy()

    # Export_Terminals to Import_China by Ocean shipment @(e,i)
    Cost_Export_Improt_Stream = pd.read_csv('.\Data\CostByOcean.csv', index_col=0).to_numpy()

    # Country_Elevator to Domestic Processing Facility @(P^D)
    Cost_Country_Facility = pd.read_csv('.\Data\CostToFacility.csv', index_col=0,
                                        usecols=['Name', 'Facility']).T.to_numpy()[0]

    # Country_Elevator to Rail_Elevator by Trucks  @(c, r)
    Cost_Country_Rail = pd.read_csv('.\Data\CostToRailByTruck.csv', index_col=0).to_numpy()

    # Rail_Elevator to Export_Terminals by Rail @(r, e)
    Cost_Rail_Export = pd.read_csv('.\Data\CostByRail.csv', index_col=0).to_numpy()

    # elevators unit holding cost @h
    Unit_Holding_Cost = pd.read_csv('.\Data\CostToFacility.csv', index_col=0,
                           usecols=['Name', 'HoldingCost']).T.to_numpy()[0]

    # Supply of each Country elevator
    Supply_Country = pd.read_csv('.\Data\ProductionByCountry.csv', index_col=0,
                                 usecols=['Name', 'Production']).T.to_numpy()[0]

    # China demand at year 2019
    Demand_China = 88e6

    # last year inventory for each country elevator @2019
    Last_Year_Inventory = pd.read_csv('.\Data\ProductionByCountry.csv', index_col=0,
                         usecols=['Name', 'Ending']).T.to_numpy()[0]

    Get_GuRoBi(Model_Name, Cost_Country_Stream, Cost_Country_Rail, Cost_Stream_Export, Cost_Rail_Export,
               Cost_Export_Improt_Stream, Cost_Export_Improt_Rail, Cost_Country_Facility, Alpha,
               Unit_Holding_Cost, Demand_China, Supply_Country, Last_Year_Inventory)