from libraries.pm4pybpmn.visualization.bpmn.util.bpmn_to_figure import bpmn_diagram_to_figure
from libraries.pm4pybpmn.visualization.bpmn.util.save_view import save
from libraries.pm4pybpmn.visualization.bpmn.util.save_view import view
from libraries.pm4pybpmn.visualization.bpmn.versions import wo_decoration, frequency, performance, alignments

WO_DECORATION = "wo_decoration"
FREQUENCY_DECORATION = "frequency"
PERFORMANCE_DECORATION = "performance"
FREQUENCY_GREEDY = "frequency_greedy"
PERFORMANCE_GREEDY = "performance_greedy"
ALIGNMENTS = "alignments"

VERSIONS = {WO_DECORATION: wo_decoration.apply, FREQUENCY_DECORATION: frequency.apply,
            PERFORMANCE_DECORATION: performance.apply, FREQUENCY_GREEDY: frequency.apply,
            PERFORMANCE_GREEDY: performance.apply, ALIGNMENTS: alignments.apply}

VERSIONS_PETRI = {WO_DECORATION: wo_decoration.apply_petri, FREQUENCY_DECORATION: frequency.apply_petri,
                  PERFORMANCE_DECORATION: performance.apply_petri,
                  FREQUENCY_GREEDY: frequency.apply_petri_greedy, PERFORMANCE_GREEDY: performance.apply_petri_greedy,
                  ALIGNMENTS: alignments.apply_petri}

VERSIONS_CONVERT = {WO_DECORATION: wo_decoration.apply_through_conv, FREQUENCY_DECORATION: frequency.apply_through_conv,
                    PERFORMANCE_DECORATION: performance.apply_through_conv, ALIGNMENTS: alignments.apply_through_conv}

VERSIONS_EMBEDDING = {WO_DECORATION: wo_decoration.apply_embedding, FREQUENCY_DECORATION: frequency.apply_embedding,
                      PERFORMANCE_DECORATION: performance.apply_embedding, ALIGNMENTS: alignments.apply_embedding}

VERSIONS_CONVERT_GREEDY = {WO_DECORATION: wo_decoration.apply_through_conv_greedy,
                           FREQUENCY_DECORATION: frequency.apply_through_conv_greedy,
                           PERFORMANCE_DECORATION: performance.apply_through_conv_greedy,
                           FREQUENCY_GREEDY: frequency.apply_through_conv_greedy,
                           PERFORMANCE_GREEDY: performance.apply_through_conv_greedy}

VERSIONS_EMBEDDING_GREEDY = {WO_DECORATION: wo_decoration.apply_embedding,
                             FREQUENCY_DECORATION: frequency.apply_embedding_greedy,
                             PERFORMANCE_DECORATION: performance.apply_embedding_greedy,
                             FREQUENCY_GREEDY: frequency.apply_embedding_greedy,
                             PERFORMANCE_GREEDY: performance.apply_embedding_greedy}


def apply(bpmn_graph, bpmn_aggreg_statistics=None, parameters=None, variant="wo_decoration"):
    """
    Factory method to visualize a BPMN graph using the given parameters

    Parameters
    -----------
    bpmn_graph
        BPMN graph object
    bpmn_aggreg_statistics
        Element-wise statistics that should be represented on the BPMN graph
    parameters
        Possible parameters, of the algorithm, including:
            format -> Format of the image to render (pdf, png, svg)
    variant
        Variant of the algorithm to use, possible values:
            wo_decoration, frequency, performance, frequency_greedy, performance_greedy

    Returns
    ----------
    file_name
        Path of the figure in which the rendered BPMN has been saved
    """
    return VERSIONS[variant](bpmn_graph, bpmn_aggreg_statistics=bpmn_aggreg_statistics, parameters=parameters)


def apply_petri(net, initial_marking, final_marking, log=None, aggregated_statistics=None, parameters=None,
                variant="wo_decoration"):
    """
    Visualize a BPMN graph from a Petri net using the given parameters

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
    variant
        Variant of the algorithm to use, possible values:
            wo_decoration, frequency, performance, frequency_greedy, performance_greedy

    Returns
    -----------
    file_name
        Path of the figure in which the rendered BPMN has been saved
    """
    return VERSIONS_PETRI[variant](net, initial_marking, final_marking, log=log,
                                   aggregated_statistics=aggregated_statistics, parameters=parameters)


def apply_through_conv(bpmn_graph, log=None, aggregated_statistics=None, parameters=None, variant="wo_decoration"):
    """
    Factory method to visualize a BPMN graph decorating it through conversion to a Petri net

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
    variant
        Variant of the algorithm to use, possible values:
            wo_decoration, frequency, performance

    Returns
    -----------
    file_name
        Path of the figure in which the rendered BPMN has been saved
    """
    return VERSIONS_CONVERT[variant](bpmn_graph, log=log, aggregated_statistics=aggregated_statistics,
                                     parameters=parameters)


def apply_embedding(bpmn_graph, log=None, aggregated_statistics=None,
                    parameters=None,
                    variant="wo_decoration"):
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
    variant
        Variant of the algorithm to use, possible values:
            wo_decoration, frequency, performance

    Returns
    -----------
    bpmn_graph
        Annotated BPMN graph
    """
    return VERSIONS_EMBEDDING[variant](bpmn_graph, log=log, aggregated_statistics=aggregated_statistics,
                                       parameters=parameters)


def apply_through_conv_greedy(bpmn_graph, dfg, activities_count, log=None, aggregated_statistics=None, parameters=None,
                              variant="wo_decoration"):
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
    variant
        Variant of the algorithm to use, possible values:
            wo_decoration, frequency_greedy, performance_greedy


    Returns
    -------------
    file_name
        Path of the figure in which the rendered BPMN has been saved
    """
    if parameters is None:
        parameters = {}
    return VERSIONS_CONVERT_GREEDY[variant](bpmn_graph, dfg, activities_count, log=log,
                                            aggregated_statistics=aggregated_statistics, parameters=parameters)


def apply_embedding_greedy(bpmn_graph, dfg, activities_count, log=None, aggregated_statistics=None, parameters=None,
                           variant="wo_decoration"):
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
    variant
        Variant of the algorithm to use, possible values:
            wo_decoration, frequency_greedy, performance_greedy

    Returns
    -----------
    bpmn_graph
        Annotated BPMN graph
    """
    if parameters is None:
        parameters = {}
    return VERSIONS_EMBEDDING_GREEDY[variant](bpmn_graph, dfg, activities_count, log=log,
                                              aggregated_statistics=aggregated_statistics, parameters=parameters)


def dummy():
    """
    Dummy method
    """
    bpmn_graph = None
    image_format = None
    bpmn_figure = None
    path = None
    bpmn_diagram_to_figure(bpmn_graph, image_format)
    view(bpmn_figure)
    save(bpmn_figure, path)
