from PyQt5 import QtCore, QtGui, QtWidgets
import pandas
import darkdetect
import utils.utils
from modules.GUI.filenameDialog import getFilenameDialog
import os
import numpy as np
try:
    import pm4py
except ImportError as e:
    print("[SEGMENTATION] 'pm4py' module is not installed. See https://github.com/bpm-diag/smartRPA#1-pm4py")
    print(e)


class PandasModel(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """
    def __init__(self, data, parent=None, rows_to_color=None, row_color='red'):
        """
        Initialize class to populate table view

        :param data: pandas dataframe
        :param rows_to_color: optional, list of integers representig rows to color
        :param row_color: optional, color of rows (default is red). Supports HTML color names https://www.w3schools.com/colors/colors_names.asp
        """
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = np.array(data.values)
        self._cols = data.columns
        self.r, self.c = np.shape(self._data)

        self.row_color = row_color
        self.rows_to_color = rows_to_color if rows_to_color is not None else []

    def rowCount(self, parent=None):
        """
        Calculate row count

        :return: number of rows in dataframe
        """
        return self.r

    def columnCount(self, parent=None):
        """
        Calculate column count

        :return: number of columns in dataframe
        """
        return self.c

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """
        Handle data.

        This also colors rows based on index number.

        :param index: current index
        :param role:
        :return: processed data
        """
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data[index.row(),index.column()])
            # background color for rows is set here
            if role == QtCore.Qt.BackgroundColorRole:
                row = index.row()
                col = index.column()
                if row in self.rows_to_color:
                    return QtGui.QColor(self.row_color)
        return None

    def headerData(self, p_int, orientation, role):
        """
        Handle header, display row number and column names.

        :param p_int:
        :param orientation: either rows or columns
        :param role:
        :return: processed data
        """
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._cols[p_int]
            elif orientation == QtCore.Qt.Vertical:
                return p_int
        return None


class SegmentationDialog(QtWidgets.QWidget):
    """
    Create tableview to display event log and segmentation data
    """

    def __init__(self, parent, status_queue):
        QtWidgets.QWidget.__init__(self, parent=None)
        self.status_queue = status_queue

        # set window title
        self.setWindowTitle("Segmentation")

        # create window layout
        vLayout = QtWidgets.QVBoxLayout(self)
        hLayout = QtWidgets.QHBoxLayout()

        # text field to show file path
        self.pathLE = QtWidgets.QLineEdit(self)
        hLayout.addWidget(self.pathLE)

        # load button
        self.loadBtn = QtWidgets.QPushButton("Select event log", self)
        if darkdetect.isDark() and utils.utils.ENABLE_DARK_MODE:
            self.loadBtn.setStyleSheet('QPushButton {background-color: #656565;}')

        # add elements to layout
        hLayout.addWidget(self.loadBtn)
        vLayout.addLayout(hLayout)

        # create table view
        self.tableView = QtWidgets.QTableView(self)
        # select entire row on click
        self.tableView.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        # add table view to GUI
        vLayout.addWidget(self.tableView)

        # button to load event log
        self.loadBtn.clicked.connect(self._loadDataframeInTable)

    def _loadEventLogInDataframe(self):
        """
        Load event log into pandas dataframe

        :return: event log as dataframe
        """

        # custom dialog to select event logs, returns list of paths
        selectedFiles = getFilenameDialog(customDialog=False,
                                          title="Open event log",
                                          multipleItems=False,
                                          filter_format="Event log (*.csv *.xes)")
        event_log_path = selectedFiles[0]
        # event_log_path = "/Users/marco/Downloads/data.csv"  # DEBUG
        self.pathLE.setText(event_log_path)
        filename, extension = os.path.splitext(event_log_path)

        if extension == '.xes':  # convert xes to pandas dataframe
            log = pm4py.read_xes(event_log_path)
            df = pm4py.convert_to_dataframe(log)
            # when importing XES files, the order of columns is lost, so it needs to be set manually
            # columns that should go first in the dataframe
            first_columns = ['case:concept:name', 'time:timestamp', 'category', 'application']
            # all other columns
            remaining_columns = list(set(df.columns) - set(first_columns))
            # reorder columns
            df = df[first_columns + remaining_columns]
        else:  # import CSV into pandas dataframe
            try:
                df = pandas.read_csv(event_log_path).fillna('')
            except pandas.errors.ParserError:  # occurs if csv separator is ';' instead of ','
                df = pandas.read_csv(event_log_path, sep=';').fillna('')
            if 'time:timestamp' in df.columns:
                df = df.dropna(subset=["time:timestamp"]).sort_values(by='time:timestamp')

        return df

    def _loadDataframeInTable(self):
        """
        Display dataframe in tableview with colored rows.
        """

        # Load event log into pandas dataframe
        df = self._loadEventLogInDataframe()

        # calculate rows to color
        # (questi sono valori di prova, qui va la funzione che restituisce gli indici delle righe da colorare)
        rows_to_color = [1, 3, 5]

        # create model for tableview
        # pass optional list of rows to color and optional name of row color
        model = PandasModel(df, rows_to_color=rows_to_color, row_color='LightCoral')

        # set table model
        self.tableView.setModel(model)












