#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 24/04/2022 1:07 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : Get_DemandTariff.py
# @Software: PyCharm
# @Notes   :
import pandas as pd

class _China_Demand():
    def __init__(self, year):
        self.path = '../GCAM_full/China_Demand_022022.xlsx'
        self.data = pd.read_excel(self.path, index_col=0)
        self.year = year

        self.quantity, self.tariff = self._demand_tariff(self.year)

    def _demand_tariff(self, year):
        # unit 1e4 ton
        if year <= 2021 and year >= 2000:
            quantity = self.data.loc['中国大豆进口总量', year] * 1e4  # tons
            tariff = self.data.loc['中国大豆每年进口关税变化（针对美国）', year]  # %
        elif year < 2000:
            gap = 2000 - year
            quantity = self.data.loc['中国大豆进口总量', 2000] * 1e4 * 0.99**gap # tons
            tariff = self.data.loc['中国大豆每年进口关税变化（针对美国）', 2000] * 0.999**gap    # %
        elif year > 2021:
            gap = year - 2021
            quantity = self.data.loc['中国大豆进口总量', 2021] * 1e4 * 1.05**gap # tons
            tariff = self.data.loc['中国大豆每年进口关税变化（针对美国）', 2021] * 1.009**gap   # %

        return round(quantity,2), round(tariff,2)


if __name__ == '__main__':

    China = _China_Demand(2022)
    print(China.quantity, China.tariff)
