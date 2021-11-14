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
import FunCalCostOfCountry2
## CalCostOfCountry2(pathIn, pathOut):
FunCalCostOfCountry2.CalCostOfCountry(path+'\\Country\\', path+'\\Cost\\')

# sys.path.append('./River&Rail/')
# import FunCalCostOfRiverRail
# ## CalCostOfRiverRail(pathIn, pathOut, LimitRiver, LimitRail):
# FunCalCostOfRiverRail.CalCostOfRiverRail(path+'\\River&Rail\\', path+'\\Cost\\', [40,50], [40,50])
#
sys.path.append('./Export/')
import FunCalCostOfExport2
## CalCostOfExport2(pathIn, pathOut)
FunCalCostOfExport2.CalCostOfExport(path+'\\Export\\', path+'\\Cost\\')




