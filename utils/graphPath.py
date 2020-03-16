import networkx as nx


class HandleGraph:

    def __init__(self, dfg, source, target):
        self.source = source
        self.target = target
        self.graph = self.__createGraph(dfg)

    @staticmethod
    def __createGraph(dfg):
        DG = nx.DiGraph()
        for key, value in dfg.items():
            DG.add_edge(key[0], key[1], weight=value)
        return DG

    def __path_cost(self, path):
        return sum([self.graph[path[i]][path[i + 1]]['weight'] for i in range(len(path) - 1)])

    def __heaviest_path(self, source, target):
        return max(
            (path for path in nx.all_simple_paths(self.graph, source, target)),
            key=lambda path: self.__path_cost(path)
        )

    def frequentPath(self):
        try:
            most_frequent_path = self.__heaviest_path(self.source, self.target)
            return most_frequent_path
        except nx.exception.NodeNotFound as e:
            print(e)

    def printPath(self):
        try:
            most_frequent_path = self.frequentPath()
            print(f"[GRAPH PATH] The most frequent path from '{self.source}' to '{self.target}' is:")
            for i, p in enumerate(most_frequent_path):
                print(f"{i + 1}) {p}")
        except TypeError:
            print(f"Could not find most frequent path in graph.")