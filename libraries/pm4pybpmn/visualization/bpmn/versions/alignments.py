from libraries.pm4pybpmn.objects.conversion.bpmn_to_petri import factory as bpmn_to_petri
from libraries.pm4pybpmn.objects.conversion.petri_to_bpmn import factory as bpmn_converter
from libraries.pm4pybpmn.visualization.bpmn.util import bpmn_embedding
from libraries.pm4pybpmn.visualization.bpmn.util import convert_performance_map
from libraries.pm4pybpmn.visualization.bpmn.util.bpmn_to_figure import bpmn_diagram_to_figure
from pm4py.visualization.petrinet.util import alignments_decoration


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
        aggregated_statistics = alignments_decoration.get_alignments_decoration(net, initial_marking, final_marking,
                                                                                log=log)

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
        aggregated_statistics = alignments_decoration.get_alignments_decoration(net, initial_marking, final_marking,
                                                                                log=log)

    bpmn_aggreg_statistics = None
    if aggregated_statistics is not None:
        bpmn_aggreg_statistics = convert_performance_map.convert_performance_map_to_bpmn(aggregated_statistics,
                                                                                         inv_elements_correspondence)

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
        aggregated_statistics = alignments_decoration.get_alignments_decoration(net, initial_marking, final_marking,
                                                                                log=log)

    if aggregated_statistics is not None:
        bpmn_aggreg_statistics = convert_performance_map.convert_performance_map_to_bpmn(aggregated_statistics,
                                                                                         inv_elements_correspondence)
        bpmn_graph = bpmn_embedding.embed_info_into_bpmn(bpmn_graph, bpmn_aggreg_statistics, "conformance")

    return bpmn_graph
