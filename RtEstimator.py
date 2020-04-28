# This work has been converted from MS Excel macros found in http://tools.epidemiology.net/EpiEstim.xls which is an
# implementation for the work explained in this paper: "New Framework and Software to Estimate Time-Varying Reproduction
# Numbers During Epidemics", American journal of epidemiology 178(9), September 2013

from math import sqrt

from scipy.stats import gamma

class RtEstimator:
    def __init__(self, incidence, si_mean, si_sd):
        self.TimeMin = 1
        self.TimeMax = len(incidence)
        self.Incidence = incidence
        self.aPrior = 0.0
        self.bPrior = 0.0
        self.startTime = []
        self.endTime = []
        self.NbTimePeriods = 0
        self.StartEstimDate = 0
        self.MeanSI = si_mean
        self.sdSI = si_sd

    def estimR(self):
        self.ReadPrior()
        self.ReadTimeSteps()

        # 'error message if inconsistent data
        if self.MeanSI <= 1:
            raise Exception("The mean serial interval must be >1 time step of incidence. Estimation aborted.")

        # 'error message if inconsistent data
        if self.sdSI < 0:
            raise Exception("The std of the serial interval must be >=0. Estimation aborted.")

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
            raise Exception("The epidemic is too short compared to the distribution of the SI. Estimation aborted.")

        MeanSIFinal = SumPiXi
        sdSIFinal = sqrt(SumPiXi2 - SumPiXi * SumPiXi)

        for t in range(self.TimeMin, self.TimeMax + 1):
            if t == self.TimeMin and SIDistr[t - self.TimeMin] != 0:
                raise Exception("serial interval distribution at time " + str(t) + " is not null." + "\n" + "Our model does not account for the possibility that index cases infect individuals on the very day when they are infected" + "\n" + "Estimation aborted.")

            if SIDistr[t - self.TimeMin] < 0:
                raise Exception("serial interval distribution at time " + str(t) + " is negative. Estimation aborted.")

            if abs(SumPi - 1) > 0.01:
                raise Exception("Error: the serial interval distribution you provided does not sum to 1. Estimation aborted.")


        if MeanSIFinal < 1:
            raise Exception("The parameters you provided lead to a mean discrete serial interval <1 time step of incidence. Estimation aborted.")

        self.StartEstimDate = max(self.StartEstimDate, MeanSIFinal)

        # ''' Estimation of R '''

        TimePeriodNb = 1
        if self.endTime[TimePeriodNb - 1] < self.StartEstimDate:
            raise Exception("You are trying to estimate R too early in the epidemic to get the desired posterior CV")


        while self.endTime[TimePeriodNb - 1] != 0:
            if self.startTime[TimePeriodNb - 1]> self.endTime[TimePeriodNb - 1]:
                raise Exception("Time period " + str(TimePeriodNb) + " has its starting date after its ending date. Estimation aborted.")
            elif self.endTime[TimePeriodNb - 1] > self.TimeMax:
                raise Exception("Time period " + str(TimePeriodNb) + " ends after the end of the epidemic.  Estimation aborted.")

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
            TimePeriodNb = TimePeriodNb + 1
        return RQuantile975, self.endTime


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
