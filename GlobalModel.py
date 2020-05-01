from SIR import SIR


class GlobalModel(SIR):
    def __init__(self):
        super().__init__()
        self._m1 = SIR()
        self._m2 = SIR()

    def set_r(self, r, t):
        super().set_r(r, t)
        self._m1.set_r(r, t)
        self._m2.set_r(r, t)

    def execute(self, t, s0, i0, r0):
        super().execute(t, s0, i0, r0)

        i1 = self._m1.execute(t, s0 / 2, i0 / 2, r0 / 2)
        i2 = self._m2.execute(t, s0 / 2, i0 / 2, r0 / 2)

        i = i1 + i2
        return i

