#/bin/sh
. /cvmfs/sft.cern.ch/lcg/views/setupViews.sh LCG_96python3 x86_64-centos7-gcc8-opt
cd /user/olkes/Gamma-ray\ FastMC/run
python MC_run.py -r 123457
