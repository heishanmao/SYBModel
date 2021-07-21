#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/07/2021 3:22 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : GModel.py
# @Software: PyCharm
# @Notes   : GUROBI code for the SYBModel V13
import numpy as np
from gurobipy import *

def Get_GuRoBi(Model_Name, Cost_Country_Stream, Cost_Country_Rail, Cost_Stream_Export, Cost_Rail_Export,
               Cost_Export_Import, Cost_Country_Facility, Alpha, Unit_Holding_Cost, Demand_China,
               Supply_Country, Inventory_Country_LastYear, Inventory_Stream_LastYear, Inventory_Rail_LastYear):
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

    Num_Country_Elevators = Cost_Country_Stream.shape[0]
    Num_Stream_Elevators = Cost_Stream_Export.shape[0]
    Num_Rail_Elevators = Cost_Rail_Export.shape[0]
    Num_Export_Terminals = Cost_Export_Import.shape[0]
    Num_Import_Terminals = Cost_Export_Import.shape[1]

    # Model
    model = Model(Model_Name)

    # Var
    X_Country_Stream = model.addVars(Num_Country_Elevators, Num_Stream_Elevators, lb = 0)
    X_Country_Rail = model.addVars(Num_Country_Elevators, Num_Rail_Elevators, lb=0)
    X_Facility = model.addVars(Num_Country_Elevators, lb=0)
    I_Country = model.addVars(Num_Country_Elevators, lb=0)
    I_Stream = model.addVars(Num_Country_Elevators, lb=0)
    I_Rail = model.addVars(Num_Country_Elevators, lb=0)
    Y_Stream_Export = model.addVars(Num_Stream_Elevators, Num_Export_Terminals, lb=0)
    Y_Rail_Export = model.addVars(Num_Rail_Elevators, Num_Export_Terminals, lb=0)
    Z_Export_Import = model.addVars(Num_Export_Terminals, Num_Import_Terminals, lb=0)
    Domestic_Price = model.addVar(vtype=GRB.CONTINUOUS, name='DomesticP')
    Global_Price = model.addVar(vtype=GRB.CONTINUOUS, name='GlobalP')
    Slack_Climate = model.addVar(T, vtype=GRB.BINARY, name='L-Climate')     # Slack Vars
    Slack_Tariff = model.addVar(T, vtype=GRB.BINARY, name='F-GOVPolicy')

    # Constraints
        # 2
    # for c in range(Num_Country_Elevators):
    #     model.addConstr(Alpha * Inventory_Country_LastYear[c] + Supply_Country[c] - X_Facility[c] - I_Country[c]
    #                     - quicksum(X_Country_Stream[c, s] for s in range(Num_Stream_Elevators))
    #                     - quicksum(X_Country_Rail[c, r] for r in range(Num_Rail_Elevators)) == 0)

        # 3
    for s in range(Num_Stream_Elevators):
        model.addConstr(Alpha*Inventory_Stream_LastYear[s] + quicksum(X_Country_Stream[c,s] for c in range(Num_Country_Elevators))
                        - quicksum(Y_Stream_Export[s,e] for e in range(Num_Export_Terminals)) - I_Stream[s] ==0)
        # 4
    for r in range(Num_Rail_Elevators):
        model.addConstr(Alpha*Inventory_Rail_LastYear[r] + quicksum(X_Country_Rail[c,r] for c in range(Num_Country_Elevators))
                        - quicksum(Y_Rail_Export[r,e] for e in range(Num_Export_Terminals)) - I_Rail[r] == 0)

        # 5
    for e in range(Num_Export_Terminals):
        model.addConstr(quicksum(Y_Stream_Export[s, e] for s in range(Num_Stream_Elevators))
                        + quicksum(Y_Rail_Export[r, e] for r in range(Num_Rail_Elevators))
                        - quicksum(Z_Export_Import[e, i] for i in range(Num_Import_Terminals)) == 0)

        # 6
    model.addConstr(quicksum(Z_Export_Import[e,i] for e in range(Num_Export_Terminals)
                                                  for i in range(Num_Import_Terminals)) <= Demand_China)

        # 7
    model.addConstr(Domestic_Price - Beta2 * Slack_Climate - Beta3 * quicksum(I_Country) == Beta1)

        # 8
    model.addConstr(Global_Price - Gamma2 * Slack_Tariff - Gamma3 * quicksum(Z_Export_Import) == Gamma1)

    # Objective
    obj = LinExpr()
    obj += quicksum((Global_Price-Cost_Export_Import[e, i]) * Z_Export_Import[e, i] for e in range(Num_Export_Terminals)
                                                                                    for i in range(Num_Import_Terminals))
    obj += quicksum((Domestic_Price-Cost_Country_Facility[c]) * X_Facility[c] for c in range(Num_Country_Elevators))
    obj -= quicksum(Cost_Country_Stream[c,s] * X_Country_Stream[c,s] for c in range(Num_Country_Elevators)
                                                                     for s in range(Num_Stream_Elevators))
    obj -= quicksum(Cost_Country_Rail[c, r] * X_Country_Rail[c, r] for c in range(Num_Country_Elevators)
                                                                   for r in range(Num_Rail_Elevators))
    obj -= quicksum(Cost_Stream_Export[s, e] * Y_Stream_Export[s, e] for s in range(Num_Stream_Elevators)
                                                                     for e in range(Num_Export_Terminals))
    obj -= quicksum(Cost_Rail_Export[r, e] * Y_Rail_Export[r, e] for r in range(Num_Rail_Elevators)
                                                                 for e in range(Num_Export_Terminals))
    obj -= quicksum(Unit_Holding_Cost*(quicksum(I_Country)+quicksum(I_Rail)+quicksum(I_Stream)))

    model.setObjective(
        obj,
        GRB.MAXIMIZE
    )

    # Compile
    model.update()
    model.params.NonConvex = 2
    model.optimize()
    model.write(Model_Name + '.lp')


