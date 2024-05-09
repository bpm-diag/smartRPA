from pm4py.algo.discovery.dfg import factory as dfg_factory
from pm4py.algo.filtering.log.attributes import attributes_filter
from libraries.pm4pybpmn.objects.conversion.bpmn_to_petri import factory as bpmn_to_petri
from libraries.pm4pybpmn.objects.conversion.petri_to_bpmn import factory as bpmn_converter
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from libraries.pm4pybpmn.visualization.bpmn.util import bpmn_embedding
from libraries.pm4pybpmn.visualization.bpmn.util import convert_performance_map
from libraries.pm4pybpmn.visualization.bpmn.util.bpmn_to_figure import bpmn_diagram_to_figure
from pm4py.visualization.petrinet.util import vis_trans_shortest_paths
from pm4py.visualization.petrinet.versions import token_decoration


def apply(bpmn_graph, parameters=None, bpmn_aggreg_statistics=None):
    """
    Visualize a BPMN graph from a BPMN graph, decorated with frequency, using the given parameters

    Parameters
    -----------
    bpmn_graph
        BPMN graph object
    bpmn_aggreg_statistics
        Element-wise statistics that should be represented on the BPMN graph
    parameters
        Possible parameters, of the algorithm, including:
            format -> Format of the image to render (pdf, png, svg)

    Returns
    ----------
    file_name
        Path of the figure in which the rendered BPMN has been saved
    """
    if parameters is None:
        parameters = {}

    image_format = parameters["format"] if "format" in parameters else "png"

    file_name = bpmn_diagram_to_figure(bpmn_graph, image_format, bpmn_aggreg_statistics=bpmn_aggreg_statistics)
    return file_name


def apply_petri(net, initial_marking, final_marking, log=None, aggregated_statistics=None, parameters=None):
    """
    Visualize a BPMN graph from a Petri net, decorated with frequency, using the given parameters

    Parameters
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    log
        (Optional) log where the replay technique should be applied
    aggregated_statistics
        (Optional) element-wise statistics calculated on the Petri net
    parameters
        Possible parameters of the algorithm, including:
            format -> Format of the image to render (pdf, png, svg)
            aggregationMeasure -> Measure to use to aggregate statistics
            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> Specification of the activity key
            (if not concept:name)
            pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY -> Specification of the timestamp key
            (if not time:timestamp)

    Returns
    -----------
    file_name
        Path of the figure in which the rendered BPMN has been saved
    """

    if parameters is None:
        parameters = {}

    image_format = parameters["format"] if "format" in parameters else "png"

    bpmn_graph, elements_correspondence, inv_el_corr, el_corr_keys_map = bpmn_converter.apply(net,
                                                                                              initial_marking,
                                                                                              final_marking)

    if aggregated_statistics is None and log is not None:
        aggregated_statistics = token_decoration.get_decorations(log, net, initial_marking, final_marking,
                                                                 parameters=parameters, measure="frequency")

    bpmn_aggreg_statistics = None
    if aggregated_statistics is not None:
        bpmn_aggreg_statistics = convert_performance_map.convert_performance_map_to_bpmn(aggregated_statistics,
                                                                                         inv_el_corr)

    file_name = bpmn_diagram_to_figure(bpmn_graph, image_format, bpmn_aggreg_statistics=bpmn_aggreg_statistics)
    return file_name


def apply_through_conv(bpmn_graph, log=None, aggregated_statistics=None, parameters=None):
    """
    Visualize a BPMN graph decorating it through conversion to a Petri net

    Parameters
    -----------
    bpmn_graph
        BPMN graph object
    log
        (Optional) log where the replay technique should be applied
    aggregated_statistics
        (Optional) element-wise statistics calculated on the Petri net
    parameters
        Possible parameters, of the algorithm, including:
            format -> Format of the image to render (pdf, png, svg)

    Returns
    -----------
    file_name
        Path of the figure in which the rendered BPMN has been saved
    """

    if parameters is None:
        parameters = {}

    image_format = parameters["format"] if "format" in parameters else "png"

    net, initial_marking, final_marking, elements_correspondence, inv_elements_correspondence, el_corr_keys_map = \
        bpmn_to_petri.apply(bpmn_graph)

    if aggregated_statistics is None and log is not None:
        aggregated_statistics = token_decoration.get_decorations(log, net, initial_marking, final_marking,
                                                                 parameters=parameters, measure="frequency")

    bpmn_aggreg_statistics = None
    if aggregated_statistics is not None:
        bpmn_aggreg_statistics = convert_performance_map.convert_performance_map_to_bpmn(aggregated_statistics,
                                                                                         inv_elements_correspondence)

    file_name = bpmn_diagram_to_figure(bpmn_graph, image_format, bpmn_aggreg_statistics=bpmn_aggreg_statistics)
    return file_name


