from ActualData import ActualData
from RData import RData
from SIR import SIR


class GlobalModel:

    @staticmethod
    def execute(t):
        i = []
        cs = ActualData.actual_data.shape[1] // 3
        for x in range(cs):
            sir = SIR()
            s0 = ActualData.actual_data.item((-1, x * 3))
            i0 = ActualData.actual_data.item((-1, x * 3 + 1))
            r0 = ActualData.actual_data.item((-1, x * 3 + 2))
            sir.set_r(RData.get_R_for(x), RData.Rt_t1)
            infected = sir.execute(t, s0, i0, r0)
            if len(i) < 1:
                i = infected
            else:
                i = i + infected
        return i
