#!/usr/bin/python2
# -*- coding: UTF-8 -*-

#  Copyright 2013 Steffen Aßmann <steffen.a@live.de>
#  Version 0.1
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

import sys
import numpy as np
from numpy import log, log10, exp, sqrt

def total2free(S,T):
    return 1/(1 + ST(S)/KS(S,T))

#   Conversion of the pH scales
#   Written by Steffen Aßmann after seacarb (last modified Feb. 2013)
def pHconvert(S,T,pH,flag):
    ks = KS(S,T)
    kf = KF(S,T)
    st = ST(S)
    ft = FT(S)
    fh = fH(S,T)

    ## seawater to total
    if flag == 1:
        return pH + log10(1 + st/ks + ft/kf) - log10(1 + st/ks)
    ## free to total
    elif flag == 2:
        return pH - log10(1 + st/ks)
    ## total to seawater
    elif flag == 3:
        return pH - log10(1 + st/ks + ft/kf) + log10(1 + st/ks)
    ## total to free
    elif flag == 4:
        return pH + log10(1 + st/ks)
    ## seawater to free
    elif flag == 5:
        return pH + log10(1 + st/ks + ft/kf)
    ## free to sewater
    elif flag == 6:
        return pH - log10(1 + st/ks + ft/kf)
    ## NBS to sewater
    elif flag == 7:
        return -log10(10**-pH / fh)
    ## seawater to NBS
    elif flag == 8:
        return -log10(10**-pH * fh)
    ## NBS to total
    elif flag == 9:
        return -log10(10**-pH / fh) + log10(1 + st/ks + ft/kf) - log10(1 + st/ks)

## activity coefficients for conversion of sws/nbs scale
def fH(S=35,T=25):
    z0 = 0.71498
    a = 4.71783E-4
    b = 4.14022E-4
    c = -4.4482E-5
    d = 6.43017E-5
    f = -1.18468E-4
    return (z0 + a*T + b*S + c*T**2 + d*S**2 + f*T*S)

#   Subroutine to calculate appropriate total concentrations,
#   for sea water of salinity, S.
#
#   Written by Andrew G. Dickson (last modified August 1994)
#
#   Called with:
#       S    -  salinity of sample
#
#   Returns:
#       BT      -  total boron     (mol/kg-soln)
#       ST      -  total sulfate   (mol/kg-soln)
#       FT      -  total fluoride  (mol/kg-soln)

##   Uppstrom (1974) Deep-Sea Res. 21, 161.
def BT(S=35):
    return (0.000232/10.811) * (S/1.80655)

##   Morris & Riley (1966) Deep-Sea Res. 13, 699
def ST(S=35):
    return (0.1400/96.062) * (S/1.80655)

##   Riley (1965) Deep-Sea Res. 12, 219.
def FT(S=35):
    return (0.000067/18.998) * (S/1.80655)

#   Subroutine to calculate values of dissociation constants,
#   appropriate to sea water of salinity, S, and temperature, T.
#
#   Written by Andrew G. Dickson (last modified August 1997)
#
#   Called with:
#       S    -  salinity of sample
#       T    -  titration temperature (deg C)
#
#   Returns:
#       K1      -  [H][HCO3]/[H2CO3]
#       K2      -  [H][CO3]/[HCO3]
#       KB      -  [H][BO2]/[HBO2]
#       K1P     -  [H][H2PO4]/[H3PO4]
#       K2P     -  [H][HPO4]/[H2PO4]
#       K3P     -  [H][PO4]/[HPO4]
#       KSI     -  [H][SiO(OH)3]/[Si(OH)4]
#       KS      -  [h][SO4]/[HSO4]
#       KF      -  [H][F]/[HF]
#       KW      -  [H][OH]
#

## Gleichgewichtskonstanten
## K1, K2, KB aus seacarb ergeben gleiche Werte, wie Buch (Zeebe & Wolf-Gladrow 2001)

