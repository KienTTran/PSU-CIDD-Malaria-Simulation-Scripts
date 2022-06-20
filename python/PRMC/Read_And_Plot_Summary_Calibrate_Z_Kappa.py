# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 21:02:18 2022

@author: kient
"""
import os
import re
import pandas as pd
import numpy as np
import math

exp_number = 14

local_path = "D:\\plot\\PRMC_2_Genotypes_Exp_" + str(exp_number) + "\\"
local_path_raw = local_path + "\\raw"
local_path_bin = local_path + "\\bin"

config_df = pd.read_csv(local_path + 'configs.csv',index_col=False)
config_df.set_index('Index', inplace=True)

n_run = 1

data = []
#%%
for index,config in config_df.iterrows(): 
    for run in range(n_run):
        # print(run)
        filename = "summary_%d.txt"%(index*1000 + run)
        # print(filename)        
        kappa = config.kappa
        z = config.z
        beta = config.beta
        # print(beta,ifr)        
        file_path = os.path.join(local_path_raw, filename)
        try:
            csv = pd.read_csv(file_path,sep='\t',header=None,index_col=None)
            row = csv.iloc[0,[4,6] + [*range(13,73)]]            
            r = row.to_list()
            r.append((float)(kappa))
            r.append((float)(z))
            r.append((float)(beta))
            data.append(r)        
        except Exception as e:
            print(filename + " error reading " + str(e))
            
data_plot = pd.DataFrame(data)
data_plot.columns = ["eir","pfpr",*["age"+str(x) for x in range(60)],"kappa","z","beta"]

#data_plot["eir_log10"] = math.log10(data_plot.eir)
#%%
data_plot.to_csv(local_path + "data_dev_exp_" + str(exp_number) + ".csv",index=False)
#%%
data_plot = pd.read_csv(local_path + "data_dev_exp_" + str(exp_number) + ".csv")
#%%
import seaborn as sns
from matplotlib import pyplot as plt
import math

kappas = [0.1,0.5,1.0,2,4]
data_plot_by_kappa = []

for kappa in kappas:
    data_plot_by_kappa.append(data_plot[data_plot.kappa == kappa])
    
fig, axes = plt.subplots(3,3,sharex=True,sharey=True, squeeze=True)
for index,data_by_kappa in enumerate(data_plot_by_kappa):
    # data_by_kappa_plot = data_by_kappa[(data_by_kappa.eir > 19) & (data_by_kappa.eir < 20)]
    r = index//3
    c = index % 3
    sns.scatterplot(data=data_by_kappa,x="eir",y="age2",hue="z", ax=axes[r,c])
    