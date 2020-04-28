# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CoronaSimulationDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CoronaSimulationDialog(object):
    def setupUi(self, CoronaSimulationDialog):
        CoronaSimulationDialog.setObjectName("CoronaSimulationDialog")
        CoronaSimulationDialog.resize(982, 578)
        self.verticalLayout = QtWidgets.QVBoxLayout(CoronaSimulationDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.figuresLayout = QtWidgets.QHBoxLayout()
        self.figuresLayout.setObjectName("figuresLayout")
        self.verticalLayout.addLayout(self.figuresLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.tableViewR = QtWidgets.QTableView(CoronaSimulationDialog)
        self.tableViewR.setObjectName("tableViewR")
        self.verticalLayout.addWidget(self.tableViewR)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.actualDataFileButton = QtWidgets.QPushButton(CoronaSimulationDialog)
        self.actualDataFileButton.setObjectName("actualDataFileButton")
        self.horizontalLayout_2.addWidget(self.actualDataFileButton)
        self.estimateRButton = QtWidgets.QPushButton(CoronaSimulationDialog)
        self.estimateRButton.setObjectName("estimateRButton")
        self.horizontalLayout_2.addWidget(self.estimateRButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(-1, -1, 0, -1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.sliderRo = QtWidgets.QSlider(CoronaSimulationDialog)
        self.sliderRo.setMaximum(1000)
        self.sliderRo.setOrientation(QtCore.Qt.Horizontal)
        self.sliderRo.setObjectName("sliderRo")
        self.verticalLayout_2.addWidget(self.sliderRo)
        self.labelRo = QtWidgets.QLabel(CoronaSimulationDialog)
        self.labelRo.setObjectName("labelRo")
        self.verticalLayout_2.addWidget(self.labelRo)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(-1, -1, 0, -1)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.sliderGamma = QtWidgets.QSlider(CoronaSimulationDialog)
        self.sliderGamma.setMaximum(1000)
        self.sliderGamma.setOrientation(QtCore.Qt.Horizontal)
        self.sliderGamma.setObjectName("sliderGamma")
        self.verticalLayout_3.addWidget(self.sliderGamma)
        self.labelGamma = QtWidgets.QLabel(CoronaSimulationDialog)
        self.labelGamma.setObjectName("labelGamma")
        self.verticalLayout_3.addWidget(self.labelGamma)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setContentsMargins(-1, -1, 0, -1)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.sliderBeta = QtWidgets.QSlider(CoronaSimulationDialog)
        self.sliderBeta.setMaximum(1000)
        self.sliderBeta.setOrientation(QtCore.Qt.Horizontal)
        self.sliderBeta.setObjectName("sliderBeta")
        self.verticalLayout_4.addWidget(self.sliderBeta)
        self.labelBeta = QtWidgets.QLabel(CoronaSimulationDialog)
        self.labelBeta.setObjectName("labelBeta")
        self.verticalLayout_4.addWidget(self.labelBeta)
        self.horizontalLayout.addLayout(self.verticalLayout_4)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.lineEditSimulationDays = QtWidgets.QLineEdit(CoronaSimulationDialog)
        self.lineEditSimulationDays.setObjectName("lineEditSimulationDays")
        self.verticalLayout_5.addWidget(self.lineEditSimulationDays)
        self.label = QtWidgets.QLabel(CoronaSimulationDialog)
        self.label.setObjectName("label")
        self.verticalLayout_5.addWidget(self.label)
        self.horizontalLayout.addLayout(self.verticalLayout_5)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(CoronaSimulationDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(CoronaSimulationDialog)
        self.buttonBox.accepted.connect(CoronaSimulationDialog.accept)
        self.buttonBox.rejected.connect(CoronaSimulationDialog.reject)
        self.actualDataFileButton.clicked.connect(CoronaSimulationDialog.actual_data_file_selected)
        self.estimateRButton.clicked.connect(CoronaSimulationDialog.estimate_R)
        self.lineEditSimulationDays.textEdited['QString'].connect(CoronaSimulationDialog.simulationDaysChanged)
        QtCore.QMetaObject.connectSlotsByName(CoronaSimulationDialog)

    def retranslateUi(self, CoronaSimulationDialog):
        _translate = QtCore.QCoreApplication.translate
        CoronaSimulationDialog.setWindowTitle(_translate("CoronaSimulationDialog", "Dialog"))
        self.actualDataFileButton.setText(_translate("CoronaSimulationDialog", "Actual Data File"))
        self.estimateRButton.setText(_translate("CoronaSimulationDialog", "Estimate R"))
        self.labelRo.setText(_translate("CoronaSimulationDialog", "TextLabel"))
        self.labelGamma.setText(_translate("CoronaSimulationDialog", "TextLabel"))
        self.labelBeta.setText(_translate("CoronaSimulationDialog", "TextLabel"))
        self.lineEditSimulationDays.setText(_translate("CoronaSimulationDialog", "30"))
        self.label.setText(_translate("CoronaSimulationDialog", "Simulation Days"))
