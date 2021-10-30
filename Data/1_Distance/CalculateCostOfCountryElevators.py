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

distanceCountry_RiverByTruck = pd.read_csv('CountryToRiverDistance.csv', index_col = 0)
distanceCountry_RiverByTruck['min_val'] = distanceCountry_RiverByTruck.min(axis=1)
distanceCountry_RiverByTruck.head()

def NormalizateData(OriginData, NMin, NMax, OMax, OMin):
    N = NMin + ((NMax-NMin)/(OMax-OMin))*(OriginData-OMin)
    return ("%.2f"  %N)

OMax = distanceCountry_RiverByTruck['min_val'].max()
OMin = distanceCountry_RiverByTruck['min_val'].min()

## a test part
Cost = []
for i in range(len(distanceCountry_RiverByTruck['min_val'])):
    Cost.append(NormalizateData(distanceCountry_RiverByTruck['min_val'].iloc[i], 3, 18, OMax, OMin))  ## new distribuation range of the cost
Cost

## write truck's cost to facility and Holding Cost of Country Elevators to file
CostToFacility = distanceCountry_RiverByTruck['min_val'].copy()
CostToFacility = CostToFacility.rename('Facility').to_frame()
CostToFacility['HoldingCost'] = 0

for i in range(CostToFacility.shape[0]):
    # assume this value is 1.5 times the cost to its River elevators
    CostToFacility.iloc[i,0]= 1.5 * float(NormalizateData(distanceCountry_RiverByTruck['min_val'].iloc[i], 20, 30, OMax, OMin)) ## new distribuation range of the cost
    # assume this valeu is between 8 to 15
    CostToFacility.iloc[i,1] = round(np.random.uniform(8,15),2)   ## holding cost

CostToFacility.to_csv('.\Cost\CostToFacility.csv')

## write trucks' cost from Country to River to file
Cost_CountryToRiver = distanceCountry_RiverByTruck.copy()
Cost_CountryToRiver = Cost_CountryToRiver.drop('min_val',axis=1)

for i in range(Cost_CountryToRiver.shape[0]):
    for j in range(Cost_CountryToRiver.shape[1]):
        Cost_CountryToRiver.iloc[i,j] = NormalizateData(distanceCountry_RiverByTruck.iloc[i,j], 10, 50, OMax, OMin)
    
Cost_CountryToRiver.to_csv('.\Cost\CostToStreamByTruck.csv')


## write trucks' cost from Country to Rail to file
distanceCountry_RailByTruck = pd.read_csv('CountryToRailDistance.csv', index_col = 0)
distanceCountry_RailByTruck['min_val'] = distanceCountry_RiverByTruck.min(axis=1)

OMax_Rail = distanceCountry_RiverByTruck['min_val'].max()
OMin_Rail = distanceCountry_RiverByTruck['min_val'].min()

for i in range(distanceCountry_RiverByTruck.shape[0]):
    for j in range(distanceCountry_RiverByTruck.shape[1]):
        distanceCountry_RiverByTruck.iloc[i,j] = NormalizateData(distanceCountry_RiverByTruck.iloc[i,j], 10, 50, OMax_Rail, OMin_Rail)

distanceCountry_RiverByTruck.to_csv('.\Cost\CostToRailByTruck.csv')
