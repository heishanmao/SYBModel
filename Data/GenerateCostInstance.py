#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 30/10/2021 10:27 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : GenerateCostInstance.py.py
# @Software: PyCharm
# @Notes   : Generate Cost Instance according to the configuration
import os
path = os.path.abspath('.')  # D:\OneDrive - University of Tennessee\Scripts\SYBModel\Data
import sys

sys.path.append('./Country/')
import FunCalCostOfCountry
## CalCostOfCountry(pathIn, pathOut, LimitFacility, LimitCountryToRiver, LimitCountryToRail):
FunCalCostOfCountry.CalCostOfCountry(path+'\\Country\\', path+'\\Cost\\', [20,35], [30,40], [30,40])

sys.path.append('./River&Rail/')
import FunCalCostOfRiverRail
## CalCostOfRiverRail(pathIn, pathOut, LimitRiver, LimitRail):
FunCalCostOfRiverRail.CalCostOfRiverRail(path+'\\River&Rail\\', path+'\\Cost\\', [50,90], [40,80])

sys.path.append('./Export/')
import FunCalCostOfExport
## CalCostOfExport(pathIn, pathOut, LimitExport)
FunCalCostOfExport.CalCostOfExport(path+'\\Export\\', path+'\\Cost\\', [100,120])




