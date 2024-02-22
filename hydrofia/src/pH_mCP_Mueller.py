###############################################################################
# Calculation of seawater pHT from spectrophotometric measurements with mCP   #
###############################################################################
# 
# The following code allows to calculate 
# seawater pH values on the total scale (pHT)
# from spectrophotometric measurements
# with the indicator dye m-Cresol purple (mCP).
# 
# It requires as input variables the salinity (S) of the sample,
# the temperature (T) in Kelvin at which measurements where performed,
# and the absorbance ratio (Rspec),
# which is the mCP absorbance determined at wavelength 578 nm divided
# by the absorbance at 434 nm.
# 
# The underlying characterization of the pK2e2 value of mCP is valid for:
# 5 < S < 40
# and
# 278.15 K < T < 308.15 K
# 
# When using this code, please cite:
# Mueller J. D., Rehder G., 2018,
# Metrology of pH Measurements in Brackish Waters - Part 2:
# Experimental Characterization of Purified meta-Cresol Purple
# for Spectrophotometric pHT Measurements,
# Frontiers in Marine Science 5, doi:10.3389/fmars.2018.00177
# 
###############################################################################

import numpy as np

# Definition of pK2e2 according to Eq. 9 and Table 1 in Mueller and Rehder (2018)
def pK2e2(S, T):
    return  1.08071477e+03                       - \
            1.35394946e-01  *S**0.5              - \
            1.98063716e+02  *S**1.5              + \
            6.31924397e+01  *S**2                - \
            5.18141866e+00  *S**2.5              - \
            2.66457425e+04  *T**-1               + \
            5.08796578e+03  *S**1.5 * T**-1      - \
            1.62454827e+03  *S**2 * T**-1        + \
            1.33276788e+02  *S**2.5 * T**-1      - \
            1.89671212e+02  *np.log(T)           + \
            3.49038762e+01  *S**1.5 * np.log(T)  - \
            1.11336508e+01  *S**2 * np.log(T)    + \
            9.12761930e-01  *S**2.5 * np.log(T)  + \
            3.27430677e-01  *T                   - \
            7.51448528e-04  *S**0.5 * T          + \
            3.94838229e-04  *S * T               - \
            6.00237876e-02  *S**1.5 * T          + \
            1.90997693e-02  *S**2 * T            - \
            1.56396488e-03  *S**2.5 * T

# Definition of absorptivity ratios e1 and e2/e3
# as originally published by Liu et al. (2011)
# and applied by Mueller and Rehder (2018).
def e1(T):
    return -0.007762 + 4.5174e-5*T
def e3e2(S, T):
    return -0.020813 + 2.60262e-4*T + 1.0436e-4*(S-35)

# final calculation of pHT as a funciton of S, T, and Rspec
def pHTspec(S, T, Rspec):
    return pK2e2(S, T) + np.log10((Rspec-e1(T)) / (1-(Rspec*e3e2(S, T))))


if __name__=='__main__':

    S = 20
    T = 298.15

    # Testing the pK2e2 function with S = 20 and T = 298.15 should
    # give the control value 7.6920.
    print pK2e2(S, T)


    # Testing the pHTspec function with S = 20, T = 298.15, and Rspec = 1
    # should give the control value 7.7142
    print pHTspec(35.23, 298.01, 1.650761)