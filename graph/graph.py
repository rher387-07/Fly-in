#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   graph.py                                             :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/19 12:46:42 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/11 21:59:33 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""
graph = {
   "A": {"B": 3, "C": 3},
   "B": {"A": 3, "D": 3.5, "E": 2.8},
   "C": {"A": 3, "E": 2.8, "F": 3.5},
   "D": {"B": 3.5, "E": 3.1, "G": 10},
   "E": {"B": 2.8, "C": 2.8, "D": 3.1, "G": 7},
   "F": {"G": 2.5, "C": 3.5},
   "G": {"F": 2.5, "E": 7, "D": 10},
}
"""
# from .graph
from heapq import heappop, heappush
from parser.models import Hub
# from parser.errors import BlockedZone
# from ..parser.utils import VALID_ZONE_TYPES


class Graph:
    def __init__(
        self,
        turn: float = 0.0, graph: dict[str, dict[str, float]] | None = None
    ) -> None:
        self.graph = graph if graph is not None else {}
        self.turn = turn
        self.shortest_paths: list = []

    def add_summit(self, node1: str, node2: str, hub_: list[Hub]) -> None:
        # determine edge weight from node1's hub zone type without
        # mutating shared state (self.turn)
        """Add a directed edge weighted by the destination zone."""
        weight = 1.0
        for hub in hub_:
            if node2 == hub.name:
                if hub.zone_type == "restricted":
                    weight = 2.0
                break
        # tmp_node1 = node1
        # print(tmp_node1, node1)
        if node1 not in self.graph:
            self.graph[node1] = {}
        self.graph[node1][node2] = weight

    def dijkstra(
        self,
        start: str,
        end: str,
        ign_summit: set | None = None, ign_seq: set | None = None
    ) -> tuple[float, list[str]]:
        # distances = {node: float('inf') for node in self.graph}
        ign_seq = ign_seq or set()
        ign_summit = ign_summit or set()

        if start in ign_summit or end in ign_summit:
            return float("inf"), []

        distances: dict[str, float] = {start: 0}
        queue: list[tuple[float, str, list[str]]] = [(0, start, [start])]
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
        # res = sum(self.graph[path[i]][path[i + 1]] for i
        # in range(len(path) - 1))
        return sum(
            self.graph[path[i]][path[i + 1]]
            for i in range(len(path) - 1)
            )

        # for i in range(len(path) - 1):
        #     return sum(self.graph[path[i]][path[i + 1]])

    # def yen(self, start, end, path_len):
    #     shortest_paths = []
    #     dist, path = self.dijkstra(start, end)
    #     if not path:
    #         return shortest_paths

    #     shortest_paths.append((dist, path))
    #     print(shortest_paths)

    #     possible_paths = []
    #     for _ in range(1, path_len):
    #         prev_path = shortest_paths[-1][1]
    #         # print(prev_path)
    #         for i in range(len(prev_path) - 1):
    #             alternative = prev_path[i]
    #             accumulate_path = prev_path[:i + 1]
    #             # print(accumulate_path)

    #             ign_seq = set()
    #             for (_, path_) in shortest_paths:
    #                 if len(path_) > i and path_[:i + 1] == accumulate_path:
    #                     ign_seq.add((path_[i], path_[i + 1]))
    #             ign_summit = set(accumulate_path[:-1])

    #             alternative_dist, alternative_path = self.dijkstra(alternativ
    # e, end, ign_summit, ign_seq)

    #             if alternative_path:
    #                 total_path = accumulate_path[:-1] + alternative_path
    #                 print(total_path)
    #                 total_dist = self.sum_distance_path(total_path)
    #                 possible_path = (total_dist, total_path)
    #                 if possible_path not in shortest_paths and possible_p
    # ath not in possible_paths:
    #                     possible_paths.append(possible_path)

    #             if not possible_paths:
    #                 break

    #             possible_paths.sort(key=lambda x: x[0])
    #             # print(possible_paths)
    #             shortest_paths.append(possible_paths.pop(0))
    def yen(
        self,
        source: str,
        destination: str, k: int
    ) -> list[tuple[float, list[str]]]:
        self.shortest_paths = []

        dist, path = self.dijkstra(source, destination)
        if not path:
            return self.shortest_paths
        self.shortest_paths.append((dist, path))

        all_path = []
        # print(self.shortest_paths)
        for _ in range(1, k):
            prev_path = self.shortest_paths[-1][1]
            # print(len(prev_path))
            for i in range(len(prev_path) - 1):
                alternative_summit = prev_path[i]
                accumulate = prev_path[:i + 1]
                # print(accumulate)

                sequence_ignore = set()
                for (_, p) in self.shortest_paths:
                    if len(p) > i and p[:i + 1] == accumulate:
                        sequence_ignore.add((p[i], p[i + 1]))
                ignored_summit = set(accumulate[:-1])

                alt_dist, alternative_path = self.dijkstra(alternative_summit,
                                                           destination,
                                                           ignored_summit,
                                                           sequence_ignore)
                if alternative_path:
                    total_path = accumulate[:-1] + alternative_path
                    # print(total_path)
                    total_dist = self.sum_distance_path(total_path)
                    alt_path = (total_dist, total_path)
                    if (alt_path not in self.shortest_paths
                       and alt_path not in all_path):
                        all_path.append(alt_path)

            if not all_path:
                break

            all_path.sort(key=lambda x: x[0])
            self.shortest_paths.append(all_path.pop(0))

        # print(type(self.shortest_paths))
        return self.shortest_paths
