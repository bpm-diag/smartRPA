=================
Event abstraction
=================

The Event Abstraction component is used to convert the low-level dataframe with detailed information about each event that has occurred into a high-level one to be exploited for diagnostic and analysis purposes by expert RPA analysts.

In particular, the high-level event log can be used to derive the flowchart representing the abstract workflow underlying the routine execution.
This is done by filtering out irrelevant events, grouping similar ones together (i.e.: copy/paste actions are combined into one) and returning a descriptive string for each recorded event.

.. figure:: ../../../images/3_event_abstraction.png
   :figwidth: 60%
   :align: center

.. automodule:: modules.eventAbstraction
   :members:
   :private-members:
