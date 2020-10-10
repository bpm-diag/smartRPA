# import networkx as nx
# import matplotlib.pyplot as plt
# import matplotlib.image as mpimg
# from io import StringIO
# from IPython.display import SVG
import pydot
from itertools import tee
import pandas
import modules.eventAbstraction


class Flowchart:
    def __init__(self, df: pandas.DataFrame):
        high_level_df, _, _ = modules.eventAbstraction.aggregateData(df, remove_duplicates=True)
        self.process_hl = high_level_df['customClassifier'].to_list()
        self.dot_graph = pydot.Dot(graph_type='digraph')

    def __pairwise(self, iterable):
        "s -> (s0,s1), (s1,s2), (s2, s3), ..."
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)

    def __make_node(self, name, shape=None):
        cur_node = pydot.Node(name)
        if shape is not None:
            cur_node.set_shape(shape)
        self.dot_graph.add_node(cur_node)
        return cur_node

    def __make_link(self, a_node, b_node, label=None, width=1, style='dashed'):
        cur_edge = pydot.Edge(a_node, b_node)
        cur_edge.set_penwidth(width)
        cur_edge.set_style(style)
        if label is not None:
            cur_edge.set_label(label)
        self.dot_graph.add_edge(cur_edge)
        return cur_edge

    def generateFlowchart(self, path: str, name: str = None):
        # Start node
        self.__make_link(self.__make_node('Start'), self.__make_node(self.process_hl[0], 'record'))

        for v, w in self.__pairwise(self.process_hl):
            a = self.__make_node(v, 'record')
            b = self.__make_node(w, 'record')
            self.__make_link(a, b, style='solid')

        # End node
        self.__make_link(self.__make_node(self.process_hl[-1], 'record'), self.__make_node('End'))  # box3d

        if name:
            path = path.replace('BPMN', name)

        self.dot_graph.write(path, format="pdf")
