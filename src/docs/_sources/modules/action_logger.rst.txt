=============
Action logger
=============

The Action Logger can be used to record a wide range of UI actions from multiple SW applications during the enactment of a routine.

.. figure:: ../../../images/1_action_logger.png
   :figwidth: 50%
   :align: center

Operating System
================

OS
--

.. automodule:: modules.events.systemEvents
   :members:
   :private-members:

Clipboard
---------

.. automodule:: modules.events.clipboardEvents
   :members:
   :private-members:

Mouse
-----

.. automodule:: modules.events.mouseEvents
   :members:
   :private-members:

Microsoft Office
================

Microsoft Office events are logged using native COM APIs on windows while Excel on macOS is logged using a custom JavaScript AddIn.

.. note::
    For each office application there are two components in the code:

    * a function, triggered by the action logger and responsible for handling events
    * a class, which is the interface used to communicate with the application's APIs

Excel
-----

.. automodule:: modules.events.officeEvents
   :members: excelEvents, excelEventsMacServer
   :private-members:

.. autoclass:: modules.events.officeEvents.ExcelEvents
   :members:
   :private-members:

Word
----

.. automodule:: modules.events.officeEvents
   :members: wordEvents
   :private-members:

.. autoclass:: modules.events.officeEvents.WordEvents
   :members:
   :private-members:

PowerPoint
----------

.. automodule:: modules.events.officeEvents
   :members: powerpointEvents
   :private-members:

.. autoclass:: modules.events.officeEvents.PowerpointEvents
   :members:
   :private-members:

Outlook
-------

.. automodule:: modules.events.officeEvents
   :members: outlookEvents
   :private-members:

.. autoclass:: modules.events.officeEvents.OutlookEvents
   :members:
   :private-members:

Browser
=======

.. note::
    Browser events are handled in the browser extension written in JavaScript.

    In particular:

    * Browser application events (e.g. newTab, zoomTab, resizeWindow, ...) are handled in ``extensions/browserLogger/background_script.js``
    * Web page events (e.g. click, type, submit, ...) are handled in ``extensions/browserLogger/content_script.js``

Logging Server
==============

The logging server was built using Flask.
The server is launched when the user presses the Start Logger button in the GUI.

The selected browsers that needs to be enabled and the log file path are passed as parameters. At launch, the program checks if port 4444 is free on the system: in this case it starts listening for incoming requests.

The default route (/) is used to receive JSON payloads by every module containing data about an event and write them on the CSV file. This payload contains different fields depending on the type of recorded event. When the program is started, the CSV log file is created and the header is written.

.. automodule:: modules.consumerServer
   :members:
   :private-members:
