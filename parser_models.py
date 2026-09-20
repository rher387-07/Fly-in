#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   parser_models.py                                     :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/18 11:36:00 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/20 15:31:34 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from dataclasses import dataclass, field


@dataclass
class Hub:
    """Represents a hub in the drone network.

    Attributes:
        name: The unique name identifying the hub.
        x: X spatial coordinate.
        y: Y spatial coordinate.
        zone_type: The zone type. Defaults to "normal".
        color: Color associated with the hub (optional).
        max_drones: Maximum number of drones that can be stationed
            simultaneously. Defaults to 1.
    """
    name: str
    x: int
    y: int
    zone_type: str = "normal"
    color: str | None = None
    max_drones: int = 1

@dataclass
class Connection:
    """Represents a bidirectional or unidirectional link between two hubs.

    Attributes:
        hub1: The name of the first hub in the connection.
        hub2: The name of the second hub in the connection.
        max_capacity: The maximum number of drones that can use this link
            simultaneously. Defaults to 1.
    """
    hub1: str
    hub2: str
    max_capacity: int = 1


@dataclass
class Network:
    """Manages the entire network topology, including hubs, links, and the number of drones.

    Attributes:
        nb_drones: Total number of drones.
        start_hub: The main starting hub.
        end_hub: The destination hub.
        hubs: Dictionary mapping hub names to their Hub objects.
        connections: List of all connections.
    """
    nb_drones: int
    start_hub: Hub | None = None
    end_hub: Hub | None = None
    hubs: dict[str, Hub] = field(default_factory=dict)
    connections: list[Connection] = field(default_factory=list)


@dataclass
class Drone:
    """Represents a drone in transit.

    Attributes:
        paths: List of possible paths.
        current_hub: The hub where the drone is currently located.
        next_hub: The next hub the drone is heading towards.
        path_index: The index of the path currently selected from the
            `paths` list. Defaults to 0.
        position_path: The drone's current position or stage along the
            path being followed. Defaults to 0.
    """
    paths: list[tuple[float, list[str]]]
    current_hub: Hub
    next_hub: Hub
    path_index: int = 0
    position_path: int = 0

@dataclass
class DroneState:
    """Tracks a single drone's assigned identifier and route.

    Attributes:
        id: The drone's display identifier (e.g. "D1").
        path: Ordered list of hub names the drone travels through.
    """
    id: str
    path: list[str]
