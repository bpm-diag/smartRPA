from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtWidgets import (QApplication, QDialog, QDialogButtonBox, QFormLayout,
                             QGroupBox, QLabel, QLineEdit, QVBoxLayout)
import pandas
import sys
import ntpath
from utils import utils


class ChoicesDialog(QDialog):
    # df is low level dataframe with all the actions
    def __init__(self, df: pandas.DataFrame):
        super(ChoicesDialog, self).__init__(flags=Qt.Window |
                                                  Qt.WindowTitleHint |
                                                  Qt.CustomizeWindowHint)
        self.setWindowTitle("Choices")

        self.df = df
        self.filtered_df = self.df[self.df['concept:name'].isin(
            ['changeField',
             'editCell', 'editCellSheet', 'editRange',
             'moved', 'Unmount',
             'copy', 'cut', 'paste']
        )]
        if not self.filtered_df.empty:

            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
            buttonBox.accepted.connect(self.handleReturn)

            formGroupBox = QGroupBox()
            self.layout = QFormLayout()
            self.addRows()

            formGroupBox.setLayout(self.layout)

            mainLayout = QVBoxLayout()
            mainLayout.addWidget(QLabel("Change input variables before generating RPA script"))
            mainLayout.addWidget(formGroupBox)
            mainLayout.addWidget(buttonBox)
            self.setLayout(mainLayout)

        else:
            # if filtered dataframe is empty there isn't any row to edit, so I don't show the dialog at all
            QCoreApplication.quit()

    def addRows(self):
        for row_index, row in self.df.iterrows():
            e = row["concept:name"]
            url = utils.getHostname(row['browser_url'])
            app = row['application']

            label = ""
            value = ""

            if e == "changeField":
                label = f"[{app}] Write in {row['tag_type']} {row['tag_category'].lower()} on {url}:"
                value = row['tag_value']
            elif e in ["editCell", "editCellSheet", "editRange"]:
                label = f"[Excel] Edit cell {row['cell_range']} on {row['current_worksheet']} with value:"
                value = row['cell_content']
            elif e in ["moved", 'Unmount']:
                path = row['event_dest_path'] if e == "moved" else row['event_src_path']
                _, extension = ntpath.splitext(path)
                if extension:
                    label = f"[{app}] Rename file as:"
                else:
                    label = f"[{app}] Rename folder as:"
                value = path
            elif e in ["copy", "cut", "paste"]:
                cb = utils.removeWhitespaces(row['clipboard_content'])
                if len(cb) > 0:
                    label = f"[{app}] Copy and Paste:"
                    value = cb

            if label != "" and value != "":
                lineEdit = QLineEdit(value)
                lineEdit.setMinimumWidth(270)
                self.layout.addRow(QLabel(label), lineEdit)

    def handleReturn(self):
        # close dialog
        self.accept()

        # edit original dataframe with new values

        # get list of values inserted in QLineEdit, like ['aspirapolvere', 'tavolo', 'sedie']
        widgets = (self.layout.itemAt(i).widget() for i in range(self.layout.count()))
        new_values = [widget.text() for widget in widgets if isinstance(widget, QLineEdit)]

        # To know which lines I need to change in the dataframe, I loop in a subset of the current dataframe
        # I take only the rows that may have been modified above, like the ones where changeField is, into filtered_df
        # Then I iterate through these rows, taking note also of the current iteration
        # 'i' is the current iteration (like 0,1,2) while row_index is the index of the row that I need to modify
        # (like 0,3,6)
        for i, (row_index, row) in enumerate(self.filtered_df.iterrows()):
            e = row["concept:name"]
            if e == "changeField":
                self.df.loc[row_index, 'tag_value'] = new_values[i]
            elif e in ["editCell", "editCellSheet", "editRange"]:
                self.df.loc[row_index, 'cell_content'] = new_values[i]
            elif e in ["moved", "Unmount"]:
                path = 'event_dest_path' if e == "moved" else 'event_src_path'
                self.df.loc[row_index, path] = new_values[i]
            elif e in ["copy", "cut", "paste"]:
                self.df.loc[row_index, 'clipboard_content'] = new_values[i]

    def getDF(self):
        # self.df.to_csv('/Users/marco/Desktop/temp.csv', encoding='utf-8-sig', index=False)
        return self.df


def buildOptionDialog(df: pandas.DataFrame):
    app = QApplication(sys.argv)
    dialog = ChoicesDialog(df)
    if dialog.exec_() in [0, 1]:
        return dialog.getDF()
    # sys.exit(0)