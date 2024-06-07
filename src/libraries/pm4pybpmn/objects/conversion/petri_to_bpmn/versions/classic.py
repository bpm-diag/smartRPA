import uuid

import bpmn_python.bpmn_diagram_rep as diagram

from libraries.pm4pybpmn.objects.bpmn.importer import bpmn_diagram_rep as diagram
from libraries.pm4pybpmn.objects.conversion.petri_to_bpmn.util import constants
from pm4py.objects.petri.petrinet import PetriNet


def get_start_trans_petri_given_imarking(initial_marking):
    """
    Deduce the start activities given the initial marking of the Petri net

    Parameters
    ----------
    initial_marking
        Initial marking of the Petri net

    Returns
    ----------
    start_trans
        List of start transitions deduced from the Petri net
    """
    start_trans = []
    start_involved_places = set()
    start_involved_arcs = set()
    start_involved_trans = set()

    for place in initial_marking:
        start_involved_places.add(place)
        for arc in place.out_arcs:
            start_involved_arcs.add(arc)
            trans = arc.target
            start_involved_trans.add(trans)
            if trans.label is not None:
                if trans not in start_trans:
                    start_trans.append(trans)

    if len(start_trans) == 0:
        for place in initial_marking:
            for arc in place.out_arcs:
                trans = arc.target
                for arc2 in trans.out_arcs:
                    place2 = arc2.target
                    start_involved_places.add(place2)
                    start_involved_arcs.add(arc2)
                    for arc3 in place2.out_arcs:
                        start_involved_arcs.add(arc3)
                        trans2 = arc3.target
                        start_involved_trans.add(trans2)
                        if trans2.label is not None:
                            if trans2 not in start_trans:
                                start_trans.append(trans2)

    return start_trans, start_involved_places, start_involved_arcs, start_involved_trans


def get_final_trans_petri_given_fmarking(final_marking):
    """
    Deduce the end activities given the final marking of the Petri net

    Parameters
    -----------
    final_marking
        Final marking of the Petri net

    Returns
    -----------
    final_trans
        List of final transitions deduced from the Petri net
    """
    final_trans = []
    final_involved_places = set()
    final_involved_arcs = set()
    final_involved_trans = set()

    for place in final_marking:
        final_involved_places.add(place)
        for arc in place.in_arcs:
            final_involved_arcs.add(arc)
            trans = arc.source
            final_involved_trans.add(trans)
            if trans.label is not None:
                if trans not in final_trans:
                    final_trans.append(trans)

    if len(final_trans) == 0 or True:
        for place in final_marking:
            for arc in place.in_arcs:
                trans = arc.source
                for arc2 in trans.in_arcs:
                    final_involved_arcs.add(arc2)
                    place2 = arc2.source
                    final_involved_places.add(place2)
                    for arc3 in place2.in_arcs:
                        final_involved_arcs.add(arc3)
                        trans2 = arc3.source
                        final_involved_trans.add(trans2)
                        if trans2.label is not None:
                            if trans not in final_trans:
                                final_trans.append(trans2)

    return final_trans, final_involved_places, final_involved_arcs, final_involved_trans


def get_petri_el_type(petri_el):
    """
    Gets the type (in string) of the current Petri net element

    Parameters
    -----------
    petri_el
        Petri net element

    Returns
    -----------
    type
        Type (string) of the BPMN graph element
    """

    if type(petri_el) is PetriNet.Transition:
        return "transition"
    elif type(petri_el) is PetriNet.Place:
        return "place"
    return "arc"


def get_bpmn_el_type(el):
    """
    Gets the type (in string) of the current BPMN element

    Parameters
    ----------
    el
        BPMN graph element

    Returns
    ----------
    type
        Type (string) of the BPMN graph element
    """
    if 'type' in el:
        return "task"
    elif 'sourceRef' in el and 'targetRef' in el:
        return "arc"
    return "other"


