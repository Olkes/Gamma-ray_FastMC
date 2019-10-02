import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chisquare


class analysis:
    def __init__(self, **kwargs):
        """

        Initialize a analysis
        :param kwargs:
            nevents_ref: Select which file you want to use as a reference file.
            nevents_sim: size of simulation that is used
            vrt: if want to use a variance reduction simulation(anything) or a normal MC(None)
            nscatter: if the file is a vrt-sim specify the number of scatters of the gamma-rays (integers 1,2,3)
            rseed: if you want to use the file with a random seed(anything) or not(None)


        """

        self.nevents_ref = kwargs.pop('nevents_ref', 10000001)
        self.nevents_sim = kwargs.pop('nevents_sim', 100000)
        self.vrt = kwargs.pop('vrt', None)
        self.nscatter = kwargs.pop('nscatter', 1)
        self.rseed = kwargs.pop('rseed', None)
        self.ecut = kwargs.pop('ecut',None)

    def load_ref_file(self):
        """
        Load in the data that is used as a reference.
        In general this is a large nevent non-vrt simulation is used

        :param nevents: Select which file you want to use as a reference file.
         all reference files are non-vrt and therefore only the size matters for selection.

        :return df: returns pandas dataframe with all the events

        """

        self.ref_df = pd.read_csv('../mcdata/Reference files/Reference%i.csv' % self.nevents_ref,
                                  names=['#', 'nscatters', 'w', 'de', 'x0', 'y0', 'z0', 'x1', 'y1', 'z1', 'de1', 'x2',
                                         'y2',
                                         'z2', 'de2', 'x3', 'y3', 'z3', 'de3', 'x4', 'y4', 'z4', 'de4'],
                                  error_bad_lines=False)
        # load file as pandas dataframe

        self.ref_df.insert(10, 'r2_1', self.ref_df['x1'] ** 2 + self.ref_df['y1'] ** 2)
        self.ref_df.insert(15, 'r2_2', self.ref_df['x2'] ** 2 + self.ref_df['y2'] ** 2)
        self.ref_df.insert(20, 'r2_3', self.ref_df['x3'] ** 2 + self.ref_df['y3'] ** 2)
        self.ref_df.insert(25, 'r2_4', self.ref_df['x3'] ** 2 + self.ref_df['y3'] ** 2)
        # insert the r squared coordinates of the first 4 scatters

        return (self.ref_df)

    def load_file(self):
        """
        load a data file that is used for further analysis

        :param nevents: size of simulation that is used
        :param vrt: if want to use a variance reduction simulation(anything) or a normal MC(None)
        :param nscatter: if the file is a vrt-sim specify the number of scatters of the gamma-rays (integers)
        :param rseed: if you want to use the file with a random seed(anything) or not(None)



        :return df: returns pandas dataframe with all the events

        """

        if self.vrt == None:
            file = '../mcdata/wo_rseed/testdata' + str(self.nevents_sim) + '.csv'  # wo_rseed
        else:
            if self.ecut == 250:
                file = '../mcdata/wo_rseed/VRT_edep_max250/testdata' + str(self.nevents_sim) + '_' + str(
                    self.nscatter) + '.csv'  # wo_rseed_vrt
            else:
                file = '../mcdata/wo_rseed/VRT/testdata' + str(self.nevents_sim) + '_' + str(
                    self.nscatter) + '.csv'  # wo_rseed_vrt_with Edep max cut

        print(file)
        self.sim_df = pd.read_csv(file,
                                  names=['#', 'nscatters', 'w', 'de', 'x0', 'y0', 'z0', 'x1', 'y1', 'z1', 'de1', 'x2',
                                         'y2',
                                         'z2', 'de2', 'x3', 'y3', 'z3', 'de3', 'x4', 'y4', 'z4', 'de4', 'a'],
                                  error_bad_lines=False)

        self.sim_df.insert(10, 'r2_1', self.sim_df['x1'] ** 2 + self.sim_df['y1'] ** 2)
        self.sim_df.insert(15, 'r2_2', self.sim_df['x2'] ** 2 + self.sim_df['y2'] ** 2)
        self.sim_df.insert(20, 'r2_3', self.sim_df['x3'] ** 2 + self.sim_df['y3'] ** 2)
        self.sim_df.insert(25, 'r2_4', self.sim_df['x3'] ** 2 + self.sim_df['y3'] ** 2)

        return (self.sim_df)

    def cuts(self, df):
        """
        When using a non-vrt simulation cuts need to be made in order to compare it with a vrt sim

        :param df: input the pandas dataframe with the events




        :return df: returns pandas dataframe with all the events after the cuts
        :return efficiency_factor: the factor about the fraction of events left after the cut
                compared to the total before the cuts

        """

        if self.nscatter == 1:
            cuts = ((df['r2_1'] < 3249) & (abs(df['z1']) < 67) & (df['nscatters'] == 1))
        elif self.nscatter == 2:
            cuts = ((df['r2_1'] < 3249) & (abs(df['z1']) < 67) & (df['r2_2'] < 3249) & (abs(df['z2']) < 67) & (
                    df['nscatters'] == 2))
        elif self.nscatter == 3:
            cuts = ((df['r2_1'] < 3249) & (abs(df['z1']) < 67) & (df['r2_2'] < 3249) & (abs(df['z2']) < 67) & (
                    df['r2_3'] < 3249) & (abs(df['z3']) < 67) & (df['nscatters'] == 3))
        else:
            print('nscatter is out of range possible values are 1,2,3')

        dfcut = df[cuts]

        rows_bc = len(df)
        # get the number of events from the dataframe before the cuts
        rows_ac = len(dfcut)  # and number after the cuts
        # print(rows_ac)

        efficiency_factor = rows_ac / rows_bc

        return (dfcut, efficiency_factor)

    def plot(self, df_ref, df_sim):
        """
        Make energy distribution of the selected data

        :param df: input the pandas dataframe with the events
        :param scalling: Default value of 1, but if its the reference file
        use scaling to scale distribution to the desired size

        :return plotarray: numpy array of the energy distribution +(plot)
        """
        self.df_ref = self.cuts(df_ref)
        self.df_sim = self.cuts(df_sim)

        self.scalling = self.scaling(self.df_ref, self.df_sim)

        print(self.scaling)

        de_x = ['de1', 'de2', 'de3', 'de4']
        nb = 100

        self.tde_sim = list(self.df_sim[0]['de1'])
        self.tw_sim = list(self.df_sim[0]['w'])
        self.tde_ref = list(self.df_ref[0]['de1'])
        self.tw_ref = list(self.df_ref[0]['w'])

        for j in de_x[1:4]:
            self.tde_sim.extend(self.df_sim[0][j])
            self.tw_sim.extend(self.df_sim[0]['w'])
            self.tde_ref.extend(self.df_ref[0][j])
            self.tw_ref.extend(self.df_ref[0]['w'])

        self.plotarray_ref = np.array(plt.hist(self.tde_ref, weights=self.tw_ref, bins=nb, histtype='step'))
        plt.clf()  # clear plot so the unscaled histogram will not show up

        if self.scaling != 1:
            plt.clf()
            ref = self.plotarray_ref[0] * self.scalling
            plt.plot(self.plotarray_ref[1][:-1], ref, marker='o', markersize=3, linestyle='None')
            self.plotarray_ref[0] = ref

        self.plot_sim = plt.hist(self.tde_sim, weights=self.tw_sim, bins=nb, histtype='step')
        self.plotarray_sim = np.array(self.plot_sim)

        plt.xlabel('$E_{dep}$ in fiducial (keV)')
        plt.yscale('log')
        plt.title('total energy distribution')

        return

    def scaling(self, ref, sim):
        """
    Calculate the scaling factor. This can be used to compare
    the reference file with a simulation file


        :param ref:use the output of the cut function on reference data (So data frame AND efficiency factor)
        :param sim:use the output of the cut function on simulated data (So data frame AND efficiency factor)

        :return scaling:
        """

        if len(ref) == 2:
            # normal case where output of cut is used
            # this should be the case when the ref file is a non vrt
            size_ref = len(ref[0])
            factor_ref = ref[1]

        elif len(ref) > 100:
            # In the case that the reference file is a vrt file
            # and no cuts are made the factor is 1 (nothing is cut off).
            # Print is to check if it's on purpose to use a non-cut data frame.

            size_ref = len(ref)
            factor_ref = 1
            print('non cut data frame is used as reference file')

        else:
            # If something else is givens as a parameter
            # for the reference file an error is printed

            print('error: input should be cut output or data frame')

        if len(sim) == 2:
            # normal case where output of cut is used
            # this should allays be the case when the ref file is a non vrt
            size_sim = len(sim[0])
            factor_sim = sim[1]

        elif len(sim) > 100:
            # In the case that the simulated file is a vrt file
            # and no cuts are made the factor is 1 (nothing is cut off).

            size_sim = len(sim)
            factor_sim = 1

        else:
            print('error: input should be cut output or data frame')

        n_ref = size_ref / factor_ref
        n_sim = size_sim / factor_sim

        scaling = n_sim / n_ref

        return scaling

    def chi2(self, df_ref, df_sim):
        """
        :param df: input the pandas dataframe with the events
        :param scalling: Default value of 1, but if its the reference file

        :return:
        """

        analysis.plot(self, df_ref, df_sim)
        print(self.plotarray_sim[0])
        print(self.plotarray_ref[0])

        # chi2 of P.E. peak
        chi2_PE = chisquare(max(self.plotarray_sim[0]),f_exp=max(self.plotarray_ref[0]))[0]
        print(chi2_PE)

        # chi2 of Compton
        self.masked_ref = np.ma.masked_where(self.plotarray_ref[0] == 0, self.plotarray_ref[0])
        self.masked_ref = np.ma.masked_where(self.plotarray_ref[0] == max(self.plotarray_sim[0]), self.masked_ref)

        chi2_compton = chisquare(self.plotarray_sim[0], f_exp=self.masked_ref)[0] / self.masked_ref.count()

        return (chi2_compton,chi2_PE)

