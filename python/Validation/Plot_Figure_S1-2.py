# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 12:53:46 2022

@author: kient
"""
import math
import seaborn as sns
from matplotlib import pyplot as plt
import numpy as np

z = np.arange(1,10.01,0.2)	
kappa = np.arange(0.1,2.51,0.1)



kappa = []
a = range(1,101)
a2 = []
a2o10 = []
for age in a:
    if age < 10:
        a2.append(math.pow(age/10.0,kappa) * math.pow(1.01,age) * 0.00125)
    else:
        a2.append(math.pow(1.01,age-10) * 0.0013809)
        
for age in a[0:10]:
    a2o10.append(a2[age]/a2[10])
    

sns.lineplot(a2o10)