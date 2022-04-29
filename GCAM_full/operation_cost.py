#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 27/04/2022 11:33 AM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : operation_cost.py
# @Software: PyCharm
# @Notes   :

import pandas as pd
import numpy as np
from sklearn import linear_model
import os

class OperationCost:
    def __init__(self, year):
        self.root = 'D:/OneDrive - University of Tennessee/Scripts/SYBModel'
        self.input_path = self.root + '/GCAM_full/USDA_cost_data.csv'
        self.year = year
        self.data = pd.read_csv(self.input_path, header=7)

        self.data.query('Crop == "Soybeans"', inplace=True)
        self.data.query('Item == "Fertilizer" or Item == "Irrigated" or Item =="Total operating costs"', inplace=True)

        self.years = self.data.columns[4:].to_numpy().astype('int')
        self.operation_cost = self.data.query('Item =="Total operating costs"').iloc[:,4:].to_numpy()
        self.irrigated_cost = self.data.query('Item == "Irrigated"').iloc[:,4:].to_numpy()
        self.fertilized_cost = self.data.query('Item == "Fertilizer"').iloc[:,4:].to_numpy()

        self.IRR_lo = round(self._predict_IRR_lo()[0][0], 2)  # dollars per km2
        self.IRR_hi = round(self._predict_IRR_hi()[0][0], 2)
        self.RFD_lo = round(self._predict_RFD_lo()[0][0], 2)
        self.RFD_hi = round(self._predict_RFD_hi()[0][0], 2)

    def _predict_IRR_lo(self):
        Y = self.operation_cost - self.irrigated_cost - self.fertilized_cost
        self.X = self.years.reshape(-1, 1)
        return self.__train(self.X, Y.reshape(-1, 1))

    def _predict_IRR_hi(self):
        Y = self.operation_cost - self.fertilized_cost
        return self.__train(self.X, Y.reshape(-1, 1))

    def _predict_RFD_lo(self):
        Y = self.operation_cost - self.fertilized_cost - self.irrigated_cost / 2
        return self.__train(self.X, Y.reshape(-1, 1))

    def _predict_RFD_hi(self):
        Y = self.operation_cost - self.irrigated_cost / 2
        return self.__train(self.X, Y.reshape(-1, 1))

    def __train(self, X, Y):
        regr = linear_model.LinearRegression().fit(X, Y)
        a = np.array(self.year).reshape(-1, 1)
        return regr.predict(np.array(self.year).reshape(-1, 1))


if __name__ == '__main__':
    cost = OperationCost(2100)
