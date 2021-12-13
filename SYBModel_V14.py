#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/07/2021 3:22 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : SYBModel_V13SYBModel_V13.py
# @Software: PyCharm
# @Notes   : GUROBI code for the SYBModel V13
import numpy as np
from gurobipy import *
import pandas as pd

def Get_GuRoBi(Model_Name, Cost_Country_Stream, Cost_Country_Rail, Cost_Stream_Export, Cost_Rail_Export,
               Cost_Export_Import, Cost_Country_Facility, Alpha, Unit_Holding_Cost, Demand_China,
               Yield_Country, Inventory_Country_LastYear, Inventory_Stream_LastYear, Inventory_Rail_LastYear):
    # Parameters
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
    X_Country_Stream = model.addVars(Num_Country_Elevators, Num_Stream_Elevators, lb=0, name='X_Country_Stream')
    X_Country_Rail = model.addVars(Num_Country_Elevators, Num_Rail_Elevators, lb=0, name='X_Country_Rail')
    X_Facility = model.addVars(Num_Country_Elevators, lb=0, name='X_Facility')
    I_Country = model.addVars(Num_Country_Elevators, lb=0, name='I_Country')
    I_Stream = model.addVars(Num_Stream_Elevators, lb=0, name='I_Stream')
    I_Rail = model.addVars(Num_Rail_Elevators, lb=0, name='I_Rail')
    Y_Stream_Export = model.addVars(Num_Stream_Elevators, Num_Export_Terminals, lb=0, name='Y_Stream_Export')
    Y_Rail_Export = model.addVars(Num_Rail_Elevators, Num_Export_Terminals, lb=0, name='Y_Rail_Export')
    Z_Export_Import = model.addVars(Num_Export_Terminals, Num_Import_Terminals, lb=0 , name='Z_Export_Import')
    Domestic_Price = model.addVar(vtype=GRB.CONTINUOUS, name='Domestic_Price')
    Global_Price = model.addVar(vtype=GRB.CONTINUOUS, name='Global_Price')
    Slack_Climate = model.addVar(1, vtype=GRB.BINARY, name='Slack_Climate')     # Slack Vars
    Slack_Tariff = model.addVar(1, vtype=GRB.BINARY, name='Slack_Tariff')
    # Farmer decisions
    Framer_Decision = model.addVars(Num_Country_Elevators, 4, vtype=GRB.CONTINUOUS, name='Framer_Decision')
    Supply_Country = model.addVars(Num_Country_Elevators, vtype=GRB.CONTINUOUS, name='Supplyment')

    # Constraints
        # 1 Farmer Decisions
    for c in range(Num_Country_Elevators):
        model.addConstr((Yield_Country[c,0]*Framer_Decision[c,0]+Yield_Country[c,1]*Framer_Decision[c,1]+Yield_Country[c,2]*Framer_Decision[c,2]+
        Yield_Country[c, 3] * Framer_Decision[c, 3])*Yield_Country[c, 4] - Supply_Country[c] == 0)

        model.addConstr(quicksum(Framer_Decision[c,d] for d in range(4)) == 1 )

        # 2
    for c in range(Num_Country_Elevators):
        model.addConstr(Alpha * Inventory_Country_LastYear[c] + Supply_Country[c] - X_Facility[c] - I_Country[c]
                        - quicksum(X_Country_Stream[c, s] for s in range(Num_Stream_Elevators))
                        - quicksum(X_Country_Rail[c, r] for r in range(Num_Rail_Elevators)) == 0)

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
                        - quicksum(Z_Export_Import[e, i] for i in range(Num_Import_Terminals)) >= 0)  # here should be >= instead of <= . Dr. Jin is totally wrong!!

        # 6
    model.addConstr(quicksum(Z_Export_Import[e,i] for e in range(Num_Export_Terminals)
                                                  for i in range(Num_Import_Terminals)) <= Demand_China)

        # 7
    model.addConstr(Domestic_Price - Beta2 * Slack_Climate - Beta3 * quicksum(I_Country) == Beta1)

        # 8
    model.addConstr(Global_Price - Gamma2 * Slack_Tariff - Gamma3 * quicksum(Z_Export_Import) == Gamma1)

        # 9
    model.addConstr(Global_Price - Domestic_Price >= 0)
    model.addConstrs(Alpha * Inventory_Country_LastYear[c] + Supply_Country[c] - 10 * X_Facility[c] >= 0 for c in range(Num_Country_Elevators))

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
    obj -= Unit_Holding_Cost*(quicksum(I_Country)+quicksum(I_Rail)+quicksum(I_Stream))

    model.setObjective(
        obj,
        GRB.MAXIMIZE
    )

    # Compile
    model.update()
    model.params.NonConvex = 2
    model.optimize()
    # model.write(Model_Name + '.lp')

    # 查看单目标规划模型的目标函数值
    print("Optimal Objective Value", model.objVal)
    # 查看多目标规划模型的目标函数值
    # for i in range(model.NumObj):
    #     model.setParam(gurobipy.GRB.Param.ObjNumber, i)
    #     print(f"Obj {i + 1} = {model.ObjNVal}")
    # 查看变量取值，这个方法用的很少，请看第 4 部分案例
    for var in model.getVars():
        if var.X != 0:
            print(f"{var.varName}: {round(var.X, 3)}")

    # Create DataFrame of all results
    Matrix_X_Country_Stream = [[X_Country_Stream[a, b].X for a in range(Num_Country_Elevators)] for b in range(Num_Stream_Elevators)]
    Matrix_X_Country_Stream = pd.DataFrame(Matrix_X_Country_Stream).T
    Matrix_X_Country_Stream = Matrix_X_Country_Stream.add_prefix('ToRiver_')
    Matrix_X_Country_Rail = [[X_Country_Rail[a, b].X for a in range(Num_Country_Elevators)] for b in range(Num_Rail_Elevators)]
    Matrix_X_Country_Rail= pd.DataFrame(Matrix_X_Country_Rail).T
    Matrix_X_Country_Rail = Matrix_X_Country_Rail.add_prefix('ToRail_')
    Matrix_X_Facility = [X_Facility[a].X for a in range(Num_Country_Elevators)]
    Matrix_X_Facility= pd.Series(Matrix_X_Facility, name='X_Facility')

    Matrix_I_Country = [I_Country[a].X for a in range(Num_Country_Elevators)]
    Matrix_I_Country= pd.Series(Matrix_I_Country, name='I_Country')
    Matrix_I_Stream = [I_Stream[a].X for a in range(Num_Stream_Elevators)]
    Matrix_I_Stream= pd.Series(Matrix_I_Stream, name='I_Stream')
    Matrix_I_Rail = [I_Rail[a].X for a in range(Num_Rail_Elevators)]
    Matrix_I_Rail= pd.Series(Matrix_I_Rail, name='I_Rail')
    #Matrix_I = pd.DataFrame(list(zip(Matrix_X_Facility, Matrix_I_Country, Matrix_I_Stream, Matrix_I_Rail)), columns=['X_Facility','I_Country', 'I_Stream', 'I_Rail'])

    Matrix_Y_Stream_Export = [[Y_Stream_Export[a, b].X for a in range(Num_Stream_Elevators)] for b in range(Num_Export_Terminals)]
    Matrix_Y_Stream_Export= pd.DataFrame(Matrix_Y_Stream_Export).T
    Matrix_Y_Rail_Export = [[Y_Rail_Export[a, b].X for a in range(Num_Rail_Elevators)] for b in range(Num_Export_Terminals)]
    Matrix_Y_Rail_Export= pd.DataFrame(Matrix_Y_Rail_Export).T

    Matrix_Z_Export_Import = [[Z_Export_Import[a, b].X for a in range(Num_Export_Terminals)] for b in range(Num_Import_Terminals)]
    Matrix_Z_Export_Import= pd.DataFrame(Matrix_Z_Export_Import).T.add_prefix('Import_')

    # write to file
    Results_Country = pd.concat([Matrix_X_Country_Stream, Matrix_X_Country_Rail, Matrix_X_Facility, Matrix_I_Country], axis=1)
    Results_River = pd.concat([Matrix_Y_Stream_Export.add_prefix('RiverToExport_'), Matrix_I_Stream], axis=1)
    Results_Rail = pd.concat([Matrix_Y_Rail_Export.add_prefix('RailToExport_'), Matrix_I_Rail], axis=1)

    Results_Country.to_csv('.\Outputs\ResultsOfCountryElevators.csv')
    Results_River.to_csv('.\Outputs\ResultsOfRiverElevators.csv')
    Results_Rail.to_csv('.\Outputs\ResultsOfRailElevators.csv')
    Matrix_Z_Export_Import.to_csv('.\Outputs\ResultsOfExports.csv')

    return Matrix_X_Country_Stream, Matrix_X_Country_Rail, Matrix_X_Facility, Matrix_I_Country, Matrix_I_Stream, Matrix_I_Rail, \
           Matrix_Y_Stream_Export, Matrix_Y_Rail_Export, Matrix_Z_Export_Import, Domestic_Price.X, Global_Price.X, Matrix_Z_Export_Import.sum().sum()

