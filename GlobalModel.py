from SIR import SIR


class GlobalModel():
    def __init__(self):
        super().__init__()
        self._communities_sir_models = []
        self.Rt = None
        self.Rt_t1 = []
        self.actual_data = []

    def execute(self, t):
        i = []
        x = 0
        for sir in self._communities_sir_models:
            s0 = self.actual_data.item((-1, x * 3))
            i0 = self.actual_data.item((-1, x * 3 + 1))
            r0 = self.actual_data.item((-1, x * 3 + 2))
            sir.set_r(self.Rt[:,x].tolist(), self.Rt_t1)
            infected = sir.execute(t, s0, i0, r0)
            if len(i) < 1:
                i = infected
            else:
                i = i + infected
            x = x + 1
        return i

    def set_actual_data(self, actual_data):
        self.actual_data = actual_data
        cs = actual_data.shape[1] // 3
        for i in range(cs):
            self._communities_sir_models.append(SIR())