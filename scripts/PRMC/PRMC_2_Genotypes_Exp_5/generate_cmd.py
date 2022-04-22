# import the regex module
import re
import os 
from pathlib import Path
import numpy as np
import yaml
import math
import copy

def read_parameters():
    params = {}
    print("Reading parameters.yml")
    with open(r'parameters.yml') as file:
        documents = yaml.full_load(file)
        for item, doc in documents.items():
            params[item] = doc
    return params
        
if __name__=="__main__":
    file_path = str(Path.cwd())
    if "\\" in file_path:
        folder = file_path.split("\\")[-1]  
    else:
        folder = file_path.split("/")[-1]
    print("Will generate configs to folder: " + folder)
    params = read_parameters()
    print(params)

    template = (r"cmd.template")   
    all_value_list = []  
    
    #Calculate beta log10
    start = math.log10(params['beta'][0])
    stop = math.log10(params['beta'][1])
    step = (stop - start)/params['beta'][-1]
    log10_beta = np.arange(start,stop,step)
    betas = 10**log10_beta
    params['beta'] = betas
        
    #Write to cmd.sh (for Rob queue job version)
    for index,key in enumerate(params):
        print(index,key,params[key])
        if len(all_value_list) == 0:
            for value in params[key]:
                all_value_list.append(str(value))
        else:
            temp = []
            for line in all_value_list:
                for value in params[key]:
                    temp.append(line + "#" + str(value))
            all_value_list = temp
            
    for index,line in enumerate(all_value_list):
        print(index, line)          
    line_template = ""
    line_out = []
    with open(r"cmd.template", "r") as old_file:
        for line in old_file:
            line_template = line            
    line_template = re.sub("#folder#", folder, line_template)
    with open(r"run_cmd.sh", "w") as new_file:
        line_out.append("#!/bin/bash\n")
        line_out.append("source Scripts/%s/Schedule_Run_PRMC.sh &&\n"%(folder))
        for index,value_list in enumerate(all_value_list):
            line_temp = line_template
            for k_index,key in enumerate(params):
                if key == 'beta':
                        line_temp = re.sub("#"+key+"#", '%.3f'%(float)(value_list.split("#")[k_index]), line_temp)
                else:
                    line_temp = re.sub("#"+key+"#", value_list.split("#")[k_index], line_temp)
            print(line_temp)
            if index == len(all_value_list) - 1:
                line_out.append(line_temp)
            else:
                line_out.append(line_temp+" &&\n")
        new_file.writelines(line_out)
            
        
    
                
            