#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18/07/2021 11:50 PM
# @Author  : Scott
# @Main    : Zheng@utk.edu
# @File    : SYBMobel.py
# @Software: PyCharm
# @Notes   : A model function for SYB supply chain with Gurobi

from gurobipy import *
import pandas as pd

# import Datasets
    ## from CElevts to LElevts by Trucks  e ,j
Cost_C_L = pd.read_csv('..\SYBM_Data_Cost&Production\CostByTruck.csv', index_col = 0).to_numpy()
    ## from LElevts to ETerminals by Barges j,k
Cost_L_E = pd.read_csv('..\SYBM_Data_Cost&Production\CostByBarge.csv', index_col = 0).to_numpy()
    ## from ETerminals to IChina by Ocean shipment k,m
Cost_E_I = pd.read_csv('..\SYBM_Data_Cost&Production\CostByOcean.csv', index_col = 0).to_numpy()
    ## from CElevts to Domestic Processing Facility C^P
Cost_E_F = pd.read_csv('..\SYBM_Data_Cost&Production\CostToFacility.csv', index_col = 0, usecols =['Name','Facility']).T.to_numpy()[0]
    ## Country elevators hoding cost C^H
Cost_E_H = pd.read_csv('..\SYBM_Data_Cost&Production\CostToFacility.csv', index_col = 0, usecols =['Name','HoldingCost']).T.to_numpy()[0]
    ## Supply of each Country elevator
S = pd.read_csv('..\SYBM_Data_Cost&Production\ProductionByCountry.csv',index_col = 0,usecols=['Name','Production']).T.to_numpy()[0]
    ## Chian demand at year 2019
D = 88e6
    ## last year inventory for each country elevator 2019
I_last = pd.read_csv('..\SYBM_Data_Cost&Production\ProductionByCountry.csv',index_col = 0,usecols=['Name','Ending']).T.to_numpy()[0]

# Parameters
T = 1   # Do not change! period year
Year = 2019

CElevts = Cost_C_L.shape[0] # number of Country elevators
LElevts = Cost_L_E.shape[0] # number of Larger elevators
ETerminals = Cost_E_I.shape[0] # number of export terminals
IChina = Cost_E_I.shape[1] # number of import terminals in China
Alpha = 0.9    # Inventory deterioration rate

#Dom_P =  200   # Domestic Soybean price
Beta1 = 315.948
Beta2 = 0
Beta3 = -4.43476   # Regression coefficients

#Glo_P =  400   # Global Soybean price
Gamma1 = 117.09
Gamma2 = 0
Gamma3 = 5.6e-6  # Regression coefficients

## Model
ModelName = "Soybean_V13_Ju;y-18-2021"
model = Model(ModelName)


# %%
# Vars
x = model.addVars(CElevts, LElevts, lb=0, name="x_ejt")
I = model.addVars(CElevts, lb=0, name='I_et')
f = model.addVars(CElevts, lb=0, name='f_et')
y = model.addVars(LElevts, ETerminals, lb=0, name='y_jkt')
z = model.addVars(ETerminals, IChina, lb=0, name='z_kmt')
Dp= model.addVar(vtype=GRB.CONTINUOUS, name='DomesticP')
Gp= model.addVar(vtype=GRB.CONTINUOUS, name='GlobalP')
## Slack Vars
L = model.addVar(T, vtype=GRB.BINARY, name='L-Climate')
F = model.addVar(T, vtype=GRB.BINARY, name='F-GOVPolicy')


# %%
# add constraints 2
for e in range(CElevts):
    model.addConstr(Alpha*I_last[e] + S[e] == f[e] + I[e] + quicksum(x[e,j] for j in range(LElevts)))


# %%
# add Constraints 3
for j in range(LElevts):
    model.addConstr(quicksum(x[e,j] for e in range(CElevts)) == quicksum(y[j,k] for k in range(ETerminals)))


# %%
# add Constratints 4
for k in range(ETerminals):
    model.addConstr(quicksum(y[j,k] for j in range(LElevts)) == quicksum(z[k,m] for m in range(IChina)))


# %%
# add Constratints 5
model.addConstr(quicksum(z[k,m] for k in range(ETerminals)
                                for m in range(IChina)) <= D)


# %%
# add Constratints 6
model.addConstr(Dp == Beta1 + Beta2*L + Beta3*quicksum(I))


# %%
# add Constratints 7
model.addConstr(Gp == Gamma1 + Gamma2*F + Gamma3*quicksum(z))


# %%
# Obj
obj = LinExpr()
obj += quicksum((Gp-Cost_E_I[k,m])*z[k,m] for k in range(ETerminals)
                                             for m in range(IChina))
obj -= quicksum(Cost_C_L[e,j]*x[e,j] for e in range(CElevts)
                                     for j in range(LElevts))
obj += quicksum((Dp-Cost_E_F[e])*f[e] for e in range(CElevts))
obj -= quicksum(Cost_E_H[e]*I[e] for e in range(CElevts))
obj -= quicksum(Cost_L_E[j,k]*y[j,k] for j in range(LElevts)
                                     for k in range(ETerminals))
model.setObjective(
    obj,
    GRB.MAXIMIZE
)


# %%
model.update()
model.params.NonConvex = 2
model.optimize()
model.write(ModelName+'.lp')


# %%
# Print solution
print('Number of variables: ' + str(model.getAttr("NumVars")))
print('Number of linear constraints: '+ str(model.getAttr("NumConstrs")))
print('Objective value for current solution: '+ str(model.getAttr("ObjVal")))