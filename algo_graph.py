#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   algo_graph.py                                        :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/19 12:46:42 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/20 14:28:38 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #


from heapq import heapify, heappop, heappush
from parser_models import Hub, Network


class Graph:
    """Represents a weighted graph and provides pathfinding utilities.

    The graph is stored as an adjacency dict mapping each node to a dict
    of its neighbors and the corresponding edge weights.

    Example:
        graph = {
            "A": {"B": 3, "C": 3},
            "B": {"A": 3, "D": 3.5, "E": 2.8}
        }

    Attributes:
        graph (dict[str, dict[str, float]]): Adjacency list of the graph.
        shortest_paths (list): The K shortest paths found by `yen`,
            populated after calling that method.
    """
    def __init__(
        self,
        graph: dict[str, dict[str, float]] | None = None
    ) -> None:
        """Initializes the Graph.

        Args:
            graph (dict[str, dict[str, float]] | None, optional): A set of
                vertices and the associated distances (or weights) that
                characterize a weighted graph. Defaults to None, in which
                case an empty graph is created.
        """
        self.graph = graph if graph is not None else {}
        self.shortest_paths: list = []

    def add_summit(self, node1: str, node2: str, hub_: list[Hub]) -> None:
        """Adds a directed edge between two nodes, weighted by zone type.

        The edge weight defaults to 1.0, but is adjusted depending on the
        zone type of `node2`'s corresponding hub: 2.0 for a "restricted"
        zone, or 0.99 for a "priority" zone.

        Args:
            node1 (str): First node of the edge (source).
            node2 (str): Second node of the edge (destination).
            hub_ (list[Hub]): List of all hubs, used to look up `node2`'s
                zone type.
        """
        weight = 1.0
        for hub in hub_:
            if node2 == hub.name:
                if hub.zone_type == "restricted":
                    weight = 2.0
                if hub.zone_type == "priority":
                    weight = 0.99
                break
        if node1 not in self.graph:
            self.graph[node1] = {}
        self.graph[node1][node2] = weight

    @staticmethod
    def build_graph(network: Network) -> 'Graph':
        """Builds a complete graph from a network's hubs and connections.

        Connections involving a "blocked" hub (on either end) are skipped.
        Every remaining connection is added as two directed edges (one in
        each direction) so the resulting graph is effectively undirected.

        Args:
            network (Network): Object containing all the data (i.e. all
                hubs and all connections) used to build the graph.

        Returns:
            Graph: A new Graph instance populated with the network's data.
        """
        graph = Graph()
        hubs = list(network.hubs.values())
        for connection in network.connections:
            if (network.hubs[connection.hub1].zone_type == "blocked"
                    or network.hubs[connection.hub2].zone_type == "blocked"):
                continue
            graph.add_summit(connection.hub1, connection.hub2, hubs)
            graph.add_summit(connection.hub2, connection.hub1, hubs)
        return graph

    def dijkstra(
        self,
        start: str,
        end: str,
        ign_summit: set | None = None, ign_seq: set | None = None
    ) -> tuple[float, list[str]]:
        """Computes the shortest path between two nodes.

        Uses Dijkstra's algorithm on the internal adjacency graph, with
        optional support for excluding specific nodes and/or specific
        directed edges (sequences) from consideration.

        Args:
            start (str): Starting node.
            end (str): Destination node.
            ign_summit (set | None, optional): Nodes to ignore entirely.
                Defaults to None (no nodes ignored).
            ign_seq (set | None, optional): Directed edges, as
                (from_node, to_node) tuples, to ignore. Defaults to None
                (no edges ignored).

        Returns:
            tuple[float, list[str]]: The total distance and the ordered
            list of nodes forming the shortest path from `start` to `end`.
            If no path exists (or `start`/`end` is ignored), returns
            (float("inf"), []).
        """
        ign_seq = ign_seq or set()
        ign_summit = ign_summit or set()

        if start in ign_summit or end in ign_summit:
            return float("inf"), []

        distances: dict[str, float] = {start: 0}
        queue: list[tuple[float, str, list[str]]] = [(0, start, [start])]
        heapify(queue)
        visited: set = set()

        while queue:
            dist, current, path = heappop(queue)
            if current in visited:
                continue
            visited.add(current)

            if current == end:
                return dist, path

            for neighbor, neig_dist in self.graph.get(current, {}).items():
                if neighbor in ign_summit:
                    continue
                if (current, neighbor) in ign_seq:
                    continue
                new_distance = dist + neig_dist
                if new_distance < distances.get(neighbor, float("inf")):
                    distances[neighbor] = new_distance
                    heappush(queue, (new_distance, neighbor, path+[neighbor]))
        return float("inf"), []

    def sum_distance_path(self, path: list[str]) -> float:
        """Calculates the total length of a specific path.

        Args:
            path (list[str]): Ordered list of nodes forming the path.

        Returns:
            float: The sum of the edge weights along the path.
        """
        return sum(
            self.graph[path[i]][path[i + 1]]
            for i in range(len(path) - 1)
            )

    def yen(
        self,
        source: str,
        destination: str, k: int
    ) -> list[tuple[float, list[str]]]:
        """Finds the K shortest loopless paths between two nodes.

        This is a direct extension of Dijkstra's algorithm. While Dijkstra
        finds only the shortest (best) path, Yen's algorithm finds the K
        shortest paths (1st, 2nd, 3rd best, etc.) without any of them
        containing loops.

        Args:
            source (str): Starting node.
            destination (str): Destination node.
            k (int): Number of paths to find (if that many exist).

        Returns:
            list[tuple[float, list[str]]]: A list of (distance, path)
            tuples, sorted from shortest to longest, containing up to `k`
            paths. Also stored on `self.shortest_paths`. Returns an empty
            list if no path exists between `source` and `destination`.
        """
        self.shortest_paths = []

        dist, path = self.dijkstra(source, destination)
        if not path:
            return self.shortest_paths
        self.shortest_paths.append((dist, path))

        all_path = []
        for _ in range(1, k):
            prev_path = self.shortest_paths[-1][1]
            for i in range(len(prev_path) - 1):
                alternative_summit = prev_path[i]
                accumulate = prev_path[:i + 1]

                sequence_ignore = set()
                for (_, p) in self.shortest_paths:
                    if len(p) > i and p[:i + 1] == accumulate:
                        sequence_ignore.add((p[i], p[i + 1]))
                ignored_summit = set(accumulate[:-1])

                _, alternative_path = self.dijkstra(alternative_summit,
                                                           destination,
                                                           ignored_summit,
                                                           sequence_ignore)
                if alternative_path:
                    total_path = accumulate[:-1] + alternative_path
                    total_dist = self.sum_distance_path(total_path)
                    alt_path = (total_dist, total_path)
                    if (alt_path not in self.shortest_paths
                       and alt_path not in all_path):
                        all_path.append(alt_path)

            if not all_path:
                break

            all_path.sort(key=lambda x: x[0])
            self.shortest_paths.append(all_path.pop(0))

        return self.shortest_paths
