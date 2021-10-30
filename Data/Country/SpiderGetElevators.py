#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 30/07/2020 5:08 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : SpiderGetElevators.py
            # a spider script to obtain all informations of country elevators
            # outputs: data.csv
# @Software: PyCharm

from selenium import webdriver
import pandas as pd

def MakeUrl(sn):
    url = 'https://grain-elevators.regionaldirectory.us/' + sn + '.htm'
    return url

def OpenWeb(url):
    browser = webdriver.Chrome()
    browser.get(url)
    browser.implicitly_wait(3)
    data = browser.find_elements_by_css_selector('#top > tbody > tr:nth-child(4) > td.b > table.b > tbody > tr > td')
    return data

def DataClean(data, sn, SN):
    ## 第一个td
    box = []
    for i in range(1, len(data), 3):
        name = data[i].text.split('\n')
        box.append(name[0:5])
    box = pd.DataFrame(box, columns=['Name', 'Address', 'Phone', 'Website', 'Located'])

    ## 第二个td
    FU = []
    for i in range(2, len(data), 3):
        function = data[i].text.split('\n')
        function = ', '.join(function)
        FU.append(function)
    #print(FU)
    s = pd.Series(FU)
    box['Function'] = s
    ## 增加州及简写列
    state_name = pd.Series([sn]*int((len(data)-1)/3))
    State_Name = pd.Series([SN]*int((len(data)-1)/3))

    box['StateName'] = state_name
    box['SN'] = State_Name

    end_order = ['Name', 'StateName', 'SN', 'Address', 'Phone', 'Website', 'Located', 'Function']
    box = box[end_order]

    return box


if __name__ == '__main__':
    '''
    state = 'illinois'
    SL = 'IL'
    '''

    statelist = ['illinois', 'iowa', 'minnesota', 'indiana', 'nebraska', 'ohio', 'missouri',
                 'north-dakota', 'kansas', 'south-dakota', 'arkansas', 'michigan', 'mississippi',
                 'wisconsin', 'kentucky', 'tennessee']
    StateList = ['IL', 'IA', 'MN', 'IN', 'NE', 'OH', 'MO', 'ND', 'KS', 'SD', 'AR', 'MI', 'MS', 'WI', 'KY',
                 'TN']

    STATE = pd.DataFrame({
        'sn': pd.Series(statelist),
        'SN': pd.Series(StateList)
    })

    # i = 8
    # url = MakeUrl(STATE.iloc[i][0])
    # #print(url)
    # elements = OpenWeb(url)
    # data = DataClean(elements, STATE.iloc[i][0], STATE.iloc[i][1])
    # print(data)
    # data.to_csv('./data.csv', mode='a', index=False, header=None)


    for i in range(0, len(STATE)):
        url = MakeUrl(STATE.iloc[i][0])
        #print(url)
        elements = OpenWeb(url)
        data = DataClean(elements, STATE.iloc[i][0], STATE.iloc[i][1])
        print(data)
        data.to_csv('./data.csv', mode='a', index=False, header=None)
