# import the regex module
import re
import os 
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
import math
import copy
import sys

def read_parameters(parameter):
    params = {}
    print("Reading " + parameter)
    with open(parameter,'r') as file:
        documents = yaml.full_load(file)
        for item, doc in documents.items():
            params[item] = doc
    return params
        
if __name__=="__main__":
    parameter_file = str(sys.argv[1])
    job_template_file = str(sys.argv[2])
    submit_job_template_file = str(sys.argv[3])
    username = str(sys.argv[4])
    job_name = str(sys.argv[5])
    job_pbs_file = str(sys.argv[6])
    submit_job_pbs_file = str(sys.argv[7])
    job_exe = 'MaSim'
    
    params = read_parameters(parameter_file)
    print(params)   
    
    #Calculate beta log10
    start = math.log10(params['beta'][0])
    stop = math.log10(params['beta'][1])
    step = (stop - start)/params['beta'][-1]
    log10_beta = np.arange(start,stop,step)
    betas = 10**log10_beta
    params['beta'] = betas
    #kappa
    params['kappa'] = np.arange(params['kappa'][0],params['kappa'][1],params['kappa'][2])
    #z
    params['z'] = np.arange(params['z'][0],params['z'][1],params['z'][2])
  
    config_number = 0
    for beta in params['beta']:
        for z in params['z']:
            for k in params['kappa']:                
                config_number += 1
                
    print("Total %d configs, %d runs"%(config_number,config_number * params['replicates'][0]))
            
    #Change job_template file
    f = open(job_template_file,'r')
    template = f.read()
    f.close()
    new_file_data = template.replace("#JOB_NAME#", job_name + "\n")
    new_file_data = new_file_data.replace("#JOB_EXE#", job_exe + "\n")
    
    f = open(job_pbs_file,'w')
    f.write(new_file_data)
    f.close()            
    	
    #Change submit_all_jobs file
    f = open(submit_job_template_file,'r')
    template = f.read()
    f.close()
    new_file_data = template.replace("#USERNAME#",username + "\n")
    new_file_data = new_file_data.replace("#TOTAL_CONFIGS#",str(config_number - 1) + "\n")
    new_file_data = new_file_data.replace("#REPLICATES#",str(params['replicates'][0]) + "\n")
    f = open(submit_job_pbs_file,'w')
    f.write(new_file_data)
    f.close()
    
    
    
            
        
    
                
            