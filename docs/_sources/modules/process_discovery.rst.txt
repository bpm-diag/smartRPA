=================
Process Discovery
=================

The Process Discovery component is initialised by the GUI when a calculation on a log file has to be performed. It takes as input a list of CSV logs previously recorded and a multiprocessing queue used to communicate with the main process.

Decision points
===============

.. autoclass:: modules.decisionPoints.DecisionPoints
   :members:
   :private-members:

Most frequent routine
=====================

Once a log composed by different traces of execution is captured and analysed, the routine that was repeated most often is selected and passed to RPA tool for script creation.

.. warning::
    This method has been deprecated after the introduction of decision points analysis

.. automodule:: modules.mostFrequentRoutine
   :members:
   :private-members:

Diagrams
========

Different high-level diagrams are generated during the analysis of the log file:

1. Directly-Follows Graphs (DFG) of the entire process model;
2. Business Process Model and Notation (BPMN) of the most frequent routine;
3. Petri Net of the most frequent routine.

.. autoclass:: modules.process_mining.ProcessMining
   :members:
   :private-members:

.. autoclass:: modules.flowchart.Flowchart
   :members:
   :private-members:
