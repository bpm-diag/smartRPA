========================
Graphical User Interface
========================

GUI
---

The main interface of the tool is designed to be simple and functional, yet powerful at the same time. The user can select which modules to enable by selecting the corresponding checkbox. A menu with different options is available to perform different actions. The interface was created using PyQt5.

.. figure:: ../../../images/gui.png
   :figwidth: 90%
   :align: center

When the app opens the user needs to select the options that should be enabled and press the "Start Logger" button. Then all selected modules are started. The configuration of each module takes place in the :ref:`main` file.

.. note::
    The primary methods of this class to work with are:

    * `onButtonClick() <#modules.GUI.GUI.MainApplication.onButtonClick>`_ - triggered by 'start logger' button
    * `handleProcessMining() <#modules.GUI.GUI.MainApplication.handleProcessMining>`_ - intermediate process event log
    * `choices() <#modules.GUI.GUI.MainApplication.choices>`_ - perform all the analysis on the event log,

.. autoclass:: modules.GUI.GUI.MainApplication
   :members:
   :private-members:

Preferences window
------------------

User preferences are stored in a local preferences file, because they need to remain consistent across different runs. The cross-platform Python package nativeconfig2 was used. It uses native mechanisms such as Windows Registry or NSUserDefaults to store user settings.

.. figure:: ../../../images/preferences.png
   :figwidth: 60%
   :align: center

The first option allows the user to enable or disable Process discovery analysis described in Section 4.6 after the logs has been recorded. This is useful when the tool is used in a distributed environments where multiple people record defined steps that will later be merged together and analysed, as described in Chapter 5.

The second option allows the user to set the number of runs after which the logs are merged XES file is generated. This option is useful when the user wants to perform multiple runs at the same time to analyze different variations. After reaching the specified number of runs, the tool merges all recorded CSV into one log file and converts it to XES, as described in Subsection 4.4.

.. autoclass:: modules.GUI.PreferencesWindow.Preferences
   :members:
   :private-members:

.. autoclass:: utils.config.MyConfig
   :members:
   :private-members:

File dialog
-----------

A native file dialog to select files has been developed using the QFileDialog class available in PyQt5.
It is used to select event logs to merge or to run. It supports both single and multiple selection, and it is possible to specify the file types that can be selected, in this case only CSV log files.
It returns a list of strings representing the path of each file selected.

.. figure:: ../../../images/file_dialog.png
   :figwidth: 70%
   :align: center

.. automodule:: modules.GUI.filenameDialog
   :members:
   :private-members:

Choices dialog
--------------

Once the routine to automatize is selected, the user can customize its editable fields through a custom dialog window. The program automatically recognises which fields are editable, such as typing something in a web page, renaming a file or pasting a text, and dynamically builds the GUI to let the user edit them. After confirmation, the dataframe is updated.

.. figure:: ../../../images/choices_dialog.png
   :figwidth: 70%
   :align: center

This custom dialog has been implemented extending the QDialog class from PyQt5. It receives as input the low-level most frequent routine dataframe previously computed. This dataframe is then filtered to select only the events that needs to be edited by the user.

.. automodule:: modules.GUI.choicesDialog.ChoicesDialog
   :members: addRows, handleReturn
   :private-members: __init__


Decision dialog
---------------

The user can choose which user actions enact by means of a decision dialog, which displays data from the decided dataframe, that is used to group together all the rows of a routine trace belonging to a routine fragment into a single line.

.. figure:: ../../../images/decision_dialog.png
   :figwidth: 80%
   :align: center

.. autoclass:: modules.GUI.decisionDialogWebView.DecisionDialogWebView
   :members:
   :private-members:

.. automodule:: modules.GUI.decisionDialogWebView
   :members: dataframeToHTML
   :private-members:

