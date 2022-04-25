#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/07/2021 3:22 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : SYBModel_V13SYBModel_V13.py
# @Software: PyCharm
# @Notes   : GUROBI code for the SYBModel V14 model (with Object-oriented programming)
import numpy as np
from gurobipy import *
import pandas as pd

class SYBModel():

    def __init__(self, model_name, Cost_Country_Stream, Cost_Country_Rail, Cost_Stream_Export, Cost_Rail_Export,
               Cost_Export_Import, Cost_Country_Facility, Unit_Holding_Cost, Demand_China,
               Yield_Country, Inventory_Country_LastYear, Inventory_Stream_LastYear, Inventory_Rail_LastYear):
        # Parameters
        self.name = model_name
        self.Alpha = 0.99
        # Dom_P =  200   # Domestic Soybean price
        self.Beta1 = 315.948
        self.Beta2 = 0
        self.Beta3 = -4.43476  # Regression coefficients

        # Glo_P =  400   # Global Soybean price
        self.Gamma1 = 117.09
        self.Gamma2 = 0
        self.Gamma3 = 5.6e-6  # Regression coefficients

        # build model
        self.results = self._build_model(Cost_Country_Stream, Cost_Country_Rail, Cost_Stream_Export, Cost_Rail_Export,
                                         Cost_Export_Import, Cost_Country_Facility, Unit_Holding_Cost, Demand_China,
                                         Yield_Country, Inventory_Country_LastYear, Inventory_Stream_LastYear, Inventory_Rail_LastYear)

    def _build_model(self, Cost_Country_Stream, Cost_Country_Rail, Cost_Stream_Export, Cost_Rail_Export,
               Cost_Export_Import, Cost_Country_Facility, Unit_Holding_Cost, Demand_China,
               Yield_Country, Inventory_Country_LastYear, Inventory_Stream_LastYear, Inventory_Rail_LastYear):

        model = Model(self.name)
        Num_Country_Elevators = Cost_Country_Stream.shape[0]
        Num_Stream_Elevators = Cost_Stream_Export.shape[0]
        Num_Rail_Elevators = Cost_Rail_Export.shape[0]
        Num_Export_Terminals = Cost_Export_Import.shape[0]
        Num_Import_Terminals = Cost_Export_Import.shape[1]

        ## Variables
        Framer_Decision = model.addVars(Num_Country_Elevators, 4, vtype=GRB.CONTINUOUS, ub=1,name='Framer_Decision')  # 4 Farmer decisions
        # Framer_Decision = model.addVars(Num_Country_Elevators, 4, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='Framer_Decision')     # 4 Farmer decisions
        Supply_Country = model.addVars(Num_Country_Elevators, vtype=GRB.CONTINUOUS, name='Supplyment')
        X_Country_Stream = model.addVars(Num_Country_Elevators, Num_Stream_Elevators, lb=0, name='X_Country_Stream')
        X_Country_Rail = model.addVars(Num_Country_Elevators, Num_Rail_Elevators, lb=0, name='X_Country_Rail')
        X_Facility = model.addVars(Num_Country_Elevators, lb=0, name='X_Facility')
        I_Country = model.addVars(Num_Country_Elevators, lb=0, name='I_Country')
        I_Stream = model.addVars(Num_Stream_Elevators, lb=0, name='I_Stream')
        I_Rail = model.addVars(Num_Rail_Elevators, lb=0, name='I_Rail')
        Y_Stream_Export = model.addVars(Num_Stream_Elevators, Num_Export_Terminals, lb=0, name='Y_Stream_Export')
        Y_Rail_Export = model.addVars(Num_Rail_Elevators, Num_Export_Terminals, lb=0, name='Y_Rail_Export')
        Z_Export_Import = model.addVars(Num_Export_Terminals, Num_Import_Terminals, lb=0, name='Z_Export_Import')
        Domestic_Price = model.addVar(vtype=GRB.CONTINUOUS, name='Domestic_Price')
        Global_Price = model.addVar(vtype=GRB.CONTINUOUS, name='Global_Price')
        Slack_Climate = model.addVar(1, vtype=GRB.BINARY, name='Slack_Climate')  # Slack Vars
        Slack_Tariff = model.addVar(1, vtype=GRB.BINARY, name='Slack_Tariff')

        ## Constraints
        # 1 Farmer Decisions
        for c in range(Num_Country_Elevators):
            # model.addConstr((Yield_Country[c,0]*Framer_Decision[c,0]+Yield_Country[c,1]*Framer_Decision[c,1]+Yield_Country[c,2]*Framer_Decision[c,2]+
            # Yield_Country[c,3]*Framer_Decision[c,3])*Yield_Country[c,4] - Supply_Country[c] == 0)
            model.addConstr(
                Yield_Country[c, 4] * (quicksum(Yield_Country[c, d] * Framer_Decision[c, d] for d in range(4))) -
                Supply_Country[c] == 0)

            # model.addConstr(Framer_Decision[c,0] + Framer_Decision[c,1] + Framer_Decision[c,2] + Framer_Decision[c,3] <= 1)
            # model.addConstr( Framer_Decision[c,1] + Framer_Decision[c,2] + Framer_Decision[c,3] <= 1)
            model.addConstr(quicksum(Framer_Decision[c, d] for d in range(4)) == 1)

            # 2
        for c in range(Num_Country_Elevators):
            model.addConstr(self.Alpha * Inventory_Country_LastYear[c] + Supply_Country[c] - X_Facility[c] - I_Country[c]
                            - quicksum(X_Country_Stream[c, s] for s in range(Num_Stream_Elevators))
                            - quicksum(X_Country_Rail[c, r] for r in range(Num_Rail_Elevators)) == 0)

            # 3
        for s in range(Num_Stream_Elevators):
            model.addConstr(self.Alpha * Inventory_Stream_LastYear[s] + quicksum(
                X_Country_Stream[c, s] for c in range(Num_Country_Elevators))
                            - quicksum(Y_Stream_Export[s, e] for e in range(Num_Export_Terminals)) - I_Stream[s] == 0)
            # 4
        for r in range(Num_Rail_Elevators):
            model.addConstr(self.Alpha * Inventory_Rail_LastYear[r] + quicksum(
                X_Country_Rail[c, r] for c in range(Num_Country_Elevators))
                            - quicksum(Y_Rail_Export[r, e] for e in range(Num_Export_Terminals)) - I_Rail[r] == 0)

            # 5
        for e in range(Num_Export_Terminals):
            model.addConstr(quicksum(Y_Stream_Export[s, e] for s in range(Num_Stream_Elevators))
                            + quicksum(Y_Rail_Export[r, e] for r in range(Num_Rail_Elevators))
                            - quicksum(Z_Export_Import[e, i] for i in range(
                Num_Import_Terminals)) >= 0)  # here should be >= instead of <= . Dr. Jin is totally wrong!!

            # 6
        model.addConstr(quicksum(Z_Export_Import[e, i] for e in range(Num_Export_Terminals)
                                 for i in range(Num_Import_Terminals)) <= Demand_China)

        # 7
        model.addConstr(Domestic_Price - self.Beta2 * Slack_Climate - self.Beta3 * quicksum(I_Country) == self.Beta1)

        # 8
        model.addConstr(Global_Price - self.Gamma2 * Slack_Tariff - self.Gamma3 * quicksum(Z_Export_Import) == self.Gamma1)

        # 9
        model.addConstr(Global_Price - Domestic_Price >= 0)
        model.addConstrs(self.Alpha * Inventory_Country_LastYear[c] + Supply_Country[c] - 10 * X_Facility[c] >= 0 for c in
                         range(Num_Country_Elevators))

        # Objective
        obj = LinExpr()
        obj += quicksum(
            (Global_Price - Cost_Export_Import[e, i]) * Z_Export_Import[e, i] for e in range(Num_Export_Terminals)
            for i in range(Num_Import_Terminals))
        obj += quicksum(
            (Domestic_Price - Cost_Country_Facility[c]) * X_Facility[c] for c in range(Num_Country_Elevators))
        obj -= quicksum(Cost_Country_Stream[c, s] * X_Country_Stream[c, s] for c in range(Num_Country_Elevators)
                        for s in range(Num_Stream_Elevators))
        obj -= quicksum(Cost_Country_Rail[c, r] * X_Country_Rail[c, r] for c in range(Num_Country_Elevators)
                        for r in range(Num_Rail_Elevators))
        obj -= quicksum(Cost_Stream_Export[s, e] * Y_Stream_Export[s, e] for s in range(Num_Stream_Elevators)
                        for e in range(Num_Export_Terminals))
        obj -= quicksum(Cost_Rail_Export[r, e] * Y_Rail_Export[r, e] for r in range(Num_Rail_Elevators)
                        for e in range(Num_Export_Terminals))
        obj -= Unit_Holding_Cost * (quicksum(I_Country) + quicksum(I_Rail) + quicksum(I_Stream))

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
        # aaa = model.getVarByName('X_Country_Stream')
        for var in model.getVars():
            if var.X != 0:
                print('{0} : {1:.3f}'.format(var.varName, var.X))
                print('Objective coefficient of variable: {0:.2f}'.format(var.obj))

        return model.objVal


