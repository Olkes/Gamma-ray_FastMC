#!/bin/bash
export PATH=/data/xenon/joranang/anaconda/bin:$PATH 
source activate fastMC
python /user/olkes/FastMC/runit/generate_jobs.py -r 12345
