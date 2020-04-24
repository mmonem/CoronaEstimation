# This work has been converted from MS Excel macros found in http://tools.epidemiology.net/EpiEstim.xls which is an
# implementation for the work explained in this paper: "New Framework and Software to Estimate Time-Varying Reproduction
# Numbers During Epidemics", American journal of epidemiology 178(9), September 2013

from math import sqrt

from scipy.stats import invgamma, gamma

TimeMin = 1
TimeMax = 67
Incidence = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 12, 0, 34, 6, 4, 1, 7, 13, 29, 1, 40, 46, 0, 60, 29, 9, 33, 39, 36, 54, 39, 41, 40, 33, 47, 54, 69, 86, 120, 85, 103, 149,
    128, 110, 139, 95, 145, 126, 125, 160, 155, 168, 171, 188, 112, 189]
aPrior = 0.0
bPrior = 0.0
startTime = []
endTime = []
NbTimePeriods = 0
StartEstimDate = 0
MeanSI = 5.1
sdSI = 1
koko = 3

def estimR():
    global StartEstimDate

    ReadPrior()
    ReadTimeSteps()

    # 'error message if inconsistent data
    if MeanSI <= 1:
        print("The mean serial interval must be >1 time step of incidence. Estimation aborted.")
        exit(1)

    # 'error message if inconsistent data
    if sdSI < 0:
        print("The std of the serial interval must be >=0. Estimation aborted.")
        exit(1)

    # ''' Different code when accounting or not accounting for serial interval uncertainty '''


    aPosterior = [0.0] * (TimeMax - TimeMin + 1)
    bPosterior = [0.0] * (TimeMax - TimeMin + 1)
    MeanR = [0.0] * (TimeMax - TimeMin + 1)
    StdR = [0.0] * (TimeMax - TimeMin + 1)
    RQuantile025 = [0.0] * (TimeMax - TimeMin + 1)
    RQuantile05 = [0.0] * (TimeMax - TimeMin + 1)
    RQuantile25 = [0.0] * (TimeMax - TimeMin + 1)
    RMedian = [0.0] * (TimeMax - TimeMin + 1)
    RQuantile75 = [0.0] * (TimeMax - TimeMin + 1)
    RQuantile95 = [0.0] * (TimeMax - TimeMin + 1)
    RQuantile975 = [0.0] * (TimeMax - TimeMin + 1)

    # ''' serial interval '''

    SIDistr = [0] * (TimeMax - TimeMin + 1)

    SumPi = 0
    SumPiXi = 0
    SumPiXi2 = 0
    for t in range(TimeMin, TimeMax + 1):
        SIDistr[t - TimeMin] = max(0, DiscreteShiftedGammaSIDistr(t - TimeMin, MeanSI, sdSI))
        SumPi = SumPi + SIDistr[t - TimeMin]
        SumPiXi = SumPiXi + (t - TimeMin) * SIDistr[t - TimeMin]
        SumPiXi2 = SumPiXi2 + (t - TimeMin) * (t - TimeMin) * SIDistr[t - TimeMin]

    # 'error message if inconsistent data
    if SumPi < 0.99:
        print("The epidemic is too short compared to the distribution of the SI. Estimation aborted.")
        exit(1)

    MeanSIFinal = SumPiXi
    sdSIFinal = sqrt(SumPiXi2 - SumPiXi * SumPiXi)

    for t in range(TimeMin, TimeMax + 1):
        if t == TimeMin and SIDistr[t - TimeMin] != 0:
            print("serial interval distribution at time " + str(t) + " is not null." + "\n" + "Our model does not account for the possibility that index cases infect individuals on the very day when they are infected" + "\n" + "Estimation aborted.")
            exit(1)

        if SIDistr[t - TimeMin] < 0:
            print("serial interval distribution at time " + str(t) + " is negative. Estimation aborted.")
            exit(1)

        if abs(SumPi - 1) > 0.01:
            print("Error: the serial interval distribution you provided does not sum to 1. Estimation aborted.")
            exit(1)


    if MeanSIFinal < 1:
        print("The parameters you provided lead to a mean discrete serial interval <1 time step of incidence. Estimation aborted.")
        exit(1)

    StartEstimDate = max(StartEstimDate, MeanSIFinal)

    # ''' Estimation of R '''

    TimePeriodNb = 1
    if endTime[TimePeriodNb - 1] < StartEstimDate:
        print("Warning: you are trying to estimate R too early in the epidemic to get the desired posterior CV. Estimation will be performed anyway. Click here to continue.")


    while endTime[TimePeriodNb - 1] != 0:
        if startTime[TimePeriodNb - 1]> endTime[TimePeriodNb - 1]:
            print("Time period " + str(TimePeriodNb) + " has its starting date after its ending date. Estimation aborted.")
            exit(1)
        elif endTime[TimePeriodNb - 1] > TimeMax:
            print("Time period " + str(TimePeriodNb) + " ends after the end of the epidemic.  Estimation aborted.")
            exit(1)

        Res = CalculatePosterior(MeanSI, sdSI, SIDistr, TimePeriodNb)
        aPosterior[TimePeriodNb - 1] = Res[0]
        bPosterior[TimePeriodNb - 1] = Res[1]
        MeanR[TimePeriodNb - 1] = aPosterior[TimePeriodNb - 1] * bPosterior[TimePeriodNb - 1]
        StdR[TimePeriodNb - 1] = sqrt(aPosterior[TimePeriodNb - 1]) * bPosterior[TimePeriodNb - 1]
        RQuantile025[TimePeriodNb - 1] = gamma.ppf(0.025, aPosterior[TimePeriodNb - 1], scale=bPosterior[TimePeriodNb - 1])
        RQuantile05[TimePeriodNb - 1] = gamma.ppf(0.05, aPosterior[TimePeriodNb - 1], scale=bPosterior[TimePeriodNb - 1])
        RQuantile25[TimePeriodNb - 1] = gamma.ppf(0.25, aPosterior[TimePeriodNb - 1], scale=bPosterior[TimePeriodNb - 1])
        RMedian[TimePeriodNb - 1] = gamma.ppf(0.5, aPosterior[TimePeriodNb - 1], scale=bPosterior[TimePeriodNb - 1])
        RQuantile75[TimePeriodNb - 1] = gamma.ppf(0.75, aPosterior[TimePeriodNb - 1], scale=bPosterior[TimePeriodNb - 1])
        RQuantile95[TimePeriodNb - 1] = gamma.ppf(0.95, aPosterior[TimePeriodNb - 1], scale=bPosterior[TimePeriodNb - 1])
        RQuantile975[TimePeriodNb - 1] = gamma.ppf(0.975, aPosterior[TimePeriodNb - 1], scale=bPosterior[TimePeriodNb - 1])
        print(RQuantile975)
        TimePeriodNb = TimePeriodNb + 1


