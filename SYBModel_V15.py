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
import numpy as np
import os
import matplotlib.pyplot as plt
import geopandas as gpd  # read shapefile for map layer

class SYBModel():

    def __init__(self, model_name, year):
        self.root = os.path.abspath('.')  # 'D:\\OneDrive - University of Tennessee\\Scripts\\SYBModel'

        # Parameters
        self.model_name = model_name
        self.year = year
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
        self._load_cost()
        self._load_quantity()
        self._model_inputs_summary()
        self.model = self._build_model()

        # outputs
        self.path = self.root + '/Exps/' + self.model_name + '/' + str(self.year) + '/'
        self._mkdir(self.path)

        self._model_outputs()
        self._write_to_files()

        # plot
        self._plot_logistic_routes()

    def _mkdir(self, path):
        folder = os.path.exists(path)

        if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
            os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径
            print
            "---  new folder...  ---"
            print
            "---  OK  ---"
        else:
            print
            "---  There is this folder!  ---"

    def _load_cost(self):
        # @Datasets normal Scenarios
        # Country_Elevator to Stream_Elevator by Trucks  @(c, s)
        self.Cost_Country_Stream = pd.read_csv(self.root + '\Data\Cost\CostToStreamByTruck.csv', index_col=0).to_numpy()

        # Country_Elevator to Rail_Elevator by Trucks  @(c, r)
        self.Cost_Country_Rail = pd.read_csv(self.root + '\Data\Cost\CostToRailByTruck.csv', index_col=0).to_numpy()

        # Stream_Elevator to Export_Terminals by Barges @(s, e)
        self.Cost_Stream_Export = pd.read_csv(self.root + '\Data\Cost\CostStreamToExport.csv', index_col=0).to_numpy()

        # Rail_Elevator to Export_Terminals by Rail @(r, e)
        self.Cost_Rail_Export = pd.read_csv(self.root + '\Data\Cost\CostRaiToExport.csv', index_col=0).to_numpy()

        # Export_Terminals to Import_China by Ocean shipment from barge @(e,i)
        self.Cost_Export_Import = pd.read_csv(self.root + '\Data\Cost\CostExportToImport.csv', index_col=0).to_numpy()

        # Country_Elevator to Domestic Processing Facility @(P^D)
        self.Cost_Country_Facility = pd.read_csv(self.root + '\Data\Cost\CostToFacility.csv', index_col=0, usecols=['Name', 'Facility']).T.to_numpy()[0]

        # elevators unit holding cost @h
        self.Unit_Holding_Cost = 20

    def _load_quantity(self):
        # Supply of each Country elevator Obtain from GCAM outputs
        # Supply_Country = pd.read_csv('.\Data\ProductionByCountry.csv', index_col=0, usecols=['Name', 'Production']).T.to_numpy()[0]
        self.Yield_Country = pd.read_csv(self.root + '\GCAM_Data\Outputs\ProductionByCountry.csv', index_col=0,
                                    usecols=['Name', 'Yield_IRR_hi', 'Yield_IRR_lo', 'Yield_RFD_hi', 'Yield_RFD_lo',
                                             'PlantingArea']).to_numpy()

        # China demand at year 2020
        self.Demand_China = 88e6

        # last year inventory for each elevator @2019
        # Inventory_Country_LastYear = pd.read_csv('.\Data\ProductionByCountry.csv', index_col=0,
        #                      usecols=['Name', 'Ending']).to_numpy()
        self.Inventory_Country_LastYear = np.zeros(self.Cost_Country_Stream.shape[0])
        self.Inventory_Stream_LastYear = np.zeros(self.Cost_Stream_Export.shape[0])
        self.Inventory_Rail_LastYear = np.zeros(self.Cost_Rail_Export.shape[0])

    def _model_inputs_summary(self):
        ## model input summary
        print(f'Model Name: {self.model_name}')

        NumOfCountry = self.Cost_Country_Stream.shape[0] if self.Cost_Country_Stream.shape[0] == \
                                                            self.Cost_Country_Rail.shape[0] == \
                                                            self.Cost_Country_Facility.shape[0] == self.Yield_Country.shape[0] == \
                                                            self.Inventory_Country_LastYear.shape[0] else 0
        print(f'Country Elevators: {NumOfCountry}')

        NumOfStream = self.Cost_Country_Stream.shape[1] if self.Cost_Country_Stream.shape[1] == \
                                                           self.Cost_Stream_Export.shape[0] \
                                                           == self.Inventory_Stream_LastYear.shape[0] else 0
        print(f'Stream Elevators: {NumOfStream}')

        NumOfRail = self.Cost_Country_Rail.shape[1] if self.Cost_Country_Rail.shape[1] == self.Cost_Rail_Export.shape[0] \
                                                       == self.Inventory_Rail_LastYear.shape[0] else 0
        print(f'Rail Elevators: {NumOfRail}')

        NumOfExport = self.Cost_Stream_Export.shape[1] if self.Cost_Stream_Export.shape[1] == self.Cost_Rail_Export.shape[1] \
                                                     == self.Cost_Export_Import.shape[0] else 0
        print(f'Exports: {NumOfExport}')

        print(f'Imports: {self.Cost_Export_Import.shape[1]}')

    def _build_model(self):
        model = Model(self.model_name)
        self.Num_Country_Elevators = self.Cost_Country_Stream.shape[0]
        self.Num_Stream_Elevators = self.Cost_Stream_Export.shape[0]
        self.Num_Rail_Elevators = self.Cost_Rail_Export.shape[0]
        self.Num_Export_Terminals = self.Cost_Export_Import.shape[0]
        self.Num_Import_Terminals = self.Cost_Export_Import.shape[1]

        ## Variables
        self.Framer_Decision = model.addVars(self.Num_Country_Elevators, 4, vtype=GRB.CONTINUOUS, ub=1,name='Framer_Decision')  # 4 Farmer decisions
        # Framer_Decision = model.addVars(self.Num_Country_Elevators, 4, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='Framer_Decision')     # 4 Farmer decisions
        self.Supply_Country = model.addVars(self.Num_Country_Elevators, vtype=GRB.CONTINUOUS, name='Supplyment')
        self.X_Country_Stream = model.addVars(self.Num_Country_Elevators, self.Num_Stream_Elevators, lb=0, name='X_Country_Stream')
        self.X_Country_Rail = model.addVars(self.Num_Country_Elevators, self.Num_Rail_Elevators, lb=0, name='X_Country_Rail')
        self.X_Facility = model.addVars(self.Num_Country_Elevators, lb=0, name='X_Facility')
        self.I_Country = model.addVars(self.Num_Country_Elevators, lb=0, name='I_Country')
        self.I_Stream = model.addVars(self.Num_Stream_Elevators, lb=0, name='I_Stream')
        self.I_Rail = model.addVars(self.Num_Rail_Elevators, lb=0, name='I_Rail')
        self.Y_Stream_Export = model.addVars(self.Num_Stream_Elevators, self.Num_Export_Terminals, lb=0, name='Y_Stream_Export')
        self.Y_Rail_Export = model.addVars(self.Num_Rail_Elevators, self.Num_Export_Terminals, lb=0, name='Y_Rail_Export')
        self.Z_Export_Import = model.addVars(self.Num_Export_Terminals, self.Num_Import_Terminals, lb=0, name='Z_Export_Import')
        self.Domestic_Price = model.addVar(vtype=GRB.CONTINUOUS, name='Domestic_Price')
        self.Global_Price = model.addVar(vtype=GRB.CONTINUOUS, name='Global_Price')
        self.Slack_Climate = model.addVar(1, vtype=GRB.BINARY, name='Slack_Climate')  # Slack Vars
        self.Slack_Tariff = model.addVar(1, vtype=GRB.BINARY, name='Slack_Tariff')

        ## Constraints
        # 1 Farmer Decisions
        for c in range(self.Num_Country_Elevators):
            model.addConstr(self.Yield_Country[c, 4] * (quicksum(self.Yield_Country[c, d] * self.Framer_Decision[c, d] for d in range(4))) - self.Supply_Country[c] == 0)

            # model.addConstr(Framer_Decision[c,0] + Framer_Decision[c,1] + Framer_Decision[c,2] + Framer_Decision[c,3] <= 1)
            # model.addConstr( Framer_Decision[c,1] + Framer_Decision[c,2] + Framer_Decision[c,3] <= 1)
            model.addConstr(quicksum(self.Framer_Decision[c, d] for d in range(4)) == 1)

            # 2
        for c in range(self.Num_Country_Elevators):
            model.addConstr(self.Alpha * self.Inventory_Country_LastYear[c] + self.Supply_Country[c] - self.X_Facility[c] - self.I_Country[c]
                            - quicksum(self.X_Country_Stream[c, s] for s in range(self.Num_Stream_Elevators))
                            - quicksum(self.X_Country_Rail[c, r] for r in range(self.Num_Rail_Elevators)) == 0)

            # 3
        for s in range(self.Num_Stream_Elevators):
            model.addConstr(self.Alpha * self.Inventory_Stream_LastYear[s] + quicksum(
                self.X_Country_Stream[c, s] for c in range(self.Num_Country_Elevators))
                            - quicksum(self.Y_Stream_Export[s, e] for e in range(self.Num_Export_Terminals)) - self.I_Stream[s] == 0)
            # 4
        for r in range(self.Num_Rail_Elevators):
            model.addConstr(self.Alpha * self.Inventory_Rail_LastYear[r] + quicksum(
                self.X_Country_Rail[c, r] for c in range(self.Num_Country_Elevators))
                            - quicksum(self.Y_Rail_Export[r, e] for e in range(self.Num_Export_Terminals)) - self.I_Rail[r] == 0)

            # 5
        for e in range(self.Num_Export_Terminals):
            model.addConstr(quicksum(self.Y_Stream_Export[s, e] for s in range(self.Num_Stream_Elevators))
                            + quicksum(self.Y_Rail_Export[r, e] for r in range(self.Num_Rail_Elevators))
                            - quicksum(self.Z_Export_Import[e, i] for i in range(self.Num_Import_Terminals)) >= 0)  # here should be >= instead of <= . Dr. Jin is totally wrong!!

            # 6
        model.addConstr(quicksum(self.Z_Export_Import[e, i] for e in range(self.Num_Export_Terminals)
                                 for i in range(self.Num_Import_Terminals)) <= self.Demand_China)

        # 7
        model.addConstr(self.Domestic_Price - self.Beta2 * self.Slack_Climate - self.Beta3 * quicksum(self.I_Country) == self.Beta1)

        # 8
        model.addConstr(self.Global_Price - self.Gamma2 * self.Slack_Tariff - self.Gamma3 * quicksum(self.Z_Export_Import) == self.Gamma1)

        # 9
        model.addConstr(self.Global_Price - self.Domestic_Price >= 0)
        model.addConstrs(self.Alpha * self.Inventory_Country_LastYear[c] + self.Supply_Country[c] - 10 * self.X_Facility[c] >= 0 for c in
                         range(self.Num_Country_Elevators))

        # Objective
        obj = LinExpr()
        obj += quicksum(
            (self.Global_Price - self.Cost_Export_Import[e, i]) * self.Z_Export_Import[e, i] for e in range(self.Num_Export_Terminals)
            for i in range(self.Num_Import_Terminals))
        obj += quicksum(
            (self.Domestic_Price - self.Cost_Country_Facility[c]) * self.X_Facility[c] for c in range(self.Num_Country_Elevators))
        obj -= quicksum(self.Cost_Country_Stream[c, s] * self.X_Country_Stream[c, s] for c in range(self.Num_Country_Elevators)
                        for s in range(self.Num_Stream_Elevators))
        obj -= quicksum(self.Cost_Country_Rail[c, r] * self.X_Country_Rail[c, r] for c in range(self.Num_Country_Elevators)
                        for r in range(self.Num_Rail_Elevators))
        obj -= quicksum(self.Cost_Stream_Export[s, e] * self.Y_Stream_Export[s, e] for s in range(self.Num_Stream_Elevators)
                        for e in range(self.Num_Export_Terminals))
        obj -= quicksum(self.Cost_Rail_Export[r, e] * self.Y_Rail_Export[r, e] for r in range(self.Num_Rail_Elevators)
                        for e in range(self.Num_Export_Terminals))
        obj -= self.Unit_Holding_Cost * (quicksum(self.I_Country) + quicksum(self.I_Rail) + quicksum(self.I_Stream))

        model.setObjective(
            obj,
            GRB.MAXIMIZE
        )

        # Compile
        model.update()
        model.params.NonConvex = 2
        model.optimize()
        # model.write(Model_Name + '.lp')

        # # 查看单目标规划模型的目标函数值
        # print("Optimal Objective Value", model.objVal)
        # # 查看多目标规划模型的目标函数值
        # # for i in range(model.NumObj):
        # #     model.setParam(gurobipy.GRB.Param.ObjNumber, i)
        # #     print(f"Obj {i + 1} = {model.ObjNVal}")
        # # 查看变量取值，这个方法用的很少，请看第 4 部分案例
        # # aaa = model.getVarByName('X_Country_Stream')
        # for var in model.getVars():
        #     if var.X != 0:
        #         print('{0} : {1:.3f}'.format(var.varName, var.X))
        #         print('Objective coefficient of variable: {0:.2f}'.format(var.obj))

        return model

    def _model_outputs(self):
        # Create DataFrame of all results
        self.Matrix_Framer_Decision = [[self.Framer_Decision[a, b].X for a in range(self.Num_Country_Elevators)] for b in range(4)]
        self.Matrix_Framer_Decision = pd.DataFrame(self.Matrix_Framer_Decision).T
        
        self.Matrix_X_Country_Stream = [[self.X_Country_Stream[a, b].X for a in range(self.Num_Country_Elevators)] for b in range(self.Num_Stream_Elevators)]
        self.Matrix_X_Country_Stream = pd.DataFrame(self.Matrix_X_Country_Stream).T
        self.Matrix_X_Country_Stream = self.Matrix_X_Country_Stream.add_prefix('ToRiver_')
        
        self.Matrix_X_Country_Rail = [[self.X_Country_Rail[a, b].X for a in range(self.Num_Country_Elevators)] for b in range(self.Num_Rail_Elevators)]
        self.Matrix_X_Country_Rail = pd.DataFrame(self.Matrix_X_Country_Rail).T
        self.Matrix_X_Country_Rail = self.Matrix_X_Country_Rail.add_prefix('ToRail_')
        
        self.Matrix_X_Facility = [self.X_Facility[a].X for a in range(self.Num_Country_Elevators)]
        self.Matrix_X_Facility = pd.Series(self.Matrix_X_Facility, name='X_Facility')

        self.Matrix_I_Country = [self.I_Country[a].X for a in range(self.Num_Country_Elevators)]
        self.Matrix_I_Country = pd.Series(self.Matrix_I_Country, name='I_Country')
        
        self.Matrix_I_Stream = [self.I_Stream[a].X for a in range(self.Num_Stream_Elevators)]
        self.Matrix_I_Stream = pd.Series(self.Matrix_I_Stream, name='I_Stream')
       
        self.Matrix_I_Rail = [self.I_Rail[a].X for a in range(self.Num_Rail_Elevators)]
        self.Matrix_I_Rail = pd.Series(self.Matrix_I_Rail, name='I_Rail')
        # Matrix_I = pd.DataFrame(list(zip(self.Matrix_X_Facility, self.Matrix_I_Country, self.Matrix_I_Stream, self.Matrix_I_Rail)), columns=['X_Facility','I_Country', 'I_Stream', 'I_Rail'])

        self.Matrix_Y_Stream_Export = [[self.Y_Stream_Export[a, b].X for a in range(self.Num_Stream_Elevators)] for b in range(self.Num_Export_Terminals)]
        self.Matrix_Y_Stream_Export = pd.DataFrame(self.Matrix_Y_Stream_Export).T

        self.Matrix_Y_Rail_Export = [[self.Y_Rail_Export[a, b].X for a in range(self.Num_Rail_Elevators)] for b in range(self.Num_Export_Terminals)]
        self.Matrix_Y_Rail_Export = pd.DataFrame(self.Matrix_Y_Rail_Export).T

        self.Matrix_Supply_Country = [self.Supply_Country[a].X for a in range(self.Num_Country_Elevators)]

        self.Matrix_Z_Export_Import = [[self.Z_Export_Import[a, b].X for a in range(self.Num_Export_Terminals)] for b in range(self.Num_Import_Terminals)]
        self.Matrix_Z_Export_Import = pd.DataFrame(self.Matrix_Z_Export_Import).T.add_prefix('Import_')
        
    def _write_to_files(self):
        # write to file
        self.Results_Country = pd.concat([self.Matrix_X_Country_Stream, self.Matrix_X_Country_Rail, self.Matrix_X_Facility, self.Matrix_I_Country], axis=1)
        self.Results_River = pd.concat([self.Matrix_Y_Stream_Export.add_prefix('RiverToExport_'), self.Matrix_I_Stream], axis=1)
        self.Results_Rail = pd.concat([self.Matrix_Y_Rail_Export.add_prefix('RailToExport_'), self.Matrix_I_Rail], axis=1)

        self.Matrix_Framer_Decision.to_csv(self.path + '1_ResultsOfFramerDecision.csv')
        self.Results_Country.to_csv(self.path + '2_ResultsOfCountryElevators.csv')
        self.Results_River.to_csv(self.path + '3_ResultsOfRiverElevators.csv')
        self.Results_Rail.to_csv(self.path + '4_ResultsOfRailElevators.csv')
        self.Matrix_Z_Export_Import.to_csv(self.path + '5_ResultsOfExports.csv')

    def _plot_logistic_routes(self):

        def Coords(data, index):
            X = data.iloc[index, 1].to_numpy()
            Y = data.iloc[index, 2].to_numpy()
            return np.vstack((X, Y)).T

        ## plot setting
        fig = plt.figure(dpi=300, figsize=(13, 8))
        parameters = {'axes.labelsize': 20,
                      'axes.titlesize': 20,
                      'xtick.labelsize': 20,
                      'ytick.labelsize': 20,
                      'legend.fontsize': 20,
                      }
        plt.rcParams.update(parameters)

        # loading LON and LAT
        self.LocCountryEle = pd.read_csv(self.root + '\GCAM_full/Outputs/Reference/1990/ProductionByCountry.csv', usecols=['Name', 'LON', 'LAT'])
        self.LocRiverEle = pd.read_csv(self.root + "\Scripts\LargerRiverElevators.csv", usecols=['Name', 'X', 'Y'])
        self.LocShuttleEle = pd.read_csv(self.root + "\Scripts\Shuttle tarins and ports.csv", usecols=['Name', 'X', 'Y'])
        self.LocExports = pd.read_csv(self.root + "\Scripts\ExportTerminals.csv", usecols=['Name', 'X', 'Y'])

        ## return non-zero number of facility - 1
        X_Country_River, Y_Country_River = np.nonzero(self.Matrix_X_Country_Stream.values)
        X_Country_Rail, Y_Country_Rail = np.nonzero(self.Matrix_X_Country_Rail.values)
        X_Stream_Export, Y_Stream_Export = np.nonzero(self.Matrix_Y_Stream_Export.values)
        X_Rail_Export, Y_Rail_Export = np.nonzero(self.Matrix_Y_Rail_Export.values)
        X_Export_Import, Y_Export_Import = np.nonzero(self.Matrix_Z_Export_Import.values)

        # check out start and end coords for pair of point
        S_Country_River = Coords(self.LocCountryEle, X_Country_River)
        E_Country_River = Coords(self.LocRiverEle, Y_Country_River)
        S_Country_Rail = Coords(self.LocCountryEle, X_Country_Rail)
        E_Country_Rail = Coords(self.LocShuttleEle, Y_Country_Rail)

        S_River_Export = Coords(self.LocRiverEle, X_Stream_Export)
        E_River_Export = Coords(self.LocExports, Y_Stream_Export)
        S_Rail_Export = Coords(self.LocShuttleEle, X_Rail_Export)
        E_Rail_Export = Coords(self.LocExports, Y_Rail_Export)

        # plotting
        for i in range(len(S_Country_River)):
            plt.plot([S_Country_River[i][0], E_Country_River[i][0]], [S_Country_River[i][1], E_Country_River[i][1]],
                     color='#F05E1C', linestyle='-')

        for i in range(len(S_Country_Rail)):
            plt.plot([S_Country_Rail[i][0], E_Country_Rail[i][0]], [S_Country_Rail[i][1], E_Country_Rail[i][1]],
                     color='#FFB11B', linestyle='-')

        for i in range(len(S_River_Export)):
            plt.plot([S_River_Export[i][0], E_River_Export[i][0]], [S_River_Export[i][1], E_River_Export[i][1]],
                     color='#F05E1C', linewidth=2)
            # plt.annotate(r'1112', xy=(E_River_Export[i][0], E_River_Export[i][1]), textcoords='offset points')

        for i in range(len(S_Rail_Export)):
            plt.plot([S_Rail_Export[i][0], E_Rail_Export[i][0]], [S_Rail_Export[i][1], E_Rail_Export[i][1]],
                     color='#FFB11B', linewidth=2)

        plt.scatter(self.LocCountryEle['LON'].to_numpy(), self.LocCountryEle['LAT'].to_numpy(), label='Country Elevators', color='#7bb207', s=30, zorder=5)
        # plt.scatter(LocCountryEle['LON'].to_numpy(), LocCountryEle['LAT'].to_numpy(), label='Country Elevators', color=colors,s=30, zorder=5)
        plt.scatter(self.LocRiverEle['X'].to_numpy(), self.LocRiverEle['Y'].to_numpy(), label='River Elevators', color='#F05E1C', s=50, zorder=5)
        plt.scatter(self.LocShuttleEle['X'].to_numpy(), self.LocShuttleEle['Y'].to_numpy(), label='Rail Elevators', color='#FFB11B', s=50, zorder=5)
        plt.scatter(self.LocExports['X'].to_numpy(), self.LocExports['Y'].to_numpy(), label='Export Terminals', color='#006284', s=80, zorder=5)

        ## mapping base layer
        ax = fig.gca()
        USA = gpd.read_file(self.root + '/Shapefiles/cb_2018_us_state_20m.shp')
        # States = USA.STUSPS.tolist()
        Outside = ['AK', 'HI', 'PR']
        States = [state for state in USA.STUSPS.tolist() if state not in Outside]
        # USA.plot()
        USA[USA['STUSPS'].isin(States)].boundary.plot(ax=ax, color='#828282', zorder=-1)

        ## fig setting
        plt.legend(loc='lower left', markerscale=1.2)
        # plt.xlabel("LONGITUDE")
        # plt.ylabel("LATITUDE")
        # plt.title(r'$p^D:$'+str(round(Domestic_Price,2)) + ' $p^G:$'+ str(round(Global_Price,2)) + ' Supply:'+ str(int(Total_Supply_Country)) + ' Exported:' + str(int(Total_Exported)))
        # Exported_Rate = round((Total_Exported / sum(Supply_Country)) * 100, 2)
        # # plt.title(r'$p^D:$'+str(round(Domestic_Price,2)) + ' $p^G:$'+ str(round(Global_Price,2)) + ' Exported: '+ str(Exported_Rate)+'%')
        # plt.title(r'Export:' + format(Total_Exported, '.2e') + ' Supply:' + format(sum(Supply_Country),
        #                                                                            '.2e') + ' Export/Supply: ' + str(
        #     Exported_Rate) + '%')

        ax.set_axis_off()  # hide the axis

        plt.savefig(self.path + self.model_name + '.png', dpi=300)
        plt.show()


if __name__ =='__main__':

    scenario = "Soybean_V13_test"
    year = 2020
    ## Solving by GUROBI Model
    Model = SYBModel(scenario, year)
