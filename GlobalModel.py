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
            r = y[c * 3 + 2]

            incoming_s = 0
            incoming_i = 0
            incoming_r = 0

            if not ConnectivityData.empty():
                for a in range(len(ConnectivityData.data)):
                    if a != c:
                        incoming = ConnectivityData.data[c][a]
                        sa = y[a * 3]
                        ia = y[a * 3 + 1]
                        ra = y[a * 3 + 2]

                        s_ratio_in_a = sa / (sa + ia + ra)
                        incoming_s = incoming_s + s_ratio_in_a * incoming

                        i_ratio_in_a = ia / (sa + ia + ra)
                        incoming_i = incoming_i + i_ratio_in_a * incoming

                        r_ratio_in_a = ra / (sa + ia + ra)
                        incoming_r = incoming_r + r_ratio_in_a * incoming

                for a in range(len(ConnectivityData.data)):
                    if a != c:
                        outgoing = ConnectivityData.data[a][c]
                        sa = y[a * 3]
                        ia = y[a * 3 + 1]
                        ra = y[a * 3 + 2]

                        s_ratio_in_a = sa / (sa + ia + ra)
                        incoming_s = incoming_s - s_ratio_in_a * outgoing

                        i_ratio_in_a = ia / (sa + ia + ra)
                        incoming_i = incoming_i - i_ratio_in_a * outgoing

                        r_ratio_in_a = ra / (sa + ia + ra)
                        incoming_r = incoming_r - r_ratio_in_a * outgoing

            n = s + i + r
            si = beta * s * i / n
            ir = GlobalModel.gamma * i
            ret.append(-si + incoming_s)
            ret.append(si - ir + incoming_i)
            ret.append(ir + incoming_r)
        return ret
