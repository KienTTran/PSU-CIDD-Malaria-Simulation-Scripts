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
        file_path = os.path.join(local_path_raw, filename)
        try:
            csv = pd.read_csv(file_path,sep='\t',header=None,index_col=None)
            row = csv.iloc[120,[10,12] + [*range(22,32)]]            
            r = row.to_list()
            r.append(120)
            r.append(beta)
            data.append(r)
            row = csv.iloc[360,[10,12] + [*range(22,32)]]
            r = row.to_list()
            r.append(360)
            r.append(beta)
            data.append(r)        
        except:
            print(filename + " error reading")
        
data_plot = pd.DataFrame(data)
data_plot.columns = ["eir","pfpr",*["moi"+str(x) for x in range(10)],"month","beta"]

#%%
data_plot.to_csv(local_path + "data_plot_EIR_PfPR_" + str(exp_number) + ".csv",index=False)  

#%%
data_plot = pd.read_csv(local_path + "data_plot_EIR_PfPR_" + str(exp_number) + ".csv") 

#%%
sum_moi = data_plot[["moi"+str(x) for x in range(1,10)]].sum(axis=1)
for x in range(1,10):
    data_plot["moi"+str(x)] = data_plot["moi"+str(x)]/sum_moi   


#%%
import seaborn as sns
from matplotlib import pyplot as plt

plt.close("all")   
plot = sns.scatterplot(data=data_plot, x="eir", y="pfpr", hue="month") 
plot.set(xscale="log")
plot.set(xlim=(10**-3,10**3),ylim=(0,100))
plot.set_yticks(range(0,100,10))
plot.set_xlabel('EIR')
plot.set_ylabel('% PfPR')
# plot.set(xlim=(0, 10))

#%%
plot.figure.savefig(local_path + "Exp_" + str(exp_number) + "_EIR_PfPR_Log.png", dpi=300)

#%%
import seaborn as sns
from matplotlib import pyplot as plt

plt.close("all")   
plot = sns.scatterplot(data=data_plot, x="beta", y="eir", hue="month") 
plot.set(yscale="log")
plot.set(xlim=(0,3),ylim=(10**0,10**3))
plot.set_xlabel('EIR')
plot.set_ylabel('% PfPR')
# plot.set_yticks(range(0,100,10))
# plot.set(xlim=(0, 10))
#%%
plot.figure.savefig(local_path + "Exp_" + str(exp_number) + "_EIR_PfPR_Linear.png", dpi=300)

#%%
import seaborn as sns
from matplotlib import pyplot as plt
import math

# plt.close("all")

data_120 = data_plot[data_plot.month == 120]   
betas = data_120.beta.unique()

fig, axes = plt.subplots(4,5,sharex=True,sharey=True, squeeze=True)
for index,beta in enumerate(betas):
    r = index//5
    c = index % 5
    data_beta = data_120[((data_120.beta == beta))]
    data_moi = data_beta[["moi"+str(x) for x in range(1,10)]]
    data_moi.columns=[*range(1,10)]
    data_moi_melt = pd.melt(data_moi)
    data_moi_melt.columns = ["MOI","freq"]
    sns.boxplot(data=data_moi_melt,x="MOI",y="freq",ax=axes[r,c])
    
    eir_percentile = np.percentile(data_beta["eir"],[25,50,75])
    pfpr_percentile = np.percentile(data_beta["pfpr"],[25,50,75])
    
    if r < 3:
        axes[r,c].set_xlabel("")
    if c > 0:
        axes[r,c].set_ylabel("")
    
    axes[r,c].set_title("EIR: %.2f - PFPR: %.2f"%(eir_percentile[1],pfpr_percentile[1]))
    
#%%
import seaborn as sns
from matplotlib import pyplot as plt
import math

# plt.close("all")

data_360 = data_plot[data_plot.month == 360]   
betas = data_360.beta.unique()

fig, axes = plt.subplots(4,5,sharex=True,sharey=True, squeeze=True)
for index,beta in enumerate(betas):
    r = index//5
    c = index % 5
    data_beta = data_360[((data_360.beta == beta))]
    data_moi = data_beta[["moi"+str(x) for x in range(1,10)]]
    data_moi.columns=[*range(1,10)]
    data_moi_melt = pd.melt(data_moi)
    data_moi_melt.columns = ["MOI","freq"]
    sns.boxplot(data=data_moi_melt,x="MOI",y="freq",ax=axes[r,c])
    
    eir_percentile = np.percentile(data_beta["eir"],[25,50,75])
    pfpr_percentile = np.percentile(data_beta["pfpr"],[25,50,75])
    
    if r < 3:
        axes[r,c].set_xlabel("")
    if c > 0:
        axes[r,c].set_ylabel("")
    
    axes[r,c].set_title("EIR: %.2f - PFPR: %.2f"%(eir_percentile[1],pfpr_percentile[1]))
        

            