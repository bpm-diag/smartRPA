import itertools
import uuid

from pm4py.objects.petri import utils
from pm4py.objects.petri.petrinet import PetriNet, Marking
from pm4py.objects.petri.utils import remove_transition, remove_place, add_arc_from_to


def reduce1(net):
    """
    Reduction rule (1) to simplify the Petri net

    Parameters
    ------------
    net
        Petri net

    Returns
    ------------
    net
        Simplified Petri net
    """
    something_changed = True
    while something_changed:
        something_changed = False
        transitions = list(net.transitions)
        for trans in transitions:
            source_places = [arc.source for arc in trans.in_arcs]
            target_places = [arc.target for arc in trans.out_arcs]
            target_transes = [arc.target for place in target_places for arc in place.out_arcs]
            if len(source_places) == 1 and len(target_places) == 1 and len(target_transes) == 1:
                source_place = source_places[0]
                target_place = target_places[0]
                target_trans = target_transes[0]
                #target_places2 = [arc.target for arc in target_trans.out_arcs]
                if len(target_place.in_arcs) == 1 and len(target_trans.in_arcs) == 1 and len(
                        target_trans.out_arcs) == 1:
                    if trans.label is None:
                        net = remove_transition(net, trans)
                        net = remove_place(net, target_place)
                        add_arc_from_to(source_place, target_trans, net)
                        something_changed = True
                        continue
    return net


def reduce(net):
    """
    Reduction rule to simplify the Petri net

    Parameters
    -------------
    net
        Petri net

    Returns
    -------------
    net
        Simplified Petri net
    """
    return reduce1(net)


def remove_unconnected_places(net, sources, targets):
    """
    Remove unconnected places from the Petri net

    Parameters
    -----------
    net
        Petri net

    Returns
    -----------
    net
        Petri net
    """
    places = set(net.places)
    for place in places:
        if not place in sources and not place in targets:
            if (len(place.in_arcs) == 0) or (len(place.out_arcs) == 0):
                #print("unconnected place: " + place.name)
                remove_place(net, place)
    return net


def findsubsets(s, n):
    """
    Find subsets of size n of a set s

    Parameters
    ------------
    s
        Set
    n
        Size of the subsets that we wish to consider

    Returns
    ------------
    ps
        Set of subsets
    """
    return list(itertools.combinations(s, n))


def get_initial_marking(net, max_no_comb=4):
    """
    Get the initial marking from a Petri net
    (observing which nodes are without input connection,
    if several nodes exist, then a source place is created artificially)

    Parameters
    -------------
    net
        Petri net

    Returns
    -------------
    net
        Petri net
    initial_marking
        Initial marking of the Petri net
    """
    places = set(net.places)

    places_wo_input = []
    for place in places:
        if len(place.in_arcs) == 0:
            places_wo_input.append(place)
    places_wo_input = list(places_wo_input)

    initial_marking = Marking()

    if len(places_wo_input) > 1:
        source = PetriNet.Place('petri_source')
        net.places.add(source)
        for i in range(len(places_wo_input)):
            htrans = get_transition("itrans_" + str(i), None)
            net.transitions.add(htrans)
            utils.add_arc_from_to(source, htrans, net)
            utils.add_arc_from_to(htrans, places_wo_input[i], net)
        initial_marking[source] = 1
    elif len(places_wo_input) == 1:
        places_wo_input = list(places_wo_input)
        initial_marking[places_wo_input[0]] = 1
    return net, initial_marking


def get_final_marking(net, max_no_comb=4):
    """
    Get the final marking from a Petri net
    (observing which nodes are without output connection,
    if several nodes exist, then a sink place is created artificially)

    Parameters
    -------------
    net
        Petri net

    Returns
    -------------
    net
        Petri net
    final_marking
        Final marking of the Petri net
    """
    places = set(net.places)
    places_wo_output = []
    for place in places:
        if len(place.out_arcs) == 0:
            places_wo_output.append(place)
    places_wo_output = list(places_wo_output)

    final_marking = Marking()
    if len(places_wo_output) > 1:
        sink = PetriNet.Place('petri_sink')
        net.places.add(sink)
        for i in range(len(places_wo_output)):
            htrans = get_transition("ftrans_" + str(i), None)
            net.transitions.add(htrans)
            utils.add_arc_from_to(htrans, sink, net)
            utils.add_arc_from_to(places_wo_output[i], htrans, net)
        final_marking[sink] = 1
    elif len(places_wo_output) == 1:
        places_wo_output = list(places_wo_output)
        final_marking[places_wo_output[0]] = 1

    return net, final_marking


def get_transition(name, label):
    if label is None or len(label) == 0:
        return PetriNet.Transition(name, None)
    return PetriNet.Transition(name, label)


