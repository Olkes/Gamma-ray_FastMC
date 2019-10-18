import sys, getopt
sys.path.insert(0, "../run/")

from driver import *

def main(argv):
    ran_seed = 0

    opts, args = getopt.getopt(argv, "r:")

    for opt, arg in opts:
        if opt == '-r':
            ran_seed = int(arg)
        elif opt == "-n":
            nevent = int(arg)
        elif opt == "-e":
            energy = float(arg)
        elif opt == "-c":
            ecut = float(arg)
        elif opt == "-m":
            nscatter = int(arg)

    print('random seed = ', ran_seed)
    # vrt simulation
    generate_events(nevents=nevent,
                    energy=energy,
                    vrt='fiducial_scatter',
                    edep_max=ecut,
                    nscatter=nscatter,
                    random_seed=ran_seed,
                    mode='sim_files',
                    fiducial_volume='Normal')


if __name__ == "__main__":
    main(sys.argv[1:])
