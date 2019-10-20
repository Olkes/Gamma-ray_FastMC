import sys

sys.path.insert(0, "python/")

from particle import particle
from physics import em_physics
from cylinder import cylinder

import numpy as np
import pandas as pd
import datetime


def generate_events(nevents, energy, vrt, edep_max, nscatter, random_seed,
                    r_cryostat, z_cryostat, r_fiducial, z_fiducial,
                    mode="sim_files"):
    #
    # define the geometry
    #
    fiducial_volume = None

    # make sure the variables are floats and not strings!
    energy = float(energy)
    edep_max=float(edep_max)

    radius_cryostat = float(r_cryostat)  # cm
    height_cryostat = float(z_cryostat)
    cryostat = cylinder(R=radius_cryostat, h=height_cryostat)

    radius_fiducial = float(r_fiducial)  # cm
    height_fiducial = float(z_fiducial)  # cm
    fiducial = cylinder(R=radius_fiducial, h=height_fiducial)

    #
    # define the physics
    #
    em = em_physics()

    #
    # random seed
    #
    np.random.seed(random_seed)
    #
    # set location and file name
    if mode == 'ref':  # referance files in a separate folder
        location = '/' + str(energy) + '/ref_files/'
        if fiducial_volume == 'large':  # files with a big fiducial volume in a separate folder
            location = '/' + str(energy) + '/ref_files/large_fiducial_volume/'

    elif mode == 'sim_files':  # Simulation files (not ref)
        if vrt == 'fiducial_scatter':  # plain vrt files
            location = '/' + str(energy) + '/vrt/'
            if edep_max < energy:  # vrt files with energy cut
                location = '/' + str(energy) + '/vrt/250kev_ecut/'
        else:  # non vrt files
            location = '/' + str(energy) + '/non_vrt/'

    else:
        print('ERROR wrong mode')

    filename = str(location) + 'simdata_n=' + str(nevents)
    #
    # set write out (how many scatters are written in output file
    writeout = 4
    # Open and clear file files
    tarr = []
    open('/data/xenon/acolijn/mcdata' + str(filename) + '.' + 'csv', 'w+').close()

    # Event generation loop
    for ieve in range(nevents):

        if ieve % 25000 == 0:
            print("generated ", ieve, " events")
        #
        # make a particle,
        #
        p = particle(type='gamma',
                     energy=energy,
                     geometry=cryostat,
                     fiducial=fiducial,
                     vrt=vrt,
                     edep_max=edep_max,
                     nscatter_max=nscatter,
                     physics=em,
                     debug=False
                     )

        #
        # propagate the particle and retrieve the intersection points
        #
        p.propagate()

        #
        # store data
        #
        warr = [ieve, len(p.xint), p.weight, p.edep, p.x0start[0], p.x0start[1], p.x0start[2]]
        # Store first numbers: event, nscatters, weight, energy deposit, start point

        for i in range(len(p.xint)):
            warr.extend([p.xint[i][0][0], p.xint[i][0][1], p.xint[i][0][2], p.xint[i][1]])
            # Extend write-out with place and energy deposit of each scatter

        tarr.append(warr[:((writeout * 4) + 7)])
        # Makes sure only x scatters are written down in the file

        if ieve % 10 == 0:
            df = pd.DataFrame(tarr)

            df.to_csv('/data/xenon/acolijn/mcdata/' + str(filename) + '.' + 'csv', mode='a', index=False,
                      header=False)
            # Write the data to a file in chunks (size is a parameter)
            tarr = []
            del (df)
            # delete total array and data-frame

    # make not in sim log book
    f = open('/data/xenon/acolijn/mcdata/sim_log.csv', 'a+')

    dandt = datetime.datetime.now()
    day = dandt.strftime("%d/%m/%Y")
    time = dandt.strftime("%H:%M")

    arr = [day, time, energy, mode, nevents,
           nscatter, random_seed, writeout, edep_max,
           radius_cryostat, height_cryostat,
           radius_fiducial, height_fiducial,
           ]
    head = ['day', 'time', 'energy', 'sim_mode', 'nevents',
            'nscatter', 'seed', 'writeout', 'edep_max',
            'radius_cryostat', 'height_cryostat',
            'radius_fiducial', 'height_fiducial',
            ]

    f.write(str(arr) + '\n')

    # close log file

    f.close()
    return
