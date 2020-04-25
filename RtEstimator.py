# This work has been converted from MS Excel macros found in http://tools.epidemiology.net/EpiEstim.xls which is an
# implementation for the work explained in this paper: "New Framework and Software to Estimate Time-Varying Reproduction
# Numbers During Epidemics", American journal of epidemiology 178(9), September 2013

from math import sqrt

from scipy.stats import invgamma, gamma

class RtEstimator:
    def __init__(self):
        self.TimeMin = 1
        self.TimeMax = 67
        self.Incidence = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 12, 0, 34, 6, 4, 1, 7, 13, 29, 1, 40, 46, 0, 60, 29, 9, 33, 39, 36, 54, 39, 41, 40, 33, 47, 54, 69, 86, 120, 85, 103, 149,
            128, 110, 139, 95, 145, 126, 125, 160, 155, 168, 171, 188, 112, 189]
        self.aPrior = 0.0
        self.bPrior = 0.0
        self.startTime = []
        self.endTime = []
        self.NbTimePeriods = 0
        self.StartEstimDate = 0
        self.MeanSI = 5.1
        self.sdSI = 1

    def estimR(self):
        self.ReadPrior()
        self.ReadTimeSteps()

        # 'error message if inconsistent data
        if self.MeanSI <= 1:
            print("The mean serial interval must be >1 time step of incidence. Estimation aborted.")
            exit(1)

        # 'error message if inconsistent data
        if self.sdSI < 0:
            print("The std of the serial interval must be >=0. Estimation aborted.")
            exit(1)

        # ''' Different code when accounting or not accounting for serial interval uncertainty '''


        aPosterior = [0.0] * (self.TimeMax - self.TimeMin + 1)
        bPosterior = [0.0] * (self.TimeMax - self.TimeMin + 1)
        MeanR = [0.0] * (self.TimeMax - self.TimeMin + 1)
        StdR = [0.0] * (self.TimeMax - self.TimeMin + 1)
        RQuantile025 = [0.0] * (self.TimeMax - self.TimeMin + 1)
        RQuantile05 = [0.0] * (self.TimeMax - self.TimeMin + 1)
        RQuantile25 = [0.0] * (self.TimeMax - self.TimeMin + 1)
        RMedian = [0.0] * (self.TimeMax - self.TimeMin + 1)
        RQuantile75 = [0.0] * (self.TimeMax - self.TimeMin + 1)
        RQuantile95 = [0.0] * (self.TimeMax - self.TimeMin + 1)
        RQuantile975 = [0.0] * (self.TimeMax - self.TimeMin + 1)

        # ''' serial interval '''

        SIDistr = [0] * (self.TimeMax - self.TimeMin + 1)

        SumPi = 0
        SumPiXi = 0
        SumPiXi2 = 0
        for t in range(self.TimeMin, self.TimeMax + 1):
            SIDistr[t - self.TimeMin] = max(0, self.DiscreteShiftedGammaSIDistr(t - self.TimeMin))
            SumPi = SumPi + SIDistr[t - self.TimeMin]
            SumPiXi = SumPiXi + (t - self.TimeMin) * SIDistr[t - self.TimeMin]
            SumPiXi2 = SumPiXi2 + (t - self.TimeMin) * (t - self.TimeMin) * SIDistr[t - self.TimeMin]

        # 'error message if inconsistent data
        if SumPi < 0.99:
            print("The epidemic is too short compared to the distribution of the SI. Estimation aborted.")
            exit(1)

        MeanSIFinal = SumPiXi
        sdSIFinal = sqrt(SumPiXi2 - SumPiXi * SumPiXi)

        for t in range(self.TimeMin, self.TimeMax + 1):
            if t == self.TimeMin and SIDistr[t - self.TimeMin] != 0:
                print("serial interval distribution at time " + str(t) + " is not null." + "\n" + "Our model does not account for the possibility that index cases infect individuals on the very day when they are infected" + "\n" + "Estimation aborted.")
                exit(1)

            if SIDistr[t - self.TimeMin] < 0:
                print("serial interval distribution at time " + str(t) + " is negative. Estimation aborted.")
                exit(1)

            if abs(SumPi - 1) > 0.01:
                print("Error: the serial interval distribution you provided does not sum to 1. Estimation aborted.")
                exit(1)


        if MeanSIFinal < 1:
            print("The parameters you provided lead to a mean discrete serial interval <1 time step of incidence. Estimation aborted.")
            exit(1)

        self.StartEstimDate = max(self.StartEstimDate, MeanSIFinal)

        # ''' Estimation of R '''

        TimePeriodNb = 1
        if self.endTime[TimePeriodNb - 1] < self.StartEstimDate:
            print("Warning: you are trying to estimate R too early in the epidemic to get the desired posterior CV. Estimation will be performed anyway. Click here to continue.")


        while self.endTime[TimePeriodNb - 1] != 0:
            if self.startTime[TimePeriodNb - 1]> self.endTime[TimePeriodNb - 1]:
                print("Time period " + str(TimePeriodNb) + " has its starting date after its ending date. Estimation aborted.")
                exit(1)
            elif self.endTime[TimePeriodNb - 1] > self.TimeMax:
                print("Time period " + str(TimePeriodNb) + " ends after the end of the epidemic.  Estimation aborted.")
                exit(1)

            Res = self.CalculatePosterior(SIDistr, TimePeriodNb)
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


    def Lambda(self, t, SIDistr):
        Lambda = 0
        for s in range(1, t - self.TimeMin + 1):
            Lambda = Lambda + self.Incidence[t - s - self.TimeMin] * self.DiscreteShiftedGammaSIDistr(s)
        return Lambda


    def CalculatePosterior(self, SIDistr, TimePeriodNb):
        Temp = [None] * 2
        SumI = 0
        SumLambda = 0
        for t in range(self.startTime[TimePeriodNb - 1], self.endTime[TimePeriodNb - 1] + 1):
            SumI = SumI + self.Incidence[t - self.TimeMin]
            SumLambda = SumLambda + self.Lambda(t, SIDistr)

        Temp[0] = self.aPrior + SumI #aPosterior
        Temp[1] = 1 / (1 / self.bPrior + SumLambda) #bPosterior
        return Temp


    def DiscreteShiftedGammaSIDistr(self, k):
        a = (self.MeanSI - 1) * (self.MeanSI - 1) / (self.sdSI * self.sdSI)
        b = self.sdSI * self.sdSI / (self.MeanSI - 1)
        if k >= 2:
            return k * gamma.cdf(k, a, scale=b) + (k - 2) * gamma.cdf(k - 2, a, scale=b) - 2 * (k - 1) * gamma.cdf(k - 1, a, scale=b) + a * b * (2 * gamma.cdf(k - 1, a + 1, scale=b) - gamma.cdf(k - 2, a + 1, scale=b) - gamma.cdf(k, a + 1, scale=b))
        elif k == 1:
            return k * gamma.cdf(k, a, scale=b) - a * b * gamma.cdf(k, a + 1, scale=b)
        elif k == 0:
            return 0


    def ReadTimeSteps(self):
        # CVThreshold, CumulIncThreshold, CumulInc, CustomTimeSteps, Length, Steppp, t, TimePeriodNb

        self.startTime = [0.0] * (self.TimeMax - self.TimeMin + 1)
        self.endTime = [0.0] * (self.TimeMax - self.TimeMin + 1)

        CVThreshold = .3
        CumulIncThreshold = 1 / (CVThreshold * CVThreshold) - self.aPrior
        CumulInc = 0
        t = self.TimeMin + 1
        while CumulInc < CumulIncThreshold and t < self.TimeMax:
            t = t + 1
            CumulInc = CumulInc + self.Incidence[t - self.TimeMin]

        self.StartEstimDate = t

        Length = 7
        Steppp = 1
        self.StartEstimDate = max(self.StartEstimDate, Length)

        t = self.StartEstimDate
        TimePeriodNb = 1
        self.endTime[TimePeriodNb - 1] = t
        self.startTime[TimePeriodNb - 1] = t - Length + 1

        while t <= self.TimeMax - Steppp:
            t = t + Steppp
            TimePeriodNb = TimePeriodNb + 1
            self.endTime[TimePeriodNb - 1] = t
            self.startTime[TimePeriodNb - 1] = t - Length + 1
        self.NbTimePeriods = TimePeriodNb


    def ReadPrior(self):
        MeanPrior = 5
        StdPrior = 5
        self.aPrior = MeanPrior * MeanPrior / (StdPrior * StdPrior)
        self.bPrior = (StdPrior * StdPrior) / MeanPrior
