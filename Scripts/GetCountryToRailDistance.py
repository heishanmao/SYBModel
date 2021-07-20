#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/07/2021 12:11 AM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : GetCountryToRailDistance.py
# @Software: PyCharm
# @Notes   : a script to get distance from Country_Elevator to Rail_Elevator

from selenium import webdriver
import pandas as pd
import time
import re

def MakeUrl():
    url = 'https://www.mapdevelopers.com/mileage_calculator.php'
    return url
