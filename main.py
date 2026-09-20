#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   main.py                                              :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/11 23:52:36 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/20 16:03:29 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from parser_errors import ParseError, DotenvError, BlockedZone, RenderError
from parser import FlyInParser
from importlib import import_module
from algo_graph import Graph
from simulation import Simulation
import os


def main() -> None:
    """Runs the drone simulation end to end.

    Loads configuration (map path and render flag) from a `.env` file or
    from environment variables, parses the map into a network, builds the
    graph and computes candidate routes, runs the simulation, and
    renders the result (either in the terminal, graphically, or both,
    depending on the `RENDER` setting).

    Raises:
        DotenvError: If no `.env` file is found and no `MAP` environment
            variable is set (i.e. no configuration source exists).
        ParseError: If the `MAP` path is empty.
        BlockedZone: If no valid route exists between the start and end
            hubs.
        RenderError: If the `RENDER` value is set but is not one of
            "True", "False", "true", or "false".
    """
    WARNING_CLR = '\033[33m'
    ERROR_CLR = '\033[31m'
    RESET_CLR = '\033[0m'
    try:
        dotenv = import_module("dotenv")

        load = dotenv.load_dotenv
        find_path_conf = dotenv.find_dotenv

        path = find_path_conf()
        if path == "":
            print(f"\n{WARNING_CLR}[WARNING]: Dotenv could not find the file '.env'.{RESET_CLR}\n")
            flag_load = load()
            map = os.getenv("MAP") is not None
            if map is False and flag_load is False:
                raise DotenvError(
                      "Error loading environment variable\n"
                      "Use 'cp .env_example .env'\n"
                      "Or use the environment variable e.g.: MAP=<path> and RENDER=<flag>"
                )
        load()
        filename = str(os.getenv("MAP"))
        render = os.getenv("RENDER")
        if filename == "":
            raise ParseError("The map path must not be empty")

        parser = FlyInParser(filename)
        network = parser.parse()

        graph = Graph.build_graph(network)
        paths = graph.yen(network.start_hub.name, network.end_hub.name, 20)
        if not paths:
            raise BlockedZone("No valid route from start_hub to end_hub")

        simulation = Simulation(network, paths)
        events = simulation.run_from_all_path()
        if render is not None:
            if render == "True" or render == "true":
                from render import Lancer
                turn = max(events)
                lancer = Lancer(network, simulation.scheduled_routes, filename, turn)
                lancer.run()
                simulation.render_terminal(events)

            elif render == "False" or render == "false":
                simulation.render_terminal(events)
            else:
                print(render)
                raise RenderError("The 'RENDER' value in the configuration (.env/environment variable) must be 'True', 'False', or entirely lowercase.")
        else:
            simulation.render_terminal(events)

    except DotenvError as e:
        print(f"{ERROR_CLR}[DOTENV ERROR]: {e}{RESET_CLR}\n")
    except ParseError as e:
        print(f"{ERROR_CLR}[PARSE ERROR]: {e}{RESET_CLR}\n")
    except BlockedZone as e:
        print(f"{ERROR_CLR}[ZONE ERROR]: {e}{RESET_CLR}\n")
    except RenderError as e:
        print(f"{ERROR_CLR}[RENDER FLAG ERROR]: {e}{RESET_CLR}\n")
    except ValueError as e:
        print(f"{ERROR_CLR}[VALUE ERROR]: {e}{RESET_CLR}\n")
    except ImportError as e:
        print(f"{ERROR_CLR}[IMPORTATION ERROR]: {e}{RESET_CLR}\n")
    except KeyboardInterrupt as e:
        print(f"{ERROR_CLR}[PROGRAM INTERRUPTED]{RESET_CLR}\n")
    except Exception as e:
        print(f"{ERROR_CLR}[ERROR]: {e}{RESET_CLR}\n")


if __name__ == "__main__":
    main()
