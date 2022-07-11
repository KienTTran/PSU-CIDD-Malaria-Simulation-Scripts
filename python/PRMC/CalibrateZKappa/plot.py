# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 11:31:22 2022

@author: nguyentd
"""

import pandas as pd

exp_number = 18

local_path = "D:\\plot\\PRMC_Exp_" + str(exp_number) + "\\"
local_path_raw = local_path + "\\raw"
local_path_bin = local_path + "\\bin"

data = pd.read_csv(local_path + "data_dev_exp_" + str(exp_number) + ".csv")
data['age2to10'] = data.age2/data.age10

#%%
import seaborn as sns

g = sns.FacetGrid(data, col="kappa")

g.map_dataframe(sns.scatterplot, x="eir", y="age2to10", hue="z", palette=sns.color_palette("husl", len(data['z'].unique()))[:len(data['z'].unique())]).set(xscale = 'log')

g.add_legend()

#%%

sns.palplot(sns.hls_palette(10))
