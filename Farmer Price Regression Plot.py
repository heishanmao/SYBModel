#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 06/06/2022 12:18 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : Farmer Price Regression Plot.py
# @Software: PyCharm
# @Notes   :

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from sklearn.metrics import r2_score
import scipy.stats as stats
import scipy
from scipy.optimize import curve_fit  # nonlinear least squares

sns.set() # set the default seaborn style
sns.set_theme(style="white")

class FarmerPriceRegressionPlot:

    def __init__(self):
        self.df = pd.read_csv('Regression price.csv', usecols=['Farm price ($/metric ton)', 'Ending stocks to use ratio', 'Year'])[['Ending stocks to use ratio', 'Farm price ($/metric ton)', 'Year']]
        self._ax_setting()


    def _ax_setting(self):
        colors = ['#8ea3c2', '#a4b38c', '#eeb27e', '#b3bcb9', '#f1df82']
        self.fig, self.ax = plt.subplots(figsize=(18,9),dpi=300)
        self.ax.set_xlabel('Ending stocks to use ratio (%)')
        self.ax.set_ylabel('Farm price ($/metric ton)')

        #self._plot_original()
        self.XYA, self.XYB = self._plot_original_two()

        self._linear(colors[1])
        #self. _linear_two()
        self._curve(self.XYA, 'A', colors[0])
        self._curve(self.XYB, 'B', colors[2])

        self.ax.legend()

        self.fig.show() # show


    def _plot_original(self):
        self.ax.plot(self.df.iloc[:, 0], self.df.iloc[:, 1], 'o', label='original data')

        for i in range(len(self.df)):
            self.ax.annotate(self.df.iloc[i, 2], (self.df.iloc[i, 0], self.df.iloc[i, 1]), xytext=(self.df.iloc[i, 0] + 0.001, self.df.iloc[i, 1]))

    def _plot_original_two(self):
        ###################################################################
        # Data 分为 before07 & after07 两部分分开回归
        ###################################################################
        XYAf08 = self.df.iloc[0:13, :]
        XYBf08 = self.df.iloc[13:, :]
        XYBf08 = XYBf08.reset_index(drop=True)

        self.ax.plot(XYAf08.iloc[:, 0], XYAf08.iloc[:, 1], 'o', label='Original data (1989-2006)')
        self.ax.plot(XYBf08.iloc[:, 0], XYBf08.iloc[:, 1], 'o', label='Original data (2007-2019)')

        for i in range(len(XYAf08)):
            self.ax.annotate(XYAf08.iloc[i, 2], (XYAf08.iloc[i, 0], XYAf08.iloc[i, 1]), xytext=(XYAf08.iloc[i, 0] + 0.001, XYAf08.iloc[i, 1] - 10), fontsize=16)
        for i in range(len(XYBf08)):
            self.ax.annotate(XYBf08.iloc[i, 2], (XYBf08.iloc[i, 0], XYBf08.iloc[i, 1]), xytext=(XYBf08.iloc[i, 0] + 0.001, XYBf08.iloc[i, 1] - 10), fontsize=16)

        return  XYAf08, XYBf08

    def _linear(self, color):
        res = scipy.stats.linregress(self.df.iloc[:, 0], self.df.iloc[:, 1])
        print(f"R-squared: {res.rvalue ** 2:.6f}")
        print(f"p-value: {res.pvalue ** 2:.6f}")

        self.ax.plot(self.df.iloc[:,0], res.intercept + res.slope*self.df.iloc[:,0], color=color, label='$y_0 = {:.2f}  {:.2f}x$'.format(res.intercept, res.slope))

        #self.ax.annotate(f"p-value: {res.pvalue ** 2:.6f}", xy=(3, 3), xytext=(3, 4.5), arrowprops=dict(arrowstyle='<-', facecolor="red"))

    def _linear_two(self):
        resA = scipy.stats.linregress(self.XYA.iloc[:,0], self.XYA.iloc[:,1])
        resB = scipy.stats.linregress(self.XYB.iloc[:,0], self.XYB.iloc[:,1])

        self.ax.plot(self.XYA.iloc[:,0], resA.intercept + resA.slope*self.XYA.iloc[:,0], 'r', label='fitted line')
        self.ax.plot(self.XYB.iloc[:,0], resB.intercept + resB.slope*self.XYB.iloc[:,0], 'r', label='fitted line')

    def _curve(self, XY, label, color):
        # 拟合自定义函数
        def func(x, a, b):
            return a + b * (1 / x)

        # popt返回的是给定模型的最优参数。我们可以使用pcov的值检测拟合的质量，其对角线元素值代表着每个参数的方差。
        popt, pcov = curve_fit(func, XY.iloc[:, 0], XY.iloc[:, 1])
        a = popt[0]
        b = popt[1]
        #Yvals = func(XY.iloc[:, 0], a, b)  # 拟合y值

        XY_pred = XY.iloc[:, 0].apply(lambda x: func(x, a, b)).rename('Pred')
        XY = pd.concat([XY, XY_pred], axis=1)
        XY = XY.sort_values(by='Ending stocks to use ratio')  # 按X排序

        self.ax.plot(XY.iloc[:, 0], XY.iloc[:, 3], color=color, label='$y_{}= {:.2f} + {:.2f}/x$'.format(label, a, b), linewidth=2)

    def save(self):
        self.fig.savefig('./Figs/Ending_regression.pdf', dpi=300, bbox_inches="tight")

if __name__ == "__main__":
    SMALL_SIZE = 20
    MEDIUM_SIZE = 22
    BIGGER_SIZE = 22

    plt.rc('font', size=SMALL_SIZE)  # controls default text sizes
    plt.rc('axes', titlesize=SMALL_SIZE)  # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)  # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

    demo = FarmerPriceRegressionPlot()
    demo.save()