## Lueker et al., 2000
def K1(S=35,T=25):
    TK = T + 273.15
    lgK = -3633.86/TK + 61.2172 - 9.6777*log(TK) + 0.011555*S - 0.0001152*S**2
    return 10**lgK

def K2(S=35,T=25):
    TK = T + 273.15
    lgK = -471.78/TK - 25.9290 + 3.16967*log(TK) + 0.01781*S - 0.0001122*S**2
    return 10**lgK

## Millero (1994)
def KW(S=35,T=25):
    TK = T + 273.15
    lnK = -13847/TK + 148.9652 - 23.6521*log(TK) + (118.67/TK - 5.977 + 1.0495*log(TK))*S**0.5 - 0.01615*S
    return exp(lnK)

#def KB(S=35,T=25):
#TK = T + 273.15
#lnK =   (-8966.90 - 2890.53*S**0.5 - 77.942*S + 1.728*S**(3/2) - 0.0996*S**2)/TK + (148.0248 + 137.1942*S**0.5 + 1.62142*S) \
#+(-24.4344 - 25.085*S**0.5 - 0.2474*S)*log(TK) + 0.053105*S**0.5*TK
#return exp(lnK)

def KH(S=35,T=25):
    TK = T + 273.15
    lnK = 93.4517*100/TK - 60.2409 + 23.3585*log(TK/100) + S*(0.023517 - 0.023656*TK/100 + 0.0047036*(TK/100)**2)
    return exp(lnK)

##   Roy et al. (1993) Mar. Chem. 44, 249
#def K1(S=35,T=25):
#TK = 273.15 + T
#IS = 19.924*S/(1000 - 1.005*S)
#K1  = exp (
#+               -2307.1266/TK + 2.83655 - 1.5529413*log(TK) +
#+               (-4.0484/TK - 0.20760841)*sqrt(S) + 0.08468345*S -
#+               0.00654208*S**1.5 + log(1 - 0.001005*S)
#)
#return K1

#def K2(S=35,T=25):
#TK = 273.15 + T
#IS = 19.924*S/(1000 - 1.005*S)
#K2  = exp (
#+               -3351.6106/TK - 9.226508 - 0.2005743*log(TK) +
#+               (-23.9722/TK - 0.106901773)*sqrt(S) + 0.1130822*S -
#+               0.00846934*S**1.5 + log(1 - 0.001005*S)
#)
#return K2

#   Dickson (1990) Deep-Sea Res. 37, 755
def KB(S=35,T=25):
    TK = T + 273.15
    tmp1 = -8966.90-2890.53*sqrt(S)-77.942*S+1.728*S**(3./2.)-0.0996*S*S
    tmp2 = +148.0248+137.1942*sqrt(S)+1.62142*S
    tmp3 = +(-24.4344-25.085*sqrt(S)-0.2474*S)*log(TK)
    lnKb = tmp1 / TK + tmp2 + tmp3 + 0.053105*sqrt(S)*TK
    return exp(lnKb)

##   Millero (1994)  --  composite data (Geochim. Cosmochim Acta - in press)
def K1P(S=35,T=25):
    TK = T + 273.15
    IS = 19.924*S/(1000 - 1.005*S)
    K1P = exp (
        +               -4576.752/TK + 115.525 - 18.453*log(TK) +
        +               (-106.736/TK + 0.69171)*sqrt(S) + (-0.65643/TK - 0.01844)*S
    )
    return K1P

def K2P(S=35,T=25):
    TK = T + 273.15
    IS = 19.924*S/(1000 - 1.005*S)
    K2P = exp (
        +               -8814.715/TK + 172.0883 - 27.927*log(TK) +
        +               (-160.340/TK + 1.3566)*sqrt(S) + (0.37335/TK - 0.05778)*S
    )
    return K2P

