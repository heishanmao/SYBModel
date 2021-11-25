#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 24/11/2021 9:09 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : StateMap.py
# @Software: PyCharm
# @Notes   : map layer for the output results.

import geopandas as gpd
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt
import pandas as pd

USA = gpd.read_file('./Shapefiles/cb_2018_us_state_20m.shp')

#States = USA.STUSPS.tolist()
Outside = ['AK', 'HI', 'PR']

States = [state for state in USA.STUSPS.tolist() if state not in Outside]

#USA.plot()
USA[USA['STUSPS'].isin(States)].boundary.plot()

plt.show()