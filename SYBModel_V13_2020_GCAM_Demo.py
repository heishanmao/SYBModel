#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 21/07/2021 3:50 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : SYBModel_V13_2019_Demo.py
# @Software: PyCharm
# @Notes   : An example of 2019
import pandas as pd
import numpy as np
import SYBModel_V13 as GRB

# function parameters
Model_Name = "Soybean_V13_July-21-2021"
Year = 2019
Alpha = 0.99

# @Datasets
# Country_Elevator to Stream_Elevator by Trucks  @(c, s)
Cost_Country_Stream = pd.read_csv('.\Data\CostToStreamByTruck.csv', index_col=0).to_numpy()

# Country_Elevator to Rail_Elevator by Trucks  @(c, r)
Cost_Country_Rail = pd.read_csv('.\Data\CostToRailByTruck.csv', index_col=0).to_numpy()

# Stream_Elevator to Export_Terminals by Barges @(s, e)
Cost_Stream_Export = pd.read_csv('.\Data\CostStreamToExport.csv', index_col=0).to_numpy()

# Rail_Elevator to Export_Terminals by Rail @(r, e)
Cost_Rail_Export = pd.read_csv('.\Data\CostRaiToExport.csv', index_col=0).to_numpy()

# Export_Terminals to Import_China by Ocean shipment from barge @(e,i)
Cost_Export_Import = pd.read_csv('.\Data\CostExportToOcean.csv', index_col=0).to_numpy()

# Country_Elevator to Domestic Processing Facility @(P^D)
Cost_Country_Facility = pd.read_csv('.\Data\CostToFacility.csv', index_col=0,
                                    usecols=['Name', 'Facility']).T.to_numpy()[0]

# elevators unit holding cost @h
Unit_Holding_Cost = 10

# Supply of each Country elevator
Supply_Country = pd.read_csv('.\Data\ProductionByCountry.csv', index_col=0,
                             usecols=['Name', 'Production']).T.to_numpy()[0]

# China demand at year 2019
Demand_China = 88e6

# last year inventory for each elevator @2019
# Inventory_Country_LastYear = pd.read_csv('.\Data\ProductionByCountry.csv', index_col=0,
#                      usecols=['Name', 'Ending']).to_numpy()
Inventory_Country_LastYear = np.zeros(Cost_Country_Stream.shape[0])
Inventory_Stream_LastYear = np.zeros(Cost_Stream_Export.shape[0])
Inventory_Rail_LastYear = np.zeros(Cost_Rail_Export.shape[0])

# model input summary
print(f'Model Name: {Model_Name}')
NumOfCountry = Cost_Country_Stream.shape[0] if Cost_Country_Stream.shape[0] == Cost_Country_Rail.shape[0] == \
                                               Cost_Country_Facility.shape[0] == Supply_Country.shape[0] == \
                                               Inventory_Country_LastYear.shape[0] else 0
print(f'Country Elevators: {NumOfCountry}')
NumOfStream = Cost_Country_Stream.shape[1] if Cost_Country_Stream.shape[1] == Cost_Stream_Export.shape[0] \
                                              == Inventory_Stream_LastYear.shape[0] else 0
print(f'Stream Elevators: {NumOfStream}')
NumOfRail = Cost_Country_Rail.shape[1] if Cost_Country_Rail.shape[1] == Cost_Rail_Export.shape[0] \
                                          == Inventory_Rail_LastYear.shape[0] else 0
print(f'Rail Elevators: {NumOfRail}')
NumOfExport = Cost_Stream_Export.shape[1] if Cost_Stream_Export.shape[1] == Cost_Rail_Export.shape[1] \
                                             == Cost_Export_Import.shape[0] else 0
print(f'Exports: {NumOfExport}')
print(f'Imports: {Cost_Export_Import.shape[1]}')

GRB.Get_GuRoBi(Model_Name, Cost_Country_Stream, Cost_Country_Rail, Cost_Stream_Export, Cost_Rail_Export,
           Cost_Export_Import, Cost_Country_Facility, Alpha,
           Unit_Holding_Cost, Demand_China, Supply_Country, Inventory_Country_LastYear,
           Inventory_Stream_LastYear, Inventory_Rail_LastYear)