def K3P(S=35,T=25):
    TK = T + 273.15
    IS = 19.924*S/(1000 - 1.005*S)
    K3P = exp (
        +               -3070.75/TK - 18.141  +
        +               (17.27039/TK + 2.81197)*sqrt(S) + (-44.99486/TK - 0.09984)*S
    )
    return K3P

##   Millero (1994)  --  composite data (Geochim. Cosmochim Acta - in press)
def KSi(S=35,T=25):
    TK = T + 273.15
    IS = 19.924*S/(1000 - 1.005*S)
    KSi = exp (
        +               -8904.2/TK + 117.385 - 19.334*log(TK) +
        +               (-458.79/TK + 3.5913)*sqrt(IS) +
        +               (188.74/TK - 1.5998)*IS + (-12.1652/TK + 0.07871)*(IS)**2 +
        +               log(1 - 0.001005*S)
    )
    return KSi

###   Millero (1994)  -- composite data (Geochim. Cosmochim Acta - in press)
#def KW(S=35,T=25):
#TK = 273.15 + T
#IS = 19.924*S/(1000 - 1.005*S)
#KW  = exp (
#+               -13847.26/TK + 148.9652 - 23.6521*log(TK) +
#+               (118.67/TK - 5.977 + 1.0495*log(TK))*sqrt(S) - 0.01615*S
#)
#return KW

##   Dickson (1990) -- free hydrogen ion flag (J. Chem. Thermodynamics 22, 113)
def KS(S=35,T=25):
    TK = T + 273.15
    IS = 19.924*S/(1000 - 1.005*S)
    KS  = exp (
        +               -4276.1/TK + 141.328 - 23.093*log(TK) +
        +               (-13856/TK + 324.57 - 47.986*log(TK)) * sqrt(IS) +
        +               (35474/TK - 771.54 + 114.723*log(TK)) * IS -
        +               2698*IS**1.5/TK + 1776*IS**2/TK + log(1 - 0.001005*S)
    )
    return KS

def KF(S=35,T=25,flag="T"):
    TK = T + 273.15
    IS = 19.924*S/(1000 - 1.005*S)

    ##   Dickson & Riley (1979) -- change pH flag to total (Mar. Chem. 7, 89)
    #if flag == "F":
    #KF  = 1590.2/TK - 12.641 + 1.525 * sqrt(IS) + log(1 - 0.001005*S)
    #KF  = KF + log(1 + (0.1400/96.062)*(S/1.80655)/KS(S,T))
    #KF  = exp(KF)
    #elif flag == "T":
    #KF  = 1590.2/TK - 12.641 + 1.525 * sqrt(IS) + log(1 - 0.001005*S)
    #KF  = KF + log(1 + (0.1400/96.062)*(S/1.80655)/KS(S,T))
    #KF  = exp(KF)
    #KF = free2total(S,T) * KF                      # conversion from free to total flag

    ##   Perez and Fraga (1987) -- total flag (Mar Chem. 21, 161-168)
    if flag == "F":                                        #free flag
        KF = exp(874/TK - 9.68 + 0.111*S**0.5)
        KF = KF * total2free(S,T)
    elif flag == "T":                                      #total flag
        KF = exp(874/TK - 9.68 + 0.111*S**0.5)
    return KF

##   Breland, J. A.; Byrne, R. H. Deep Sea Res., Part I 1993, 40 (3), 629−641.
##   Dissociation constant of Bromocresol green on the free scale. (20<S<35)
def KBCG25(S=35):
    pKI = 4.4166 + 0.0005946*(35-S)
    KI = 10**(-pKI)
    return KI

##  Equilibrium constant of mCP after Mosley et al., 2004
def KmCP25(S=35):
    pKI = (8.6353 - 0.3238*S**(0.5) + 0.0807*S - 0.01157*S**(1.5) + 0.000694*S**2)
    KI = 10**(-pKI)
    return KI

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


