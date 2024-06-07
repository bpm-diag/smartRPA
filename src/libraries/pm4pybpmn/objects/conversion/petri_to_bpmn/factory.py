from libraries.pm4pybpmn.objects.conversion.petri_to_bpmn.versions import classic

CLASSIC = "classic"

VERSIONS = {CLASSIC: classic.apply}


def apply(net, initial_marking, final_marking, parameters=None, variant="classic"):
    """
    Factory method to convert the Petri net to a BPMN graph

    Parameters
    -----------
    net
        Petri net
    initial_marking
        Initial marking of the Petri net
    final_marking
        Final marking of the Petri net
    parameters
        Parameters of the algorithm
    variant
        Variant of the algorithm to use, possible values:
            classic

    Returns
    -----------
    bpmn_graph
        BPMN graph
    elements_correspondence
        Correspondence between meaningful elements of the Petri net and meaningful elements of the BPMN graph
    inv_elements_correspondence
        Correspondence between meaningful elements of the BPMN graph and meaningful elements of the Petri net
    el_corr_keys_map
        Correspondence between string-ed keys of elements_correspondence with the corresponding elements
    """
    return VERSIONS[variant](net, initial_marking, final_marking, parameters=parameters)
