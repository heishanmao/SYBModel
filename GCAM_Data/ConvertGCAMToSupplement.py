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

if __name__=='__main__':
    Year = '2020'
    Technologies = ['IRR', 'RFD']
    Levels = ['hi', 'lo']

    # Reading data
    # Production
    ProductByBasin = pd.read_csv('GCAM outputs_20210910.csv', usecols=['subregion', 'management', 'level', Year])  #unit: 10*6 t
    ProductByBasin['Reg_Areas'] = pd.read_csv('Oilcrop_LandleafArea.csv', usecols=[Year])                          #unit:  1000 km2
    ProductByBasin['Reg_Yield'] = ProductByBasin.apply(lambda x: x['2020'] / x['Reg_Areas'], axis=1)               #unit: 10*6 t/1000 km2
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
    CountryElevators['PlantingArea'] = 0
    CountryElevators['Yield Unit'] = 't/km2'

    #Basins = CountryElevators['BasinName'].unique()
    # Basins['#Country'] = CountryElevators['BasinName'].value_counts()
    Basins = CountryElevators['BasinName'].value_counts().to_frame( name='Numbers')
    for basin in Basins.iterrows():
        data = ProductByBasin[ProductByBasin['subregion'] == basin[0]]
        # print(basin[0]) # subRegion
        # print(basin[1]['Numbers'])  # number of elevators in the subRegion
        for technology in Technologies:
            for level in Levels:
                RegionYield = data.loc[(data['management'] == technology) & (data['level'] == level)]['Reg_Yield']
                EleYield = 1000 * RegionYield / basin[1]['Numbers'] # unit to t/km2
                # Region Yield allocated to each Country elevator based on water basins
                CountryElevators.loc[CountryElevators['BasinName']==basin[0], 'Yield_' + technology + '_' + level] = EleYield.to_list() * basin[1]['Numbers']

        # Total areas to each Country Elevator
        Tol_Areas = data.loc[(data['management'] == technology) & (data['level'] == level)]['Tol_Areas']  # unit 10^3 km2
        EleArea = 1000 * Tol_Areas / basin[1]['Numbers']
        CountryElevators.loc[CountryElevators['BasinName'] == basin[0], 'PlantingArea'] = EleArea.to_list() * basin[1]['Numbers']  # unit km2

    CountryElevators['EndingRate'] = random_list(CountryElevators.shape[0])
    CountryElevators['Ending'] = round(1000 * CountryElevators['EndingRate'], 2)

    # CountryElevators.to_csv('Outputs\ProductionByCountry_' + str(Year) +'.csv', index=False)
    CountryElevators.to_csv('Outputs\ProductionByCountry.csv', index=False)

    ## Production Scenarios
    Scenarios = [0.2, 0.5, 0.8, 1.2, 1.5, 3.0]  # increase or decrease percentage
    for index, s in enumerate(Scenarios):
        name = 'ProductionByCountry' + str(s)
        newData = CountryElevators.copy()
        newData['Yield_IRR_hi'] = newData['Yield_IRR_hi'].apply(lambda x:x*s)
        newData['Yield_IRR_lo'] = newData['Yield_IRR_lo'].apply(lambda x:x*s)
        newData['Yield_RFD_hi'] = newData['Yield_RFD_hi'].apply(lambda x:x*s)
        newData['Yield_RFD_lo'] = newData['Yield_RFD_lo'].apply(lambda x:x*s)
        newData.to_csv('Outputs\\'+ name +'.csv', index=False)




