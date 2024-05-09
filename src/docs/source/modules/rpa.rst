===
RPA
===

The Robotic Process Automation python script is generated based on the low-level most frequent routine, after the user had the opportunity to edit some fields.

.. figure:: ../../../images/5_rpa.png
   :figwidth: 60%
   :align: center

Check and edit event log
========================
Explained in :ref:`Choices dialog`.

Python RPA script
=================

.. autoclass:: modules.RPA.generateRPAScript.RPAScript
   :members:
   :private-members:

UiPath RPA project
==================

.. note::
    The primary methods of this class to work with are:

    * `generateUiPathRPA() <#modules.RPA.uipath.UIPathXAML.generateUiPathRPA>`_ - method called to start UiPath SW Robot generation process
    * `__generateRPA() <#modules.RPA.uipath.UIPathXAML.__generateRPA>`_ - Main method to generate UiPath SW robot
    * `__generateActivities() <#modules.RPA.uipath.UIPathXAML.__generateActivities>`_ - convert an event into a UiPath XML node

.. autoclass:: modules.RPA.uipath.UIPathXAML
   :members:
   :private-members:
