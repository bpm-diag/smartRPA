import networkx as nx


class HandleGraph:

    def __init__(self, dfg, source, target):
        self.source = source
        self.target = target
        self.graph = self._createGraph(dfg)

    @staticmethod
    def _createGraph(dfg):
        DG = nx.DiGraph()
        for key, weight in dfg.items():
            # key is like ('event_type-row_index', 'changeField-2')
            node1 = key[0].split('-')[0]
            row_index1 = int(key[0].split('-')[1])
            node2 = key[1].split('-')[0]
            row_index2 = int(key[1].split('-')[1])

            DG.add_node(node1)
            DG.add_node(node2)

            try:
                DG.nodes[node1]['row_index'].add(row_index1)
            except KeyError:
                DG.nodes[node1]['row_index'] = {row_index1}

            try:
                DG.nodes[node2]['row_index'].add(row_index2)
            except KeyError:
                DG.nodes[node2]['row_index'] = {row_index2}

            # if edge between nodes already exist, increment weight (frequency) by one
            # else set weight to -1
            # use negative weight to find maximum cost path later
            try:
                w = DG[node1][node2]['weight'] + 1
            except KeyError:
                w = 1

            if node1 != node2:
                DG.add_edge(node1, node2, weight=w)

        return DG

    def _path_cost(self, path):
        return sum([self.graph[path[i]][path[i + 1]]['weight'] for i in range(len(path) - 1)])

    def _heaviest_path(self, source, target):
        return max(
            (path for path in nx.all_simple_paths(self.graph, source, target)),
            key=lambda path: self._path_cost(path)
        )

    def frequentPath(self):
        try:
            #     most_frequent_path = nx.bellman_ford_path(self.graph, self.source, self.target)
            most_frequent_path = self._heaviest_path(self.source, self.target)
            return most_frequent_path
        except (nx.exception.NodeNotFound, nx.exception.NetworkXUnbounded) as e:
            print(e)

    def printPath(self):
        try:
            most_frequent_path = self.frequentPath()
            print(f"[GRAPH PATH] The most frequent path from '{self.source}' to '{self.target}' is:")
            for i, p in enumerate(most_frequent_path):
                row_index = self.graph.nodes[p]['row_index']
                print(f"{i + 1}) {p}, row_index={row_index}")
        except TypeError:
            print(f"Could not find most frequent path in graph.")
