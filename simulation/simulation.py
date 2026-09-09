#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   simulation.py                                        :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/08 11:28:13 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/09 16:29:00 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #


from dataclasses import dataclass
from math import ceil
from typing import Dict, List, Tuple

from parser.parser import FlyInParser
from parser.models import Network, Hub, Connection
from graph.graph import Graph


@dataclass
class DroneState:
    id: str
    path: List[str]
    pos_index: int = 0
    status: str = "WAITING"


class Simulation:
    def __init__(self, network: Network, graph_or_paths):
        self.network = network

        if isinstance(graph_or_paths, Graph):
            self.graph = graph_or_paths
            self.all_path = None
        else:
            self.all_path = graph_or_paths
            hubs = list(network.hubs.values())
            g = Graph()
            for conn in network.connections:
                g.add_summit(conn.hub1, conn.hub2, hubs)
                g.add_summit(conn.hub2, conn.hub1, hubs)
            self.graph = g

        self.node_reservations: Dict[str, Dict[int, int]] = {}
        self.edge_reservations: Dict[Tuple[str, str], Dict[int, int]] = {}

        self.drones: List[DroneState] = []

    def reserve_node(self, node: str, t: int, capacity: int = 1) -> bool:
        times = self.node_reservations.setdefault(node, {})
        if times.get(t, 0) >= capacity:
            return False
        times[t] = times.get(t, 0) + 1
        return True

    def reserve_edge(self, u: str, v: str, t: int, capacity: int = 1) -> bool:
        key = (u, v)
        times = self.edge_reservations.setdefault(key, {})
        if times.get(t, 0) >= capacity:
            return False
        times[t] = times.get(t, 0) + 1
        return True

    def plan_drone(self, drone_id: str, waypoints: List[str]) -> None:
        full_path: List[str] = []
        for i in range(len(waypoints) - 1):
            _, sub = self.graph.dijkstra(waypoints[i], waypoints[i + 1])
            if not sub:
                raise RuntimeError(f"no path {waypoints[i]}->{waypoints[i+1]}")
            if full_path:
                full_path += sub[1:]
            else:
                full_path += sub

        self.drones.append(DroneState(id=drone_id, path=full_path))

    def run(self, max_steps: int = 100) -> None:
        t = 0
        hub_capacities: Dict[str, int] = {name: hub.max_drones for name, hub in self.network.hubs.items()}
        conn_caps: Dict[Tuple[str, str], int] = {}
        for c in self.network.connections:
            conn_caps[(c.hub1, c.hub2)] = c.max_capacity
            conn_caps[(c.hub2, c.hub1)] = c.max_capacity

        for d in self.drones:
            start = d.path[0]
            self.reserve_node(start, 0, capacity=hub_capacities.get(start, 1))
            d.status = "AT_NODE"

        print("Starting simulation")
        while t < max_steps:
            progressed = False
            for d in self.drones:
                if d.pos_index >= len(d.path) - 1:
                    continue

                cur = d.path[d.pos_index]
                nxt = d.path[d.pos_index + 1]

                edge_weight = self.graph.graph.get(cur, {}).get(nxt, 1.0)
                travel_time = max(1, ceil(edge_weight))

                arrival_t = t + travel_time
                node_cap = hub_capacities.get(nxt, 1)
                can_reserve_node = self.node_reservations.get(nxt, {}).get(arrival_t, 0) < node_cap

                edge_cap = conn_caps.get((cur, nxt), 1)
                can_reserve_edge = all(
                    self.edge_reservations.get((cur, nxt), {}).get(tt, 0) < edge_cap
                    for tt in range(t + 1, arrival_t + 1)
                )

                if can_reserve_node and can_reserve_edge:
                    for tt in range(t + 1, arrival_t + 1):
                        self.reserve_edge(cur, nxt, tt, capacity=edge_cap)
                    self.reserve_node(nxt, arrival_t, capacity=node_cap)
                    d.pos_index += 1
                    progressed = True
                    print(f"{d.id}->{cur} ", end="")
                else:
                    print(f"{d.id}->{cur}", end="\n")
                print()

            if not progressed:
                break
            t += 1

    def run_from_all_path(self, max_steps: int = 100) -> None:
        if not self.all_path:
            raise RuntimeError("no all_path available; construct with list of paths")

        shortest = min(self.all_path, key=lambda x: x[0])[1]

        for i in range(1, self.network.nb_drones + 1):
            self.drones.append(DroneState(id=f"D{i}", path=shortest.copy()))

        self.run_turns(max_turns=max_steps)

    def run_turns(self, max_turns: int = 100) -> None:
        hub_capacities: Dict[str, int] = {name: hub.max_drones for name, hub in self.network.hubs.items()}
        conn_caps: Dict[Tuple[str, str], int] = {}
        for c in self.network.connections:
            conn_caps[(c.hub1, c.hub2)] = c.max_capacity
            conn_caps[(c.hub2, c.hub1)] = c.max_capacity

        for d in self.drones:
            start = d.path[0]
            self.reserve_node(start, 1, capacity=hub_capacities.get(start, 1))
            d.status = "AT_NODE"

        for turn in range(1, max_turns + 1):
            # print(turn)
            for d in self.drones:
                pos = d.path[d.pos_index]
                if pos == "start" or pos == "goal":
                    continue
                print(f"{d.id}->{pos}", end=" ")
            print()
            progressed = False
            for d in self.drones:
                if d.pos_index >= len(d.path) - 1:
                    continue

                cur = d.path[d.pos_index]
                nxt = d.path[d.pos_index + 1]

                edge_weight = self.graph.graph.get(cur, {}).get(nxt, 1.0)
                travel_time = max(1, ceil(edge_weight))

                arrival_turn = turn + travel_time
                node_cap = hub_capacities.get(nxt, 1)
                can_reserve_node = self.node_reservations.get(nxt, {}).get(arrival_turn, 0) < node_cap

                edge_cap = conn_caps.get((cur, nxt), 1)
                can_reserve_edge = all(
                    self.edge_reservations.get((cur, nxt), {}).get(tt, 0) < edge_cap
                    for tt in range(turn + 1, arrival_turn + 1)
                )

                if can_reserve_node and can_reserve_edge and arrival_turn <= max_turns:
                    for tt in range(turn + 1, arrival_turn + 1):
                        self.reserve_edge(cur, nxt, tt, capacity=edge_cap)
                    self.reserve_node(nxt, arrival_turn, capacity=node_cap)
                    d.pos_index += 1
                    progressed = True

            if not progressed:
                exit(0)