# final calculation of pHT as a funciton of S[psu], T[Kelvin], and Rspec
# "mueller": After Mueller and Rehder (2018)
# "mosley" : After Mosley et al. (2004) at 25 °C only!
def pHTspec(S, T, Rspec, x):
    if x == "mueller":
        # Definition of absorptivity ratios e1 and e2/e3
        # as originally published by Liu et al. (2011)
        # and applied by Mueller and Rehder (2018).
        e1Mueller = -0.007762 + 4.5174e-5*T
        e3e2Mueller = -0.020813 + 2.60262e-4*T + 1.0436e-4*(S-35)
        return pK2e2(S, T) + np.log10((Rspec-e1Mueller) / (1-(Rspec*e3e2Mueller)))
    elif x == "mosley":
        e1Mosley = 0.00691
        e2Mosley = 2.2220
        e3Mosley = 0.1331
        return -np.log10(KmCP25(S)) + np.log10((Rspec - e1Mosley) / (e2Mosley - Rspec * e3Mosley))
    else:
        return np.nan


#   Function to calculate the density of sea water.
#   Based on Millero & Poisson (1981) Deep-Sea Res. 28, 625.
#
#   Written by Andrew G. Dickson (last modified February 1994)
#
#   Called with:
#       S    -  salinity of sample
#       T    -  titration temperature (Centigrade)

def densSW(S=35,T=25):
    #   Density of SMOW (kg/m3)
    DH2O = (999.842594 + 6.793952e-2 * T - 9.095290e-3 * T**2 +
            +    1.001685e-4 * T**3 - 1.120083e-6 * T**4 + 6.536332e-9 * T**5)

    #   Density of sea water
    A = (8.24493e-1 - 4.0899e-3 * T + 7.6438e-5 * T**2 -
         +    8.2467e-7 * T**3 + 5.3875e-9 * T**4)
    B = -5.72466e-3 + 1.0227e-4 * T - 1.6546e-6 * T**2
    C = 4.8314e-4

    return (DH2O + A*S + B*S**1.5 + C*S**2)/1000

#   Function to calculate the density of a sodium cloride solution.
#   Based on equation by Lo Surdo et al.
#      J. Chem. Thermodynamics 14, 649 (1982).
#
#   Written by Andrew G. Dickson (last modified March 1994)
#
#   Called with:
#       CNaCl  -  concentration of sodium chloride (mol/kg-soln)
#       T      -  titration temperature (Centigrade)

def densNaCl(CNaCl, T=25):
    #   Calculate the molality of NaCl
    mNaCl = CNaCl/(1 - 0.058443*CNaCl)

    #   Density of SMOW (kg/m3)
    DH2O = (999.842594 + 6.793952e-2 * T - 9.095290e-3 * T**2 +
            +    1.001685e-4 * T**3 - 1.120083e-6 * T**4 - 6.536332e-9 * T**5)

    #   Density of NaCl (kg/m3)
    DNaCl = (DH2O + mNaCl*(46.5655 - 0.2341*T + 3.4128e-3 * T**2
                           +                       - 2.7030e-5 * T**3 + 1.4037e-7 * T**4) +
             +       mNaCl**1.5 * (-1.8527 + 5.3956e-2 * T - 6.2635e-4 * T**2) +
             +       mNaCl**2 * (-1.6368 - 9.5653e-4 * T + 5.2829e-5 * T**2) +
             +       0.2274 * mNaCl**2.5)

    return 1e-3 * DNaCl

#   Function to calculate the density of a solution of with
#   sodium cloride and hydrochloric acid at 25 °C.
#
#   Written by Steffen Aßmann (last modified Okt. 2011)
#
#   Called with:
#       CNaCl  -  concentration of sodium chloride (mol/kg-soln)
#       CHCl   -  concentration of hydrochloric acid (mol/kg-soln)

