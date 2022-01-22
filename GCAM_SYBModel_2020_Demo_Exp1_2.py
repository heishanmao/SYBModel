#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 21/07/2021 3:50 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : GCAM_SYBModel_2020_Demo.py.py
# @Software: PyCharm
# @Notes   : Based on the 2020 GCAM output dataset and update cost files.
           # Solving by SYBModel_V13.py
import pandas as pd
import numpy as np
import SYBModel_V14 as GRB
import ResultsFigure as FIG

import os
root = os.path.abspath('.')  # 'D:\\OneDrive - University of Tennessee\\Scripts\\SYBModel'

# function parameters
Model_Name = "Soybean_V14_Oct-27-2021"
Year = 2020
Alpha = 0.99  # Inventory deterioration rate per year

# @Datasets normal Scenarios
# Country_Elevator to Stream_Elevator by Trucks  @(c, s)
Cost_Country_Stream = pd.read_csv(root + '\Data\Cost\CostToStreamByTruck.csv', index_col=0).to_numpy()

# Country_Elevator to Rail_Elevator by Trucks  @(c, r)
Cost_Country_Rail = pd.read_csv(root + '\Data\Cost\CostToRailByTruck.csv', index_col=0).to_numpy()

# Stream_Elevator to Export_Terminals by Barges @(s, e)
Cost_Stream_Export = pd.read_csv(root + '\Data\Cost\CostStreamToExport.csv', index_col=0).to_numpy()

# Rail_Elevator to Export_Terminals by Rail @(r, e)
Cost_Rail_Export = pd.read_csv(root + '\Data\Cost\CostRaiToExport.csv', index_col=0).to_numpy()

# Export_Terminals to Import_China by Ocean shipment from barge @(e,i)
Cost_Export_Import = pd.read_csv(root + '\Data\Cost\CostExportToImport.csv', index_col=0).to_numpy()

# Country_Elevator to Domestic Processing Facility @(P^D)
Cost_Country_Facility = pd.read_csv(root + '\Data\Cost\CostToFacility.csv', index_col=0, usecols=['Name', 'Facility']).T.to_numpy()[0]

# elevators unit holding cost @h
Unit_Holding_Cost = 20

Scenarios = [0.2, 0.5, 0.8, 1.0, 1.2, 1.5, 3.0]
ExpRES = pd.DataFrame()
for index, s in enumerate(Scenarios):
    name = 'ProductionByCountry' + str(s)
    # Supply of each Country elevator
    Yield_Country = pd.read_csv(root + '\GCAM_Data\Outputs\\'+ name +'.csv', index_col=0, usecols=['Name', 'Yield_IRR_hi', 'Yield_IRR_lo', 'Yield_RFD_hi', 'Yield_RFD_lo', 'PlantingArea']).to_numpy()

    # China demand at year 2020
    Demand_China = 88e6*1.2

    # last year inventory for each elevator @2019
    # Inventory_Country_LastYear = pd.read_csv('.\Data\ProductionByCountry.csv', index_col=0,
    #                      usecols=['Name', 'Ending']).to_numpy()
    Inventory_Country_LastYear = np.zeros(Cost_Country_Stream.shape[0])
    Inventory_Stream_LastYear = np.zeros(Cost_Stream_Export.shape[0])
    Inventory_Rail_LastYear = np.zeros(Cost_Rail_Export.shape[0])

    ## model input summary
    print(f'Model Name: {Model_Name}')
    NumOfCountry = Cost_Country_Stream.shape[0] if Cost_Country_Stream.shape[0] == Cost_Country_Rail.shape[0] == \
                                                   Cost_Country_Facility.shape[0] == Yield_Country.shape[0] == \
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

    ## Solving by GUROBI Model --SYBModel_V13.py
    CountryToStream, CountryToRail, CountryToFacility, CountryInventory, StreamInventory, RailInventory, StreamToExport, \
    RailToExport, ExportToImport, Domestic_Price, Global_Price, Supply_Country, Total_Exported, ObjVal= GRB.Get_GuRoBi(Model_Name,Cost_Country_Stream,
                                                                                Cost_Country_Rail, Cost_Stream_Export,
                                                                                Cost_Rail_Export, Cost_Export_Import,
                                                                                Cost_Country_Facility, Alpha, Unit_Holding_Cost,
                                                                                Demand_China, Yield_Country,
                                                                                Inventory_Country_LastYear, Inventory_Stream_LastYear, Inventory_Rail_LastYear)
    ## Figure
    #FIG.ResultsFigure(CountryToStream, CountryToRail, StreamToExport, RailToExport, ExportToImport, Domestic_Price, Global_Price, Supply_Country, Total_Exported)

    ExpRES.loc[s, 'Demand'] = Demand_China
    ExpRES.loc[s, 'Supply'] = sum(Supply_Country)
    ExpRES.loc[s, 'Export'] = Total_Exported
    ExpRES.loc[s, 'Supply/Demand'] = round(sum(Supply_Country) / Demand_China,4)
    ExpRES.loc[s, 'Export/Demand'] = round(Total_Exported / Demand_China, 4)
    ExpRES.loc[s, 'Export/Supply'] = round(Total_Exported / sum(Supply_Country),4)
    ExpRES.loc[s, 'ObjVal'] = ObjVal

ExpRES.to_csv(root+'\Exp\Exp1_2_88e6_1.2.csv')