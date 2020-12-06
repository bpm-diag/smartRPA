======================
SmartRPA documentation
======================

.. figure:: ../../images/readme-header.png
   :figwidth: 80%
   :align: center

What is SmartRPA
================

**Robotic Process Automation (RPA)** is a technology which automates mouse and keyboard interactions by means of a software (SW) robot to remove intensive routines. The current generation of RPA tools is driven by predefined rules and manual configurations made by expert users rather than automated techniques.

**SmartRPA** is a cross-platform tool that tackles such issues. It allows to easily record event logs and to automatically generating executable RPA scripts that will drive a SW robots in emulating an observed user behavior (previously recorded in dedicated UI logs) during the enactment of a routine of interest.

Links
=====

* **Source code** is available on `GitHub <https://github.com/bpm-diag/smartRPA/>`_.
* The associated **paper** is available on `Springer <https://doi.org/10.1007/978-3-030-58779-6_8/>`_, and has been presented at the RPA Forum of 18th International Conference on Business Process Management.
* A **screencast** of the tool is available on `Vimeo <https://vimeo.com/marco2012/smartRPA/>`_.


Authors
=======

SmartRPA has been developed at DIAG, *Department of Computer, Control, and Management Engineering* Antonio Ruberti in Sapienza University of Rome by:

* Simone Agostinelli
* Marco Lupia
* Andrea Marrella
* Massimo Mecella

Architecture
============

The architecture of SmartRPA integrates five main SW components.

.. figure:: ../../images/architecture.jpeg
   :figwidth: 60%
   :align: center

Key features include:

* **Action Logger**, log user behaviour, cross-platform, modular, supports wide range of applications;
* **Log Processing**, generates both CSV and XES event log;
* **Event abstraction**, abstracts events to a higher level;
* **Process Discovery**, selects the most suitable routine variant to automate and generates high-level flowchart diagram, thus skipping completely the manual modeling activity;
* **Decision Points**, discover differencies between multiple traces in a process and build a new routine based on user decisions;
* **RPA**, implements and enacts a SW robot emulating a routine reflecting the observed behavior (either the most frequent one or the one based on decision points). Available both as a cross-platform Python script and as a UiPath project.

A list of events supported by the Action Logger is available in `SmartRPA_events.pdf <https://github.com/bpm-diag/smartRPA/blob/master/images/SmartRPA_events.pdf>`_.

`Installation and execution  <https://github.com/bpm-diag/smartRPA/#installation-and-execution>`_
=================================================================================================

`Download  <https://github.com/bpm-diag/smartRPA/releases>`_
============================================================

Contents
========

.. toctree::
   :maxdepth: 2
   :caption: Main

   main

.. toctree::
   :maxdepth: 2
   :caption: Modules

   modules/gui
   modules/action_logger
   modules/log_processing
   modules/event_abstraction
   modules/process_discovery
   modules/rpa

.. toctree::
   :maxdepth: 2
   :caption: Utils

   utils

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
