#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   models.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/18 11:36:00 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/17 14:09:48 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from dataclasses import dataclass, field


@dataclass
class Hub:
    """_summary_
    """
    name: str
    x: int
    y: int
    zone_type: str = "normal"
    color: str | None = None
    max_drones: int = 1


@dataclass
class Connection:
    """_summary_
    """
    hub1: str
    hub2: str
    max_capacity: int = 1


@dataclass
class Network:
    """_summary_
    """
    nb_drones: int
    start_hub: Hub | None = None
    end_hub: Hub | None = None
    hubs: dict[str, Hub] = field(default_factory=dict)
    connections: list[Connection] = field(default_factory=list)


@dataclass
class Drone:
    """_summary_
    """
    paths: list[tuple[float, list[str]]]
    current_hub: Hub
    next_hub: Hub
    path_index: int = 0
    position_path: int = 0
