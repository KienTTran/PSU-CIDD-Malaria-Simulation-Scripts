# -*- coding: utf-8 -*-
"""
Created on Wed May 25 22:40:17 2022

@author: kient
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

#%%
# Generate synthetic data
omega = np.linspace(0, 50)

A0s = [1., 18., 40., 100.]

dfs = []
for A0 in A0s:
    V_w_dr = np.sin(A0*omega)
    V_w_tr = np.cos(A0*omega)
    dfs.append(pd.DataFrame({'omega': omega,
                             'V_w_dr': V_w_dr,
                             'V_w_tr': V_w_tr,
                             'A0': A0}))
df = pd.concat(dfs, axis=0)

dfm = df.melt(id_vars=['A0', 'omega'], value_vars=['V_w_dr', 'V_w_tr'])
g = sns.FacetGrid(dfm, col='A0', hue='A0', row='variable', sharey='row', margin_titles=True)
g.map(plt.plot, 'omega', 'value')

#%%
df=pd.DataFrame({'depth':[499,500,501,502,503],'parameter1':[25,29,24,23,25],'parameter2':[72,80,65,64,77]})
df2 = df.melt(id_vars=['depth'])

g = sns.FacetGrid(data=df2, col='variable')
g.map_dataframe(sns.lineplot, x='depth', y='value')