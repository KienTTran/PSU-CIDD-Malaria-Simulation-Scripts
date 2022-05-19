# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 11:04:48 2022

@author: kient
"""
import os
import re
import pandas as pd
import numpy as np
import math

exp_number = 10

local_path = "D:\\plot\\PRMC_2_Genotypes_Exp_" + str(exp_number) + "\\"
local_path_raw = local_path + "\\raw"
local_path_bin = local_path + "\\bin"

config_df = pd.read_csv(local_path_bin + '\\configs.csv',index_col=False)
config_df.set_index('Index', inplace=True)

n_run = 10

data = []

for index,config in config_df.iterrows():
    for run in range(n_run):
        # print(run)
        filename_db = "gene_db_%d.txt"%(index*1000 + run)
        filename_freq = "gene_freq_%d.txt"%(index*1000 + run)
        # print(filename_db) 
        beta = config.beta 
        prmc_size = config.prmc_size      
        ifr = config.ifr   
        ifr = config.ifr
        # print(beta,ifr)        
        file_path_db = os.path.join(local_path_raw, filename_db)
        file_path_freq = os.path.join(local_path_raw, filename_freq)
        try:
            csv_db = pd.read_csv(file_path_db, sep='\t', header=None,index_col=None)
            csv_db.columns = ["id","aa_sequence"]   
            genotype_names = csv_db.aa_sequence
            genotype_names = pd.concat([genotype_names, pd.Series(["temp"])], ignore_index=True)
            csv_freq = pd.read_csv(file_path_freq, sep='\t', header=None, names = genotype_names, index_col=None)
            csv_freq = csv_freq.fillna(0)
            csv_freq = csv_freq.drop(['temp'], axis=1)
            csv_freq['month'] = csv_freq.index
            csv_freq['beta'] = [beta]*len(csv_freq)
            csv_freq['prmc_size'] = [prmc_size]*len(csv_freq)
            csv_freq['ifr'] = [ifr]*len(csv_freq)
            csv_freq['ld'] = csv_freq[csv_db.aa_sequence[0]]*csv_freq[csv_db.aa_sequence[1]]
            
            if len(csv_db.aa_sequence) == 4:
                csv_freq['ld'] = csv_freq['ld'] - csv_freq[csv_db.aa_sequence[2]]*csv_freq[csv_db.aa_sequence[3]]
            
            data.append(csv_freq)            
        except Exception as e:
            raise
            print(file_path_freq + " error reading " + str(e))
        
data_plot = pd.concat(data,ignore_index=True, axis = 0)
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


#%%
import seaborn as sns
from matplotlib import pyplot as plt
import math

# plt.close("all")

data_120 = data_plot[data_plot.month == 120]   
betas = data_120.beta.unique()
ifrs = data_120.ifr.unique()

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
        

            