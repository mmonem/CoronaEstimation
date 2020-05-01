import datetime
import numpy as np
from PyQt5.QtCore import pyqtSlot, QSettings
from matplotlib.ticker import FuncFormatter
from PyQt5.QtWidgets import QDialog, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import csv

from RtEstimator import RtEstimator
from gen.Ui_CoronaSimulationDialog import Ui_CoronaSimulationDialog
from GlobalModel import GlobalModel


class CoronaSimulationDialog(QDialog):
    def __init__(self):
        super().__init__(None)
        self.sir = GlobalModel()
        self.ui = Ui_CoronaSimulationDialog()
        self.ui.setupUi(self)
        self.fig = Figure()
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.ax = self.canvas.figure.add_subplot(111)
        self.ax2 = self.ax.twinx()
        self.ui.figuresLayout.addWidget(self.canvas)
        self.showMaximized()
        self.actual_data = np.array
        self.simulation_days = 30
        self.days = []
        self.first_day = ''

        actual_data_file = QSettings().value("actual_data_file", "")
        if actual_data_file:
            self.load_actual_data_file(actual_data_file)

        r_data_file = QSettings().value("r_data_file", "")
        if r_data_file:
            self.load_r_data_file(r_data_file)

        self.start_execution()

    def load_r_data_file(self, file_name):
        with open(file_name, newline='') as file:
            r = list(csv.reader(file))
            for i in range(len(r)):
                if self.sir.Rt is None:
                    self.sir.Rt = np.empty([len(r), len(r[0]) - 1])
                self.sir.Rt[i, :] = np.asarray(r)[i, 1:].astype(float)
                r = np.asarray(r)
                self.sir.Rt_t1 = r[:, 0].astype(int).tolist()

        self.ui.RDataFileButton.setText('R Data File: ' + file_name)

    @staticmethod
    def save_r_data_file(file_name, r, t):
        f = open(file_name, 'w')
        with f:
            writer = csv.writer(f)
            for i in range(len(t)):
                row = [t[i]]
                row.extend(r[i,:])
                writer.writerow(row)

    # noinspection PyUnusedLocal
    def x_formatter(self, x, pos):
        x = int(x)
        if 0 < x < len(self.days):
            return self.days[x]
        return ''

    # noinspection PyUnusedLocal
    @staticmethod
    def y_formatter(x, pos):
        return '{:,}'.format(int(x))

    def start_execution(self):
        if len(self.actual_data) < 4 or len(self.sir.Rt) < 1:
            return

        actual_infected = []
        r, c = self.actual_data.shape
        for i in range(r):
            infected = 0
            for j in range(c // 3):
                v = self.actual_data.item((i, j * 3 + 1))
                infected += v
            actual_infected.append(infected)

        base = datetime.datetime.strptime(self.first_day, '%Y-%m-%d')
        self.days = [(base + datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(len(self.actual_data) + self.simulation_days)]

        t0 = len(actual_infected)
        t = np.linspace(t0, t0 + self.simulation_days - 1, self.simulation_days)
        i = self.sir.execute(t)

        self.ax.cla()
        self.ax.xaxis.grid()
        self.ax.yaxis.grid()
        # self.ax.minorticks_on()
        self.ax.set_xticklabels(self.days, rotation=90)
        self.ax.xaxis.set_major_formatter(FuncFormatter(self.x_formatter))
        self.ax.yaxis.set_major_formatter(FuncFormatter(self.y_formatter))

        self.ax.plot(list(range(len(actual_infected))), actual_infected, label='Actual')
        t_for_i = [int(i) for i in t]
        t_for_i = t_for_i[:len(t_for_i) - 1]
        self.ax.plot(t_for_i, i, label='Expected')

        self.ax.set_xlim(0, len(self.actual_data) + self.simulation_days)
        self.ax.legend(loc="upper right")
        self.canvas.draw_idle()

    def load_actual_data_file(self, file_name):
        with open(file_name, newline='') as file:
            actual_data = list(csv.reader(file))
            actual_data = np.asarray(actual_data)
            days = actual_data[:, 0].tolist()
            self.first_day = days[0]
            self.actual_data = actual_data[:, 1:].astype(float)
            self.sir.set_actual_data(self.actual_data)

        self.ui.actualDataFileButton.setText('Actual Data File: ' + file_name)

    @pyqtSlot()
    def actual_data_file_selected(self):
        t = QFileDialog.getOpenFileName(self, filter="csv(*.csv)")
        file_name = t[0]
        if file_name:
            QSettings().setValue("actual_data_file", file_name)
            self.load_actual_data_file(file_name)
            self.start_execution()

    @pyqtSlot()
    def r_data_file_selected(self):
        t = QFileDialog.getOpenFileName(self, filter="csv(*.csv)")
        file_name = t[0]
        if file_name:
            QSettings().setValue("r_data_file", file_name)
            self.load_r_data_file(file_name)
            self.start_execution()

    @pyqtSlot()
    def estimate_R(self):
        days_count = self.actual_data.shape[0]
        communities_count = self.actual_data.shape[1] // 3
        time_for_r = []
        super_r = None

        for i in range(communities_count):
            actual_infected = self.actual_data[:, i * 3 + 1]
            actual_infected = [int(i) for i in actual_infected]
            incidents = [actual_infected[0]]
            incidents.extend(np.diff(actual_infected))
            r, rt = RtEstimator(incidents, 5.1, 1).estimR()
            rt = np.trim_zeros(rt)
            r = r[:len(rt)]
            time_for_r = rt
            if super_r is None:
                super_r = np.empty([len(rt), communities_count])
            super_r[:, i] = r

        t = QFileDialog.getSaveFileName(self, filter="csv(*.csv)")
        file_name = t[0]
        if file_name:
            QSettings().setValue("r_data_file", file_name)
            self.save_r_data_file(file_name, super_r, time_for_r)
            self.load_r_data_file(file_name)
            self.start_execution()

    @pyqtSlot()
    def simulationDaysChanged(self):
        default = 30
        str = self.ui.lineEditSimulationDays.text()
        x = int(str)
        if x < 10:
            x = default
        if self.simulation_days != x:
            self.simulation_days = x
            self.start_execution()