def apply(net, initial_marking, final_marking, parameters=None):
    """
    Convert the Petri net to a BPMN graph

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

    Returns
    -----------
    bpmn_graph
        BPMN graph
    elements_correspondence
        Correspondence between meaningful elements of the Petri net (objects) and meaningful
        elements of the BPMN graph (dicts)
    inv_elements_correspondence
        Correspondence between meaningful elements of the BPMN graph (dicts) and meaningful
        elements of the Petri net (objects)
    el_corr_keys_map
        Correspondence between string-ed keys of elements_correspondence with the corresponding elements
    """
    if parameters is None:
        parameters = {}
    del parameters
    bpmn_transitions_map = {}
    bpmn_graph = diagram.BpmnDiagramGraph()
    elements_correspondence = {}
    bpmn_graph.create_new_diagram_graph(diagram_name="diagram")
    process_id = bpmn_graph.add_process_to_diagram("1")
    [start_id, _] = bpmn_graph.add_start_event_to_diagram(process_id, start_event_name="start",
                                                          node_id=constants.START_EVENT_ID)
    [end_id, _] = bpmn_graph.add_end_event_to_diagram(process_id, end_event_name="end", node_id=constants.END_EVENT_ID)
    start_trans, start_involved_places, start_inv_arcs, start_inv_trans = get_start_trans_petri_given_imarking(
        initial_marking)
    final_trans, final_involved_places, final_inv_arcs, final_inv_trans = get_final_trans_petri_given_fmarking(
        final_marking)

    for trans in net.transitions:
        this_trans_id = str(uuid.uuid4())
        this_trans_id_0 = this_trans_id[0]
        while not this_trans_id_0.isalpha():
            this_trans_id = str(uuid.uuid4())
            this_trans_id_0 = this_trans_id[0]

        if trans.label is not None:
            if trans in start_trans and len(start_trans) == 1:
                [task_id, task] = bpmn_graph.add_task_to_diagram(process_id, task_name=trans.label,
                                                                 node_id=this_trans_id)
            elif trans in final_trans and len(final_trans) == 1:
                [task_id, task] = bpmn_graph.add_task_to_diagram(process_id, task_name=trans.label,
                                                                 node_id=this_trans_id)
            else:
                [task_id, task] = bpmn_graph.add_task_to_diagram(process_id, task_name=trans.label,
                                                                 node_id=this_trans_id)
            bpmn_transitions_map[trans] = task_id
            elements_correspondence[trans] = task

    mapped_trans = {}
    mapped_arcs = {}
    mapped_places = {}

    for place in initial_marking:
        mapped_places[place] = start_id
    for place in final_marking:
        mapped_places[place] = end_id

    for place in net.places:
        if len(place.in_arcs) == 1 and len(place.out_arcs) == 1:
            in_trans = None
            out_trans = None

            in_arc = None
            out_arc = None

            for arc in place.in_arcs:
                in_arc = arc
                in_trans = arc.source
            for arc in place.out_arcs:
                out_arc = arc
                out_trans = arc.target

            if len(in_trans.out_arcs) > 1 and len(out_trans.in_arcs) == 1:
                if in_trans not in mapped_trans:
                    gateway_name_split = in_trans.name
                    gateway_id_split = in_trans.name
                    [gateway_split, _] = bpmn_graph.add_parallel_gateway_to_diagram(process_id,
                                                                                    gateway_name=gateway_name_split,
                                                                                    node_id=gateway_id_split)
                    mapped_trans[in_trans] = gateway_split
            elif len(out_trans.in_arcs) > 1 and len(in_trans.out_arcs) == 1:
                if out_trans not in mapped_trans:
                    gateway_name_join = out_trans.name
                    gateway_id_join = out_trans.name
                    [gateway_join, _] = bpmn_graph.add_parallel_gateway_to_diagram(process_id,
                                                                                   gateway_name=gateway_name_join,
                                                                                   node_id=gateway_id_join)
                    mapped_trans[out_trans] = gateway_join
            elif len(in_trans.out_arcs) == 1 and len(out_trans.in_arcs) == 1:
                # sequential place between two activities, convert it into direct arc :)
                flow = None
                if in_trans.label is not None and out_trans.label is not None:
                    seq_flow_id, flow = bpmn_graph.add_sequence_flow_to_diagram(process_id,
                                                                                bpmn_transitions_map[in_trans],
                                                                                bpmn_transitions_map[out_trans])
                    if in_trans not in mapped_trans:
                        mapped_trans[in_trans] = bpmn_transitions_map[in_trans]
                    if out_trans not in mapped_trans:
                        mapped_trans[out_trans] = bpmn_transitions_map[out_trans]

                if flow is not None:
                    mapped_places[place] = flow
                    mapped_arcs[in_arc] = flow
                    mapped_arcs[out_arc] = flow

                    elements_correspondence[in_arc] = flow
                    elements_correspondence[out_arc] = flow

    # add remaining elements of the Petri net as happen in a Petri net
    for trans in net.transitions:
        if len(trans.in_arcs) == 1 and len(trans.out_arcs) == 1 and trans.label is None and not \
                [arc.source for arc in trans.in_arcs][0] in initial_marking and not \
                [arc.target for arc in trans.out_arcs][
                    0] in final_marking:
            pass
        else:
            if trans not in mapped_trans:
                if trans.label is None:
                    gateway_name = trans.name
                    gateway_id_principal = trans.name
                    if (len(trans.in_arcs) == 1 and len(trans.out_arcs) > 1) or (
                            len(trans.out_arcs) == 1 and len(trans.in_arcs) > 1):
                        [gateway_princ, _] = bpmn_graph.add_parallel_gateway_to_diagram(process_id,
                                                                                        gateway_name=gateway_name,
                                                                                        node_id=gateway_id_principal)
                    else:
                        [gateway_princ, _] = bpmn_graph.add_exclusive_gateway_to_diagram(process_id,
                                                                                         gateway_name=gateway_name,
                                                                                         node_id=gateway_id_principal)
                    mapped_trans[trans] = gateway_princ
                else:
                    mapped_trans[trans] = bpmn_transitions_map[trans]

    for trans in net.transitions:
        if len(trans.in_arcs) == 1 and len(trans.out_arcs) == 1 and trans.label is None and not \
                [arc.source for arc in trans.in_arcs][0] in initial_marking and not \
                [arc.target for arc in trans.out_arcs][0] in final_marking:
            pass
        else:
            if trans in mapped_trans:
                for arc in trans.in_arcs:
                    if arc not in mapped_arcs:
                        place = arc.source

                        if place not in mapped_places and len(place.in_arcs) == 1 and len(place.out_arcs) == 1 and \
                                list(place.in_arcs)[0].source in mapped_trans:
                            in_arc_0 = list(place.in_arcs)[0]
                            in_trans = in_arc_0.source

                            if not mapped_trans[in_trans] == mapped_trans[trans]:
                                seq_flow_id, inplace_flow = bpmn_graph.add_sequence_flow_to_diagram(process_id,
                                                                                                    mapped_trans[
                                                                                                        in_trans],
                                                                                                    mapped_trans[
                                                                                                        trans])
                                mapped_arcs[arc] = inplace_flow
                                elements_correspondence[arc] = inplace_flow
                                elements_correspondence[in_arc_0] = inplace_flow
                            mapped_places[place] = mapped_trans[in_trans]
                        else:
                            if place not in mapped_places:
                                gateway_name_inplace = place.name
                                gateway_id_inplace = place.name
                                [i, _] = bpmn_graph.add_exclusive_gateway_to_diagram(process_id,
                                                                                     gateway_name=gateway_name_inplace,
                                                                                     node_id=gateway_id_inplace)
                                mapped_places[place] = i

                            if not mapped_places[place] == mapped_trans[trans]:
                                seq_flow_id, inplace_flow = bpmn_graph.add_sequence_flow_to_diagram(process_id,
                                                                                                    mapped_places[
                                                                                                        place],
                                                                                                    mapped_trans[
                                                                                                        trans])
                                mapped_arcs[arc] = inplace_flow
                                elements_correspondence[arc] = inplace_flow

                for arc in trans.out_arcs:
                    if arc not in mapped_arcs:
                        place = arc.target

                        if place not in mapped_places and len(place.in_arcs) == 1 and len(place.out_arcs) == 1 and \
                                list(place.out_arcs)[0].target in mapped_trans:
                            out_arc_0 = list(place.out_arcs)[0]
                            out_trans = out_arc_0.target

                            if not mapped_trans[trans] == mapped_trans[out_trans]:
                                seq_flow_id, outp_flow = bpmn_graph.add_sequence_flow_to_diagram(process_id,
                                                                                                 mapped_trans[
                                                                                                     trans],
                                                                                                 mapped_trans[
                                                                                                     out_trans])
                                mapped_arcs[out_arc_0] = outp_flow
                                elements_correspondence[out_arc_0] = outp_flow
                                elements_correspondence[arc] = outp_flow
                                mapped_places[place] = mapped_trans[out_trans]
                        else:
                            if place not in mapped_places:
                                gateway_name_out = place.name
                                gateway_id_outplace = place.name
                                [go, _] = bpmn_graph.add_exclusive_gateway_to_diagram(process_id,
                                                                                      gateway_name=gateway_name_out,
                                                                                      node_id=gateway_id_outplace)
                                mapped_places[place] = go

                            if not mapped_trans[trans] == mapped_places[place]:
                                seq_flow_id, outp_flow = bpmn_graph.add_sequence_flow_to_diagram(process_id,
                                                                                                 mapped_trans[
                                                                                                     trans],
                                                                                                 mapped_places[
                                                                                                     place])
                                mapped_arcs[arc] = outp_flow
                                elements_correspondence[arc] = outp_flow

    for trans in net.transitions:
        if len(trans.in_arcs) == 1 and len(trans.out_arcs) == 1 and trans.label is None and not \
                [arc.source for arc in trans.in_arcs][0] in initial_marking and not \
                [arc.target for arc in trans.out_arcs][
                    0] in final_marking:
            arc_source = [arc for arc in trans.in_arcs][0]
            arc_target = [arc for arc in trans.out_arcs][0]
            place_source = arc_source.source
            place_target = arc_target.target

            if place_source in mapped_places and place_target in mapped_places:
                seq_flow_id, place_flow = bpmn_graph.add_sequence_flow_to_diagram(process_id,
                                                                                  mapped_places[place_source],
                                                                                  mapped_places[place_target])
                mapped_arcs[arc_source] = place_flow
                # elements_correspondence[arc_source] = place_flow
                # elements_correspondence[arc_target] = place_flow

    for arc in net.arcs:
        if not arc in mapped_arcs:
            if type(arc.source) is PetriNet.Place:
                if not arc.source in mapped_places:
                    [gateway_princ, _] = bpmn_graph.add_exclusive_gateway_to_diagram(process_id,
                                                               gateway_name=arc.source.name,
                                                               node_id=arc.source.name)
                    mapped_places[arc.source] = gateway_princ
                    elements_correspondence[arc.source] = gateway_princ
                if not arc.target in mapped_trans:
                    [gateway_princ, _] = bpmn_graph.add_exclusive_gateway_to_diagram(process_id,
                                                               gateway_name=arc.target.name,
                                                               node_id=arc.target.name)
                    mapped_trans[arc.target] = gateway_princ
                    elements_correspondence[arc.target] = gateway_princ
                if not mapped_places[arc.source] == mapped_trans[arc.target]:
                    seq_flow_id, place_flow = bpmn_graph.add_sequence_flow_to_diagram(process_id,
                                                                                      mapped_places[arc.source],
                                                                                      mapped_trans[arc.target])
                    mapped_arcs[arc] = place_flow
                    elements_correspondence[arc] = place_flow
            else:
                if not arc.source in mapped_trans:
                    [gateway_princ, _] = bpmn_graph.add_exclusive_gateway_to_diagram(process_id,
                                                               gateway_name=arc.source.name,
                                                               node_id=arc.source.name)
                    mapped_trans[arc.source] = gateway_princ
                    elements_correspondence[arc.source] = gateway_princ
                if not arc.target in mapped_places:
                    [gateway_princ, _] = bpmn_graph.add_exclusive_gateway_to_diagram(process_id,
                                                               gateway_name=arc.target.name,
                                                               node_id=arc.target.name)
                    mapped_places[arc.target] = gateway_princ
                    elements_correspondence[arc.target] = gateway_princ
                if not mapped_trans[arc.source] == mapped_places[arc.target]:
                    seq_flow_id, place_flow = bpmn_graph.add_sequence_flow_to_diagram(process_id,
                                                                                      mapped_trans[arc.source],
                                                                                      mapped_places[arc.target])
                    mapped_arcs[arc] = place_flow
                    elements_correspondence[arc] = place_flow

    inv_elements_correspondence = {}
    for el in elements_correspondence.keys():
        petri_el_type = get_petri_el_type(el)
        el_type = get_bpmn_el_type(elements_correspondence[el])

        if (petri_el_type == "transition" and el_type == "task") or (petri_el_type == "arc" and el_type == "arc"):
            corresp_el = str(elements_correspondence[el])
            if corresp_el not in inv_elements_correspondence:
                inv_elements_correspondence[corresp_el] = []
            if el not in inv_elements_correspondence[corresp_el]:
                inv_elements_correspondence[corresp_el].append(el)

    el_corr_keys_map = {}
    for el in elements_correspondence:
        el_corr_keys_map[str(el)] = el


    removed = True
    while removed:
        removed = False
        nodes = bpmn_graph.diagram_graph.nodes
        nodes_keys = list(nodes.keys())
        i = 0
        while i < len(nodes_keys):
            node_key = nodes_keys[i]
            node = nodes[nodes_keys[i]]
            if node['type'] != 'startEvent' and node['type'] != 'endEvent' and (len(node['incoming']) == 0 or len(node['outgoing']) == 0):
                bpmn_graph.diagram_graph.remove_node(node_key)
                del nodes_keys[i]
                removed = True
                continue
            i = i + 1

    return bpmn_graph, elements_correspondence, inv_elements_correspondence, el_corr_keys_map
