# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 11:31:22 2022

@author: nguyentd
"""

import pandas as pd

data = pd.read_csv('data_0422.csv')
data['age2to10'] = data.age2/data.age10

#%%
import seaborn as sns

g = sns.FacetGrid(data, col="kappa")

g.map_dataframe(sns.scatterplot, x="eir", y="age2to10", hue="z", palette=sns.color_palette("husl", 9)[:4]).set(xscale = 'log')

g.add_legend()

#%%

sns.palplot(sns.hls_palette(10))