if __name__ =='__main__':
    import numpy as np

    # A Small Demo
    # function parameters
    Model_Name = "Soybean_V13_test"
    Year = 'Demo'
    Alpha = 0.99

    # @Datasets
    # Country_Elevator to Stream_Elevator by Trucks  @(c, s)
    Cost_Country_Stream = np.array([[20, 50], [55, 56], [33, 22]])

    # Country_Elevator to Rail_Elevator by Trucks  @(c, r)
    Cost_Country_Rail = np.array([[20, 45, 60], [55, 50, 30], [44, 33, 22]])

    # Stream_Elevator to Export_Terminals by Barges @(s, e)
    Cost_Stream_Export = np.array([[60, 80, 79, 82], [67, 70, 68, 69]])

    # Rail_Elevator to Export_Terminals by Rail @(r, e)
    Cost_Rail_Export = np.array([[60, 80, 79, 82], [67, 70, 68, 69], [66, 80, 76, 77]])

    # Export_Terminals to Import_China by Ocean shipment from barge @(e,i)
    Cost_Export_Import = np.array([[100, 110], [109, 119], [125, 136], [133, 145]])

    # Country_Elevator to Domestic Processing Facility @(P^D)
    Cost_Country_Facility = np.array([15, 16, 15])

    # elevators unit holding cost @h
    Unit_Holding_Cost = 50

    # Supply of each Country elevator
    Supply_Country = np.array([65650, 90900, 80800])

    # China demand at year 2019
    Demand_China = 205500

    # last year inventory for each elevator @2019
    Inventory_Country_LastYear = np.array([6565, 9090, 8080])
    Inventory_Stream_LastYear = np.array([0, 0])
    Inventory_Rail_LastYear = np.array([0, 0, 0])

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

    Get_GuRoBi(Model_Name, Cost_Country_Stream, Cost_Country_Rail, Cost_Stream_Export, Cost_Rail_Export,
                  Cost_Export_Import, Cost_Country_Facility, Alpha,
                  Unit_Holding_Cost, Demand_China, Supply_Country, Inventory_Country_LastYear,
                  Inventory_Stream_LastYear, Inventory_Rail_LastYear)