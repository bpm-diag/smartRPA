import pydot
from itertools import tee
import pandas
import modules.eventAbstraction


class Flowchart:
    """
    Generate high level flowchart diagram (BPMN) from a given trace
    """
    def __init__(self, df: pandas.DataFrame):
        """

        :param df: high level pandas dataframe of a trace
        """
        high_level_df, _, _ = modules.eventAbstraction.aggregateData(
            df, remove_duplicates=True)
        self.process_hl = high_level_df['customClassifier'].to_list()
        self.dot_graph = pydot.Dot(graph_type='digraph')

    def __pairwise(self, iterable):
        """
        Generate list of pairs from a given list.
        Used to connect nodes and generate diagram.

        :param iterable: list of values
        :return: list of pairs
        """

        "s -> (s0,s1), (s1,s2), (s2, s3), ..."
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)

    def __make_node(self, name, shape=None):
        """
        Generate pydot node

        :param name: name of the node
        :param shape: shape of the node (default is square)
        :return: pydot node
        """

        cur_node = pydot.Node(name)
        if shape is not None:
            cur_node.set_shape(shape)
        self.dot_graph.add_node(cur_node)
        return cur_node

    def __make_link(self, a_node, b_node, label=None, width=1, style='dashed'):
        """
        Make an edge between two nodes

        :param a_node: first node
        :param b_node: second node
        :param label: label between nodes
        :param width: width of the link
        :param style: link style (dashed or straight)
        :return: edge
        """

        cur_edge = pydot.Edge(a_node, b_node)
        cur_edge.set_penwidth(width)
        cur_edge.set_style(style)
        if label is not None:
            cur_edge.set_label(label)
        self.dot_graph.add_edge(cur_edge)
        return cur_edge

    def generateFlowchart(self, path: str, name: str = None):
        """
        Generate flowchart between all the nodes in a trace

        :param path: where to save diagram
        :param name: name of generated diagram
        """

        # Start node
        self.__make_link(
            self.__make_node('Start'),
            self.__make_node(self.process_hl[0], 'record')
        )

        for v, w in self.__pairwise(self.process_hl):
            a = self.__make_node(v, 'record')
            b = self.__make_node(w, 'record')
            self.__make_link(a, b, style='solid')

        # End node
        self.__make_link(
            self.__make_node(self.process_hl[-1], 'record'),
            self.__make_node('End')
        )  # box3d

        if name:
            path = path.replace('BPMN', name)

        try:
            self.dot_graph.write(path, format="pdf")
        except FileNotFoundError as e:
            print(
                "[FLOWCHART] Could not generate flowchart. Make sure that 'graphviz' is in system path.")
            print(e)
