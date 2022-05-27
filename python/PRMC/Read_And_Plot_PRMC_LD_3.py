# -*- coding: utf-8 -*-
"""
Created on Tue May 17 15:55:41 2022

@author: kient
"""

import os
import re
import pandas as pd
import numpy as np
import math
import itertools
import os
import re
import pandas as pd
import numpy as np
import math
import seaborn as sns
import random
import matplotlib.pyplot as plt
from itertools import combinations
import yaml

exp_number = 12

a4_dims = (15, 8.27)

local_path = "D:\\plot\\PRMC_2_Genotypes_Exp_" + str(exp_number) + "\\"
local_path_raw = local_path + "\\raw"
local_path_bin = local_path + "\\bin"

config_df = pd.read_csv(local_path_bin + '\\configs.csv',index_col=False)
config_df.set_index('Index', inplace=True)

n_run = 10

#%%
data = []
data_plot = []


with open(os.path.join(local_path_bin, 'sim_prmc.yml'), 'r') as stream:
    content = yaml.full_load(stream)
    mutation_mask = content['mutation_mask']

for index,config in config_df.iterrows():
    for run in range(n_run):
        # if index == 140:
        # print(run)
        filename_db = "gene_db_%d.txt"%(index*1000 + run)
        filename_freq = "gene_freq_%d.txt"%(index*1000 + run)
        # print(filename_db) 
        beta = config.beta 
        prmc_size = config.prmc_size      
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
            csv_freq['genotype_column_length'] = len(csv_freq.columns)
            csv_freq['mutation_mask'] = mutation_mask
            csv_freq['month'] = csv_freq.index
            csv_freq['year'] = np.floor(csv_freq['month'] / 12)
            csv_freq['beta'] = [beta]*len(csv_freq)
            csv_freq['prmc_size'] = [prmc_size]*len(csv_freq)
            csv_freq['ifr'] = [ifr]*len(csv_freq)
            data.append(csv_freq)
        except Exception as e:
            raise
            print(file_path_freq + " error reading " + str(e))
data_plot = pd.concat(data,ignore_index=True, axis = 0)    

#%%
data_plot.to_csv(local_path + "data_plot_exp_" + str(exp_number) + "_LD_2.csv",index=False)          

#%%

data_plot = pd.read_csv(local_path + "data_plot_exp_" + str(exp_number) + "_LD_2.csv")

mask = data_plot['mutation_mask'][0]
masked_loci = []

genotype_column_length = data_plot['genotype_column_length'][0]
all_genotypes = data_plot.columns[0:genotype_column_length]

for index,locus in enumerate(mask):
    if locus == '1':
        masked_loci.append(index)

loci_3 = random.sample(masked_loci,3)
# loci_3 = [31,33,4]
loci_3_all = list(combinations(masked_loci, 3)) 
    
observe_index = 0
observe_genotype = all_genotypes[observe_index]

allele_map = {}

#p_i, p_j, p_k
for locus in masked_loci:
    allele_map[locus] = observe_genotype[locus]    
    data_plot[str(locus) + '-' + observe_genotype[locus]] = 0

for index,loci_3 in enumerate(loci_3_all):  
    loci_3_str = '-'.join([str(elem) for elem in loci_3])
    loci_2 = list(combinations(loci_3, 2)) 
    
    #Psi_ij, Psi_jk, Psi_ik   
    for locus,locus_pair in zip(loci_3,loci_2):
        pair = str(locus_pair[0]) + '-' + observe_genotype[locus_pair[0]] + '-' + str(locus_pair[1]) + '-' + observe_genotype[locus_pair[1]]
        data_plot[pair] = 0
     
    #Psi_ijk
    pair = str(loci_3[0]) + '-' + allele_map[loci_3[0]] + '-' + str(loci_3[1]) + '-' + allele_map[loci_3[1]] + '-' + str(loci_3[2]) + '-' + allele_map[loci_3[2]]
    data_plot[pair] = 0
    
    #Allele freq
    for genotype in all_genotypes:
        #p_i, p_j, p_k
        for locus in loci_3:
            if genotype[locus] == allele_map[locus]:
                data_plot[str(locus) + '-' + allele_map[locus]] += data_plot[genotype];
        #Psi_ij, Psi_jk, Psi_ik
        for locus_pair in loci_2:
            if genotype[locus_pair[0]] == allele_map[locus_pair[0]] and genotype[locus_pair[1]] == allele_map[locus_pair[1]]:
                pair = str(locus_pair[0]) + '-' + allele_map[locus_pair[0]] + '-' + str(locus_pair[1]) + '-' + allele_map[locus_pair[1]]
                data_plot[pair] += data_plot[genotype]   
        #Psi_ijk
        if genotype[loci_3[0]] == allele_map[loci_3[0]] and genotype[loci_3[1]] == allele_map[loci_3[1]] and genotype[loci_3[2]] == allele_map[loci_3[2]]:
            pair = str(loci_3[0]) + '-' + allele_map[loci_3[0]] + '-' + str(loci_3[1]) + '-' + allele_map[loci_3[1]] + '-' + str(loci_3[2]) + '-' + allele_map[loci_3[2]]
            data_plot[pair] += data_plot[genotype]
            
#%%   
    ld_columns = data_plot.columns[-4:]
    print(loci_3,ld_columns)
    
    p_i = data_plot[ld_columns[0]]
    p_j = data_plot[ld_columns[1]]
    p_k = data_plot[ld_columns[2]]
    Psi_ij = data_plot[ld_columns[3]]
    Psi_ik = data_plot[ld_columns[4]]
    Psi_jk = data_plot[ld_columns[5]]
    Psi_ijk = data_plot[ld_columns[6]]
    C_ij = Psi_ij - p_i * p_j
    C_jk = Psi_jk - p_j * p_k
    C_ik = Psi_ik - p_i * p_k
    data_plot['ld'] = Psi_ijk - p_i * C_jk - p_j * C_ik - p_k * C_ij - p_i*p_j*p_k  
    
#%%
data_plot.to_csv(local_path + "data_plot_exp_" + str(exp_number) + "_LD_3.csv",index=False)   

#%%

data_plot = pd.read_csv(local_path + "data_plot_exp_" + str(exp_number) + "_LD_3.csv")

plot = sns.relplot(data = data_plot, 
            x = 'month',
            y = 'ld',
            col = 'prmc_size',
            row = 'beta',
            hue = 'ifr',
            # style = "prmc_size",
            kind = "line",
            ci = 'sd',
            palette=sns.color_palette("husl",7)[:len(data_plot.ifr.unique())],
            height = a4_dims[1], aspect = 1.5
            )

plt.subplots_adjust(hspace = 0.2, wspace = 0.1) 

# for ax in plot.axes.flat:
#     ax.set_title("test")
#     ax.title.set_position([0.5, 1.0])
#%%
plot.savefig(local_path + "data_plot_exp_" + str(exp_number) + "_LD_2_" + str(loci_3_str) + " .png", dpi=300)        
        
