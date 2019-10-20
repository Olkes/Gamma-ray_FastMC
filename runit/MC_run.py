import argparse

import sys
sys.path.insert(0, "../python/")

from driver import *

def main(argv):

    #
    # parse the arguments
    #
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--nevents')
    parser.add_argument('--energy')
    parser.add_argument('--vrt')
    parser.add_argument('--edep_max')
    parser.add_argument('--nscatter')
    parser.add_argument('--ran_seed')
    parser.add_argument('--r_cryostat')
    parser.add_argument('--z_cryostat')
    parser.add_argument('--r_fiducial')
    parser.add_argument('--z_fiducial')

    
    args = parser.parse_args()

    ###print(args)

    #
    # execute simulation
    #
    generate_events(nevents=int(args.nevents),
                    energy=args.energy,
                    vrt=args.vrt,
                    edep_max=args.edep_max,
                    nscatter=int(args.nscatter),
                    random_seed=int(args.ran_seed),
                    r_cryostat=float(args.r_cryostat),
                    z_cryostat=float(args.z_cryostat),
                    r_fiducial=float(args.r_fiducial),
                    z_fiducial=float(args.z_fiducial),
                    mode="sim_files"
                    )

#
# main function
#
if __name__ == "__main__":
    main(sys.argv[1:])