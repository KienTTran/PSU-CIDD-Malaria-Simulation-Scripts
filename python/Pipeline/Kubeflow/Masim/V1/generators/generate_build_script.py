# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 14:34:47 2022

@author: kient
"""

import sys
import os

if __name__=="__main__":
    template_file = sys.argv[1]
    username = sys.argv[2]
    f = open(template_file,'r')
    template = f.read()
    f.close()
    build_sh_file_data = template.replace("#username#",username)
    print('Writing build script')
    f = open(template_file,'w')
    f.write(build_sh_file_data)
    f.close()