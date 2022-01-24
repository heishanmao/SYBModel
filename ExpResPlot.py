#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 21/01/2022 10:16 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : ExpResPlot.py
# @Software: PyCharm
# @Notes   :
import pandas as pd
import matplotlib.pyplot as plt
import os

SMALL_SIZE = 14
MEDIUM_SIZE = 14
BIGGER_SIZE = 14

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

import seaborn as sns
sns.color_palette("Set2")
#sns.set_theme()
sns.set_style("white")
root = os.path.abspath('.')  # 'D:\\OneDrive - University of Tennessee\\Scripts\\SYBModel'

filelist=os.listdir(root+'\Exp\/')
# 遍历输出每一个文件的名字和类型
for item in filelist:
    # 输出指定后缀类型的文件
    if(item.endswith('.csv')):
        print(os.path.splitext(item)[0])
        #fileName = 'Exp1_1_88e6'
        fileName = os.path.splitext(item)[0]
        data = pd.read_csv(root+'\Exp\/'+ fileName+'.csv')

        data['Demand'] = data['Demand'] / 1e7
        data['Supply'] = data['Supply'] / 1e6
        data['Export'] = data['Export'] / 1e6
        data['Supply/Demand'] = data['Supply/Demand']
        data['Export/Demand'] = data['Export/Demand']
        data['Export/Supply'] = data['Export/Supply']
        data['ObjVal'] = data['ObjVal'] / 1e8

        data1 = data.loc[:, ['Demand', 'Supply', 'Export', 'ObjVal']]
        data2 = data.loc[:, ['Supply/Demand', 'Export/Demand', 'Export/Supply']]
        x_ticks = [str(x) for x in data.iloc[:,0].tolist()]
        fig,ax = plt.subplots(1,1,figsize=(9,6))
        ax1 = ax.twinx()

        data1.plot(kind='bar', ax = ax, alpha =0.5)
        ax.legend(loc='center left')
        ax1 = data2.plot(kind='line', ax = ax1, style=['-x','-+','-v'], alpha =1)
        ax.set_xticklabels(x_ticks, rotation=360)
        ax1.legend(loc='center')

        plt.savefig(root+'\Exp\/'+ fileName + '.png', dpi=300)
        plt.show()