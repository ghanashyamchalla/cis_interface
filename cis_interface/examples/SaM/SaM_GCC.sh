#!/bin/bash

# make output dir if it's not there
[ -d Output ] || mkdir Output

# ----------------Your Commands------------------- #


cisrun SaM_GCC.yml > ./Output/SaM_log.txt
