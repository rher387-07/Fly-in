#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   main.py                                              :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/18 11:36:20 by hery-rak            #+#    #+#            #
#   Updated: 2026/08/21 14:07:23 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from parser.errors import ParseError, DotenvError, BlockedZone
from parser.parser import FlyInParser
from parser.dotenv_parser import dot_parse
from graph.graph import Graph
import os


def main() -> None:

    try:
        load, find_path = dot_parse()
        path = find_path()
        if path == "":
            print("[WARNING] Dotenv could not find the file '.env'.\n")
            flag_load = load()
            map = os.getenv("MAP") is not None
            if map is False and flag_load is False:
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

        dict_graph = {}
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
        start_hub = list_hub[0]
        end_hub = list_hub[-1]
        if network.start_hub is start_hub and network.end_hub is end_hub:
            start = start_hub.name
            end = end_hub.name
        else:
            raise BlockedZone("The hub 'start_hub/end_hub' zone is defined as a blocked zone")

        for connect in network.connections:

            if not(connect.hub1 in list_hub_blocked):
                graph.add_summit(connect.hub1, connect.hub2, list_hub)


        for key, value_dict in dict_graph.copy().items():
            for value in value_dict:
                if value == end:
                    graph.add_summit(value, key, list_hub)

        list_path = graph.yen(start, end, 20)
        if not list_path:
            raise BlockedZone("There is no possible solution. "
                              "you have to look at the type of zone or the connection between the hubs")
        print(f"nr_drones: {network.nb_drones}")
        print(f"start_hub: {network.start_hub}")
        print(f"end_hub  : {network.end_hub}")
        print(f"Path     : {list_path}")
        print(f"Turn min : {list_path[0][0]}")
        # for y in list_path:
        #     print(f"    {y}")


    except DotenvError as e:
        print(f"Dotenv error: {e}")
    except ParseError as e:
        print(f"Parse error: {e}")
    except BlockedZone as e:
        print(f"Zone Error: {e}")
    # except Exception as e:
    #     print(f"Error: {e}")

if __name__ == "__main__":
    main()
