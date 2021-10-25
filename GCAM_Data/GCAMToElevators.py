#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 23/10/2021 12:00 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : GACM_ProductionByEle.py
# @Software: PyCharm
# @Notes   : Transfer the GCAM output data to input of SYBmodel

import pandas as pd
import random

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

    #Production By Basin to ELevators
    #print(type(BProdcution.iloc[0,1]))
    YeildByEles = 1000000 * BProdcution.iloc[0,1]
    YeildByEle = YeildByEles / NumOfEles

    return NumOfEles, YeildByEles, round(YeildByEle, 2)



if __name__=='__main__':

    ## import data
    # Country elevators and its allocated water basin
    EleAndBasin = pd.read_csv('data10top_converted_waterbasin.csv',usecols=['Name','BasinName'])  

    # pandas >1.3 if engine=None default to engine='openpyxl'
    ## GCAM Output
    ProductByBasin = pd.read_excel('GCAM outputs_20210910.xlsx', sheet_name=0,index_col=0, usecols='D,F,G:AB') 

    Year = 2020
    Technologies = ['_IRR_hi','_IRR_lo','_RFD_hi','_RFD_lo']
    Technology = Technologies[0]
    Basins = EleAndBasin.BasinName.unique()

    EleAndBasin['Production'] = 0
    EleAndBasin['Ending'] = 0
    EleAndBasin['EndingRate'] = 0

    for basin in Basins:
        # Production of Basin
        BProdcution = GetBasinProduction(basin, ProductByBasin, Year, Technology)
        # Production by elevators
        EYield = GetEleProduciton(EleAndBasin, basin, BProdcution)

        #print(EYield)
        EleAndBasin.loc[EleAndBasin['BasinName']== basin, 'Production'] = EYield[2]
        
    for index, row in EleAndBasin.iterrows():
        # Random Ending Stock [0,0.1]
        EndingRate = random.random() / 10
        EleAndBasin.iloc[index, 4] = EndingRate
        EleAndBasin.iloc[index, 3] = round( row['Production'] * EndingRate, 2) 
    
    ## output
    EleAndBasin.to_csv('Outputs\ProductionByCountry_'+ str(Year) + Technology +'.csv', index=False)
