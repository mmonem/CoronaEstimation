import datetime
import numpy as np
from PyQt5.QtCore import pyqtSlot, QSettings
from matplotlib.ticker import FuncFormatter, LinearLocator
from PyQt5.QtWidgets import QDialog, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import csv

from RoTableModel import RoTableModel
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
        self.actual_data = []
        self.simulation_days = 30
        self.days = []

        actual_data_file = QSettings().value("actual_data_file", "")
        if actual_data_file:
            self.load_actual_data_file(actual_data_file)
        r, rt = self.load_r()
        self.set_r(r, rt)

    @staticmethod
    def load_r():
        r = QSettings().value("rt_values", [])
        if isinstance(r, list):
            r = [float(i) for i in r]
        else:
            r = []
        rt = QSettings().value("rt_times", [])
        if isinstance(rt, list):
            rt = [float(i) for i in rt]
        else:
            rt = []
        return r, rt

    def save_r(self):
        QSettings().setValue("rt_values", self.sir.Rt)
        QSettings().setValue("rt_times", self.sir.Rt_t1)

    def set_r(self, r, t):
        self.sir.set_r(r, t)
        self.start_execution()


    def x_formatter(self, x, pos):
        x = int(x)
        if 0 < x < len(self.days):
            return self.days[x]
        return ''

    def y_formatter(self, x, pos):
        return '{:,}'.format(int(x))

    def start_execution(self):
        if len(self.actual_data) < 4 or len(self.sir.Rt) < 1:
            return

        actual_infected = self.actual_data[:, 1]
        actual_infected = [int(i) for i in actual_infected]
        first_day = np.unicode(self.actual_data[0:1, 0].item(0))
        I0 = actual_infected[len(actual_infected) - 1]
        R0 = 1500
        S0 = 100000000
        base = datetime.datetime.strptime(first_day, '%Y-%m-%d')
        self.days = [(base + datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(len(actual_infected) + self.simulation_days)]

        t0 = len(actual_infected)
        t = np.linspace(t0, t0 + self.simulation_days - 1, self.simulation_days)
        i = self.sir.execute(t, S0, I0, R0)

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

        self.ax.set_xlim(0, len(actual_infected) + self.simulation_days)
        self.ax.legend(loc="upper right")
        self.canvas.draw_idle()

    def load_actual_data_file(self, file_name):
        with open(file_name, newline='') as file:
            self.actual_data = list(csv.reader(file))
            self.actual_data = np.asarray(self.actual_data)

        self.ui.actualDataFileButton.setText('Actual Data File: ' + file_name)
        self.start_execution()

    @pyqtSlot()
    def actual_data_file_selected(self):
        t = QFileDialog.getOpenFileName(self, filter="csv(*.csv)")
        file_name = t[0]
        if file_name:
            QSettings().setValue("actual_data_file", file_name)
            self.load_actual_data_file(file_name)

    @pyqtSlot()
    def estimate_R(self):
        actual_infected = self.actual_data[:, 1]
        actual_infected = [int(i) for i in actual_infected]
        incidents = [actual_infected[0]]
        incidents.extend(np.diff(actual_infected))
        r, rt = RtEstimator(incidents, 5.1, 1).estimR()
        rt = np.trim_zeros(rt)
        r = r[:len(rt)]
        self.set_r(r, rt)
        self.save_r()

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
