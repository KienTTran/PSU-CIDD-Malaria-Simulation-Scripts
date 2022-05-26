# -*- coding: utf-8 -*-
"""
Created on Thu May 19 21:42:01 2022

@author: kient
"""

import os
import re
import pandas as pd
import numpy as np
import math
import itertools

exp_number = 99

local_path = "D:\\plot\\PRMC_2_Genotypes_Exp_" + str(exp_number) + "\\"
local_path_raw = local_path + "\\raw"
local_path_bin = local_path + "\\bin"

data = []

index = 0
run = 0

# print(run)
filename_db = "gene_db_%d.txt"%(index*1000 + run)
filename_freq = "gene_freq_%d.txt"%(index*1000 + run)
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
    data.append(csv_freq)
except Exception as e:
    raise
    print(file_path_freq + " error reading " + str(e))
    
data_plot = pd.concat(data,ignore_index=True, axis = 0)    

data = []

# print(run)
filename_db = "allele_db_%d.txt"%(index*1000 + run)
filename_freq = "allele_freq_%d.txt"%(index*1000 + run)
file_path_db = os.path.join(local_path_raw, filename_db)
file_path_freq = os.path.join(local_path_raw, filename_freq)
try:
    csv_db = pd.read_csv(file_path_db, sep='\t', header=None,index_col=None)
    csv_db.columns = ["id","aa_sequence"]   
    genotype_names = csv_db.aa_sequence
    genotype_names = pd.concat([genotype_names, pd.Series(["temp"])], ignore_index=True)
    csv_freq = pd.read_csv(file_path_freq, sep='\t', header=None, names = genotype_names)
    csv_freq = csv_freq.fillna(0)
    csv_freq = csv_freq.drop(['temp'], axis=1)  
    data.append(csv_freq)
except Exception as e:
    raise
    print(file_path_freq + " error reading " + str(e))
    
data_plot_2 = pd.concat(data,ignore_index=True, axis = 0)    

# initial_genotypes = [
#                         "||||YY1||KTHFI,x||||||FNMYRIPRPC|1", 
#                         "||||YY1||TTHFI,x||||||FNMYRIPRPY|1"
#                      ]
# X_i = []
# mutated_allele_pairs = []
# mutated_loci = []

# data_columns = data_plot.columns
            
# for index,pair in enumerate(zip(*data_columns)):
#     mutated_allele = []
#     for elem in pair:
#         if elem not in mutated_allele:
#             mutated_allele.append(elem)
#     if len(mutated_allele) > 1:
#         mutated_allele_pairs.append(mutated_allele)
#         mutated_loci.append(index)
        
# # Calculate Allele freq     
# for allele_pair in mutated_allele_pairs:
#     for allele in allele_pair:
#         data_plot["Allele " + allele] = 0
#         data_plot["X_" + allele] = 0
        
# for column in data_columns:
#     for index,pos in enumerate(mutated_loci):
#         if column[pos] == mutated_allele_pairs[index][1]:
#             data_plot["Allele " + column[pos]] += data_plot[column]
         
#%%
if len(csv_db.aa_sequence) == 4:
    LD_1 = data_plot.iloc[:,0]*data_plot.iloc[:,1] - data_plot.iloc[:,2]*data_plot.iloc[:,3] 
else:
    LD_1 = data_plot.iloc[:,0]*data_plot.iloc[:,1] 
LD_2 = data_plot_2.mean(axis=1)
    
norm = np.linalg.norm(LD_2)
LD_2 = LD_2/norm

#%%
import seaborn as sns
from matplotlib import pyplot as plt

# plt.close("all")   
# plot = sns.lineplot(data=data_plot_2, x=data_plot_2.index, y="LD") 
plot = sns.lineplot(data=data_plot_2, x=data_plot_2.index, y=LD_2)
plot.set_xlabel('Month')
plot.set_ylabel('LD')
# plot.set_yticks(range(0,100,10))
# plot.set(xlim=(0, 10))