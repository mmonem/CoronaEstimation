import csv
import os

import numpy as np


# noinspection PyBroadException
class ActualData:
    actual_data = np.zeros((0,0))
    days = []
    first_day = ''
    actual_infected = []

    @staticmethod
    def load_file(file_name):
        if os.path.exists(file_name):
            with open(file_name, newline='') as file:
                try:
                    ActualData.actual_data = list(csv.reader(file))
                    actual_data = np.asarray(ActualData.actual_data)
                    ActualData.days = actual_data[:, 0].tolist()
                    ActualData.first_day = ActualData.days[0]
                    ActualData.actual_data = actual_data[:, 1:].astype(float)

                    ActualData.actual_infected = []
                    r, c = ActualData.actual_data.shape
                    for i in range(r):
                        infected = 0
                        for j in range(c // 3):
                            v = ActualData.actual_data.item((i, j * 3 + 1))
                            infected += v
                        ActualData.actual_infected.append(infected)
                    return True

                except Exception:
                    return False

        return False

    @staticmethod
    def empty():
        if len(ActualData.days) < 1:
            return True
        return False

    @staticmethod
    def last_data(c):
        t = ActualData.actual_data.shape[0] - 1
        c = c * 3
        return ActualData.actual_data.item((t, c)), ActualData.actual_data.item((t, c + 1)), ActualData.actual_data.item((t, c + 2))