def apply(bpmn_graph, parameters=None):
    """
    Apply conversion from a BPMN graph to a Petri net
    along with an initial and final marking

    Parameters
    -----------
    bpmn_graph
        BPMN graph
    parameters
        Parameters of the algorithm

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking of the Petri net
    final_marking
        Final marking of the Petri net
    elements_correspondence
        Correspondence between meaningful elements of the Petri net (objects) and meaningful elements of the
        BPMN graph (dicts)
    inv_elements_correspondence
        Correspondence between meaningful elements of the BPMN graph (dicts) and meaningful elements of the
        Petri net (objects)
    el_corr_keys_map
        Correspondence between string-ed keys of elements_correspondence with the corresponding elements
    """
    if parameters is None:
        parameters = {}
    enable_reduction = parameters["enable_reduction"] if "enable_reduction" in parameters else False

    del parameters
    net = PetriNet("converted_net")
    nodes = bpmn_graph.get_nodes()
    corresponding_in_nodes = {}
    corresponding_out_nodes = {}
    elements_correspondence = {}
    inv_elements_correspondence = {}
    el_corr_keys_map = {}
    start_event_subprocess = {}
    end_event_subprocess = {}
    sources = []
    targets = []
    # adds nodes
    for node in nodes:
        node_id = node[1]['id'] if 'id' in node[1] else node[0]
        node_name = node[1]['node_name'].replace("\r", " ").replace("\n", " ").strip() if 'node_name' in node[
            1] else None
        node_type = node[1]['type'].lower() if 'type' in node[1] else ""
        node_process = node[1]['process'] if 'process' in node[1] else None

        if not "type" in node[1]:
            # some problem with the importing of inclusive gateways
            node_type = 'inclusivegateway'

        trans = None
        if "task" in node_type:
            trans = get_transition(node_id, node_name)
            net.transitions.add(trans)
            elements_correspondence[trans] = node[1]
            if not str(node[1]) in inv_elements_correspondence:
                inv_elements_correspondence[str(node[1])] = []
            inv_elements_correspondence[str(node[1])].append(trans)
            input_place = PetriNet.Place('it_' + node_id)
            net.places.add(input_place)
            output_place = PetriNet.Place('ot_' + node_id)
            net.places.add(output_place)
            corresponding_in_nodes[node_id] = [input_place]
            corresponding_out_nodes[node_id] = [output_place]
            utils.add_arc_from_to(input_place, trans, net)
            utils.add_arc_from_to(trans, output_place, net)
        elif "gateway" in node_type:
            if "parallelgateway" in node_type:
                place = PetriNet.Place('pp_' + node_id)
                net.places.add(place)
                corresponding_in_nodes[node_id] = []
                corresponding_out_nodes[node_id] = []
                htrans = get_transition(str(uuid.uuid4()), None)
                net.transitions.add(htrans)
                utils.add_arc_from_to(htrans, place, net)
                for edge in node[1]['incoming']:
                    str(edge)
                    hplace = PetriNet.Place(str(uuid.uuid4()))
                    net.places.add(hplace)
                    utils.add_arc_from_to(hplace, htrans, net)
                    corresponding_in_nodes[node_id].append(hplace)
                htrans = get_transition(str(uuid.uuid4()), None)
                net.transitions.add(htrans)
                utils.add_arc_from_to(place, htrans, net)
                for edge in node[1]['outgoing']:
                    str(edge)
                    hplace = PetriNet.Place(str(uuid.uuid4()))
                    net.places.add(hplace)
                    utils.add_arc_from_to(htrans, hplace, net)
                    corresponding_out_nodes[node_id].append(hplace)
            elif "inclusivegateway" in node_type:
                input_place = PetriNet.Place('i_' + node_id)
                net.places.add(input_place)
                corresponding_in_nodes[node_id] = []
                added_places_input = []
                for edge in node[1]['incoming']:
                    str(edge)
                    hplace = PetriNet.Place(str(uuid.uuid4()))
                    net.places.add(hplace)
                    added_places_input.append(hplace)
                    corresponding_in_nodes[node_id].append(hplace)
                for i in range(1, len(added_places_input)+1):
                    subsets = findsubsets(set(added_places_input), i)
                    for subset in subsets:
                        htrans = get_transition(str(uuid.uuid4()), None)
                        net.transitions.add(htrans)
                        utils.add_arc_from_to(htrans, input_place, net)
                        for place in subset:
                            utils.add_arc_from_to(place, htrans, net)
                corresponding_out_nodes[node_id] = []
                added_places_output = []
                for edge in node[1]['outgoing']:
                    str(edge)
                    hplace = PetriNet.Place(str(uuid.uuid4()))
                    net.places.add(hplace)
                    added_places_output.append(hplace)
                    corresponding_out_nodes[node_id].append(hplace)
                for i in range(1, len(added_places_output)+1):
                    subsets = findsubsets(set(added_places_output), i)
                    for subset in subsets:
                        htrans = get_transition(str(uuid.uuid4()), None)
                        net.transitions.add(htrans)
                        utils.add_arc_from_to(input_place, htrans, net)
                        for place in subset:
                            utils.add_arc_from_to(htrans, place, net)
            else:
                input_place = PetriNet.Place('i_' + node_id)
                net.places.add(input_place)
                output_place = PetriNet.Place('o_' + node_id)
                net.places.add(output_place)
                trans = get_transition(node_id, None)
                net.transitions.add(trans)
                utils.add_arc_from_to(input_place, trans, net)
                utils.add_arc_from_to(trans, output_place, net)
                corresponding_in_nodes[node_id] = [input_place] * len(node[1]['incoming'])
                corresponding_out_nodes[node_id] = [output_place] * len(node[1]['outgoing'])
        elif node_type == "startevent":
            source_place_source = PetriNet.Place("sourceplacesource_"+str(node_id))
            net.places.add(source_place_source)
            sources.append(source_place_source)
            corresponding_in_nodes[node_id] = [source_place_source]
            if node_process not in corresponding_in_nodes:
                corresponding_in_nodes[node_process] = []
            corresponding_in_nodes[node_process].append(source_place_source)
            start_event_subprocess[node_process] = source_place_source
            if not node_name.lower().startswith("start"):
                trans = get_transition("stt_" + node_id, node_name)
                net.transitions.add(trans)
                source_place_target = PetriNet.Place("stp_" + node_id)
                net.places.add(source_place_target)
                utils.add_arc_from_to(source_place_source, trans, net)
                utils.add_arc_from_to(trans, source_place_target, net)
                corresponding_out_nodes[node_id] = [source_place_target]
            else:
                corresponding_out_nodes[node_id] = [source_place_source]
        elif node_type == "endevent":
            sink_place_target = PetriNet.Place("sinkplacetarget_"+str(node_id))
            net.places.add(sink_place_target)
            targets.append(sink_place_target)
            corresponding_out_nodes[node_id] = [sink_place_target]
            if node_process not in corresponding_out_nodes:
                corresponding_out_nodes[node_process] = []
            corresponding_out_nodes[node_process].append(sink_place_target)
            end_event_subprocess[node_process] = sink_place_target
            if not node_name.lower().startswith("end"):
                trans = get_transition("ett_" + node_id, node_name)
                net.transitions.add(trans)
                sink_place_source = PetriNet.Place("etp_" + node_id)
                net.places.add(sink_place_source)
                utils.add_arc_from_to(sink_place_source, trans, net)
                utils.add_arc_from_to(trans, sink_place_target, net)
                corresponding_in_nodes[node_id] = [sink_place_source]
            else:
                corresponding_in_nodes[node_id] = [sink_place_target]
        elif "event" in node_type:
            input_place = PetriNet.Place('i_' + node_id)
            net.places.add(input_place)
            output_place = PetriNet.Place('o_' + node_id)
            net.places.add(output_place)
            if not node_id == node_name:
                trans = get_transition(node_id, node_name)
            else:
                trans = get_transition(node_id, None)
            net.transitions.add(trans)
            corresponding_in_nodes[node_id] = [input_place]
            corresponding_out_nodes[node_id] = [output_place]
            utils.add_arc_from_to(input_place, trans, net)
            utils.add_arc_from_to(trans, output_place, net)

    flows = bpmn_graph.get_flows()
    for flow in flows:
        flow_id = flow[2]['id']
        source_ref = flow[2]['sourceRef']
        target_ref = flow[2]['targetRef']
        if source_ref in corresponding_out_nodes and target_ref in corresponding_in_nodes and corresponding_out_nodes[
            source_ref] and corresponding_in_nodes[target_ref]:
            trans = get_transition(flow_id, None)
            net.transitions.add(trans)
            source_arc = utils.add_arc_from_to(corresponding_out_nodes[source_ref][0], trans, net)
            target_arc = utils.add_arc_from_to(trans, corresponding_in_nodes[target_ref][0], net)
            if len(corresponding_out_nodes[source_ref]) > 1:
                del corresponding_out_nodes[source_ref][0]
            if len(corresponding_in_nodes[target_ref]) > 1:
                del corresponding_in_nodes[target_ref][0]
            elements_correspondence[target_arc] = flow
            if not str(flow) in inv_elements_correspondence:
                inv_elements_correspondence[str(flow[2])] = []
            inv_elements_correspondence[str(flow[2])].append(target_arc)
            inv_elements_correspondence[str(flow[2])].append(source_arc)

    net = remove_unconnected_places(net, sources, targets)

    for el in elements_correspondence:
        el_corr_keys_map[str(el)] = el

    if enable_reduction:
        net = reduce(net)
        #net, initial_marking = remove_places_im_that_go_to_fm_through_hidden(net, initial_marking, final_marking)

    net, initial_marking = get_initial_marking(net)
    net, final_marking = get_final_marking(net)

    return net, initial_marking, final_marking, elements_correspondence, inv_elements_correspondence, el_corr_keys_map
