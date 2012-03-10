# -*- coding: utf-8 -*-
"""
file   arlmmodel.py
author ernesto.adorio@gmail.com
       UPDEPP at Clarkfield
"""
from matlib import *
from lm import *
def arLMmodel(Xdata, lag = 2, withdrift= True):
    """
    Outputs the model matrix and response vector for the lm solver.
    """
    p = lag
    n = len(Xdata)
    X = []
    for i in reversed(range(0, p)):
       X.append(Xdata[i:n-p+i])
    Y = Xdata[p:]
    X = transpose(X)
    if withdrift:
       matInsertConstCol(X, 0, 1)
    return X, Y
"""
Here is  a test routine for generating the MLR model for a small time series data. The data is from page.398, Table 9-5 of Hanke and Wichern.
"""
if __name__ == "__main__":
    Xdata = [60.0, 81.0, 72.0, 78.0, 61.5, 78.0, 57.0, 84.0, 72.0, 67.8,
             99.0, 25.5, 93.0, 75.0, 57.0, 88.5, 76.5, 82.5, 72.0, 76.5,
             75.0, 78.0, 66.0, 97.5, 60.0, 97.5, 61.5, 96.0, 79.5, 72.0,
             79.5, 64.5, 99.0, 72.0, 78.0, 63.0, 66.0, 84.0, 66.0, 87.0,
             61.5, 81.0, 76.5, 84.0, 57.0, 84.0, 73.5, 78.0, 49.5, 78.0,
             88.5, 51.0, 85.5, 58.5, 90.0, 60.0, 78.0, 66.0, 97.5, 64.5,
             72.0, 66.0, 73.5, 66.0, 73.5,103.5, 60.0, 81.0, 87.0, 73.5,
             90.0, 78.0, 87.0, 99.0, 72.0]
    X, Y = arLMmodel(Xdata, lag=1)
    mataugprint(X,Y)
    fit = ols(X,Y)
    print fit.betas