if __name__ =='__main__':
    import pandas as pd

    # function parameters
    Model_Name = "Soybean_V13_July-19-2021"
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

    # Export_Terminals to Import_China by Ocean shipment from rail @(e,i)
    #Cost_Export_Import_Rail = pd.read_csv('.\Data\CostRailToOcean.csv', index_col=0).to_numpy()
    #Cost_Export_Import = pd.concat([Cost_Export_Import_Rail, Cost_Export_Import_Stream]).to_numpy()  #merge export terminal together

    # elevators unit holding cost @h
    Unit_Holding_Cost = pd.read_csv('.\Data\CostToFacility.csv', index_col=0,
                           usecols=['Name', 'HoldingCost']).T.to_numpy()[0]

    # Supply of each Country elevator
    Supply_Country = pd.read_csv('.\Data\ProductionByCountry.csv', index_col=0,
                                 usecols=['Name', 'Production']).T.to_numpy()[0]

    # China demand at year 2019
    Demand_China = 88e6

    # last year inventory for each elevator @2019
    Inventory_Country_LastYear = pd.read_csv('.\Data\ProductionByCountry.csv', index_col=0,
                         usecols=['Name', 'Ending']).to_numpy()
    Inventory_Stream_LastYear = np.zeros(Cost_Stream_Export.shape[0])
    Inventory_Rail_LastYear = np.zeros(Cost_Rail_Export.shape[0])

    Get_GuRoBi(Model_Name, Cost_Country_Stream, Cost_Country_Rail, Cost_Stream_Export, Cost_Rail_Export,
               Cost_Export_Import, Cost_Country_Facility, Alpha,
               Unit_Holding_Cost, Demand_China, Supply_Country, Inventory_Country_LastYear,
               Inventory_Stream_LastYear, Inventory_Rail_LastYear)