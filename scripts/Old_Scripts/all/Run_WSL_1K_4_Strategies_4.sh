#!/bin/bash
./MaSim -i ../../kientt/Demo_WSL_1K_4_SFT_AS.yml -r MonthlyReporter -x "SFT_AS"
./MaSim -i ../../kientt/Demo_WSL_1K_4_5YearCycling.yml -r MonthlyReporter -x "5YearCycling"
./MaSim -i ../../kientt/Demo_WSL_1K_4_AdaptiveCycling.yml -r MonthlyReporter -x "AdaptiveCycling"
./MaSim -i ../../kientt/Demo_WSL_1K_4_MFT.yml -r MonthlyReporter -x "MFT"