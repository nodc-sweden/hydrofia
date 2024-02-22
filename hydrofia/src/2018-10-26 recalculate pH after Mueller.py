#!/usr/bin/python2
# -*- coding: UTF-8 -*-

import sqlite3
import os
import numpy as np
import fnmatch
import datetime

##  Equilibrium constant of mCP after Mosley et al. (2004)
def KmCP25(S):
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

if __name__=='__main__':

    foundDark = False
    dark  = np.array([])
    blank = np.array([])
    dyed  = np.array([])
    data  = np.array([])
    absorbanceIsosbesticMininma = np.arange(0.02,0.41,0.01)

    # Find path and create filelist of the current directory
    full_path = os.path.realpath(__file__)
    path, filename = os.path.split(full_path)
    print path
    filelist = os.listdir(path)
    filelist = fnmatch.filter(filelist, '*.sqlite')
    # filelist = ["0061_2018-07-20.sqlite"]

    ## create output file
    phFileName = "%s pH recalculated.csv" %(str(datetime.datetime.utcnow())[:19])
    phFileName = phFileName.replace(":","-")
    phFileName = phFileName.replace(" ","-")
    print "file name:", phFileName
    phFile = open(os.path.join(path,phFileName),"w")
    phFile.write("timeStamp,sampleName,salinity,temperature,counter,ph_mueller,ph_mueller_error,ph_mosley,ph_mosley_error\r")

    for datafile in filelist:
        ## find file path
        filepath = os.path.join(path,datafile)
        print filepath

        ## open database
        db = sqlite3.connect(filepath)
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute('SELECT UsedWavelengths from Spectrometer')

        ## get wavelength array
        for row in cursor:
            wlArr = np.array([float(e) for e in row['UsedWavelengths'].split(' ')])

        ## index ranges for spectral noise reduction / fitting
        use434 = np.invert((wlArr < 444) - (wlArr > 424))
        use487 = np.invert((wlArr < 497) - (wlArr > 477))
        use578 = np.invert((wlArr < 588) - (wlArr > 568))
        use730 = np.invert((wlArr < 740) - (wlArr > 720))

        ## find measurement counters
        result = cursor.execute('SELECT DISTINCT measurementCounter from Spectra')
        measurementCounterArray = [ row['measurementCounter'] for row in result ]

        for counter in measurementCounterArray:
            try:
                ## Initialize variables
                dark = np.array([])
                blank = np.array([])
                dyed = np.array([])
                temperature = 25.0
                salinity = 35.0
                foundDark = False
                foundBlank = False
                intensities = []
                temperatures = np.array([])

                result = cursor.execute('SELECT * from Spectra WHERE spectrumType!="Result" AND measurementCounter=%d' %(counter))
                countArr = []

                for row in result:
                    spectrum = np.array([float(e) for e in row['Spectrum'].split(',')])
                    if row['temperatureSample'] != "NULL":
                        temperature = float(row['temperatureSample'])
                    if row['salinity'] != "NULL":
                        salinity = float(row['salinity'])
                    timeStamp = row['timeStamp']
                    sampleName = row['sampleName']
                    action = row['action']
                    spectrumType = row['spectrumType']
                    measurementCounter = row["measurementCounter"]

                    if not foundDark:
                        if "Dark" in spectrumType:
                            foundDark = True
                            # print "found Dark"
                            # print timeStamp
                        else:
                            continue

                    ## Polynomial fits of the raw spektra
                    I434 = np.poly1d(np.polyfit(wlArr[use434], spectrum[use434], 5))(434)
                    I487 = np.poly1d(np.polyfit(wlArr[use487], spectrum[use487], 5))(487.6)
                    I578 = np.poly1d(np.polyfit(wlArr[use578], spectrum[use578], 5))(578)
                    I730 = np.poly1d(np.polyfit(wlArr[use730], spectrum[use730], 5))(730)
                    intensities = [I434,I487,I578,I730]

                    ## Collect spectra
                    if "Dyed" in spectrumType:
                        dyed = np.append(dyed,intensities)
                        temperatures = np.append(temperatures,temperature)
                    elif "Dark" in spectrumType:
                        dark = np.append(dark,intensities)
                    elif "Blank" in spectrumType:
                        blank = np.append(blank,intensities)

                if (len(dark) > 0) and (len(blank) > 0) and (len(dyed) > 0) :

                    temperature = np.mean(temperatures)
                    darkMean = np.mean(dark.reshape(-1,len(intensities)),0)
                    blankMean = np.mean(blank.reshape(-1,len(intensities)),0) - darkMean
                    dyed = dyed.reshape(-1,len(intensities)) - darkMean

                    ## Calculate absorbance
                    absorbance = np.log10(blankMean / dyed)
                    absorbanceReferenceCorrected = absorbance.T - absorbance[:,3]
                    A434 = absorbanceReferenceCorrected[0]
                    A487 = absorbanceReferenceCorrected[1] # iso
                    A578 = absorbanceReferenceCorrected[2]

                    ## Find indicator peak
                    maxindex = np.argmax(A487) # iso
                    A434 = A434[maxindex:]
                    A487 = A487[maxindex:]
                    A578 = A578[maxindex:]

                    ## Cut relevant gradient values
                    absorbanceIsosbesticMininma = np.arange(0.02,0.41,0.01)
                    absorbanceIsosbesticMax = 0.9

                    for mcpCharacterization in ["mueller", "mosley"]:

                        errorResiduals = []
                        errorIntercept = []
                        phRanges = []
                        isoRanges = []
                        nRanges = []

                        for absorbanceIsosbesticMin in absorbanceIsosbesticMininma:
                            use = np.invert((A487 < absorbanceIsosbesticMin) - (A487 > absorbanceIsosbesticMax))
                            a434 = A434[use]
                            a578 = A578[use]
                            a487 = A487[use]

                            R = (a578/a434)
                            reset = False

                            pH = pHTspec(salinity,temperature+273.15,R,mcpCharacterization)

                            if len(a487) > 5:
                                n = 2  # degree of polynomial
                                sampleFit, C_p = np.polyfit(a487, pH, n, cov=True)

                                # calculate error
                                # Do the interpolation for plotting:
                                t = np.linspace(0, absorbanceIsosbesticMax, 100)
                                # Matrix with rows 1, t, t**2, ...:
                                TT = np.vstack([t**(n-i) for i in range(n+1)]).T
                                yi = np.dot(TT, sampleFit)  # matrix multiplication calculates the polynomial values
                                C_yi = np.dot(TT, np.dot(C_p, TT.T)) # C_y = TT*C_z*TT.T
                                sig_yi = np.sqrt(np.diag(C_yi))  # Standard deviations are sqrt of diagonal

                                errorIntercept.append(sig_yi[0])
                                errorResiduals.append(np.mean(sig_yi))
                                phRanges.append(yi[0])
                                isoRanges.append(absorbanceIsosbesticMin)
                                nRanges.append(len(pH))

                                phError = round(sig_yi[0], 4)

                            else:
                                errorIntercept.append(np.nan)
                                errorResiduals.append(np.nan)
                                phRanges.append(np.nan)
                                isoRanges.append(absorbanceIsosbesticMin)
                                nRanges.append(0)

                        ## Find best fitting Range
                        # errorIntercept = np.asarray(errorIntercept)
                        # errorResiduals = np.asarray(errorResiduals)
                        lowerFittingEndIndex = np.argmin(abs(np.asarray(errorIntercept) + np.asarray(errorResiduals)))

                        ph = phRanges[lowerFittingEndIndex]
                        phError = abs(np.asarray(errorIntercept) + np.asarray(errorResiduals))[lowerFittingEndIndex]*3

                        print "%s,%s,%s,%.4f,%.4f,%.2f,%.2f,%d" %(timeStamp, sampleName, mcpCharacterization, ph, phError, salinity, temperature, counter)

                        if mcpCharacterization == "mueller":
                            phFile.write("%s,%s,%.2f,%.2f,%d,%.4f,%.4f," %(timeStamp, sampleName, salinity, temperature, counter, ph, phError))
                        else:
                            phFile.write("%.4f,%.4f\r" %(ph, phError))

            except:
                print "faulty dataset"

    phFile.close()
    print "done processing"
    # raw_input("press enter to end script")