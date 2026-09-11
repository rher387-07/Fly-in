#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   simulation.py                                        :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/11 23:52:26 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/11 23:52:31 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #


"""Turn-based scheduling for the Fly-in drone network."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from graph.graph import Graph
from parser.models import Network


@dataclass
class DroneState:
    """A drone and the route assigned to it."""

    id: str
    path: List[str]


class Simulation:
    """Schedule all drones while respecting map capacities."""

    def __init__(
        self,
        network: Network,
        graph_or_paths: Graph | List[Tuple[float, List[str]]],
    ) -> None:
        self.network = network
        if network.end_hub is None:
            raise RuntimeError("network has no end_hub")
        self.end_name = network.end_hub.name
        self.all_path: Optional[List[Tuple[float, List[str]]]] = None
        if isinstance(graph_or_paths, Graph):
            self.graph = graph_or_paths
        else:
            self.all_path = graph_or_paths
            self.graph = Graph()
            hubs = list(network.hubs.values())
            for connection in network.connections:
                first_blocked = (
                    network.hubs[connection.hub1].zone_type == "blocked"
                )
                second_blocked = (
                    network.hubs[connection.hub2].zone_type == "blocked"
                )
                if first_blocked or second_blocked:
                    continue
                self.graph.add_summit(connection.hub1, connection.hub2, hubs)
                self.graph.add_summit(connection.hub2, connection.hub1, hubs)

        self.node_reservations: Dict[str, Dict[int, int]] = {}
        self.edge_reservations: Dict[Tuple[str, str], Dict[int, int]] = {}
        self.drones: List[DroneState] = []
        self.route_order: List[int] = []
        self.scheduled_routes: List[
            Tuple[List[str], List[Tuple[str, str, int, int]]]
        ] = []
        self._last_movements: List[Tuple[str, str, int, int]] = []

    def _edge_capacity(self, first: str, second: str) -> int:
        """Return the capacity of an undirected connection."""
        for connection in self.network.connections:
            if {connection.hub1, connection.hub2} == {first, second}:
                return connection.max_capacity
        return 0

    def _travel_time(self, destination: str) -> int:
        """Return the movement duration for a destination zone."""
        if self.network.hubs[destination].zone_type == "restricted":
            return 2
        return 1

    def _can_schedule(
        self,
        first: str,
        second: str,
        departure: int,
        arrival: int,
    ) -> bool:
        """Check edge and destination reservations for one movement."""
        edge_capacity = self._edge_capacity(first, second)
        edge_times = self.edge_reservations.get((first, second), {})
        edge_is_full = any(
            edge_times.get(turn, 0) >= edge_capacity
            for turn in range(departure, arrival)
        )
        if edge_is_full:
            return False
        if second == self.end_name:
            return True
        capacity = self.network.hubs[second].max_drones
        reserved = self.node_reservations.get(second, {}).get(arrival, 0)
        return reserved < capacity

    def _reserve(
        self,
        first: str,
        second: str,
        departure: int,
        arrival: int,
    ) -> None:
        """Reserve a movement and its destination arrival slot."""
        edge_times = self.edge_reservations.setdefault((first, second), {})
        for turn in range(departure, arrival):
            edge_times[turn] = edge_times.get(turn, 0) + 1

    def _reserve_node_occupancy(
        self,
        movements: List[Tuple[str, str, int, int]],
        max_turns: int,
    ) -> None:
        """Reserve hub occupancy until the drone's next departure."""
        for index, (_, second, _, arrival) in enumerate(movements):
            if second == self.end_name:
                continue
            next_departure = (
                movements[index + 1][2]
                if index + 1 < len(movements)
                else max_turns + 1
            )
            node_times = self.node_reservations.setdefault(second, {})
            for turn in range(arrival, next_departure):
                node_times[turn] = node_times.get(turn, 0) + 1

    def _schedule_path(
        self,
        path: List[str],
        earliest_start: int,
        max_turns: int,
    ) -> Optional[Dict[int, List[str]]]:
        """Reserve a path at the first feasible departure time."""
        for start in range(earliest_start, max_turns + 1):
            arrival = start
            movements: List[Tuple[str, str, int, int]] = []
            valid = True
            for first, second in zip(path, path[1:]):
                travel_time = self._travel_time(second)
                departure = arrival
                while departure + travel_time <= max_turns:
                    target = departure + travel_time
                    if self._can_schedule(first, second, departure, target):
                        break
                    departure += 1
                else:
                    valid = False
                    break
                arrival = target
                movements.append((first, second, departure, target))
            if not valid or arrival > max_turns:
                continue
            for first, second, departure, target in movements:
                self._reserve(first, second, departure, target)
            self._reserve_node_occupancy(movements, max_turns)
            self._last_movements = movements
            events: Dict[int, List[str]] = {}
            for first, second, departure, target in movements:
                if target - departure == 2:
                    events.setdefault(departure + 1, []).append(
                        f"{first}-{second}"
                    )
                events.setdefault(target, []).append(second)
            return events
        return None

    def run_from_all_path(self, max_steps: int = 100) -> None:
        """Assign routes, schedule drones, and print the simulation turns."""
        if not self.all_path:
            raise RuntimeError("no paths available")
        paths = [path for _, path in self.all_path]
        route_order = self._find_best_route_order(paths, max_steps)
        self.route_order = route_order
        self.node_reservations.clear()
        self.edge_reservations.clear()
        self.drones.clear()
        self.scheduled_routes.clear()
        events: Dict[int, List[str]] = {}
        for number, chosen in enumerate(route_order, 1):
            scheduled = self._schedule_path(paths[chosen], 1, max_steps)
            if scheduled is None:
                raise RuntimeError("unable to schedule all drones")
            self.scheduled_routes.append(
                (paths[chosen], list(self._last_movements))
            )
            drone_id = f"D{number}"
            self.drones.append(DroneState(drone_id, paths[chosen]))
            for turn, destinations in scheduled.items():
                events.setdefault(turn, [])
                events[turn].extend(
                    f"{drone_id}-{destination}" for destination in destinations
                )
        for turn in sorted(events):
            print(f"{' '.join(events[turn])}")
        if events:
            print(f"Max turn: {max(events) - 1}")

    def _find_best_route_order(
        self,
        paths: List[List[str]],
        max_steps: int,
    ) -> List[int]:
        """Choose a repeated two-route pattern with the earliest finish."""
        best_order = [0] * self.network.nb_drones
        best_finish = max_steps + 1
        route_count = len(paths)
        for first in range(route_count):
            for second in range(route_count):
                order = [
                    first if number % 2 == 0 else second
                    for number in range(self.network.nb_drones)
                ]
                trial = Simulation(self.network, self.all_path or [])
                finish = 0
                feasible = True
                for route in order:
                    scheduled = trial._schedule_path(
                        paths[route], 1, max_steps
                    )
                    if scheduled is None:
                        feasible = False
                        break
                    finish = max(finish, max(scheduled))
                if feasible and finish < best_finish:
                    best_finish = finish
                    best_order = order
        return best_order

    def plan_drone(self, drone_id: str, path: List[str]) -> None:
        """Register a drone with an explicit path for compatibility."""
        self.drones.append(DroneState(drone_id, path))

    def run(self, max_steps: int = 100) -> None:
        """Schedule explicitly registered drones and print their movements."""
        events: Dict[int, List[str]] = {}
        for drone in self.drones:
            scheduled = self._schedule_path(drone.path, 1, max_steps)
            if scheduled is None:
                raise RuntimeError(f"unable to schedule {drone.id}")
            for turn, destinations in scheduled.items():
                events.setdefault(turn, [])
                events[turn].extend(
                    f"{drone.id}-{destination}" for destination in destinations
                )
        for turn in sorted(events):
            print(f"Turn {turn - 1}: {' '.join(events[turn])}")
        if events:
            print(f"Max turn: {max(events) - 1}")
