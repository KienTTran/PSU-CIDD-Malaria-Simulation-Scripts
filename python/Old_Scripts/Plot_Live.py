# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 10:51:43 2021

@author: ktt5121

"""

import sys
import os
from ftplib import FTP

ftp = FTP("datamgr.aci.ics.psu.edu")
ftp.login('ktt5121@psu.edu')
ftp.cwd("/storage/home/k/ktt5121/")

ftp.quit()