#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 26/04/2022 10:46 AM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : SYBModel_V16.py
# @Software: PyCharm
# @Notes   :

import pandas as pd
import numpy as np
from GCAM_full.Get_DemandTariff import China_Demand # with init file
from GCAM_full.operation_cost import OperationCost
import matplotlib.pyplot as plt
import geopandas as gpd  # read shapefile for map layer
import os
from gurobipy import *
# import seaborn as sns
# sns.set_theme()

class GCAM_SYB():
    def __init__(self, model_name, year, china_demand, figs, tax, **kwargs):
        # Parameters
        self.root = os.path.abspath('.')  # 'D:\\OneDrive - University of Tennessee\\Scripts\\SYBModel'
        self.model_name = model_name
        self.year = year
        self.china_demand = china_demand
        self.tax = tax
        self.holding_cost = 50  # $/ton
        self.IRR_lo = kwargs['IRR_lo']
        self.IRR_hi = kwargs['IRR_hi']
        self.RFD_lo = kwargs['RFD_lo']
        self.RFD_hi = kwargs['RFD_hi']
        self.truck_rate = kwargs['truck_rate']
        self.barge_rate = kwargs['barge_rate']
        self.rail_rate = kwargs['rail_rate']
        self.ocean_rate = kwargs['ocean_rate']
        self.scenario_text = str(self.truck_rate) + '_' + str(self.barge_rate) + '_' + str(self.rail_rate) + '_' + str(self.ocean_rate)

        # build model
        self._load_cost(self.truck_rate, self.barge_rate, self.rail_rate, self.ocean_rate)
        self._load_quantity()
        self._model_inputs_summary()

        try:
            self._build_model(lp_to_file=False)
        except GurobiError as e:
            print('Error code ' + str(e.errno) + ": " + str(e))

        if self.model.Status == 2:
            print('\033[1;32m Model solved successfully \033[0m')
            # outputs
            self.path = self.root + '/Exps/' + self.model_name + '/' + str(self.year) + '/'
            self._mkdir(self.path)

            self._model_outputs()
            self._write_to_files()

            # plot
            self._plot_logistic_routes(figs)

        else:
            print('\033[1;31m Model failed \033[0m')

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

    def _load_cost(self, truck_rate, barge_rate, rail_rate, ocean_rate):
        # @Datasets normal Scenarios
        # Country_Elevator to Stream_Elevator by Trucks  @(c, s)
        self.Cost_Country_Stream = pd.read_csv(self.root + '\Data\Cost\CostToStreamByTruck.csv', index_col=0).to_numpy() * truck_rate

        # Country_Elevator to Rail_Elevator by Trucks  @(c, r)
        self.Cost_Country_Rail = pd.read_csv(self.root + '\Data\Cost\CostToRailByTruck.csv', index_col=0).to_numpy() * truck_rate

        # Stream_Elevator to Export_Terminals by Barges @(s, e)
        self.Cost_Stream_Export = pd.read_csv(self.root + '\Data\Cost\CostStreamToExport.csv', index_col=0).to_numpy() * barge_rate

        # Rail_Elevator to Export_Terminals by Rail @(r, e)
        self.Cost_Rail_Export = pd.read_csv(self.root + '\Data\Cost\CostRaiToExport.csv', index_col=0).to_numpy() * rail_rate

        # Export_Terminals to Import_China by Ocean shipment from barge @(e,i)
        self.Cost_Export_Import = pd.read_csv(self.root + '\Data\Cost\CostExportToImport.csv', index_col=0).to_numpy() * ocean_rate

        # Country_Elevator to Domestic Processing Facility @(P^D)
        self.Cost_Country_Facility = pd.read_csv(self.root + '\Data\Cost\CostToFacility.csv', index_col=0, usecols=['Name', 'Facility']).T.to_numpy()[0] * truck_rate

    def _load_quantity(self):
        self.input_path = self.root + '/GCAM_full/Outputs/' + self.model_name + '/' + str(self.year) + '/ProductionByCountry.csv'
        self.Yield_Country = pd.read_csv(self.input_path, index_col=0, usecols=['Name', 'Yield_IRR_hi', 'Yield_IRR_lo', 'Yield_RFD_hi', 'Yield_RFD_lo', 'PlantingArea(km2)']).to_numpy()

        # China demand at year 2020
        if self.tax:
            self.Demand_China = self.china_demand * 0.5
            self.Demand_ROW = 0.8 * self.Demand_China * 1.2
        else:
            self.Demand_China = self.china_demand
            self.Demand_ROW = 0.8 * self.Demand_China

        self.tau = 60.621       # 1.65 * 36.74 /tou

        # self.Inventory_Country_LastYear = np.zeros(self.Cost_Country_Stream.shape[0])
        self.Inventory_Country = pd.read_csv(self.input_path, usecols=['Ending']).to_numpy()
        # self.Inventory_Stream_LastYear = np.zeros(self.Cost_Stream_Export.shape[0])
        # self.Inventory_Rail_LastYear = np.zeros(self.Cost_Rail_Export.shape[0])

    def _model_inputs_summary(self):
        ## model input summary
        print(f'\033[1;31m Model Name: {self.model_name + "_" + str(self.year)}')

        self.Num_Country_Elevators = self.Cost_Country_Stream.shape[0] if self.Cost_Country_Stream.shape[0] == \
                                                            self.Cost_Country_Rail.shape[0] == \
                                                            self.Cost_Country_Facility.shape[0] == self.Yield_Country.shape[0] == \
                                                            self.Inventory_Country.shape[0] else 0
        print(f'Country Elevators: {self.Num_Country_Elevators}')

        self.Num_Stream_Elevators = self.Cost_Country_Stream.shape[1] if self.Cost_Country_Stream.shape[1] == \
                                                           self.Cost_Stream_Export.shape[0] else 0
        print(f'Stream Elevators: {self.Num_Stream_Elevators}')

        self.Num_Rail_Elevators = self.Cost_Country_Rail.shape[1] if self.Cost_Country_Rail.shape[1] == self.Cost_Rail_Export.shape[0] else 0
        print(f'Rail Elevators: {self.Num_Rail_Elevators}')

        self.Num_Export_Terminals = self.Cost_Stream_Export.shape[1] if self.Cost_Stream_Export.shape[1] == self.Cost_Rail_Export.shape[1] \
                                                     == self.Cost_Export_Import.shape[0] else 0
        print(f'Exports: {self.Num_Export_Terminals}')

        self.Num_Import_Terminals = self.Cost_Export_Import.shape[1]
        print(f'Imports: {self.Num_Import_Terminals}\033[0m')

    def _build_model(self, lp_to_file=False):
        self.model = Model(self.model_name)

        # Variables
        self.Framer_Decision = self.model.addVars(self.Num_Country_Elevators, 4, vtype=GRB.BINARY, name='Framer_Decision')     # 4 Farmer decisions
        self.Supply_Country = self.model.addVars(self.Num_Country_Elevators, vtype=GRB.CONTINUOUS, name='Supplyment')
        self.X_Country_Stream = self.model.addVars(self.Num_Country_Elevators, self.Num_Stream_Elevators, lb=0, name='X_Country_Stream')
        self.X_Country_Rail = self.model.addVars(self.Num_Country_Elevators, self.Num_Rail_Elevators, lb=0, name='X_Country_Rail')
        self.X_Facility = self.model.addVars(self.Num_Country_Elevators, lb=0, name='X_Facility')
        # self.I_Country = self.model.addVars(self.Num_Country_Elevators, lb=0, name='I_Country')
        # self.I_Stream = self.model.addVars(self.Num_Stream_Elevators, lb=0, name='I_Stream')
        # self.I_Rail = self.model.addVars(self.Num_Rail_Elevators, lb=0, name='I_Rail')
        self.Y_Stream_Export = self.model.addVars(self.Num_Stream_Elevators, self.Num_Export_Terminals, lb=0, name='Y_Stream_Export')
        self.Y_Rail_Export = self.model.addVars(self.Num_Rail_Elevators, self.Num_Export_Terminals, lb=0, name='Y_Rail_Export')
        self.Z_Export_Import = self.model.addVars(self.Num_Export_Terminals, self.Num_Import_Terminals, lb=0, name='Z_Export_Import')
        self.D_Price = self.model.addVar(vtype=GRB.CONTINUOUS, name='Domestic_Price')
        self.C_Price = self.model.addVar(vtype=GRB.CONTINUOUS, name='Global_Price')
        self.R_Price = self.model.addVar(vtype=GRB.CONTINUOUS, name='Global_Price')


        ## Constraints
        # 1 Farmer Decisions
        for c in range(self.Num_Country_Elevators):
            self.model.addConstr(self.Yield_Country[c, 4] * (quicksum(self.Yield_Country[c, d] * self.Framer_Decision[c, d] for d in range(4))) - self.Supply_Country[c] == 0)

            # model.addConstr(Framer_Decision[c,0] + Framer_Decision[c,1] + Framer_Decision[c,2] + Framer_Decision[c,3] <= 1)
            self.model.addConstr(quicksum(self.Framer_Decision[c, d] for d in range(4)) == 1)

        # 2 Supplyment
        for c in range(self.Num_Country_Elevators):
            self.model.addConstr(self.Supply_Country[c] - quicksum(self.X_Country_Stream[c, s] for s in range(self.Num_Stream_Elevators)) - quicksum(self.X_Country_Rail[c, r] for r in range(self.Num_Rail_Elevators))
                                 - self.X_Facility[c] - self.Inventory_Country[c] == 0)

        # 3 X_Country_Stream
        for s in range(self.Num_Stream_Elevators):
            self.model.addConstr(quicksum(self.X_Country_Stream[c, s] for c in range(self.Num_Country_Elevators)) -
                                 quicksum(self.Y_Stream_Export[s, k] for k in range(self.Num_Export_Terminals))  == 0)

        # 4 X_Country_Rail
        for r in range(self.Num_Rail_Elevators):
            self.model.addConstr(quicksum(self.X_Country_Rail[c,r] for c in range(self.Num_Country_Elevators)) -
                                          quicksum(self.Y_Rail_Export[r, k] for k in range(self.Num_Export_Terminals)) == 0)

        # 5 Y_Stream_Rail_Export
        for k in range(self.Num_Export_Terminals):
            self.model.addConstr(quicksum(self.Y_Stream_Export[s, k] for s in range(self.Num_Stream_Elevators)) + quicksum(self.Y_Rail_Export[r, k] for r in range(self.Num_Rail_Elevators))
                                 - quicksum(self.Z_Export_Import[k, m] for m in range(self.Num_Import_Terminals)) == 0)

        # 6 Z_Export_Import
        self.model.addConstr(quicksum(self.Z_Export_Import[k, m] for k in range(self.Num_Export_Terminals) for m in range(self.Num_Import_Terminals)) >= self.Demand_China + self.Demand_ROW)

        # 7 additional_constraints for the objective function
        for c in range(self.Num_Country_Elevators):
            self.model.addConstr(self.Supply_Country[c] * 0.30 - self.X_Facility[c] >= 0)


        # Objective
        cost = LinExpr()
        cost += quicksum(self.Cost_Export_Import[k, m] * self.Z_Export_Import[k, m] for k in range(self.Num_Export_Terminals) for m in range(self.Num_Import_Terminals))
        cost += quicksum(self.Cost_Country_Facility[c] * self.X_Facility[c] for c in range(self.Num_Country_Elevators))
        cost += quicksum(self.Cost_Country_Stream[c, s] * self.X_Country_Stream[c, s] for c in range(self.Num_Country_Elevators) for s in range(self.Num_Stream_Elevators))
        cost += quicksum(self.Cost_Country_Rail[c, r] * self.X_Country_Rail[c, r] for c in range(self.Num_Country_Elevators) for r in range(self.Num_Rail_Elevators))
        cost += quicksum(self.Cost_Stream_Export[s, k] * self.Y_Stream_Export[s, k] for s in range(self.Num_Stream_Elevators) for k in range(self.Num_Export_Terminals))
        cost += quicksum(self.Cost_Rail_Export[r, k] * self.Y_Rail_Export[r, k] for r in range(self.Num_Rail_Elevators) for k in range(self.Num_Export_Terminals))
        cost += quicksum(self.holding_cost * self.Inventory_Country[c] for c in range(self.Num_Country_Elevators))
        cost += quicksum(self.Yield_Country[c, 4] * (self.IRR_lo * self.Framer_Decision[c, 0] + self.IRR_hi * self.Framer_Decision[c, 1] + self.RFD_lo * self.Framer_Decision[c, 2] +
                        self.RFD_hi * self.Framer_Decision[c, 3]) for c in range(self.Num_Country_Elevators))

        profit = LinExpr()
        profit += (quicksum((self.Supply_Country[c] - self.Inventory_Country[c]) / self.Inventory_Country[c] for c in range(self.Num_Country_Elevators)) * 180.87 + 2.97) * quicksum(self.X_Facility[c] for c in range(self.Num_Country_Elevators))
        # if self.tax:
        #     profit += (-0.019 * self.Demand_China**2 + 2478 * 1e5 * self.Demand_China) * 5
        #     profit += (-0.029 * self.Demand_ROW ** 2 + 1594.667 * 1e5 * self.Demand_ROW) * 0.8
        # else:
        profit += -0.019 * self.Demand_China ** 2 + 2478 * 1e5 * self.Demand_China
        profit += -0.029 * self.Demand_ROW ** 2 + 1594.667 * 1e5 * self.Demand_ROW

        profit += self.tau * quicksum(self.Supply_Country[c] for c in range(self.Num_Country_Elevators))

        #obj = LinExpr()
        obj = profit - cost

        self.model.setObjective(
            obj,
            GRB.MAXIMIZE
        )

        # Compile
        self.model.update()
        self.model.params.NumericFocus = 3
        self.model.params.NonConvex = 2
        self.model.optimize()
        if lp_to_file:
            self.model.write(self.model_name + '-' + str(self.year) + '.lp')

    def _model_outputs(self):
        self.Matrix_Framer_Decision = [[self.Framer_Decision[a, b].x for a in range(self.Num_Country_Elevators)] for b in range(4)]
        self.Matrix_Framer_Decision = pd.DataFrame(self.Matrix_Framer_Decision).T

        self.Matrix_X_Country_Stream = [[self.X_Country_Stream[a, b].x for a in range(self.Num_Country_Elevators)] for b in range(self.Num_Stream_Elevators)]
        self.Matrix_X_Country_Stream = pd.DataFrame(self.Matrix_X_Country_Stream).T
        self.Matrix_X_Country_Stream = self.Matrix_X_Country_Stream.add_prefix('ToRiver_')
        self.Quantity_X_Country_Stream = self.Matrix_X_Country_Stream.sum().sum()

        self.Matrix_X_Country_Rail = [[self.X_Country_Rail[a, b].x for a in range(self.Num_Country_Elevators)] for b in range(self.Num_Rail_Elevators)]
        self.Matrix_X_Country_Rail = pd.DataFrame(self.Matrix_X_Country_Rail).T
        self.Matrix_X_Country_Rail = self.Matrix_X_Country_Rail.add_prefix('ToRail_')
        self.Quantity_X_Country_Rail = self.Matrix_X_Country_Rail.sum().sum()

        self.Matrix_X_Facility = [self.X_Facility[a].x for a in range(self.Num_Country_Elevators)]
        self.Matrix_X_Facility = pd.Series(self.Matrix_X_Facility, name='X_Facility')
        self.Quantity_X_Facility = self.Matrix_X_Facility.sum()

        self.Matrix_Y_Stream_Export = [[self.Y_Stream_Export[a, b].x for a in range(self.Num_Stream_Elevators)] for b in range(self.Num_Export_Terminals)]
        self.Matrix_Y_Stream_Export = pd.DataFrame(self.Matrix_Y_Stream_Export).T
        self.Quantity_Y_Stream_Export = self.Matrix_Y_Stream_Export.sum().sum()

        self.Matrix_Y_Rail_Export = [[self.Y_Rail_Export[a, b].x for a in range(self.Num_Rail_Elevators)] for b in range(self.Num_Export_Terminals)]
        self.Matrix_Y_Rail_Export = pd.DataFrame(self.Matrix_Y_Rail_Export).T
        self.Quantity_Y_Rail_Export = self.Matrix_Y_Rail_Export.sum().sum()

        self.Matrix_Supply_Country = [self.Supply_Country[a].x for a in range(self.Num_Country_Elevators)]
        self.Quantity_Supply_Country = sum(self.Matrix_Supply_Country)

        self.Matrix_Z_Export_Import = [[self.Z_Export_Import[a, b].x for a in range(self.Num_Export_Terminals)] for b in range(self.Num_Import_Terminals)]
        self.Matrix_Z_Export_Import = pd.DataFrame(self.Matrix_Z_Export_Import).T.add_prefix('Import_')
        self.Quantity_Z_Export_Import = self.Matrix_Z_Export_Import.sum().sum()

        ## cost & obj
        self.OBJ_vaules = self.model.getObjective().getValue()
        cost_farmer = LinExpr()
        cost_farmer += quicksum(self.Cost_Country_Facility[c] * self.X_Facility[c] for c in range(self.Num_Country_Elevators))
        cost_farmer += quicksum(self.Cost_Country_Stream[c, s] * self.X_Country_Stream[c, s] for c in range(self.Num_Country_Elevators) for s in range(self.Num_Stream_Elevators))
        cost_farmer += quicksum(self.Cost_Country_Rail[c, r] * self.X_Country_Rail[c, r] for c in range(self.Num_Country_Elevators) for r in range(self.Num_Rail_Elevators))
        cost_farmer += quicksum(self.holding_cost * self.Inventory_Country[c] for c in range(self.Num_Country_Elevators))
        self.total_farmer = cost_farmer.getValue()

        self.total_barge = quicksum(self.Cost_Stream_Export[s, k] * self.Y_Stream_Export[s, k] for s in range(self.Num_Stream_Elevators) for k in range(self.Num_Export_Terminals)).getValue()
        self.total_rail = quicksum(self.Cost_Rail_Export[r, k] * self.Y_Rail_Export[r, k] for r in range(self.Num_Rail_Elevators) for k in range(self.Num_Export_Terminals)).getValue()
        self.total_ocaen = quicksum(self.Cost_Export_Import[k, m] * self.Z_Export_Import[k, m] for k in range(self.Num_Export_Terminals) for m in range(self.Num_Import_Terminals)).getValue()

        self.total_production = quicksum(self.Supply_Country[c] for c in range(self.Num_Country_Elevators)).getValue()

        self.D_profit = (quicksum((self.Supply_Country[c] - self.Inventory_Country[c]) / self.Inventory_Country[c] for c in range(self.Num_Country_Elevators)).getValue() * 180.87 + 2.97) * quicksum(self.X_Facility[c] for c in range(self.Num_Country_Elevators)).getValue()
        self.C_profit = -0.019 * self.Demand_China ** 2 + 2478 * 1e5 * self.Demand_China
        self.R_profit = -0.029 * self.Demand_ROW ** 2 + 1594.667 * 1e5 * self.Demand_ROW
        self.Subsidy = self.tau * quicksum(self.Supply_Country[c] for c in range(self.Num_Country_Elevators)).getValue()

        rate1 = quicksum(self.Supply_Country[c] for c in range(self.Num_Country_Elevators)).getValue() / self.Demand_China
        rate2 = (self.C_profit + self.R_profit) / (self.D_profit)

    def _write_to_files(self):
        # write to file
        self.Results_Country = pd.concat([self.Matrix_X_Country_Stream, self.Matrix_X_Country_Rail, self.Matrix_X_Facility], axis=1)
        self.Results_River = pd.concat([self.Matrix_Y_Stream_Export.add_prefix('RiverToExport_')], axis=1)
        self.Results_Rail = pd.concat([self.Matrix_Y_Rail_Export.add_prefix('RailToExport_')], axis=1)

        self.Matrix_Framer_Decision.to_csv(self.path + '1_ResultsOfFramerDecision_' + self.scenario_text + '.csv')
        self.Results_Country.to_csv(self.path + '2_ResultsOfCountryElevators_' + self.scenario_text + '.csv')
        self.Results_River.to_csv(self.path + '3_ResultsOfRiverElevators_' + self.scenario_text + '.csv')
        self.Results_Rail.to_csv(self.path + '4_ResultsOfRailElevators_' + self.scenario_text + '.csv')
        self.Matrix_Z_Export_Import.to_csv(self.path + '5_ResultsOfExports_' + self.scenario_text + '.csv')

    def _plot_logistic_routes(self, figs=False):
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
                      'legend.fontsize': 16,
                      }
        plt.rcParams.update(parameters)

        # loading LON and LAT
        self.LocCountryEle = pd.read_csv(self.root + '\GCAM_full/Outputs/Reference/1990/ProductionByCountry.csv', usecols=['Name', 'LON', 'LAT'])
        self.LocRiverEle = pd.read_csv(self.root + "\Scripts\LargerRiverElevators.csv", usecols=['Name', 'X', 'Y'])
        self.LocShuttleEle = pd.read_csv(self.root + "\Scripts\Shuttle tarins and ports.csv", usecols=['Name', 'X', 'Y'])
        self.LocExports = pd.read_csv(self.root + "\Scripts\ExportTerminals.csv", usecols=['Ports', 'X', 'Y'])

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
        plt.scatter(self.LocRiverEle['X'].to_numpy(), self.LocRiverEle['Y'].to_numpy(), label='River Elevators', color='#F05E1C', s=50, zorder=5)
        plt.scatter(self.LocShuttleEle['X'].to_numpy(), self.LocShuttleEle['Y'].to_numpy(), label='Rail Elevators', color='#FFB11B', s=50, zorder=5)
        plt.scatter(self.LocExports['X'].to_numpy(), self.LocExports['Y'].to_numpy(), label='Export Terminals', color='#006284', s=80, zorder=5)
        for i in range(self.Num_Export_Terminals):
            if self.LocExports.iloc[i, 1] <= -95:
                plt.annotate(self.LocExports.iloc[i, 0], xy=(self.LocExports.iloc[i, 1], self.LocExports.iloc[i, 2]), xytext=(self.LocExports.iloc[i, 1] - 4, self.LocExports.iloc[i, 2] - 1.3), fontsize=14)
            else:
                plt.annotate(self.LocExports.iloc[i, 0], xy=(self.LocExports.iloc[i, 1], self.LocExports.iloc[i, 2]), xytext=(self.LocExports.iloc[i, 1] - 1, self.LocExports.iloc[i, 2] - 1.3), fontsize=14)

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
        plt.title('Total Production: {:.2e}  Total China Demand: {:.2e}'.format(self.total_production, self.china_demand))

        textstr = 'Total Cost: {:.2e}\nFarmer Cost: {:.2e}\nBarge Cost: {:.2e}\nRail Cost: {:.2e}\nOcean Cost: {:.2e}'.format(self.OBJ_vaules, self.total_farmer, self.total_barge, self.total_rail, self.total_ocaen)
        plt.text(-65, 27, textstr, fontsize=16, verticalalignment='center',horizontalalignment='right', bbox=dict(facecolor='white', edgecolor='#d6d6d6', boxstyle='round', alpha=0.75))

        #plt.text(-75, 30, 'Total Barge Cost:: {:.2e}  Total Shuttle Cost: {:.2e} Total Ocean Cost: {:.2e}'.format(self.total_barge, self.total_rail, self.total_ocaen), fontsize=15)

        #ax.set_axis_off()  # hide the axis

        if figs:
            plt.savefig(self.path + '/' + str(self.year) + '_' + self.model_name + '.png', dpi=300)
            plt.savefig(self.path + '/' + str(self.year) + '_' + self.model_name + '_' + self.scenario_text + '.pdf', dpi=600, bbox_inches="tight")
            plt.show()
            plt.close()

if __name__ == '__main__':

    scenario = "SSP1"
    year = 2020

    #root = 'D:/OneDrive - University of Tennessee/Scripts/SYBModel'
    root = './'

    Op_cost = OperationCost(year, root)
    china = China_Demand(year, root)

    ## Solving by GUROBI Model
    instacne = GCAM_SYB(scenario, year, china.quantity*10,
                        IRR_lo = Op_cost.IRR_lo, IRR_hi = Op_cost.IRR_hi, RFD_lo =Op_cost.RFD_lo, RFD_hi = Op_cost.RFD_hi,
                        truck_rate=1, barge_rate=1, rail_rate=1, ocean_rate=8, figs = False, tax=False)