def densHClNaCl(CNaCl=0.6, CHCl=0.1):
    mNaCl = 1000*CNaCl / (1000-58.44247*CNaCl)
    mHCl  = 1000*CHCl / (1000-58.44247*CNaCl-36.46*CHCl)
    mT    = (36.46*mHCl + 58.44247*mNaCl) / (mHCl+mNaCl)
    fHCl  = 17.854+(1.46*mHCl**0.5)-0.307*mHCl
    fNaCl = 16.613+(1.811*mNaCl**0.5)+0.094*mNaCl
    mix   = (mHCl*fHCl+mNaCl*fNaCl)/(mNaCl+mHCl)

    return 0.99704*(1000+mT*(mHCl+mNaCl))/(1000+mix*(mHCl+mNaCl)*0.99704)

#   Density of 0.1 mol/kg-soln HCl in 0.6 mol/kg-soln NaCl from Dicksons lab
def densHClCRM(T=25):
    return -0.00000401*T**2 - 0.00011179*T + 1.02896024

#   Density of gas free H2O
def densH2O(T=25):
    a0 = 999.83952
    a1 = 16.952577
    a2 = -7.9905127e-3
    a3 = -4.6241757e-5
    a4 = 1.0584601e-7
    a5 = -2.8103006e-10
    b  = 0.0168872

    return (a0 + a1*T + a2*T**2 + a3*T**3 + a4*T**4 + a5*T**5) / (1 + b*T) / 1000

#   Density of HCl in pure water (working range -5 to 40 °C and 0.2 to ? mol/kg)
def densHCl(T=25,CHCl=0.1):
    z0 = 1.00692
    A1 = -4.51909E-4
    A2 = -1.2672E-6
    A3 = 3.68644E-8
    A4 = -5.16047E-10
    A5 = 2.10802E-12
    B1 = 0.0181
    B2 = 1.51822E-4
    B3 = -4.60734E-5
    B4 = 6.14603E-6
    B5 = -2.67022E-7

    return (z0+ A1*T + A2*T**2 + A3*T**3 + A4*T**4 + A5*T**5 + B1*CHCl + B2*CHCl**2 + B3*CHCl**3 + B4*CHCl**4 + B5*CHCl**5)

###########################################################
###     Calculation of the missing parameters           ###
###########################################################

# flag = 1      pH and CO2 given
# flag = 2      CO2 and HCO3 given
# flag = 3      CO2 and CO3 given
# flag = 4      pCO2 and ALK given
# flag = 5      pCO2 and DIC given
# flag = 6      pH and HCO3 given
# flag = 7      pH and CO3 given
# flag = 8      pH and ALK given
# flag = 9      pH and DIC given
# flag = 10     HCO3 and CO3 given
# flag = 11     HCO3 and ALK given
# flag = 12     HCO3 and DIC given
# flag = 13     CO3 and ALK given
# flag = 14     CO3 and DIC given
# flag = 15     ALK and DIC given
# flag = 16     pH and pco2 given

