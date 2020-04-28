from PyQt5.QtCore import Qt
from PyQt5 import QtCore


class RoTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(RoTableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]

    # noinspection PyUnusedLocal
    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid():
            row = index.row()
            col = index.column()
            self._data[row][col] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        n_columns = len(self._data[0])
        for i in range(len(self._data)):
            n_columns = max(n_columns, len(self._data[i]))
        return n_columns

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def get_raw_data(self):
        return self._data

