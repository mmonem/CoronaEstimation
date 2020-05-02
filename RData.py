import csv
import os
import numpy as np
from scipy.interpolate import interp1d
from ActualData import ActualData


# noinspection PyBroadException
class RData:
    Rt = None
    Rt_t1 = []
    Rt_interpolate = []

    @staticmethod
    def load_file(file_name):
        if os.path.exists(file_name):
            with open(file_name, newline='') as file:
                try:
                    r = list(csv.reader(file))
                    for i in range(len(r)):
                        if RData.Rt is None:
                            RData.Rt = np.empty([len(r), len(r[0]) - 1])
                        RData.Rt[i, :] = np.asarray(r)[i, 1:].astype(float)
                        r = np.asarray(r)
                        RData.Rt_t1 = r[:, 0].astype(int).tolist()

                    for c in range(RData.Rt.shape[1]):
                        x = RData.Rt_t1[-5:]
                        y = RData.Rt[-5:, c]
                        s0, i0, r0 = ActualData.last_data(c)
                        y = [x * s0 / (s0 + i0 + r0) for x in y]  # Multiplying by S/N as suggested by Dr. Aly Farahat
                        RData.Rt_interpolate.append(interp1d(x, y, kind='nearest', fill_value="extrapolate"))

                    return True

                except Exception as e:
                    print(e)
                    quit(-1)
                    return False

        return False

    @staticmethod
    def save_r_data_file(file_name):
        f = open(file_name, 'w')
        with f:
            writer = csv.writer(f)
            for i in range(len(RData.Rt_t1)):
                row = [RData.Rt_t1[i]]
                row.extend(RData.Rt[i, :])
                writer.writerow(row)
            return True

    @staticmethod
    def get_R_for(c):
        return RData.Rt[:, c].tolist()

    @staticmethod
    def empty():
        if len(RData.Rt_t1) < 1:
            return True
        return False