def carb(S, T, var1, var2, flag):
    kw = KW(S,T)
    kb = KB(S,T)
    k1 = K1(S,T)
    k2 = K2(S,T)
    kh = KH(S,T)
    bt = BT(S)
    st = ST(S)
    ft = FT(S)

    index = max([np.shape(S), np.shape(T), np.shape(var1), np.shape(var2)])
    if index == (): index = 1
    else: index = index[0]

    pH, co2, pco2, hco3, co3, dic, alk = None, None, None, None, None, None, None

    #var1 = pH and var2 = pCO2 are given
    if flag == 1:
        pH   = var1
        h    = 10**-pH
        pco2 = var2
        co2  = kh*pco2
        dic  = co2*(1.+k1/h+k1*k2/h/h)
        hco3 = dic/(1.+h/k1+k2/h)
        co3  = dic/(1.+h/k2+h*h/k1/k2)
        alk  = co2*(k1/h+2.*k1*k2/h/h)+kb*bt/(kb+h)+kw/h-h


    #var1 = pCO2 and var2 = ALK are given
    elif flag == 4:
        pco2 = var1
        co2  = pco2*kh
        alk  = var2
        p3   = kb+alk
        p2   = alk*kb-co2*k1-kb*bt-kw
        p1   = -co2*kb*k1-co2*2.*k1*k2-kw*kb
        p0   = -2.*co2*kb*k1*k2
        if index == 1:
            p4 = 1.
            p   = [p4, p3, p2, p1, p0]
            h   = max(np.real(np.roots(p)))
        else:
            p4  = np.ones(index)
            p   = np.transpose([p4, p3, p2, p1, p0])
            h   = np.empty(index)
            for i in range(index):
                h[i] = max(np.real(np.roots(p[i])))
        pH   = -log10(h)
        dic  = co2*(1.+k1/h+k1*k2/h/h)
        hco3 = dic/(1+h/k1+k2/h)
        co3  = dic/(1+h/k2+h*h/k1/k2)

    #var1 = pCO2 and var2 = DIC are given
    elif flag == 5:
        pco2 = var1
        dic  = var2
        co2  = pco2*kh
        p2   = dic - co2
        p1   = -co2*k1
        p0   = -co2*k1*k2
        p    = [p2, p1, p0]
        h    = max(np.real(np.roots(p)))
        hco3 = dic/(1+h/k1+k2/h)
        co3  = dic/(1+h/k2+h*h/k1/k2)
        alk  = co2*(k1/h+2.*k1*k2/h/h)+kb*bt/(kb+h)+kw/h-h
        pH   = -log10(h)

    #var1 = pH and var2 = ALK are given
    elif flag == 8:
        alk  = var2
        pH   = var1
        h    = 10**-pH
        co2  = (alk-kw/h+h-kb*bt/(kb+h)) / (k1/h+2.*k1*k2/h/h)
        dic  = co2*(1.+k1/h+k1*k2/h/h)
        hco3 = dic/(1+h/k1+k2/h)
        co3  = dic/(1+h/k2+h*h/k1/k2)
        pco2 = co2/kh

    #var1 = pH and var2 = DIC are given
    elif flag == 9:
        pH = var1
        h = 10**-pH
        dic = var2
        co2 = dic / (1.+k1/h+k1*k2/h/h)
        hco3 = dic/(1+h/k1+k2/h)
        co3 = dic/(1+h/k2+h*h/k1/k2)
        alk = co2*(k1/h+2.*k1*k2/h/h)+kb*bt/(kb+h)+kw/h-h
        pco2 = co2/kh

    #var1 = ALK and var2 = DIC are given
    elif flag == 15:
        alk = var1
        dic = var2

        p4  = -alk-kb-k1
        p3  = dic*k1-alk*(kb+k1)+kb*bt+kw-kb*k1-k1*k2
        tmp = dic*(kb*k1+2.*k1*k2)-alk*(kb*k1+k1*k2)+kb*bt*k1
        p2  = tmp+(kw*kb+kw*k1-kb*k1*k2)
        tmp = 2.*dic*kb*k1*k2-alk*kb*k1*k2+kb*bt*k1*k2
        p1  = tmp+(+kw*kb*k1+kw*k1*k2)
        p0  = kw*kb*k1*k2
        if index == 1:
            p5  = -1.
            p   = [p5, p4, p3, p2, p1, p0]
            h   = max(np.real(np.roots(p)))
        else:
            p5  = -np.ones(index)
            p   = np.transpose([p5, p4, p3, p2, p1, p0])
            h   = np.empty(index)
            for i in range(index):
                h[i] = max(np.real(np.roots(p[i])))
        co2  = dic / (1.+k1/h+k1*k2/h/h)
        hco3 = dic/(1+h/k1+k2/h)
        co3  = dic/(1+h/k2+h*h/k1/k2)
        pco2 = co2/kh
        pH   = -log10(h)

    return {"T":    T,
            "S":    S,
            "pH":   pH,
            "CO2":  co2,
            "pCO2": pco2,
            "HCO3": hco3,
            "CO3":  co3,
            "DIC":  dic,
            "ALK":  alk,
            "units": u"mol/kg, atm, °C, psu"}

