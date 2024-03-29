#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 29/04/2022 1:59 AM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : Exp1_all_scearios.py
# @Software: PyCharm
# @Notes   :

from SYBModel_V17 import GCAM_SYB
import pandas as pd
from GCAM_full.Get_DemandTariff import China_Demand # with init file
from GCAM_full.operation_cost import OperationCost
import os

def _mkdir(path):
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

if __name__ == '__main__':
    root = './'
    ####################################################################################################################
    #        Exp 1 - Run All scenarios on server (support by SYBModel_V16.py)
    ####################################################################################################################

    Year = pd.read_csv('./GCAM_full/20220421_gcam_production.csv')
    Year = Year.columns.values.tolist()[5:-1]
    Scenario = pd.read_csv('./GCAM_full/20220421_gcam_production.csv', usecols=['scenario']).squeeze().unique().tolist()[0:-1]

    Rates = ['1_1_1_10']
    taxs = [True, False]

    Trucks = [0.5, 1, 5, 10]
    Barges = [0.5, 1, 5, 10]
    Rails = [0.5, 1, 5, 10]
    Oceans = [0.5, 1, 5, 10]

    columns = ['Scenario', 'Year', 'Rates', 'OBJ_vaules', 'Cost_Farmers', 'Cost_Barges', 'Cost_Rails', 'Cost_Oceans', 'Total_production',
               'Quantity_X_Facility', 'Quantity_X_Country_Stream', 'Quantity_X_Country_Rail', 'Quantity_Y_Stream_Export',
               'Quantity_Y_Rail_Export', 'Quantity_Z_Export_Import', 'Demand', 'Domestic_Price', 'China_Price', 'ROW_Price', 'Subsidy',
               'Tax']


    for scenario in Scenario:
        if scenario == 'SSP2':
            for year in Year:
                if int(year) == 2030:
                    Res = pd.DataFrame(columns=columns)
                    for tax in taxs:
                        Op_cost = OperationCost(year, root)
                        china = China_Demand(int(year), root)
                        print(year, scenario)
                        for truck in Trucks:
                            for barge in Barges:
                                for rail in Rails:
                                    for ocean in Oceans:
                                        rate = str(truck) + '_' + str(barge) + '_' + str(rail) + '_' + str(ocean)
                                        if rate in Rates:
                                            instance = GCAM_SYB(scenario, year, china.quantity * 10,
                                                                IRR_lo=Op_cost.IRR_lo, IRR_hi=Op_cost.IRR_hi, RFD_lo=Op_cost.RFD_lo, RFD_hi=Op_cost.RFD_hi,
                                                                truck_rate=truck, barge_rate=barge, rail_rate=rail, ocean_rate=ocean, tax=tax, figs=False)

                                            if instance.model.Status == 2:
                                                res = [scenario, year, instance.scenario_text, int(instance.OBJ_vaules), int(instance.total_farmer), int(instance.total_barge), int(instance.total_rail),
                                                    int(instance.total_ocaen),int(instance.total_production), int(instance.Quantity_X_Facility), int(instance.Quantity_X_Country_Stream),
                                                    int(instance.Quantity_X_Country_Rail), int(instance.Quantity_Y_Stream_Export), int(instance.Quantity_Y_Rail_Export), int(instance.Quantity_Z_Export_Import), int(china.quantity),
                                                    int(instance.D_profit), int(instance.C_profit), int(instance.R_profit), int(instance.Subsidy), str(tax)]
                                            else:
                                                res = [0] * (len(columns)-3)
                                                res = [scenario, year, instance.scenario_text] + res

                                            res = pd.Series(res, index=columns)
                                            Res = Res.append(res, ignore_index=True)
                                            del instance

                    dir = './Exps-tax/' + scenario
                    _mkdir(dir)
                    Res.to_csv(dir + '/all_rates_' + str(year) + '.csv', index=False)
    print('Done')


