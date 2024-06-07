from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.objects.log.util import xes
from pm4py.util import constants
import difflib


def get_log_match_with_model(log, bpmn_graph, parameters=None):
    """
    Get log match with model

    Parameters
    ------------
    log
        Trace log
    bpmn_graph
        BPMN graph
    parameters
        Possible parameters of the algorithm

    Returns
    ------------
    model_to_log
        Correspondence between model activities and log activities
    log_to_model
        Correspondence between log activities and model activities
    """
    if parameters is None:
        parameters = {}

    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY

    model_to_log = {}
    log_to_model = {}

    log_activities = list(attributes_filter.get_attribute_values(log, activity_key).keys())
    nodes = bpmn_graph.diagram_graph.nodes
    bpmn_activities = list([nodes[n]["node_name"] for n in nodes if "task" in nodes[n]["type"].lower()])

    for act in bpmn_activities:
        close_matches = difflib.get_close_matches(act, log_activities)
        if close_matches and close_matches[0] not in log_to_model:
            model_to_log[act] = close_matches[0]
            log_to_model[close_matches[0]] = act

    return model_to_log, log_to_model