def test_set():
    TC    = 25.
    S     = 35.
    P     =  0.
    bor   = (416.*(S/35.))* 1.e-6   # (mol/kg), DOE94
    ph1   = 8.0902                  # pH (8.0902 Total, 8.1979 Free)
    h1    = 10**(-ph1)              # [H+]
    co21  = 10.1304e-6              # [CO2]
    hco31 = 1735.9e-06              # [HCO3-]
    co31  = 253.9924e-6             # [CO3--]
    dic1  = 2000.e-6                # [DIC]
    alk1  = 2350.e-6                # Alk
    pco21 = 356.8058e-6             # pCO2

    print("\nTC  ", TC   , \
          "\nS   ", S    , \
          "\nP   ", P    , \
          "\nbor ", bor  , \
          "\nph  ", ph1  , \
          "\nh   ", h1   , \
          "\nco2 ", co21 , \
          "\nhco3", hco31, \
          "\nco3 ", co31 , \
          "\ndic ", dic1 , \
          "\nalk ", alk1 , \
          "\npco2", pco21)

if __name__ == '__main__':
    ###########################################################
    ###     Calculation of the missing parameters           ###
    ###########################################################

    # flag = 1      pH and pCO2 given       OK
    # flag = 2      CO2 and HCO3 given
    # flag = 3      CO2 and CO3 given
    # flag = 4      pCO2 and ALK given      OK
    # flag = 5      pCO2 and DIC given      OK
    # flag = 6      pH and HCO3 given
    # flag = 7      pH and CO3 given
    # flag = 8      pH and ALK given        OK
    # flag = 9      pH and DIC given        OK
    # flag = 10     HCO3 and CO3 given
    # flag = 11     HCO3 and ALK given
    # flag = 12     HCO3 and DIC given
    # flag = 13     CO3 and ALK given
    # flag = 14     CO3 and DIC given
    # flag = 15     ALK and DIC given       OK

    S = np.arange(0,40,0.1)
    T = 298.15
    pH = 8.2
    R = np.arange(0.2,2,0.1)

    pH_mueller_result = np.array([])
    pH_mosley_result = np.array([])
    R_result = np.array([])
    S_result = np.array([])

    for r in R:
        pH_mueller_result = np.append(pH_mueller_result, pHTspec(S,T,r,"mueller"))
        pH_mosley_result = np.append(pH_mosley_result, pHTspec(S,T,r,"mosley"))
        S_result = np.append(S_result, S)
        R_result = np.append(R_result, np.ones(len(S))*r)

    merge_arr = np.array([S_result, R_result, np.ones(len(S_result))*T, pH_mosley_result, pH_mueller_result]).T

    np.savetxt("dpH_Mueller_Mosley_recalc.csv", merge_arr, delimiter=",")

    sys.exit()

    print(densHCl(25, 0.2))
    sys.exit()
    print((0.14/96.062) * (S/1.80655))
    print(ST(S))
    sys.exit()
    print(pH)
    print(pHconvert(S,T,pH,flag=4))
    sys.exit()
    x  = carb(S,T, var1=np.array([2.264e-3,2.264e-3]), var2=np.array([2.036e-3,2.036e-3]), flag=15)
    print(x)
    #plot(T,x["pCO2"]*1e6)
    #show()

    #test_set()

    #parameter = ["T", "S", "pH", "CO2", "pCO2", "HCO3", "CO3", "DIC", "ALK"]
    #for i in parameter:
    #print i, "\t", carb(S,T, var1=8.0902, var2=2.e-3, flag=9)[i]