def Lambda(t, MeanSI, stdSI, SIDistr):
    Lambda = 0
    for s in range(1, t - TimeMin + 1):
        Lambda = Lambda + Incidence[t - s - TimeMin] * DiscreteShiftedGammaSIDistr(s, MeanSI, stdSI)
    return Lambda


def CalculatePosterior(MeanSI, stdSI, SIDistr, TimePeriodNb):
    Temp = [None] * 2
    SumI = 0
    SumLambda = 0
    for t in range(startTime[TimePeriodNb - 1], endTime[TimePeriodNb - 1] + 1):
        SumI = SumI + Incidence[t - TimeMin]
        SumLambda = SumLambda + Lambda(t, MeanSI, stdSI, SIDistr)

    Temp[0] = aPrior + SumI #aPosterior
    Temp[1] = 1 / (1 / bPrior + SumLambda) #bPosterior
    return Temp


def DiscreteShiftedGammaSIDistr(k, mean, sd):
    a = (mean - 1) * (mean - 1) / (sd * sd)
    b = sd * sd / (mean - 1)
    if k >= 2:
        return k * gamma.cdf(k, a, scale=b) + (k - 2) * gamma.cdf(k - 2, a, scale=b) - 2 * (k - 1) * gamma.cdf(k - 1, a, scale=b) + a * b * (2 * gamma.cdf(k - 1, a + 1, scale=b) - gamma.cdf(k - 2, a + 1, scale=b) - gamma.cdf(k, a + 1, scale=b))
    elif k == 1:
        return k * gamma.cdf(k, a, scale=b) - a * b * gamma.cdf(k, a + 1, scale=b)
    elif k == 0:
        return 0


def ReadTimeSteps():
    # CVThreshold, CumulIncThreshold, CumulInc, CustomTimeSteps, Length, Steppp, t, TimePeriodNb

    global startTime
    global endTime
    startTime = [0.0] * (TimeMax - TimeMin + 1)
    endTime = [0.0] * (TimeMax - TimeMin + 1)

    CVThreshold = .3
    CumulIncThreshold = 1 / (CVThreshold * CVThreshold) - aPrior
    CumulInc = 0
    t = TimeMin + 1
    while CumulInc < CumulIncThreshold and t < TimeMax:
        t = t + 1
        CumulInc = CumulInc + Incidence[t - TimeMin]

    StartEstimDate = t

    Length = 7
    Steppp = 1
    StartEstimDate = max(StartEstimDate, Length)

    t = StartEstimDate
    TimePeriodNb = 1
    endTime[TimePeriodNb - 1] = t
    startTime[TimePeriodNb - 1] = t - Length + 1

    while t <= TimeMax - Steppp:
        t = t + Steppp
        TimePeriodNb = TimePeriodNb + 1
        endTime[TimePeriodNb - 1] = t
        startTime[TimePeriodNb - 1] = t - Length + 1
    NbTimePeriods = TimePeriodNb


def ReadPrior():
    global aPrior
    global bPrior
    MeanPrior = 5
    StdPrior = 5
    aPrior = MeanPrior * MeanPrior / (StdPrior * StdPrior)
    bPrior = (StdPrior * StdPrior) / MeanPrior
