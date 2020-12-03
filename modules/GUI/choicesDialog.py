import darkdetect
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QDialog, QDialogButtonBox, QFormLayout,
                             QGroupBox, QLabel, QLineEdit, QVBoxLayout, QScrollArea)
import pandas

# remove pandas warning
pandas.options.mode.chained_assignment = None
import sys
import ntpath
from utils import utils
from utils.utils import WINDOWS


class ChoicesDialog(QDialog):
    """
    Choices dialog allows the user to customize editable fields before generating the SW robot.
    """
    def __init__(self, df: pandas.DataFrame):
        """

        :param df: low level dataframe of decided trace or most frequent routine
        """
        
        # flags = Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint
        super(ChoicesDialog, self).__init__()
        self.setWindowTitle("Choices")

        # self.setMaximumWidth(1000)
        # self.setMaximumHeight(600)
        if WINDOWS:
            self.setFixedWidth(1000)
        else:
            self.setFixedWidth(750)

        self.df = df

        # remove empty clipboard items
        for row_index, row in self.df.iterrows():
            e = row['concept:name']
            if (e in ['cut', 'copy', 'paste']) and utils.removeWhitespaces(row['clipboard_content']) == '':
                self.df = self.df.drop(row_index)

        # take selected event names
        mask1 = self.df['concept:name'].isin(
            ['changeField',
             'editCell', 'editCellSheet', 'editRange',
             'created', 'moved', 'Unmount', 'hotkey', 'copy']
        )
        # exclude paste in browser, take only paste in OS, do not consider cut or copy
        mask2 = ((self.df['concept:name'] == 'paste') & (self.df['category'] != 'Browser'))
        self.filtered_df = self.df[mask1 | mask2]

        if not self.filtered_df.empty:

            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
            buttonBox.accepted.connect(self.handleReturn)
            if darkdetect.isDark():
                buttonBox.setStyleSheet('QPushButton {background-color: #656565;}')

            formGroupBox = QGroupBox()
            self.layout = QFormLayout()
            self.addRows()
            formGroupBox.setLayout(self.layout)

            scroll = QScrollArea()
            scroll.setWidget(formGroupBox)
            scroll.setMaximumHeight(600)
            scroll.setMaximumWidth(1000)

            mainLayout = QVBoxLayout()
            mainLayout.addWidget(QLabel("Change input variables before generating RPA script"))
            mainLayout.addWidget(scroll)
            mainLayout.addWidget(buttonBox)

            self.setLayout(mainLayout)

        else:
            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
            buttonBox.accepted.connect(self.accept)
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Most frequent trace does not contain editable fields.\n"
                                    "Press OK to generate RPA script."))
            layout.addWidget(buttonBox)
            self.setLayout(layout)

    def addRows(self):
        """
        Add editable rows to custom dialog, such as typing in a web page, renaming a file or pasting a text.

        For each row there is a label, the description of the field, and a value, the element to be edited
        """
        for row_index, row in self.filtered_df.iterrows():
            e = row["concept:name"]
            url = utils.getHostname(row['browser_url'])
            app = row['application']
            label = ""
            value = ""

            if e == "changeField":
                tags = list({row['tag_type'], row['tag_category'].lower(), row['tag_name']})
                label = f"[{app}] Write in {' '.join(tags)} on {url}:"
                value = row['tag_value'].replace('\n', ', ')
            elif e in ["editCell", "editCellSheet", "editRange"]:
                label = f"[Excel] Edit cell {row['cell_range']} on {row['current_worksheet']} with value:"
                value = row['cell_content']
            elif e in ["moved", "Unmount", "created"]:
                path = row['event_dest_path'] if e == "moved" else row['event_src_path']
                _, extension = ntpath.splitext(path)
                if extension:
                    if e == 'created':
                        label = f"[OS] Create new file:"
                    else:
                        label = f"[OS] Rename file as:"
                else:
                    if e == 'created':
                        label = f"[OS] Create new folder:"
                    else:
                        label = f"[OS] Rename folder as:"
                value = path
            elif e in ["copy", "cut", "paste"]:
                cb = utils.removeWhitespaces(row['clipboard_content'])
                label = f"[{app}] Copy and Paste:"
                value = cb
            elif e == 'hotkey':
                if 'hotkey' in self.df.columns:
                    hotkey = row['hotkey']
                else:
                    hotkey = row['id']
                label = f"[{app if app else 'Operating System'}] Hotkey:"
                value = hotkey

            if label != "" and value != "":
                lineEdit = QLineEdit(value)
                lineEdit.setMinimumWidth(270)
                self.layout.addRow(QLabel(label), lineEdit)
            else:
                # remove rows with empty fields from filtered dataframe so it's equal to the dialog shown
                self.filtered_df = self.filtered_df.drop(row_index)

    def handleReturn(self):
        """
        Called when choices dialog is closed (OK button is pressed)

        Each row of the dataframe in input is updated with the values inserted by the user.
        """

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
            try:
                e = row["concept:name"]
                if e == "changeField":
                    self.df.loc[row_index, 'tag_value'] = new_values[i]
                elif e in ["editCell", "editCellSheet", "editRange"]:
                    self.df.loc[row_index, 'cell_content'] = new_values[i]
                elif e in ["moved", "Unmount", "created"]:
                    path = 'event_dest_path' if e == "moved" else 'event_src_path'
                    self.df.loc[row_index, path] = new_values[i]
                elif e in ["copy", "cut", "paste"]:
                    self.df.loc[row_index, 'clipboard_content'] = new_values[i]
                elif e == "hotkey":
                    col = 'hotkey' if 'hotkey' in self.df.columns else 'id'
                    self.df.loc[row_index, col] = new_values[i]
            except Exception:
                pass

        # self.df.to_csv('/Users/marco/Desktop/temp2.csv', encoding='utf-8-sig', index=False)

    def getDF(self):
        """
        Get edited dataframe

        :return: dataframe of trace with user edits
        """
        # self.df.to_csv('/Users/marco/Desktop/temp.csv', encoding='utf-8-sig', index=False)
        return self.df


# used for testing
def buildOptionDialog(df: pandas.DataFrame):
    app = QApplication(sys.argv)
    dialog = ChoicesDialog(df)
    if dialog.exec_() in [0, 1]:
        return dialog.getDF()
    # sys.exit(0)
