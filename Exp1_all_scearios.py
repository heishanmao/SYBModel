#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 29/04/2022 1:59 AM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : Exp1_all_scearios.py
# @Software: PyCharm
# @Notes   :

from SYBModel_V16 import GCAM_SYB
import pandas as pd
from GCAM_full.Get_DemandTariff import China_Demand # with init file
from GCAM_full.operation_cost import OperationCost


if __name__ == '__main__':

    Year = pd.read_csv('./GCAM_full/20220421_gcam_production.csv')
    Year = Year.columns.values.tolist()[5:-1]
    Scenario = pd.read_csv('./GCAM_full/20220421_gcam_production.csv', usecols=['scenario']).squeeze().unique().tolist()[0:-1]

    Trucks = [0.5, 1, 1.5, 2]
    Barges = [0.5, 1, 1.5, 2]
    Rails = [0.5, 1, 1.5, 2]
    Oceans = [0.5, 1, 1.5, 2]

    columns = ['Scenario', 'Year', 'Rates', 'OBJ_vaules', 'Cost_Farmers', 'Cost_Barges', 'Cost_Rails', 'Cost_Oceans', 'Total_production',
               'Quantity_Supply_Country',
               'Quantity_X_Facility', 'Quantity_X_Country_Stream', 'Quantity_X_Country_Rail', 'Quantity_Y_Stream_Export',
               'Quantity_Y_Rail_Export', 'Quantity_Z_Export_Import']
    Res = pd.DataFrame(columns=columns)
    for year in Year:
        for scenario in Scenario:
            print(year, scenario)
            Op_cost = OperationCost(year)
            china = China_Demand(int(year))
            instance = GCAM_SYB(scenario, year, china.quantity * 0.5,
                                IRR_lo=Op_cost.IRR_lo, IRR_hi=Op_cost.IRR_hi, RFD_lo=Op_cost.RFD_lo, RFD_hi=Op_cost.RFD_hi,
                                truck_rate=1, barge_rate=1, rail_rate=1, ocean_rate=1)

            if instance.model.Status == 2:
                res = [scenario, year, instance.scenario_text, int(instance.OBJ_vaules), int(instance.total_farmer), int(instance.total_barge), int(instance.total_rail),
                       int(instance.total_ocaen),int(instance.total_production), int(instance.Quantity_Supply_Country), int(instance.Quantity_X_Facility), int(instance.Quantity_X_Country_Stream),
                       int(instance.Quantity_X_Country_Rail), int(instance.Quantity_Y_Stream_Export), int(instance.Quantity_Y_Rail_Export), int(instance.Quantity_Z_Export_Import)]
            else:
                res = [0] * (len(columns)-3)
                res = [scenario, year, instance.scenario_text] + res

            res = pd.Series(res, index=columns)
            Res = Res.append(res, ignore_index=True)


    Res.to_csv('./Exps/all_scenarios_'+ instance.scenario_text + '.csv', index=False)
    print('Done')



