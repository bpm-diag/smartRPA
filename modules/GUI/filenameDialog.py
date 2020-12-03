from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QFileDialog, QDialog
from utils.utils import DESKTOP


def getFilenameDialog(customDialog=True,
                      title="Open",
                      hiddenItems=False,
                      multipleItems=False,
                      isFolder=False,
                      forOpen=True,
                      directory='',
                      filter_format=''):

    """
    Build custom dialog to select multiple files

    :param customDialog: if False, use native system dialog, otherwise use custom dialog
    :param title: dialog title
    :param hiddenItems: display hidden items
    :param multipleItems: allow selection of multiple items
    :param isFolder: allow selection of folders
    :param forOpen: select files for opening or saving
    :param directory: start directory
    :param filter_format: filter to select only certain file types (for example *.csv)
    :return: path of selected file (list of paths if multiple files are selected)
    """

    options = QFileDialog.Options()
    if customDialog:
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.DontUseCustomDirectoryIcons

    dialog = QFileDialog()
    dialog.setOptions(options)
    dialog.setWindowTitle(title)

    if hiddenItems:
        dialog.setFilter(dialog.filter() | QDir.Hidden)

    # Files or folders
    if isFolder:
        dialog.setFileMode(QFileDialog.DirectoryOnly)
    elif multipleItems:
        dialog.setFileMode(QFileDialog.ExistingFiles)
    else:
        dialog.setFileMode(QFileDialog.AnyFile)

    # Opening or saving
    if forOpen:
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
    else:
        dialog.setAcceptMode(QFileDialog.AcceptSave)

    # Set format
    if filter_format != '' and isFolder is False:  # ["Text files (*.txt)", "Images (*.png *.jpg)"]
        # dialog.setDefaultSuffix(filter_format)
        dialog.setNameFilters([filter_format])

    # starting directory
    if directory != '':
        dialog.setDirectory(str(directory))
    else:
        dialog.setDirectory(DESKTOP)

    if dialog.exec_() == QDialog.Accepted:
        path = dialog.selectedFiles()  # returns a list
        return path
    else:
        return []
