#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   simulate.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/02 10:39:52 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/02 15:36:56 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from parser.models import Hub, Connection
from enum import Enum
from typing import Any
from collections import defaultdict

class State(Enum):
    move = "MOVING"
    wait = "WAITING"
    transit = "TRANSIT"
    arrived = "ARRIVED"


class Drone:
    def __init__(self, drone_id, hubs: list[Hub], paths):
        self.id: str = drone_id
        self.hubs = hubs
        self.paths: list = paths
        # self.select_path: int = 0
        self.pos_path: int = 0
        self.current_hub: Hub
        self.state: State

        self.path_hubs: list[Hub] | None = None
        self.path_idx: int = 0
        self.next_hub: Hub | None = None
        self.wait_ticks: int = 0

    def __str__(self):
        # path = self.paths[self.select_path][1]
        # min_turn = self.paths[self.select_path][0]
        # pos = path[self.pos_path]
        return f"id: {self.id} - {self.current_hub}"


    def _construct_hub_path(self, hubs: dict[str, Hub], pos: int = 0):
        hub_path = set()
        list_path = []
        # pos = self.select_path
        paths = self.paths[pos][1]
        def convert_set():
            for path in paths:
                for name, hub in hubs.items():
                    if name == path:
                        hub_path.add(hub)
            return hub_path

        def convert_list():
            for path in paths:
                for hub in convert_set():
                    if hub.name == path:
                        list_path.append(hub)
            return list_path

        return convert_list()

    def init_path(self, hubs: dict[str, Hub], pos: int = 0):
        self.path_hubs = self._construct_hub_path(hubs, pos)
        self.path_idx = 0
        if self.path_hubs:
            self.current_hub = self.path_hubs[0]
        return self.path_hubs

    def _construct_connection(self, paths: list[Hub], connections: list[Connection]):
        conn_set = []
        # def _construct_connect():
        #     for conn in connections:
        #         if cur == conn.hub1 and next == conn.hub2:
        #             conn_set.add(conn_set)

        def _construct_curr_next():
            for i, hub in enumerate(paths):
                for next_hub in paths[i + 1:]:
                    for conn in connections:
                        if hub.name == conn.hub1 and next_hub.name == conn.hub2:
                            conn_set.append(conn)
            return conn_set
        return _construct_curr_next()

                # if
                # print(hub.name, "->", next_hub.name)




    def simulate(self, hubs: dict[str, Hub], connections: list[Connection]):
        paths: list[Hub] = self._construct_hub_path(hubs)
        connects = self._construct_connection(paths, connections)
        self.current_hub = paths[0] if paths else None
        # for hub in path:
        #     print(hub.max_drones)
        # for c in conn:
        #     print(conn)
        # for x in paths[1:]:
        #     max_d = x.max_drones
        #     if max_d >= 1:
        #         self.current_hub = x
        #         max_d -= 1
        #     print(max_d)


class Scheduler:
    def __init__(self, hubs: dict[str, Hub], connections: list[Connection], drones: list[Drone]):
        self.hubs = hubs
        self.connections = connections
        self.drones = drones

        self.hub_occupancy: dict[str, int] = defaultdict(int)
        self.conn_usage: dict[tuple[str, str], int] = defaultdict(int)

    def _conn_key(self, a: str, b: str) -> tuple[str, str]:
        return (a, b) if (a, b) in {(c.hub1, c.hub2) for c in self.connections} else (b, a)

    def _find_connection(self, a: str, b: str) -> Connection | None:
        for c in self.connections:
            if (c.hub1 == a and c.hub2 == b) or (c.hub1 == b and c.hub2 == a):
                return c
        return None

    def initialize(self):
        for d in self.drones:
            d.init_path(self.hubs, 0)
            if d.current_hub:
                self.hub_occupancy[d.current_hub.name] += 1
                d.state = State.wait

    def simulation(self) -> None:
        self.conn_usage.clear()

        for d in self.drones:
            if not d.path_hubs:
                continue

            if d.path_idx >= len(d.path_hubs) - 1:
                d.state = State.arrived
                continue

            cur = d.path_hubs[d.path_idx]
            nxt = d.path_hubs[d.path_idx + 1]

            if d.state in (State.wait, State.move):
                is_final_hop = (d.path_idx + 1) == (len(d.path_hubs) - 1)
                if self.hub_occupancy[nxt.name] < nxt.max_drones or is_final_hop:
                    conn = self._find_connection(cur.name, nxt.name)
                    # print(self.conn_usage)
                    if conn is None or self.conn_usage[(cur.name, nxt.name)] < conn.max_capacity:
                        self.conn_usage[(cur.name, nxt.name)] += 1
                        self.hub_occupancy[cur.name] = max(0, self.hub_occupancy[cur.name] - 1)
                        d.state = State.transit
                        d.next_hub = nxt
                        print(self.hub_occupancy)
                # else:
                #     d.state = State.wait

            elif d.state == State.transit:
                # print(d)
                if d.next_hub:
                    self.hub_occupancy[d.next_hub.name] += 1
                    d.path_idx += 1
                    d.current_hub = d.next_hub
                    d.next_hub = None
                    if d.path_idx >= len(d.path_hubs) - 1:
                        d.state = State.arrived
                    else:
                        d.state = State.wait

    def run(self):
        self.initialize()
        last_line: str | None = None
        while True:
            self.simulation()
            if not all(d.state == State.wait for d in self.drones):
                # line = " ".join(
                #     f"{d.id}-{d.current_hub.name if d.current_hub else 'None'}"
                #     for d in self.drones
                # )
                # if line != last_line:
                #     print(line)
                #     last_line = line
                ...
            if all(d.state == State.arrived for d in self.drones):
                break
