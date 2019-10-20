import pandas as pd
import os,sys

def write_script(settings):
    ## OLKES SET THIS CORRECTLY
    environment_setup = ". ~/nb_venv/bin/activate"

    ## OLKES SET THIS CORRECTLY
    run_dir = "your deirectory where you run the scipts"
    run_dir = "/user/z37/Gamma-ray_FastMC/runit/"

    #
    # this is the directory where your scripts will live
    #
    script_dir = run_dir +'/scripts/'
    #
    # if the scripts directory does not exist.... make it
    #
    if not os.path.exists(script_dir):
        cmd = 'mkdir '+script_dir
        os.system(cmd)


    #
    # generate a shell script
    #
    scriptfile = script_dir+'/job'+str(settings['job_id'])+".sh"

    print('job settings: ',settings)

    print('start generation of job')
    fout = open(scriptfile,"w")
    fout.write("#/bin/sh \n")
    #fout.write("/cvmfs/sft.cern.ch/lcg/views/setupViews.sh LCG_96python3 x86_64-centos7-gcc8-opt \n")
    fout.write(environment_setup+" \n")
    fout.write("cd " + run_dir + " \n")
    fout.write("python MC_run.py --nevents="+str(settings['nevents']))
    fout.write(" --energy="+str(settings['energy']))
    fout.write(" --vrt="+str(settings['vrt']))
    fout.write(" --edep_max="+str(settings['edep_max']))
    fout.write(" --nscatter="+str(int(settings['nscatter'])))
    fout.write(" --ran_seed="+str(int(settings['ran_seed'])))
    fout.write(" --r_cryostat="+str(settings['r_cryostat']))
    fout.write(" --z_cryostat="+str(settings['z_cryostat']))
    fout.write(" --r_fiducial="+str(settings['r_fiducial']))
    fout.write(" --z_fiducial="+str(settings['z_fiducial']))
    fout.write(" --output="+str(settings['output']))

    ##fout.write(" --fiducial_volume="+str(settings['fiducial_volume']))

    fout.close()

    #
    # execute the job
    #
    os.system('chmod +x '+scriptfile)
    log_dir = run_dir +'/logs'
    #
    # if the logfile directory does not exist.... make it
    #
    if not os.path.exists(log_dir):
        cmd = 'mkdir '+log_dir
        os.system(cmd)

    os.system('qsub -e '+log_dir+' -o '+log_dir+' '+scriptfile)

#
# main function
#
def main():

    if sys.argv[1] == '--i':
        job_file = sys.argv[2]
    else:
        job_file = 'jobs.xlsx'

    print('generate_jobs:: reading settings from ',job_file)
    if not os.path.exists(job_file):
        print('generate_jobs:: ERROR job_file =',job_file,' does not exist')
        exit(-1)


    #
    # read xls fiel with job parameters
    #
    df = pd.read_excel(job_file)
    #
    # write script file and submit to queue
    #
    for index,row in df.iterrows():
        write_script(row)

if __name__ == "__main__":
    main()
