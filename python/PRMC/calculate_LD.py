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
from itertools import combinations

exp_number = 11

local_path = "D:\\plot\\PRMC_2_Genotypes_Exp_" + str(exp_number) + "\\"
local_path_raw = local_path + "\\raw"
local_path_bin = local_path + "\\bin"

config_df = pd.read_csv(local_path_bin + '\\configs.csv',index_col=False)
config_df.set_index('Index', inplace=True)

n_run = 1

#%%
data = []

for index,config in config_df.iterrows():
    for run in range(n_run):
        if index == 140:
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
                data.append(csv_freq)
            except Exception as e:
                raise
                print(file_path_freq + " error reading " + str(e))
data_plot = pd.concat(data,ignore_index=True, axis = 0)    

#%%
data_plot.to_csv(local_path + "data_plot_exp_140" + str(exp_number) + ".csv",index=False)          

#%%

data_plot = pd.read_csv(local_path + "data_plot_exp_140" + str(exp_number) + ".csv")

mask = "||||111||10000,0||||||0000000001|1"
masked_loci = []

all_genotypes = data_plot.columns
initial_genotypes = all_genotypes[0:2]

for index,locus in enumerate(mask):
    if locus == '1':
        masked_loci.append(index)

loci_3 = random.sample(masked_loci,3)
loci_2 = list(combinations(loci_3, 2))  
allele_map = {}
allele_freq_single = []
allele_freq_pair = []
    
observe_genotype = initial_genotypes[0]

#p_i, p_j, p_k
for locus,locus_pair in zip(loci_3,loci_2):
    allele_map[locus] = observe_genotype[locus]
    data_plot[str(locus) + '-' + observe_genotype[locus]] = 0

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
        data_plot[pair] += data_plot[genotype];
        

#%%
            

        
        
