# import the regex module
import re
import os 
from pathlib import Path
import numpy as np
import yaml

def read_parameters():
    keys = []
    values = []
    print("Reading parameters.yml")
    with open(r'parameters.yml') as file:
        documents = yaml.full_load(file)
        for item, doc in documents.items():
            keys.append(item)
            values.append(doc)    
    return keys,values            
        
if __name__=="__main__":
    file_path = str(Path.cwd())
    if "\\" in file_path:
        folder = file_path.split("\\")[-1]
    else:
        folder = file_path.split("/")[-1]
    print("Will generate cmd to folder: " + folder)
    param_keys, param_values = read_parameters()
    print(param_keys)
    print(param_values)
    run_line_total = 1
    for value in param_values:
        run_line_total *= len(value)
    print("Will generate " + str(run_line_total) + " lines")
    template = (r"cmd.template")   
    all_value_list = []
    
    for index,key in enumerate(param_keys):
        print("Key " + str(key) + " will be replaced by " + str(param_values[index]))
        if len(all_value_list) == 0:
            for value in param_values[index]:
                all_value_list.append(str(value))
        else:
            temp = []
            for line in all_value_list:
                for value in param_values[index]:
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
        for value_list in all_value_list:
            line_temp = line_template
            for k_index,key in enumerate(param_keys):
                line_temp = re.sub("#"+key+"#", value_list.split("#")[k_index], line_temp)
            print(line_temp)
            line_out.append(line_temp+"\n")
        new_file.writelines(line_out)
            
        
    
                
            