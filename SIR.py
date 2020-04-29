from scipy.interpolate import interp1d
from scipy.integrate import odeint


class SIR:
    def __init__(self):
        self.N = 0  # Total population
        self.beta = .25  # Infection rate
        self.gamma = .15  # The Removal rate
        self.Ro = round(self.beta / self.gamma, 2)
        self.Rt = []
        self.Rt_t1 = []
        self.rt0_interpolate = None

    def set_r(self, r, t):
        self.Rt = r
        self.Rt_t1 = t

    def execute(self, t, s0, i0, r0):
        self.N = s0 + i0 + r0
        x = self.Rt_t1[-5:]
        y = self.Rt[-5:]
        y = [x * s0 / self.N for x in y]  # Multiplying by S/N as suggested by Dr. Aly Farahat
        self.rt0_interpolate = interp1d(x, y, kind='nearest', fill_value="extrapolate")
        ret = odeint(self.derive_sir_model, (s0, i0, r0), t)
        i = ret[:, 1]
        return i[1:]

    def derive_sir_model(self, y, t):
        s, i, r = y
        beta = self.rt0_interpolate(t).item(0) * self.gamma
        si = beta * s * i / self.N
        ir = self.gamma * i
        return -si, si - ir, ir
