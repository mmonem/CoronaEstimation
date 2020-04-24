import sys
from PyQt5.QtWidgets import QApplication
from CoronaSimulationDialog import CoronaSimulationDialog

if __name__ == "__main__":
    a = QApplication(sys.argv)
    w = CoronaSimulationDialog()
    w.showMaximized()
    a.exec_()
