from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtWidgets import (QApplication, QDialog, QDialogButtonBox, QFormLayout,
                             QGroupBox, QLabel, QLineEdit, QVBoxLayout)
import pandas
import sys

from utils import utils


class ChoicesDialog(QDialog):

    def __init__(self, df: pandas.DataFrame):
        super(ChoicesDialog, self).__init__(flags=Qt.Window |
                                                  Qt.WindowTitleHint |
                                                  Qt.CustomizeWindowHint)

        self.df = df
        self.filtered_df = self.df[self.df['concept:name'].isin(['changeField', 'editCell', 'editCellSheet'])]
        if not self.filtered_df.empty:


            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
            buttonBox.accepted.connect(self.handleReturn)


            formGroupBox = QGroupBox()
            self.layout = QFormLayout()

            for index, row in self.df.iterrows():
                e = row["concept:name"]
                url = utils.getHostname(row['browser_url'])
                if e == "changeField":
                    label = f"[{row['application']}] Write in {row['tag_type']} {row['tag_category'].lower()} on {url}:"
                    self.layout.addRow(QLabel(label), QLineEdit(row['tag_value']))
                elif e in ["editCell", "editCellSheet"]:
                    pass

            formGroupBox.setLayout(self.layout)

            mainLayout = QVBoxLayout()
            mainLayout.addWidget(QLabel("Change input variables before generating RPA script"))
            mainLayout.addWidget(formGroupBox)
            mainLayout.addWidget(buttonBox)
            self.setLayout(mainLayout)

            self.setWindowTitle("Choices")

        else:
            QCoreApplication.quit()

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
            self.df.at[row_index, 'tag_value'] = new_values[i]
            self.df.at[row_index, 'cell_content'] = new_values[i]

    def getDF(self):
        return self.df


def buildOptionDialog(df: pandas.DataFrame):
    app = QApplication(sys.argv)
    dialog = ChoicesDialog(df)
    if dialog.exec_() == 1:
        return dialog.getDF()
    sys.exit(0)