def apply_petri_greedy(net, initial_marking, final_marking, log=None, aggregated_statistics=None, parameters=None):
    """
    Visualize a BPMN graph from a Petri net, decorated with frequency, using the given parameters (greedy algorithm)

    Parameters
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    log
        (Optional) log where the replay technique should be applied
    aggregated_statistics
        (Optional) element-wise statistics calculated on the Petri net
    parameters
        Possible parameters of the algorithm, including:
            format -> Format of the image to render (pdf, png, svg)
            aggregationMeasure -> Measure to use to aggregate statistics
            pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> Specification of the activity key
            (if not concept:name)
            pm4py.util.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY -> Specification of the timestamp key
            (if not time:timestamp)

    Returns
    -----------
    file_name
        Path of the figure in which the rendered BPMN has been saved
    """

    if parameters is None:
        parameters = {}

    image_format = parameters["format"] if "format" in parameters else "png"

    bpmn_graph, elements_correspondence, inv_el_corr, el_corr_keys_map = bpmn_converter.apply(net,
                                                                                              initial_marking,
                                                                                              final_marking)

    activity_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else DEFAULT_NAME_KEY

    if aggregated_statistics is None and log is not None:
        dfg = dfg_factory.apply(log, variant="frequency")
        activities_count = attributes_filter.get_attribute_values(log, activity_key)
        spaths = vis_trans_shortest_paths.get_shortest_paths(net)

        aggregated_statistics = vis_trans_shortest_paths.get_decorations_from_dfg_spaths_acticount(net, dfg, spaths,
                                                                                                   activities_count,
                                                                                                   variant="frequency")

    bpmn_aggreg_statistics = None
    if aggregated_statistics is not None:
        bpmn_aggreg_statistics = convert_performance_map.convert_performance_map_to_bpmn(aggregated_statistics,
                                                                                         inv_el_corr)

    file_name = bpmn_diagram_to_figure(bpmn_graph, image_format, bpmn_aggreg_statistics=bpmn_aggreg_statistics)
    return file_name


def apply_embedding(bpmn_graph, log=None, aggregated_statistics=None, parameters=None):
    """
    Embed decoration information inside the BPMN graph

    Parameters
    -----------
    bpmn_graph
        BPMN graph object
    log
        (Optional) log where the replay technique should be applied
    aggregated_statistics
        (Optional) element-wise statistics calculated on the Petri net
    parameters
        Possible parameters, of the algorithm

    Returns
    -----------
    bpmn_graph
        Annotated BPMN graph
    """
    if parameters is None:
        parameters = {}

    net, initial_marking, final_marking, elements_correspondence, inv_elements_correspondence, el_corr_keys_map = \
        bpmn_to_petri.apply(bpmn_graph)

    if aggregated_statistics is None and log is not None:
        aggregated_statistics = token_decoration.get_decorations(log, net, initial_marking, final_marking,
                                                                 parameters=parameters, measure="frequency")

    if aggregated_statistics is not None:
        bpmn_aggreg_statistics = convert_performance_map.convert_performance_map_to_bpmn(aggregated_statistics,
                                                                                         inv_elements_correspondence)
        bpmn_graph = bpmn_embedding.embed_info_into_bpmn(bpmn_graph, bpmn_aggreg_statistics, "frequency")

    return bpmn_graph


def apply_through_conv_greedy(bpmn_graph, dfg, activities_count, log=None, aggregated_statistics=None, parameters=None):
    """
    Decorate BPMN graph through conversion to Petri net, using shortest paths in the Petri net

    Parameters
    -------------
    bpmn_graph
        BPMN graph
    dfg
        Directly-Follows graph
    activities_count
        Count of occurrences of the activities
    log
        Log object
    aggregated_statistics
        Aggregated statistics object
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    file_name
        Path of the figure in which the rendered BPMN has been saved
    """
    if parameters is None:
        parameters = {}

    del log
    del aggregated_statistics

    image_format = parameters["format"] if "format" in parameters else "png"

    net, initial_marking, final_marking, elements_correspondence, inv_elements_correspondence, el_corr_keys_map = \
        bpmn_to_petri.apply(bpmn_graph)

    spaths = vis_trans_shortest_paths.get_shortest_paths(net, enable_extension=True)

    aggregated_statistics = vis_trans_shortest_paths.get_decorations_from_dfg_spaths_acticount(net, dfg, spaths,
                                                                                               activities_count,
                                                                                               variant="frequency")

    bpmn_aggreg_statistics = convert_performance_map.convert_performance_map_to_bpmn(aggregated_statistics,
                                                                                     inv_elements_correspondence)

    file_name = bpmn_diagram_to_figure(bpmn_graph, image_format, bpmn_aggreg_statistics=bpmn_aggreg_statistics)
    return file_name


def apply_embedding_greedy(bpmn_graph, dfg, activities_count, log=None, aggregated_statistics=None, parameters=None):
    """
    Embed decoration information inside the BPMN graph

    Parameters
    -----------
    bpmn_graph
        BPMN graph
    dfg
        Directly-Follows graph
    activities_count
        Count of occurrences of the activities
    log
        Log object
    aggregated_statistics
        Aggregated statistics object
    parameters
        Possible parameters of the algorithm

    Returns
    -----------
    bpmn_graph
        Annotated BPMN graph
    """
    del parameters
    del log
    del aggregated_statistics

    net, initial_marking, final_marking, elements_correspondence, inv_elements_correspondence, el_corr_keys_map = \
        bpmn_to_petri.apply(bpmn_graph)

    spaths = vis_trans_shortest_paths.get_shortest_paths(net, enable_extension=True)

    aggregated_statistics = vis_trans_shortest_paths.get_decorations_from_dfg_spaths_acticount(net, dfg, spaths,
                                                                                               activities_count,
                                                                                               variant="frequency")

    bpmn_aggreg_statistics = convert_performance_map.convert_performance_map_to_bpmn(aggregated_statistics,
                                                                                     inv_elements_correspondence)

    bpmn_graph = bpmn_embedding.embed_info_into_bpmn(bpmn_graph, bpmn_aggreg_statistics, "frequency")

    return bpmn_graph
