#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   main.py                                              :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/11 23:52:36 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/15 15:25:50 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from parser.errors import ParseError, DotenvError, BlockedZone, RenderError
from parser.parser import FlyInParser
from parser.dotenv_parser import dot_parse
from graph.graph import Graph
from parser.models import Network
from simulation.simulation import Simulation
import os

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
        render = os.getenv("RENDER")
        if filename == "":
            print("[INVALID] The map path must not be empty")
            return

        # dict_graph: dict[str, dict[str, float]] = {}
        # list_hub = []
        list_path = []
        # list_hub_blocked = []
        # turn = 0

        parser = FlyInParser(filename)
        network = parser.parse()
        graph = build_graph(network)
        paths = graph.yen(network.start_hub.name, network.end_hub.name, 20)
        if not paths:
            raise ParseError("no valid route from start_hub to end_hub")

        simulation = Simulation(network, paths)
        simulation.run_from_all_path()

        if render is not None:
            render = render.capitalize()
            if render == "True":
                try:
                    from renderer.render import Lancer
                    lancer = Lancer(network, simulation.scheduled_routes)
                    lancer.run()
                except Exception as error:
                    raise RuntimeError("Error dans l'importation de module") from error

            elif render == "" or render == "False" or render is None:
                pass
            else:
                print(render)
                raise RenderError("The 'render' value in the configuration (.env/environment variable) must be a case-insensitive boolean.")
        # else:
        #     pass


        # for hub in network.hubs.values():
        #     if hub.zone_type != "blocked":
        #         list_hub.append(hub)
        #     if hub.zone_type == "blocked":
        #         list_hub_blocked.append(hub.name)
        # start_hub = list_hub[0]
        # end_hub = list_hub[-1]
        # if network.start_hub is start_hub and network.end_hub is end_hub:
        #     start = start_hub.name
        #     end = end_hub.name
        # else:
        #     raise BlockedZone("The hub 'start_hub/end_hub' zone is defined"
        #                       " as a blocked zone")

        # for connect in network.connections:

        #     if not (connect.hub1 in list_hub_blocked):
        #         graph.add_summit(connect.hub1, connect.hub2, list_hub)

        # for key, value_dict in dict_graph.copy().items():
        #     for value in value_dict:
        #         if value == end:
        #             graph.add_summit(value, key, list_hub)

        # list_path = graph.yen(start, end, 20)
        # if not list_path:
        #     raise BlockedZone("There is no possible solution. "
        #                       "you have to look at the type of zone"
        #                       " or the connection between the hubs")
        # print(f"nr_drones: {network.nb_drones}")
        # print(f"start_hub: {network.start_hub}")
        # print(f"end_hub  : {network.end_hub}")
        # # print(f"Hub:")
        # for x in network.hubs.values():
        #     print(f"    {x.name}: {x}")
        # print(f"Path     : {list_path}")
        # print(f"Turn min : {list_path[0][0]}")

        # simulation = Lancer(network)
        # print(simulation.run())
        # run(simulation)

        # for y in list_path:
        #     print(f"    {y}")

    except DotenvError as e:
        print(f"Dotenv Error: {e}")
    except ParseError as e:
        print(f"Parse Error: {e}")
    except BlockedZone as e:
        print(f"Zone Error: {e}")
    except RenderError as e:
        print(f"Render Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt as e:
        print(f"Interruption with '^C'")
    except Exception as e:
        print(f"Error: {e}")



if __name__ == "__main__":
    main()