if __name__ =='__main__':
    import numpy as np
    import os

    root = os.path.abspath('.')  # 'D:\\OneDrive - University of Tennessee\\Scripts\\SYBModel'
    model_name = "Soybean_V13_test"

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

    # Supply of each Country elevator
    # Supply_Country = pd.read_csv('.\Data\ProductionByCountry.csv', index_col=0, usecols=['Name', 'Production']).T.to_numpy()[0]
    Yield_Country = pd.read_csv(root + '\GCAM_Data\Outputs\ProductionByCountry.csv', index_col=0,
                                usecols=['Name', 'Yield_IRR_hi', 'Yield_IRR_lo', 'Yield_RFD_hi', 'Yield_RFD_lo',
                                         'PlantingArea']).to_numpy()

    # China demand at year 2020
    Demand_China = 88e6

    # last year inventory for each elevator @2019
    # Inventory_Country_LastYear = pd.read_csv('.\Data\ProductionByCountry.csv', index_col=0,
    #                      usecols=['Name', 'Ending']).to_numpy()
    Inventory_Country_LastYear = np.zeros(Cost_Country_Stream.shape[0])
    Inventory_Stream_LastYear = np.zeros(Cost_Stream_Export.shape[0])
    Inventory_Rail_LastYear = np.zeros(Cost_Rail_Export.shape[0])

    ## model input summary
    print(f'Model Name: {model_name}')
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
    Model = SYBModel(model_name, Cost_Country_Stream,
        Cost_Country_Rail, Cost_Stream_Export,
        Cost_Rail_Export, Cost_Export_Import,
        Cost_Country_Facility, Unit_Holding_Cost,
        Demand_China, Yield_Country,
        Inventory_Country_LastYear, Inventory_Stream_LastYear, Inventory_Rail_LastYear)

    a =1