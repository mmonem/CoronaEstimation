from scipy.integrate import odeint

from ActualData import ActualData
from ConnectivityData import ConnectivityData
from RData import RData


class GlobalModel:

    gamma = .15

    @staticmethod
    def execute(t):
        cs = ActualData.actual_data.shape[1] // 3
        y0 = []
        for c in range(cs):
            s0 = ActualData.actual_data.item((-1, c * 3))
            i0 = ActualData.actual_data.item((-1, c * 3 + 1))
            r0 = ActualData.actual_data.item((-1, c * 3 + 2))
            y0.append(s0)
            y0.append(i0)
            y0.append(r0)
        y = odeint(GlobalModel.derive, y0, t)
        ret = []
        for i in range(1, len(t)):
            x = 0
            for c in range (cs):
                x = x + y.item(i, c * 3 + 1)
            ret.append(x)
        return ret

    @staticmethod
    def derive(y, t):
        cs = ActualData.actual_data.shape[1] // 3
        ret = []
        for c in range(cs):
            beta = RData.Rt_interpolate[c](t).item(0) * GlobalModel.gamma
            s = y[c * 3]
            i = y[c * 3 + 1]

            if not ConnectivityData.empty():
                for a in range(len(ConnectivityData.data)):
                    if a != c:
                        incoming = ConnectivityData.data[c][a]
                        sa = y[a * 3]
                        ia = y[a * 3 + 1]
                        ra = y[a * 3 + 2]
                        infection_ratio_in_a = ia / (sa + ia + ra)
                        incoming_infections = infection_ratio_in_a * incoming
                        i = i + incoming_infections

            r = y[c * 3 + 2]
            n = s + i + r
            si = beta * s * i / n
            ir = GlobalModel.gamma * i
            ret.append(-si)
            ret.append(si - ir)
            ret.append(ir)
        return ret
