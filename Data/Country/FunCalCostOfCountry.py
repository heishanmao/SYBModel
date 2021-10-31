# Author: Scott
# Date: 2021-10-30 15:18:45
# LastEditTime: 2021-10-30 15:18:46
# LastEditors: Scott Zheng
# Description: Calculate Trans Cost form Country elevators to its Facility, River, and Rail elevators.
#             Inputs: 'CountryToLargerDistance.csv'
#                     'CountryToRailDistance.csv'
#             Outputs: 'CostToFacility.csv'
#                     'MileCostByTruck.csv'
#
# FilePath: .\Data\CalculateCostOfCountryElevators.py
import pandas as pd
import numpy as np
import time

def CalCostOfCountry(pathIn, pathOut, LimitFacility, LimitCountryToRiver, LimitCountryToRail):
    #print(pathIn)
    #print(pathIn + 'CountryToRiverDistance.csv')
    def NormalizateData(OriginData, NMin, NMax, OMax, OMin):
        N = NMin + ((NMax - NMin) / (OMax - OMin)) * (OriginData - OMin)
        return ("%.2f" % N)

    distanceCountry_RiverByTruck = pd.read_csv(pathIn + 'CountryToRiverDistance.csv', index_col=0)
    distanceCountry_RiverByTruck['min_val'] = distanceCountry_RiverByTruck.min(axis=1)

    OMax = distanceCountry_RiverByTruck['min_val'].max()
    OMin = distanceCountry_RiverByTruck['min_val'].min()

    ## 1. write truck's cost to facility and Holding Cost of Country Elevators to file
    CostToFacility = distanceCountry_RiverByTruck['min_val'].copy()
    CostToFacility = CostToFacility.rename('Facility').to_frame()
    CostToFacility['HoldingCost'] = 0
    for i in range(CostToFacility.shape[0]):
        # assume this value is 1.5 times the cost to its River elevators
        CostToFacility.iloc[i, 0] = 1.5 * float(
            NormalizateData(distanceCountry_RiverByTruck['min_val'].iloc[i], LimitFacility[0], LimitFacility[1], OMax,
                            OMin))  ## new distribuation range of the cost
        # assume this valeu is between 8 to 15
        CostToFacility.iloc[i, 1] = round(np.random.uniform(8, 15), 2)  ## holding cost
    CostToFacility.to_csv(pathOut + 'CostToFacility.csv')
    localtime = time.asctime(time.localtime(time.time()))
    print(localtime + '  Successfully write out to CostToFacility.csv')

    ## 2. write trucks' cost from Country to River to file
    Cost_CountryToRiver = distanceCountry_RiverByTruck.copy()
    Cost_CountryToRiver = Cost_CountryToRiver.drop('min_val', axis=1)
    for i in range(Cost_CountryToRiver.shape[0]):
        for j in range(Cost_CountryToRiver.shape[1]):
            Cost_CountryToRiver.iloc[i, j] = NormalizateData(distanceCountry_RiverByTruck.iloc[i, j], LimitCountryToRiver[0], LimitCountryToRiver[1], OMax,
                                                             OMin)
    Cost_CountryToRiver.to_csv(pathOut + 'CostToStreamByTruck.csv')
    localtime = time.asctime(time.localtime(time.time()))
    print(localtime + '  Successfully write out to CostToStreamByTruck.csv')

    ## 3. write trucks' cost from Country to Rail to file
    Distanc_CountryToRail = pd.read_csv(pathIn + 'CountryToRailDistance.csv', index_col=0)
    # Distanc_CountryToRail['min_val'] = Distanc_CountryToRail.min(axis=1)
    OMax_Rail = Distanc_CountryToRail.min(axis=1).max()
    OMin_Rail = Distanc_CountryToRail.min(axis=1).min()
    Cost_CountryToRail = Distanc_CountryToRail.copy()
    for i in range(Cost_CountryToRail.shape[0]):
        for j in range(Cost_CountryToRail.shape[1]):
            Cost_CountryToRail.iloc[i, j] = NormalizateData(Distanc_CountryToRail.iloc[i, j], LimitCountryToRail[0], LimitCountryToRail[1],
                                                                      OMax_Rail, OMin_Rail)
    Cost_CountryToRail.to_csv(pathOut + 'CostToRailByTruck.csv')
    localtime = time.asctime(time.localtime(time.time()))
    print(localtime + '  Successfully write out to CostToRailByTruck.csv')


