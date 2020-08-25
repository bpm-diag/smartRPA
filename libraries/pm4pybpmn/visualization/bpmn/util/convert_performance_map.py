def convert_performance_map_to_bpmn(aggregated_statistics, inv_elements_correspondence):
    """
    Convert performance map to BPMN

    Parameters
    ------------
    aggregated_statistics
        Aggregated statistics calculated on elements of the Petri net
    inv_elements_correspondence:
        Correspondence between elements of the BPMN graph and elements of the Petri net

    Returns
    ------------
    bpmn_aggreg_statistics
        Aggregated statistics on elements of the BPMN graph
    """
    bpmn_aggreg_statistics = {}

    for el in inv_elements_correspondence:
        for petri_el in inv_elements_correspondence[el]:
            if petri_el in aggregated_statistics:
                bpmn_aggreg_statistics[el] = aggregated_statistics[petri_el]
                break

    return bpmn_aggreg_statistics
