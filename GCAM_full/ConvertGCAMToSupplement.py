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
import os


def random_list(length):
    random_list = []
    for i in range(length):
        random_list.append(random.random()/10)
    return random_list

class Read_GCAM():
    def __init__(self, year, scenario):
        self.year = year
        self.scenario = scenario
        self.managements = ['IRR', 'RFD']
        self.levels = ['hi', 'lo']

        self.g_production = pd.read_csv('../GCAM_full/20220421_gcam_production.csv', usecols=['scenario','subregion', 'management', 'level', self.year,'Units'],na_filter=False,nrows=792)  # megatonne
        self.g_landarea = pd.read_csv('../GCAM_full/20220421_gcam_leafarea.csv', usecols=['scenario','subregion', 'management', 'level', self.year,'Units'])
        self.g_totalarea = pd.read_csv('../GCAM_full/20220421_GCAM_totalarea.csv', usecols=['scenario','subregion', self.year,'Units'])

        self.g_basin_yield = self.Get_Yield()  # Calculate unite yeild by total _production and _landarea     # tonne / km2

        self.country_elevator_yield = self.Get_Country_Elevator()

        self.path = '../GCAM_full/Outputs/'
        self._mkdir(self.path + self.scenario)
        self._mkdir(self.path + self.scenario + '/' + self.year)

        self._Write_To_Csv(self.path + self.scenario + '/' + self.year + '/', self.country_elevator_yield)


    def Get_Yield(self):
        g_yield = pd.merge(self.g_production, self.g_landarea, on=['scenario','subregion','management','level'], suffixes=('_production','_landarea'))
        g_yield['yield'] = 1e6 * g_yield[self.year+'_production'] / (1e3 * g_yield[self.year+'_landarea'])
        g_yield['unit'] = 'tons / km2'

        # drop the redundant columns
        g_yield.drop([self.year+'_production',self.year+'_landarea','Units_production','Units_landarea'], axis=1, inplace=True)
        return g_yield

    def Get_Country_Elevator(self):
        # read location file
        CountryElevators = pd.read_csv('../GCAM_full/data10top_converted_waterbasin.csv', usecols=['Name', 'BasinName', 'LON', 'LAT'])
        CountryElevators['Yield_IRR_hi'], CountryElevators['Yield_IRR_lo'], CountryElevators['Yield_RFD_hi'], CountryElevators['Yield_RFD_lo'], \
            CountryElevators['Ending'], CountryElevators['EndingRate'], CountryElevators['PlantingArea(km2)'], CountryElevators['Yield Unit'] = [0, 0, 0, 0, 0, 0, 0, 'tons/km2']

        # Basins = CountryElevators['BasinName'].unique()
        Basins = CountryElevators['BasinName'].value_counts().to_frame(name='Numbers') # get the number of elevators in each basin
        for basin in Basins.iterrows():
            basin_areas = self.g_totalarea.query('subregion == @basin[0] & scenario == @self.scenario')
            country_average_area = 1e6 * basin_areas[self.year] / basin[1]['Numbers']  # get the total area of each country elevator  Units: km2

            CountryElevators.loc[CountryElevators['BasinName'] == basin[0], 'PlantingArea(km2)'] = [country_average_area] * basin[1]['Numbers']

            for management in self.managements:
                for level in self.levels:
                    country_yield = self.g_basin_yield.query('subregion == @basin[0] & scenario == @self.scenario & management == @management & level == @level')['yield']
                    CountryElevators.loc[CountryElevators['BasinName'] == basin[0], 'Yield_'+ management + '_' + level] = [country_yield] * basin[1]['Numbers']

        # Ending
        CountryElevators['EndingRate'] = self.Ending_Rate(LBound=0.01, UBound=0.2, Num_Country_Elevators=CountryElevators.shape[0])

        CountryElevators['Ending'] = CountryElevators[['Yield_IRR_hi', 'Yield_IRR_lo', 'Yield_RFD_hi', 'Yield_RFD_lo']].mean(1) * CountryElevators['EndingRate'] * CountryElevators['PlantingArea(km2)']
        CountryElevators['Ending'] = CountryElevators['Ending'].round(2)

        return CountryElevators

    def Ending_Rate(self, **kwargs):
        # get the ending rate of each country elevator
        if kwargs['UBound'] != 0:
            ending_rates = []
            for num_country in range(kwargs['Num_Country_Elevators']):
                ending_rates.append(round(random.uniform(kwargs['LBound'], kwargs['UBound']), 2))
        else:
            ending_rates = [0] * kwargs['Num_Country_Elevators']

        return ending_rates

    def _Modefy_Yield(self):
        pass
        ## Production Scenarios
        Scenarios = [0.2, 0.5, 0.8, 1.2, 1.5, 3.0]  # increase or decrease percentage
        for index, s in enumerate(Scenarios):
            name = 'ProductionByCountry' + str(s)
            newData = CountryElevators.copy()
            newData['Yield_IRR_hi'] = newData['Yield_IRR_hi'].apply(lambda x: x * s)
            newData['Yield_IRR_lo'] = newData['Yield_IRR_lo'].apply(lambda x: x * s)
            newData['Yield_RFD_hi'] = newData['Yield_RFD_hi'].apply(lambda x: x * s)
            newData['Yield_RFD_lo'] = newData['Yield_RFD_lo'].apply(lambda x: x * s)
            newData.to_csv('Outputs\\' + name + '.csv', index=False)

    def _Write_To_Csv(self, path, data):
        filename = 'ProductionByCountry.csv'
        # write data to csv file
        data.to_csv(path + filename, index=False)
        print('\033[1;33m Successfully write to ' + path +'\033[0m')

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

    def __del__(self):
        print('\033[1;32m Instance deleted successfully!\033[0m')

if __name__=='__main__':
    # Year = '2020'
    # Scenario = 'Reference'

    # Year = pd.read_csv('../GCAM_full/20220421_gcam_production.csv')
    # Year = Year.columns.values.tolist()[5:-1]
    # Scenario = pd.read_csv('../GCAM_full/20220421_gcam_production.csv', usecols=['scenario']).squeeze().unique().tolist()[0:-1]

    Scenarios = ['SSP1', 'SSP2', 'SSP3', 'SSP4', 'SSP5']
    # Years = ['1990', '2005', '2010', '2015', '2020', '2025', '2030', '2035', '2040', '2045', '2050', '2055', '2060', '2065', '2070', '2075', '2080', '2085', '2090', '2095', '2100']
    Years = ['2020', '2025', '2030', '2035', '2040', '2045', '2050']

    for year in Years:
        for scenario in Scenarios:
            if ~pd.isna(scenario):
                print('\033[1;33m Processing ' + year + scenario + '\033[0m')
                gcam = Read_GCAM(year, scenario)







