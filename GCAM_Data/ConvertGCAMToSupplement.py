'''
Author: Scott
Date: 2021-12-11 14:43:24
LastEditTime: 2021-10-24 14:57:01
LastEditors: Please set LastEditors
Description: recall ../GCAM_Data/GCAMToElevators.py 
            assiginment GCAM output to each elevator'e yield based on 4 sceniors.
FilePath: \SYBModel\Scripts\ConvertGCAMToElevators.py
Notes   : Transfer the GCAM output data to input of SYBModel supplement by Year
'''

import pandas as pd
import random

def random_list(length):
    random_list = []
    for i in range(length):
        random_list.append(random.random()/10)
    return random_list

# # Get each produciton by basinName, year, and technology
# def GetBasinProduction(BName, BProduction):
#     #  find the production by the basin name
#     ProducutonByScens = BProduction.loc[BName,['Scenario',BYear, 'Units']]
#     # find the production by technology
#     ScenarioName = BName+BTechnology
#
#     return ProducutonByScens.loc[ProducutonByScens['Scenario'] == ScenarioName,:]
#
# #assignment basin produciton to each eleavator
#     # calculate number of elevators in the single basin
# def GetEleProduciton(EleAndBasinList, BName, BProdcution):
#     NumOfEles = EleAndBasinList['BasinName'].value_counts()
#     NumOfEles = NumOfEles[NumOfEles.index==BName].values[0]
#
#     #print(BProdcution)
#     #Production By Basin to ELevators
#     YeildByEles = BProdcution.iloc[0,1] * 1000000
#     YeildByEle = YeildByEles / NumOfEles
#
#     return NumOfEles, YeildByEles, round(YeildByEle, 2)


if __name__=='__main__':
    Year = '2020'
    Technologies = ['IRR', 'RFD']
    Levels = ['hi', 'lo']

    # Reading data
    # Production
    ProductByBasin = pd.read_csv('GCAM outputs_20210910.csv', usecols=['subregion', 'management', 'level', Year])  #unit: Mt
    ProductByBasin['Reg_Areas'] = pd.read_csv('Oilcrop_LandleafArea.csv', usecols=[Year])                          #unit:  1000 km2
    ProductByBasin['Reg_Yield'] = ProductByBasin.apply(lambda x: x['2020'] / x['Reg_Areas'], axis=1)               #unit: Mt/1000 km2
    ProductByBasin['Tol_Areas'] = pd.read_csv('Oilcrop_TotalArea.csv', usecols=[Year])                             #unit: 1000 km2

    # data = pd.read_csv('data10top_converted_waterbasin.csv')
    # data['BasinName'] = data['BasinName'].str.replace(r'OilCrop_', '')
    # data.to_csv('data10top_converted_waterbasin.csv', index=False)

    # arrangement to elevators
    CountryElevators = pd.read_csv('data10top_converted_waterbasin.csv', usecols=['Name','BasinName', 'LON', 'LAT'])
    CountryElevators['Yield_IRR_hi'] = 0
    CountryElevators['Yield_IRR_lo'] = 0
    CountryElevators['Yield_RFD_hi'] = 0
    CountryElevators['Yield_RFD_lo'] = 0
    CountryElevators['Ending'] = 0
    CountryElevators['EndingRate'] = 0
    CountryElevators['Yield Unit'] = 'Mt/1000 km2'

    #Basins = CountryElevators['BasinName'].unique()
    # Basins['#Country'] = CountryElevators['BasinName'].value_counts()
    Basins = CountryElevators['BasinName'].value_counts().to_frame( name='Numbers')
    for basin in Basins.itertuples():
        data = ProductByBasin[ProductByBasin['subregion'] == basin[0]]
        print(basin[0])
        for technology in Technologies:
            for level in Levels:
                RegionYield = data.loc[(data['management'] == technology) & (data['level'] == level)]['Reg_Yield']
                EleYield = RegionYield / basin[1]
                # Region Yield allocated to each Country elevator based on water basins
                CountryElevators.loc[CountryElevators['BasinName']==basin[0], 'Yield_' + technology + '_' + level] = EleYield.to_list()*basin[1]

    CountryElevators['EndingRate'] = random_list(CountryElevators.shape[0])
    CountryElevators['Ending'] = round(1000 * CountryElevators['EndingRate'], 2)

    # CountryElevators.to_csv('Outputs\ProductionByCountry_' + str(Year) +'.csv', index=False)
    CountryElevators.to_csv('Outputs\ProductionByCountry.csv', index=False)




