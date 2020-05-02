import csv
import os

import numpy as np


# noinspection PyBroadException
class ConnectivityData:
    data = None

    @staticmethod
    def load_file(file_name):
        if os.path.exists(file_name):
            with open(file_name, newline='') as file:
                try:
                    ConnectivityData.data = list(csv.reader(file))
                    data = np.asarray(ConnectivityData.data)
                    ConnectivityData.data = data.astype(float)
                    return True

                except Exception:
                    return False

        return False

    @staticmethod
    def empty():
        return ConnectivityData.data is None
