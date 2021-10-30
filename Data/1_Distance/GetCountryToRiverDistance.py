#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17/06/2021 4:44 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : A spider to get the distance from country elevators to larger river elevators.
            # input: "./data10top.csv"  "./LargerElevators.csv"
            # Outputs: 'CountryToRiverDistance.csv'
# @Software: PyCharm

from selenium import webdriver
import pandas as pd
import time
import re

def MakeUrl():
    url = 'https://www.mapdevelopers.com/mileage_calculator.php'
    return url

def GetDistance(Origin, Distination):
    driver.find_element_by_id('fromInput').clear()
    driver.find_element_by_id('toInput').clear()
    driver.find_element_by_id('fromInput').send_keys(Origin)
    driver.find_element_by_id('toInput').send_keys(Distination)
    driver.find_elements_by_class_name('link_button')[0].click()

    time.sleep(2)
    FligthDis = driver.find_element_by_id('status_flight').text
    CarDis = driver.find_element_by_id('status_car').text

    FMiles = re.findall(r"\d+\.?\d*",FligthDis)[0] # miles
    CMiles = re.findall(r"\d+\.?\d*", CarDis)[0]  # miles
    return float(CMiles)

if __name__=='__main__':

    # import Data
    originLocation = pd.read_csv("./data10top.csv")
    destinationLocation = pd.read_csv("./LargerElevators.csv")

    print(originLocation.head(), destinationLocation.head())

    # Spider
    url = MakeUrl()
    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(3)

    res = pd.DataFrame(index=originLocation['Name'], columns=destinationLocation['Name'])
    for i in range(len(originLocation)):
        for j in range(len(destinationLocation)):
            res.iloc[i,j] = GetDistance(originLocation.iloc[i,3], destinationLocation.iloc[j, 1])
            print(originLocation.iloc[i,3],destinationLocation.iloc[j,1], res.iloc[i,j])
        res.to_csv('CountryToLargerDistance.csv')
