#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   simulation.py                                        :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/11 23:52:26 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/20 16:11:26 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from typing import Optional

from algo_graph import Graph
from parser_models import Network, DroneState
from sys import maxsize


class Simulation:
    """Schedules and simulates drone deliveries over a network.

    Given a network and either a pre-built `Graph` or a set of candidate
    paths (as produced by `Graph.yen`), schedules each drone's departure
    and arrival turns while respecting hub capacity, edge capacity, and
    travel-time constraints (slower through "restricted" zones), then
    exposes the resulting per-turn events.
    """
    def __init__(
        self,
        network: Network,
        graph_or_paths: Graph | list[tuple[float, list[str]]],
    ) -> None:
        """Initializes the simulation for a network.

        Args:
            network (Network): The network to simulate deliveries over.
            graph_or_paths (Graph | list[tuple[float, list[str]]]):
                Either an already-built `Graph`, or a list of candidate
                (distance, path) pairs (e.g. from `Graph.yen`). In the
                latter case, a graph is built internally from the
                network's connections, skipping any connection touching
                a "blocked" hub, and the candidate paths are stored on
                `self.all_path` for use by `run_from_all_path`.

        Raises:
            RuntimeError: If `network` has no `end_hub` defined.
        """
        self.network = network
        if network.end_hub is None:
            raise RuntimeError("network has no end_hub")
        self.end_name = network.end_hub.name
        self.all_path: Optional[list[tuple[float, list[str]]]] = None
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

        self.node_reservations: dict[str, dict[int, int]] = {}
        self.edge_reservations: dict[tuple[str, str], dict[int, int]] = {}
        self.drones: list[DroneState] = []
        self.route_order: list[int] = []
        self.scheduled_routes: list[
            tuple[list[str], list[tuple[str, str, int, int]]]
        ] = []
        self._last_movements: list[tuple[str, str, int, int]] = []

    def _edge_capacity(self, first: str, second: str) -> int:
        """Looks up the maximum simultaneous capacity of a connection.

        Args:
            first (str): Name of one hub of the connection.
            second (str): Name of the other hub of the connection.

        Returns:
            int: The connection's `max_capacity`, checked
            direction-agnostically, or 0 if no such connection exists.
        """
        for connection in self.network.connections:
            if {connection.hub1, connection.hub2} == {first, second}:
                return connection.max_capacity
        return 0

    def _travel_time(self, destination: str) -> int:
        """Returns how many turns it takes to reach a given hub.

        Args:
            destination (str): Name of the destination hub.

        Returns:
            int: 2 turns if `destination` is a "restricted" zone hub,
            1 turn otherwise.
        """
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
        """Checks whether a leg can be scheduled without exceeding capacity.

        Args:
            first (str): Name of the departure hub.
            second (str): Name of the arrival hub.
            departure (int): Turn the leg departs `first`.
            arrival (int): Turn the leg arrives at `second`.

        Returns:
            bool: False if the edge is already at capacity during any
            turn in [departure, arrival), or if `second` is not the end
            hub and is already at its `max_drones` capacity at
            `arrival`. True otherwise.
        """
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
        """Reserves edge capacity for a leg across its travel turns.

        Increments the reservation count on the (first, second) edge for
        every turn in [departure, arrival).

        Args:
            first (str): Name of the departure hub.
            second (str): Name of the arrival hub.
            departure (int): Turn the leg departs `first`.
            arrival (int): Turn the leg arrives at `second`.
        """
        edge_times = self.edge_reservations.setdefault((first, second), {})
        for turn in range(departure, arrival):
            edge_times[turn] = edge_times.get(turn, 0) + 1

    def _reserve_node_occupancy(
        self,
        movements: list[tuple[str, str, int, int]],
        max_turns: int,
    ) -> None:
        """Reserves hub occupancy for each intermediate stop of a route.

        For every movement that does not end at the network's end hub,
        marks the arrival hub as occupied from its arrival turn until
        either the drone's next departure or `max_turns + 1`, whichever
        is later.

        Args:
            movements (list[tuple[str, str, int, int]]): The route's
                movements, each as (from_hub, to_hub, departure,
                arrival).
            max_turns (int): The simulation's maximum allowed turn.
        """
        for index, (_, second, _, arrival) in enumerate(movements):
            if second == self.end_name:
                continue
            next_departure = (
                movements[index + 1][2]
                if index + 1 < len(movements)
                else max_turns + 1
            )
            node_times = self.node_reservations.setdefault(second, {})
            end_turn = max(next_departure, arrival + 1)
            for turn in range(arrival, end_turn):
                node_times[turn] = node_times.get(turn, 0) + 1

    def _schedule_path(
        self,
        path: list[str],
        earliest_start: int,
        max_turns: int,
    ) -> Optional[dict[int, list[str]]]:
        """Attempts to schedule a single drone's full path.

        Tries successive start turns (from `earliest_start` up to
        `max_turns`), and for each, greedily schedules every leg of the
        path as early as capacity allows. On success, reserves the
        chosen edge and node occupancy, records the movements on
        `self._last_movements`, and returns the resulting events.

        Args:
            path (list[str]): Ordered list of hub names to travel
                through.
            earliest_start (int): Earliest turn the drone may depart.
            max_turns (int): Latest turn by which the drone must arrive.

        Returns:
            Optional[dict[int, list[str]]]: A mapping of turn number to
            the list of hub names (or "hub1-hub2" labels for
            two-turn/restricted legs, at their midpoint turn) the drone
            reaches at that turn. Returns None if no start turn within
            the allowed range lets the whole path be scheduled.
        """
        for start in range(earliest_start, max_turns + 1):
            arrival = start
            movements: list[tuple[str, str, int, int]] = []
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
            events: dict[int, list[str]] = {}

            for first, second, departure, target in movements:
                if target - departure == 2:
                    events.setdefault(departure + 1, []).append(
                        f"{first}-{second}"
                    )
                events.setdefault(target, []).append(second)
            return events
        return None

    def run_from_all_path(self, max_steps: int = maxsize) -> dict[int, list[str]]:
        """Schedules every drone and builds the full simulation event log.

        Assigns each drone's route dynamically, one drone at a time: for
        every drone, `_choose_best_path` tests all candidate paths from
        `self.all_path` against the reservations already made by the
        drones scheduled before it, and picks whichever finishes
        earliest. The winning route is then actually reserved on
        `self`, and its path/movements are recorded in
        `self.scheduled_routes` and its state in `self.drones`.

        This greedy, drone-by-drone assignment replaces the previous
        fixed two-path alternation (`_find_best_route_order`): it scales
        as O(nb_drones x route_count) instead of O(route_count^2), and
        each drone can be routed differently based on the congestion
        actually created by earlier drones.

        Args:
            max_steps (int, optional): Maximum number of turns any drone
                may take to complete its route. Defaults to `sys.maxsize`.

        Raises:
            RuntimeError: If `self.all_path` is empty (no candidate
                paths available).
            RuntimeError: If no candidate path can be scheduled for some
                drone within `max_steps`.

        Returns:
            dict[int, list[str]]: A mapping of turn number to the list
            of "{drone_id}-{destination}" event strings occurring at
            that turn, across all scheduled drones.
        """
        if not self.all_path:
            raise RuntimeError("no paths available")
        paths = [path for _, path in self.all_path]

        self.node_reservations.clear()
        self.edge_reservations.clear()
        self.drones.clear()
        self.scheduled_routes.clear()
        self.route_order = []
        events: dict[int, list[str]] = {}

        for number in range(1, self.network.nb_drones + 1):
            choice = self._choose_best_path(paths, max_steps)
            if choice is None:
                raise RuntimeError("unable to schedule all drones")
            index, movements, scheduled = choice

            for first, second, departure, target in movements:
                self._reserve(first, second, departure, target)
            self._reserve_node_occupancy(movements, max_steps)

            self.route_order.append(index)
            self.scheduled_routes.append((paths[index], movements))
            drone_id = f"D{number}"
            self.drones.append(DroneState(drone_id, paths[index]))

            for turn, destinations in scheduled.items():
                events.setdefault(turn, [])
                events[turn].extend(
                    f"{drone_id}-{destination}" for destination in destinations
                )
        return events

    def render_terminal(self, events):
        """Prints the simulation's events to the terminal, turn by turn.

        Args:
            events (dict[int, list[str]]): Mapping of turn number to the
                list of event strings occurring at that turn, as
                returned by `run_from_all_path`.
        """
        for turn in sorted(events):
            print(f"{' '.join(events[turn])}")
        if events:
            print(f"Max turn: {max(events)}\n")

    def _choose_best_path(
        self,
        paths: list[list[str]],
        max_steps: int,
    ) -> Optional[
        tuple[int, list[tuple[str, str, int, int]], dict[int, list[str]]]
    ]:
        """Picks the candidate path that lets one more drone finish earliest.

        Tests every candidate path on a disposable `Simulation` seeded
        with a shallow copy of the current (real) reservations, so the
        actual state is left untouched until a choice is made. Among
        the candidates that can be scheduled at all, keeps the one with
        the lowest finishing turn.

        Args:
            paths (list[list[str]]): All candidate paths (as lists of
                hub names) available to the next drone.
            max_steps (int): Maximum number of turns the drone may take.

        Returns:
            Optional[tuple[int, list[tuple[str, str, int, int]], dict[int, list[str]]]]:
            A (path_index, movements, events) tuple for the best
            feasible candidate, or None if no candidate path can be
            scheduled within `max_steps` given the current reservations.
        """
        best: Optional[
            tuple[int, int, list[tuple[str, str, int, int]], dict[int, list[str]]]
        ] = None

        for index, path in enumerate(paths):
            process = Simulation(self.network, self.graph)
            process.node_reservations = {
                key: dict(value) for key, value in self.node_reservations.items()
            }
            process.edge_reservations = {
                key: dict(value) for key, value in self.edge_reservations.items()
            }

            scheduled = process._schedule_path(path, 0, max_steps)
            if scheduled is None:
                continue

            finish = max(scheduled)
            if best is None or finish < best[0]:
                best = (finish, index, process._last_movements, scheduled)

        if best is None:
            return None
        _, index, movements, scheduled = best
        return index, movements, scheduled
