# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 11:04:48 2022

@author: kient
"""
import os
import re
import pandas as pd
import numpy as np

exp_number = '18_22'

local_path = "D:\\plot\\PRMC_Exp_" + str(exp_number) + "\\"
local_path_raw = local_path + "\\raw"
local_path_bin = local_path + "\\bin"

config_df = pd.read_csv(local_path_bin + '\\configs.csv',index_col=False)
config_df.set_index('Index', inplace=True)

#%%
n_run = 1

data = []

for index,config in config_df.iterrows():
    # print(index,config)
    for run in range(n_run):
        # print(run)
        filename = "validation_monthly_data_%d.txt"%(run + index*1000)
        # print(filename)
        beta = config.beta 
        ifr = config.ifr 
        prmc_size = config.prmc_size 
        file_path = os.path.join(local_path_raw, filename)
        try:
            csv = pd.read_csv(file_path,sep='\t',header=None,index_col=None)
            row = csv.iloc[120,[10,12] + [*range(22,32)]]            
            r = row.to_list()
            r.append(120)
            r.append((float)(beta))
            r.append((float)(ifr))
            r.append((float)(prmc_size))
            data.append(r)
            row = csv.iloc[360,[10,12] + [*range(22,32)]]
            r = row.to_list()
            r.append(360)
            r.append((float)(beta))
            r.append((float)(ifr))
            r.append((float)(prmc_size))
            data.append(r)        
        except:
            print(filename + " error reading")
        
data_plot = pd.DataFrame(data)
data_plot.columns = ["eir","pfpr",*["moi"+str(x) for x in range(10)],"month","beta","ifr","prmc_size"]

sum_moi = data_plot[["moi"+str(x) for x in range(1,10)]].sum(axis=1)
for x in range(1,10):
    data_plot["moi"+str(x)] = data_plot["moi"+str(x)]/sum_moi   

#%%
data_plot.to_csv(local_path + "data_plot_EIR_PfPR_IFR_" + str(exp_number) + ".csv",index=False)  

#%%
data_plot = pd.read_csv(local_path + "data_plot_EIR_PfPR_IFR_" + str(exp_number) + ".csv") 

#%%
import seaborn as sns
from matplotlib import pyplot as plt

plt.close("all")   
plot = sns.scatterplot(data=data_plot, x="eir", y="pfpr", hue="month") 
plot.set(xscale="log")
        
#%%
import seaborn as sns
from matplotlib import pyplot as plt
import math

g = sns.FacetGrid(data_plot, col="ifr", row="month")
g.map_dataframe(sns.scatterplot, x="eir", y ="pfpr", hue="prmc_size")

#%%
import seaborn as sns
from matplotlib import pyplot as plt
import math


# plt.close("all")

data_120 = data_plot[data_plot.month == 120]   
betas = data_120.beta.unique()
ifrs = data_120.ifr.unique()
sizes = data_120.prmc_size.unique()

fig, axes = plt.subplots(len(ifrs),len(betas),sharex=True,sharey=True)

for i_index,ifr in enumerate(ifrs):
    for b_index,beta in enumerate(betas):
        r = i_index
        c = b_index
        data_beta = data_120[((data_120.beta == beta) & (data_120.ifr == ifr))]
        data_moi = data_beta[["moi"+str(x) for x in range(1,10)]]
        data_moi.columns=[*range(1,10)]
        data_moi_melt = pd.melt(data_moi)
        data_moi_melt.columns = ["MOI","freq"]
        sns.boxplot(data=data_moi_melt,x="MOI",y="freq",ax=axes[r,c])
        
        eir_percentile = np.percentile(data_beta["eir"],[25,50,75])
        pfpr_percentile = np.percentile(data_beta["pfpr"],[25,50,75])
        
        if r < len(ifrs) - 1:
            axes[r,c].set_xlabel("")
        if c > 0:
            axes[r,c].set_ylabel("")
        
        axes[r,c].set_title("EIR: %.2f - PFPR: %.2f - IFR: %.2f"%(eir_percentile[1],pfpr_percentile[1],(float)(ifr)))
        axes[r,c].grid(True, axis='both')
#%%
import seaborn as sns
from matplotlib import pyplot as plt
import math


# plt.close("all")

data_360 = data_plot[data_plot.month == 360]   
betas = data_360.beta.unique()
ifrs = data_360.ifr.unique()
sizes = data_360.prmc_size.unique()

fig, axes = plt.subplots(len(ifrs),len(betas),sharex=True,sharey=True)

for i_index,ifr in enumerate(ifrs):
    for b_index,beta in enumerate(betas):
        r = i_index
        c = b_index
        data_beta = data_360[((data_360.beta == beta) & (data_360.ifr == ifr))]
        data_moi = data_beta[["moi"+str(x) for x in range(1,10)]]
        data_moi.columns=[*range(1,10)]
        data_moi_melt = pd.melt(data_moi)
        data_moi_melt.columns = ["MOI","freq"]
        sns.boxplot(data=data_moi_melt,x="MOI",y="freq",ax=axes[r,c])
        
        eir_percentile = np.percentile(data_beta["eir"],[25,50,75])
        pfpr_percentile = np.percentile(data_beta["pfpr"],[25,50,75])
        
        if r < len(ifrs) - 1:
            axes[r,c].set_xlabel("")
        if c > 0:
            axes[r,c].set_ylabel("")
        
        axes[r,c].set_title("EIR: %.2f - PFPR: %.2f - IFR: %.2f"%(eir_percentile[1],pfpr_percentile[1],(float)(ifr)))
        axes[r,c].grid(True, axis='both')
        
#%%
import seaborn as sns
from matplotlib import pyplot as plt
import math


# plt.close("all")

data_360 = data_plot[data_plot.month == 360]   
betas = data_360.beta.unique()
ifrs = data_360.ifr.unique()
sizes = data_360.prmc_size.unique()

fig, axes = plt.subplots(len(sizes),len(betas),sharex=True,sharey=True)

for i_index,p_size in enumerate(sizes):
    for b_index,beta in enumerate(betas):
        r = i_index
        c = b_index
        data_beta = data_360[((data_360.beta == beta) & (data_360.prmc_size == p_size))]
        data_moi = data_beta[["moi"+str(x) for x in range(1,10)]]
        data_moi.columns=[*range(1,10)]
        data_moi_melt = pd.melt(data_moi)
        data_moi_melt.columns = ["MOI","freq"]
        sns.boxplot(data=data_moi_melt,x="MOI",y="freq",ax=axes[r,c])
        
        eir_percentile = np.percentile(data_beta["eir"],[25,50,75])
        pfpr_percentile = np.percentile(data_beta["pfpr"],[25,50,75])
        
        if r < len(ifrs) - 1:
            axes[r,c].set_xlabel("")
        if c > 0:
            axes[r,c].set_ylabel("")
        
        axes[r,c].set_title("PFPR: %.2f - PRMC Size: %.2f"%(pfpr_percentile[1],(float)(p_size)))
        axes[r,c].grid(True, axis='both')