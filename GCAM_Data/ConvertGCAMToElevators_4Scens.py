'''
Author: your name
Date: 2021-10-24 14:43:24
LastEditTime: 2021-10-24 14:57:01
LastEditors: Please set LastEditors
Description: recall ../GCAM_Data/GCAMToElevators.py 
            assiginment GCAM output to each elevator'e yield based on 4 sceniors.
FilePath: \SYBModel\Scripts\ConvertGCAMToElevators.py
'''


#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 23/10/2021 12:00 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : GACM_ProductionByEle.py
# @Software: PyCharm
# @Notes   : Transfer the GCAM output data to input of SYBModel

import pandas as pd
import random

def random_list(length):
    random_list = []
    for i in range(length):
        random_list.append(random.random()/10)
    return random_list

# Get each produciton by basinName, year, and technology
def GetBasinProduction(BName, BProduction, BYear, BTechnology):
    #  find the production by the basin name
    ProducutonByScens = BProduction.loc[BName,['Scenario',BYear, 'Units']]
    # find the production by technology
    ScenarioName = BName+BTechnology
    
    return ProducutonByScens.loc[ProducutonByScens['Scenario'] == ScenarioName,:]

#assignment basin produciton to each eleavator
    # calculate number of elevators in the single basin
def GetEleProduciton(EleAndBasinList, BName, BProdcution):
    NumOfEles = EleAndBasinList['BasinName'].value_counts()
    NumOfEles = NumOfEles[NumOfEles.index==BName].values[0]

    #print(BProdcution)
    #Production By Basin to ELevators
    YeildByEles = BProdcution.iloc[0,1] * 1000000 
    YeildByEle = YeildByEles / NumOfEles

    return NumOfEles, YeildByEles, round(YeildByEle, 2)


if __name__=='__main__':
    Year = 2020
    Technologies = ['_IRR_hi', '_IRR_lo','_RFD_hi','_RFD_lo']

    for Technology in Technologies:
        ## import data
        # Country elevators and its allocated water basin
        EleAndBasin = pd.read_csv('data10top_converted_waterbasin.csv', usecols=['Name','BasinName','LAT','LON'])
        EleAndBasin['Production'] = 0
        EleAndBasin['Ending'] = 0
        EleAndBasin['EndingRate'] = 0

        # pandas >1.3 if engine=None default to engine='openpyxl'
        ## import GCAM Output
        ProductByBasin = pd.read_excel('GCAM outputs_20210910.xlsx', sheet_name=0, index_col=0, usecols='D,F,G:AB')

        Basins = EleAndBasin.BasinName.unique()
        for basin in Basins:
            # Production of Basin
            BProdcution = GetBasinProduction(basin, ProductByBasin, Year, Technology)
            # Production by elevators
            EYield = GetEleProduciton(EleAndBasin, basin, BProdcution)

            #print(EYield)
            EleAndBasin.loc[EleAndBasin['BasinName']== basin, 'Production'] = EYield[2]

        ## output
        EleAndBasin.to_csv('Outputs\ProductionByCountry_' + str(Year) + Technology + '.csv', index=False)

    # adding ending rate for the same elevators at 4 scenarios
    EndingRates = random_list(227)
    for Technology in Technologies:
        data = pd.read_csv('Outputs\ProductionByCountry_' + str(Year) + Technology + '.csv')
        data['EndingRate'] = EndingRates
        data['Ending'] = round( data['Production'] * EndingRates, 2)
        data.to_csv('Outputs\ProductionByCountry_' + str(Year) + Technology + '.csv', index=False)



