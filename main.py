#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   main.py                                              :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/18 11:36:20 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/02 15:30:05 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from parser.errors import ParseError, DotenvError, BlockedZone
from parser.parser import FlyInParser
from parser.dotenv_parser import dot_parse
from graph.graph import Graph
from renderer.render import Lancer
from scheduler.simulate import Drone, Scheduler
import os


def main() -> None:

    try:
        load, find_path = dot_parse()
        path = find_path()
        if path == "":
            print("[WARNING] Dotenv could not find the file '.env'.\n")
            flag_load = load()
            map_env_present = os.getenv("MAP") is not None
            if not map_env_present and flag_load is False:
                print(
                      "[ERROR] Error loading environment variable\n"
                      "Use 'cp .env_example .env'\n"
                      "Or use the environment variable e.g.: MAP=<path>"
                )
                return
        load()
        filename = str(os.getenv("MAP"))
        if filename == "":
            print("[INVALID] The map path must not be empty")
            return

        dict_graph: dict[str, dict[str, float]] = {}
        list_hub = []
        list_path = []
        list_hub_blocked = []
        turn = 0

        parser = FlyInParser(filename)
        graph = Graph(turn, dict_graph)
        network = parser.parse()

        for hub in network.hubs.values():
            if hub.zone_type != "blocked":
                list_hub.append(hub)
            if hub.zone_type == "blocked":
                list_hub_blocked.append(hub.name)

        if not list_hub:
            raise BlockedZone(
                "No available hubs"
                " (all hubs are blocked or none defined)")

        start_hub = list_hub[0]
        end_hub = list_hub[-1]

        if (network.start_hub is not None and network.end_hub is not None
                and network.start_hub.name == start_hub.name
                and network.end_hub.name == end_hub.name):
            start = start_hub.name
            end = end_hub.name
        else:
            raise BlockedZone(
                "The hub 'start_hub/end_hub' zone is defined"
                " as a blocked zone or mismatched")

        for connect in network.connections:

            if not (connect.hub1 in list_hub_blocked):
                graph.add_summit(connect.hub1, connect.hub2, list_hub)

        for key, value_dict in dict_graph.copy().items():
            for value in value_dict:
                if value == end:
                    graph.add_summit(value, key, list_hub)

        list_path = graph.yen(start, end, 20)
        # graph.construct_hub_path(network.hubs)
        if not list_path:
            raise BlockedZone("There is no possible solution. "
                              "you have to look at the type of zone"
                              " or the connection between the hubs")
        # print(f"nr_drones: {network.nb_drones}")
        # print(f"start_hub: {network.start_hub}")
        # print(f"end_hub  : {network.end_hub}")
        # # print(f"Hub:")
        # # for x in network.hubs.values():
        # #     print(f"    {x.name}: {x}")
        # print(f"Path     : {list_path}")
        # print(f"Turn min : {list_path[0][0]}")
        # drone = []
        drones = []
        for i in range(1, network.nb_drones + 1):
            drones.append(Drone(drone_id=f"D{i}", hubs=network.hubs, paths=list_path))

        sched = Scheduler(network.hubs, network.connections, drones)
        # print(list_path )
        sched.run()
        # print(p)
            # p = d.construct_hub_path(network.hubs)
            # print(p)
        # simulation = Lancer(network, list_path)
        # simulation.run()
        # run(simulation)

        # for y in list_path:
        #     print(f"    {y}")

    except DotenvError as e:
        print(f"Dotenv error: {e}")
    except ParseError as e:
        print(f"Parse error: {e}")
    except BlockedZone as e:
        print(f"Zone Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
