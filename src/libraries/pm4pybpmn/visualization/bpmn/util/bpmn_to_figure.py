import tempfile

import bpmn_python.bpmn_python_consts as consts
import pydotplus

EXCLUSIVE_OPERATOR = ""
PARALLEL_OPERATOR = "+"


def bpmn_diagram_to_figure(bpmn_graph, image_format, bpmn_aggreg_statistics=None):
    """
    Render a BPMN graph into a figure of the given format

    Parameters
    ----------
    bpmn_graph
        BPMN graph to render
    image_format
        Render format
    bpmn_aggreg_statistics
        Statistics to represent on the BPMN diagram

    Returns
    ----------
    file_name
        Path of the file containing the render
    """
    if bpmn_aggreg_statistics is None:
        bpmn_aggreg_statistics = {}

    g = bpmn_graph.diagram_graph
    graph = pydotplus.Dot()
    graph.obj_dict['attributes']['bgcolor'] = 'transparent'
    for node in g.nodes(data=True):
        if node[1].get(consts.Consts.type) == consts.Consts.task:
            if str(node[1]) in bpmn_aggreg_statistics and "label" in bpmn_aggreg_statistics[str(node[1])] and "color" in \
                    bpmn_aggreg_statistics[str(node[1])]:
                node_statistics = bpmn_aggreg_statistics[str(node[1])]
                n = pydotplus.Node(name=node[0], shape="box", style="filled",
                                   label=node_statistics['label'], fillcolor=node_statistics['color'])
            else:
                n = pydotplus.Node(name=node[0], shape="box", style="rounded",
                                   label=node[1].get(consts.Consts.node_name))
        elif node[1].get(consts.Consts.type) == consts.Consts.exclusive_gateway:
            n = pydotplus.Node(name=node[0], shape="diamond", label=EXCLUSIVE_OPERATOR)
        elif node[1].get(consts.Consts.type) == consts.Consts.parallel_gateway:
            n = pydotplus.Node(name=node[0], shape="diamond", label=PARALLEL_OPERATOR)
        else:
            n = pydotplus.Node(name=node[0], label=node[1].get(consts.Consts.node_name))
        graph.add_node(n)
    for edge in g.edges(data=True):
        edge_source = edge[2]['sourceRef']
        edge_target = edge[2]['targetRef']

        if str(edge[2]) in bpmn_aggreg_statistics and "label" in bpmn_aggreg_statistics[str(edge[2])] and "penwidth" in \
                bpmn_aggreg_statistics[str(edge[2])]:
            edge_statistics = bpmn_aggreg_statistics[str(edge[2])]
            e = pydotplus.Edge(src=edge_source, dst=edge_target, label=edge_statistics['label'],
                               penwidth=edge_statistics['penwidth'])
            graph.add_edge(e)
        else:
            e = pydotplus.Edge(src=edge_source, dst=edge_target, label=edge[2].get(consts.Consts.name))
            graph.add_edge(e)
    file_name = tempfile.NamedTemporaryFile(suffix='.' + image_format)
    file_name.close()
    graph.write(file_name.name, format=image_format)
    return file_name
