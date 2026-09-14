#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   main.py                                              :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/11 23:52:36 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/14 21:46:49 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

import argparse
import os
from typing import Optional

from graph.graph import Graph
from parser.errors import ParseError
from parser.models import Network
from parser.parser import FlyInParser
from simulation.simulation import Simulation


def build_graph(network: Network) -> Graph:
    graph = Graph()
    hubs = list(network.hubs.values())
    for connection in network.connections:
        if (network.hubs[connection.hub1].zone_type == "blocked"
                or network.hubs[connection.hub2].zone_type == "blocked"):
            continue
        graph.add_summit(connection.hub1, connection.hub2, hubs)
        graph.add_summit(connection.hub2, connection.hub1, hubs)
    return graph


def main(argv: Optional[list[str]] = None) -> int:
    argument_parser = argparse.ArgumentParser(description="Run Fly-in.")
    argument_parser.add_argument("map", nargs="?", help="map file path")
    argument_parser.add_argument(
        "--render", action="store_true", help="open the graphical simulation"
    )
    args = argument_parser.parse_args(argv)
    filename = args.map or os.getenv("MAP")
    if not filename:
        argument_parser.error("provide a map path or set MAP")
    try:
        network = FlyInParser(filename).parse()
        if network.start_hub is None or network.end_hub is None:
            raise ParseError("map must define start_hub and end_hub")
        graph = build_graph(network)
        paths = graph.yen(network.start_hub.name, network.end_hub.name, 20)
        if not paths:
            raise ParseError("no valid route from start_hub to end_hub")
        simulation = Simulation(network, paths)
        simulation.run_from_all_path()
        if args.render:
            try:
                from renderer.render import Lancer
            except ModuleNotFoundError as error:
                if error.name != "pygame":
                    raise
                raise RuntimeError(
                    "Pygame is required for --render; "
                    "install project dependencies"
                ) from error

            Lancer(network, simulation.scheduled_routes).run()
    except (OSError, ParseError, RuntimeError) as error:
        print(f"Error: {error}")



if __name__ == "__main__":
    main()
