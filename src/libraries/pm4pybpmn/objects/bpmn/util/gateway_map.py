def get_gateway_map(bpmn_graph, consider_all_elements_to_be_task=False, use_node_id=False, relax_condition_one_entry=True):
    """
    Gets the gateway map out of a BPMN diagram

    Parameters
    ------------
    bpmn_graph
        BPMN graph
    consider_all_elements_to_be_task
        Boolean value that sets all the elements to be tasks
    use_node_id
        Use the node ID for storing elements in the gateway map
    relax_condition_one_entry
        Relax condition on the single entry of the gateway

    Returns
    -----------
    gateway_map
        Map whose:
        - key is the gateway ID
        - value is a dictionary containing:
            - type of the gateway
            - task that is source of the gateway
            - decision rules that are added
    edges_map
        Map of edge ID to edge object
    """
    gateway_map = {}
    edges_map = {}

    wanted_ret_el = "id" if use_node_id else "node_name"

    dg = bpmn_graph.diagram_graph
    for e in dg.edges:
        edge = dg.edges[e]
        edges_map[edge['id']] = edge
    for n in dg.nodes:
        node = dg.nodes[n]
        node_type = node["type"]
        if node_type == "exclusiveGateway" or node_type == "eventBasedGateway":
            node_incoming = []
            node_outgoing = []
            for x in node["incoming"]:
                if x in edges_map and edges_map[x]["sourceRef"] in dg.nodes:
                    node_incoming.append(dg.nodes[edges_map[x]["sourceRef"]])
            for x in node["outgoing"]:
                if x in edges_map and edges_map[x]["targetRef"] in dg.nodes:
                    node_outgoing.append(dg.nodes[edges_map[x]["targetRef"]])
            if consider_all_elements_to_be_task:
                incoming_tasks = [x for x in node_incoming]
                task_nodes = [x for x in node_outgoing]
            else:
                incoming_tasks = [x for x in node_incoming if "task" in x["type"].lower()]
                task_nodes = [x for x in node_outgoing if "task" in x["type"].lower()]
            if (len(incoming_tasks) == 1 or relax_condition_one_entry) and len(node_outgoing) > 1:
                gateway_nodes = [x for x in node_outgoing if "gateway" in x["type"].lower()]
                other_nodes = [x for x in node_outgoing if x not in task_nodes and x not in gateway_nodes]
                if consider_all_elements_to_be_task or (len(other_nodes) == 0 and task_nodes):
                    if gateway_nodes and len(task_nodes) == 1:
                        if len(incoming_tasks) > 0 and wanted_ret_el in incoming_tasks[0]:
                            gateway_map[n] = {"type": "gateway", "source": incoming_tasks[0][wanted_ret_el], "edges": {}}
                            for task in task_nodes:
                                gateway_map[n]["edges"][task[wanted_ret_el]] = {"edge": task["incoming"][0], "rules": []}
                    elif len(task_nodes) > 1:
                        if len(incoming_tasks) > 0 and wanted_ret_el in incoming_tasks[0]:
                            gateway_map[n] = {"type": "onlytasks", "source": incoming_tasks[0][wanted_ret_el], "edges": {}}
                            for task in task_nodes:
                                gateway_map[n]["edges"][task[wanted_ret_el]] = {"edge": task["incoming"][0], "rules": []}

    return gateway_map, edges_map
