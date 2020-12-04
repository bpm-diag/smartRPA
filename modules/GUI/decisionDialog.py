from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QStyle, QSizePolicy
import pandas
from deprecated.sphinx import deprecated


@deprecated(version='1.2.0', reason="Not in use anymore, replaced with web view version which is more versatile")
class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])


class DecisionDialog(QDialog):

    def __init__(self, df: pandas.DataFrame):

        super().__init__(flags=Qt.Window |
                               Qt.WindowTitleHint |
                               Qt.CustomizeWindowHint)

        # instance variables
        self.df = df
        # numberOfTraces = len(self.df['case:concept:name'].drop_duplicates())
        self.selectedTrace = None

        # dialog settings
        self.setWindowTitle("Decision point")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # table to display dataframe
        self.table = QtWidgets.QTableView()
        self.table.setModel(TableModel(df))
        # select entire row
        self.table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        # select only one row
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        # enable button when a row is selected
        # self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)

        # button to select trace
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        # enabled only when a row is selected
        # self.buttonBox.setEnabled(False)
        self.buttonBox.accepted.connect(self.handleReturn)

        # layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel(f"Which trace do you want to execute?"))
        mainLayout.addWidget(self.table)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

    def on_selection_changed(self):
        self.buttonBox.setEnabled(
            bool(self.table.selectionModel().selectedRows())
        )

    def handleReturn(self):
        # close dialog
        self.accept()
        try:
            # get index of selected row in pyqt table
            index = [i.row() for i in sorted(self.table.selectionModel().selectedRows())][0]
        except IndexError:
            index = 0
        # caseID of chosen trace
        self.selectedTrace = self.df.at[index, 'case:concept:name']

# test
# if __name__ == '__main__':
#     app = QtWidgets.QApplication(sys.argv)
#     df = pandas.DataFrame([
#         [1, 9, 2],
#         [1, 0, -1],
#         [3, 5, 2],
#         [3, 3, 2],
#         [5, 8, 9],
#     ], columns=['A', 'B', 'C'], index=['Row 1', 'Row 2', 'Row 3', 'Row 4', 'Row 5'])
#     window = DecisionDialog(df)
#     window.show()
#     app.exec_()
