=============
Action logger
=============

The Action Logger can be used to record a wide range of UI actions from multiple SW applications during the enactment of a routine.

.. figure:: ../../../images/1_action_logger.png
   :figwidth: 50%
   :align: center

Operating System
================

.. automodule:: modules.events.systemEvents
   :members:
   :private-members:

.. automodule:: modules.events.clipboardEvents
   :members:
   :private-members:

.. automodule:: modules.events.mouseEvents
   :members:
   :private-members:

.. note::
    Mouse events are deprecated, not in use.

Microsoft Office
================

.. automodule:: modules.events.officeEvents
   :members:
   :private-members:

Browser
=======

.. note::
    Browser events are handled in the browser extension written in JavaScript.
    It is available under ``extensions/browserLogger``

Logging Server
==============

The logging server was built using Flask.
The server is launched when the user presses the Start Logger button in the GUI.

The selected browsers that needs to be enabled and the log file path are passed as parameters. At launch, the program checks if port 4444 is free on the system: in this case it starts listening for incoming requests.

The default route (/) is used to receive JSON payloads by every module containing data about an event and write them on the CSV file. This payload contains different fields depending on the type of recorded event. When the program is started, the CSV log file is created and the header is written.

.. automodule:: modules.consumerServer
   :members:
   :private-members:
