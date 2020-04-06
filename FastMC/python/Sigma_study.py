import numpy as np
from scipy.optimize import curve_fit

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import pyplot as pp
from scipy.stats import chisquare
import os
import re
import fnmatch
import pandas as pd
from math import isnan


# This python code is made to have a single place for all the
# essential functions needed for the accelerated MC analysis.

class energy:
    def __init__(self, **kwargs):
        """"
        Initialize an energy for the analysis.
        :param kwargs:
            energy = energy of the gamma-ray in keV
            edep_max = maximum energy deposit in the xenon (keV)
            T = type of simulation normal simulation: 'sim' reference simulation: 'ref'
        """
        #
        self.energy = kwargs.pop('energy', 1000)
        self.edep_max = kwargs.pop('edep_max', 2700)
        self.T = kwargs.pop('Type', 'sim')

        return

    def select_file(self, nevents, family_number, vrt='fiducial_scatter', size_fiducial='Normal '):
        """
        Read the excel file and find the relevant file
        :param:
            nevents = size of the simulation
            family_number = which file of the 10 identical files
        :return:
            the filename of the relevant file (string)
        """
        df = pd.read_excel('~/FastMC/runit/jobs_master.xlsx')
        df = df.loc[df['energy'] == self.energy]
        if len(df) == 0:
            raise (Exception('No such energy'))

        df = df.loc[df['vrt'] == vrt]
        if len(df) == 0:
            raise (Exception('No such file'))

        if vrt == 'fiducial_scatter':
            df = df.loc[df['edep_max'] == self.edep_max]
            df = df.loc[df['size_fiducial'] == size_fiducial]
        if len(df) == 0:
            raise (Exception('No such edep_max'))

        df = df.loc[df['nevents'] == nevents]
        if len(df) == 0:
            raise (Exception('No such nevents'))
        df = df.loc[df['type'] == self.T]
        if len(df) == 0:
            raise (Exception('No such ref/sim file'))
        df = df.loc[df['family_number'] == family_number]
        if len(df) == 0:
            raise (Exception('No such family number'))

        # print(df['output'].values[0])

        return df['output'].values[0]

    def find_fam_size(self, nevents, vrt='fiducial_scatter', size_fiducial='Normal '):
        """
        Some families are larger (or smaller) than 10 so this checks the size
        :param:
            nevents = size of the simulation
        :return:
            family size (int)
        """
        df = pd.read_excel('~/FastMC/runit/jobs_master.xlsx')
        df = df.loc[df['energy'] == self.energy]
        df = df.loc[df['vrt'] == vrt]
        df = df.loc[df['type'] == self.T]

        if vrt == 'fiducial_scatter':
            df = df.loc[df['edep_max'] == self.edep_max]
            df = df.loc[df['size_fiducial'] == size_fiducial]

        df = df.loc[df['nevents'] == nevents]

        return len(df)

    def find_ns(self):
        """
        Find which sizes have been simulated
        :param:
        :return:
            size of all simulations (NumPy array)
        """
        df = pd.read_excel('~/FastMC/runit/jobs_master.xlsx')
        df = df.loc[df['energy'] == self.energy]
        df = df.loc[df['edep_max'] == self.edep_max]
        return df['nevents'].unique()

    def total_weight(self, nevents, vrt='fiducial_scatter', size_fiducial='Normal ', famsize=10):
        """
        Calculates the total weights from all families members.
        :param:
            nevents = size of the simulation
            vrt = accelerated MC('fiducial_scatter') or standard MC (None)
        :return:
            returns total weights and total weight scaled with size of the simulation (2 lists)
        """
        # clear lists
        tweight = []
        tweight_scale = []

        for i in range(1, famsize + 1):  # loop for all files in a family
            # find file
            file = self.select_file(nevents=nevents, family_number=i, vrt=vrt, size_fiducial=size_fiducial)
            print(i)
            # read file into pandas data-frame with standard headings
            df = pd.read_csv(file + '.csv',
                             names=['#', 'nscatters', 'w', 'de', 'x0', 'y0', 'z0', 'x1', 'y1', 'z1', 'de1', 't1', 'x2',
                                    'y2', 'z2', 'de2', 't2', 'x3', 'y3', 'z3', 'de3', 't3', 'x4', 'y4', 'z4', 'de4',
                                    't4'], error_bad_lines=False)
            # insert r^2 component
            df.insert(10, 'r2_1', df['x1'] ** 2 + df['y1'] ** 2)

            # Loop to make appropriate cuts for different fiducial volumes.
            # They are not used in the current analysis.
            if size_fiducial == 'Neutrinoless':
                scatter_cut = ((df['nscatters'] == 1) & (df['r2_1'] < 1600) & (np.abs(df['z1']) < 50))

            # Apply cuts also for VRT to get the events out that do not point to the fiducial
            elif self.edep_max == 250:
                scatter_cut = (
                        (df['nscatters'] == 1) & (df['r2_1'] < 3249) & (np.abs(df['z1']) < 67) & (df['de'] < 250))

            else:
                scatter_cut = (
                        (df['nscatters'] == 1) & (df['r2_1'] < 3249) & (np.abs(df['z1']) < 67) & (df['de'] < 2700))

            df_cut = df[scatter_cut]

            # sum all the weights and add them to the list
            tweight.append(sum(df_cut['w']))
            tweight_scale.append(sum(df_cut['w']) / nevents)
        # print(np.sqrt(np.var(tweight_scale)))
        return [tweight, tweight_scale]

    def load_ref(self):
        """
        Load ref. not used in the current analysis is a bug somewhere.
        :param:
        :return:
        p_gamma of reference MC
        """
        # load ref
        if self.edep_max == 250:
            df_ref = pd.read_csv('/data/xenon/olivier/mc_ref/' + str(self.energy) + 'edep_cut_ref.csv')

        else:
            df_ref = pd.read_csv('/data/xenon/olivier/mc_ref/' + str(self.energy) + 'edep_ref.csv')

        tw_ref = sum(df_ref['edep_y'][1:])
        n_mc = df_ref['nevents'][0]
        eff_fac = tw_ref / n_mc
        return eff_fac

    def get_sigma(self, nevents):
        """
        Get total weights of a family and calculate the sigma
        :param:
            nevents = size of the simulation
        :return:
            lists, 1 sigma of the VRT 2 sigma of the NON-vrt
        """
        fam_size_vrt = self.find_fam_size(nevents=nevents, vrt='fiducial_scatter', size_fiducial='Normal ')
        fam_size_nonvrt = self.find_fam_size(nevents=nevents, vrt='None', size_fiducial='Normal ')

        vrt = []
        nonvrt = []

        tw_vrt = self.total_weight(nevents=nevents, famsize=fam_size_vrt)
        tw_nonvrt = self.total_weight(nevents=nevents, vrt='None', famsize=fam_size_nonvrt)

        # Sigma
        s_vrt = np.sqrt(np.var(tw_vrt[0])) / np.mean(tw_vrt[0])
        s_nonvrt = np.sqrt(np.var(tw_nonvrt[0])) / np.mean(tw_nonvrt[0])

        return [s_vrt, s_nonvrt]

    def get_sigmas(self):
        """
        Get sigmas of all the families of simulations
        :param:
        :return:
            2 lists, 1 sigmas of the VRT 2 sigmas of the NON-vrt
        """
        sigma_vrt = []
        sigma_nonvrt = []
        ns = self.find_ns()

        for i in ns:
            print(i)
            sigma_temp = self.get_sigma(nevents=i)
            sigma_vrt.append(sigma_temp[0])
            sigma_nonvrt.append(sigma_temp[1])

        return [sigma_vrt, sigma_nonvrt]

    def sigma_alternative(self, nevents):
        """
        An alternative manner of calculating the sigma.
        Instead of the difference w.r.t. The mean (normal way)
        take the difference w.r.t. the reference value. (Didn't do much not used)
        :param:
            nevents = size of the simulation
        :return:
            lists, 1 sigma of the VRT 2 sigma of the NON-vrt
        """

        # # load total weights
        # fam_size_vrt = self.find_fam_size(nevents=nevents, vrt='fiducial_scatter', size_fiducial='Normal ')
        # fam_size_nonvrt = self.find_fam_size(nevents=nevents, vrt='None', size_fiducial='Normal ')
        #
        # tw_vrt = self.total_weight(nevents=nevents, famsize=fam_size_vrt)
        # tw_nonvrt = self.total_weight(nevents=nevents, vrt='None', famsize=fam_size_nonvrt)
        #
        # # load referance value
        # mu = np.zeros(fam_size_vrt) + self.load_ref()
        #
        # var_vrt = sum((tw_vrt[1] - mu) ** 2) / fam_size_vrt
        # var_nonvrt = sum((tw_nonvrt[1] - mu) ** 2) / fam_size_nonvrt
        #
        # s_vrt = np.sqrt(var_vrt)
        # s_nonvrt = np.sqrt(var_nonvrt)
        #
        # return [s_vrt, s_nonvrt]

    def get_sigmas_alternative(self):
        """
        Get sigmas of all the families of simulations alternative
        :param:
        :return:
            2 lists, 1 sigmas of the VRT 2 sigmas of the NON-vrt

        """
        sigma_vrt = []
        sigma_nonvrt = []

        ns = self.find_ns()

        for i in ns:
            print(i)
            sigma_vrt.append(self.sigma_alternative(nevents=i)[0])
            sigma_nonvrt.append(self.sigma_alternative(nevents=i)[1])

        return [sigma_vrt, sigma_nonvrt]

    def do_fit(self, sigmas=None):
        """
        Make a fit trough the sigmas.
        because the two fit functions have a shared constant term c it needs to be a combined fit
        If sigma is calculated elsewhere, it can be given as an argument
        :param:
            sigmas = output of get_sigmas function or None than it is calculated here
        :return:
            list of [a,b,c]
            a= fit parameter of vrt
            b= fit parameter of non-vrt
            c= constant of both fits
        """
        ns = self.find_ns()

        # if sigma is not given, calculate it here
        if sigmas is None:
            sigmas = self.get_sigmas()  # Calculate the sigmas of the different simulations

        # find first non nan value in non-vrt sigmas
        non_vrt_start = sigmas[1].index(next(filter(lambda x: not isnan(x), sigmas[1])))
        # non_vrt_start=3

        # Get the x,y and error and couple them to make a combined fit
        y1 = np.array(sigmas[0])
        y2 = np.array(sigmas[1][non_vrt_start:])
        # only take the non-zero sigmas (leave the small non-vrt out of the fit)
        comboY = np.append(y1, y2)

        x1 = ns
        x2 = ns[non_vrt_start:]
        comboX = np.append(x1, x2)

        # Calculate the error on the weight to use in the fit
        s1 = np.square(sigmas[0]) * 2
        s2 = np.square(sigmas[1][non_vrt_start:]) * 2
        comboS = np.append(s1, s2)

        if len(y1) != len(x1):
            raise (Exception('Unequal x1 and y1 data length'))
        if len(y2) != len(x2):
            raise (Exception('Unequal x2 and y2 data length'))

        # the fit functions
        def function1(data, a, b, c):  # not all parameters are used here, c is shared
            return (a / np.sqrt(data)) + c

        def function2(data, a, b, c):  # not all parameters are used here, c is shared
            return (b / np.sqrt(data)) + c

        def combinedFunction(comboData, a, b, c):
            # single data reference passed in, extract separate data
            extract1 = comboData[:len(x1)]  # first data
            extract2 = comboData[len(x1):]  # second data

            result1 = function1(extract1, a, b, c)
            result2 = function2(extract2, a, b, c)

            return np.append(result1, result2)

        # some initial parameter values, most important c can't be smaller than 0
        param_bounds = ([-np.inf, -np.inf, 0], [np.inf, np.inf, np.inf])

        initialParameters = np.array([7, 100, 1.0])

        # curve fit the combined data to the combined function
        fittedParameters, pcov = curve_fit(combinedFunction, comboX, comboY, initialParameters, sigma=comboS,
                                           bounds=param_bounds)
        # values for display of fitted function
        a, b, c = fittedParameters

        return [a, b, c]

    def acc_fac(self, sigmas=None):
        """
        Do fit and calculate the acceleration factor.
        If sigma is calculated elsewhere, it can be given as an argument
        :param:
            sigmas = output of get_sigmas function or None than it is calculated here
        :return:
        """

        if sigmas is None:
            sigmas = self.get_sigmas()  # Calculate the sigmas of the different simulations

        [a, b, c] = self.do_fit(sigmas)
        ns = self.find_ns()

        # calculate acceleration factor
        acc_fac = (b / a) ** 2

        # # calculate erros on sigma
        # # morgen kijken hoe dit ook al weer moest
        # yerr_vrt = np.square(sigmas[0]) * 2
        # yerr_nonvrt = np.square(sigmas[1]) * 2
        # xerr = np.sqrt(ns)
        #
        # # fit power law trought the points
        # popt0, pcov0 = self.fit(sigmas[0], ns)  # vrt
        # popt1, pcov1 = self.fit(sigmas[1], ns)  # non_vrt
        #
        # # set range of the fit-line
        # xfit_vrt = range(ns[0], ns[-1])
        # xfit_nonvrt = range(ns[1], ns[-1])
        #
        #
        #
        # # pcov1 = x
        # # pcov0 = y
        #
        # err_vrt = np.sqrt(np.diag(pcov0))  # 0=y
        # err_nonvrt = np.sqrt(np.diag(pcov1))  # 1=x
        #
        # err_acc = np.sqrt(
        #     (4 * pcov1 ** 2) / (pcov0 ** 4) * err_nonvrt ** 2 + (4 * pcov1 ** 4) / (pcov0 ** 6) * err_vrt ** 2)
        #
        #
        # zie formule in shrift voor hoe dit werkt!!
        # of zie dit https://www.wolframalpha.com/widgets/view.jsp?id=8ac60957610e1ee4894b2cd58e753

        return acc_fac  # , err_acc
