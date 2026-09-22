#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   main.py                                              :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/11 23:52:36 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/22 18:27:06 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from parser_errors import (ParseError, DotenvError,
                           BlockedZone, RenderError, VelocityError)
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
    color_ascii = "\033[32m"
    ascii_art = """
              ░▒▓████████▓▒░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░               \
░▒▓█▓▒░▒▓███████▓▒░
              ░▒▓█▓▒░      ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░               \
░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░
              ░▒▓█▓▒░      ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░               \
░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░
              ░▒▓██████▓▒░ ░▒▓█▓▒░    ░▒▓██████▓▒░░    ▒▓█▓▒░     \
░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░
              ░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░                   \
░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░
              ░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░                   \
░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░
              ░▒▓█▓▒░      ░▒▓████████▓▒░▒▓█▓▒░                   \
░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░


                       ░▒▒░░░░░░░░░░░░░                      ░░░░░\
░░░░░░░░▒▒░
            ░░░▒▒▒▒▓▓▓▓▓▓▓▒░░░                                    \
    ░░▒▒▓▓▓▓▓▓▓▒▒▒▒░░░
          ░ ░░░░░░░░ ░▒▓▓▓▒                                       \
      ░▒▓▓▓▒░ ░░░░░░░
           ░░░░░▒▓▓▒░░▒▓▓▓▓░░                                     \
     ░░▓▓▓▓▒░░▒▓▓▒░░░░░
            ░░▒▒▓█▓▓▓▓▓▓▓▓▓▒░░░░                                  \
  ░░░░▒▓▓▓▓▓▓▓█▓█▓▒▒░░
               ▒▓▓▓▓▒▒▓▓█▓▓░                                      \
      ░▓▓█▓▓▒▒▓▓▓▓▒
              ░▒▓▓▓▓▓▓████▓░░                  ░░░░░░             \
     ░░▓████▓▓▓▓▓▓▒
              ░▓█████▓▓███▓█▓▓▓▒░░           ▒▓██████▓▒           \
░░▒▓▓▓▓▓███▓▓█████▓░
              ░▓▓▓▓█▓▒░▒▓▒░░▒▒▓▓█▓▓▓▒░░     ▒▓████████▓▒     ░░▒▓▓\
██▓▓▒▒░░▒▓▒░▒▓█▓▓▓▓░
              ░▒▓▓▓▓▒░ ░▓▒▒░░░░░░▒▒▓▓██▓▓▒░▒▒▓████████▓▒▒░▒▓▓▓█▓▓▒\
▒░░░░░░▒▒▓░ ░▒▓▓▓▓▒░
                ▒▓▓▒   ▒▓░    ░░░░░░░░▒▒▓▓▓██▓████████▓██▓▓▓▒░░░░░\
░░░░    ░▓▒   ▒▓▓▒
                ▒█▓▒   ░▒         ░░░░░░ ░░▒▓▓████████▓▓▒░░ ░░░░░░\
         ▒░   ▒▓█▒
                ░▓▓▒                   ░░▒░░░▓████████▓░░░▒░░     \
              ▒▓▓░
                ░▓▓▒                       ░░▓▓██████▓▓░░         \
              ▒▓▓░
                ░▓▓▒                         ▒████████▒           \
              ▒▓▓░
                 ▒▓▒                         ░▓▓▓▓▓▓▓▓░           \
              ▒▓▒
                 ░▓▓                          ▒▓▓▓▓▓▓▒            \
              ▓▓░
                  ░▒                           ░▒▓▒▒░             \
              ▒░

"""

    try:
        dotenv = import_module("dotenv")

        load = dotenv.load_dotenv
        find_path_conf = dotenv.find_dotenv

        path = find_path_conf()
        if path == "":
            print(f"\n{WARNING_CLR}[WARNING]: Dotenv could not find "
                  f"the file '.env'.{RESET_CLR}\n")
            flag_load = load()
            map = os.getenv("MAP") is not None
            if map is False and flag_load is False:
                raise DotenvError(
                      "Error loading environment variable\n"
                      "Use 'cp .env_example .env'\n"
                      "Or use the environment variable "
                      "e.g.: MAP=<path> RENDER=<flag> and "
                      "(SPEED=<value> — this is optional)")

        load()
        filename = str(os.getenv("MAP"))
        if filename == "":
            raise ParseError("The map path must not be empty")

        render = os.getenv("RENDER")

        velocity = os.getenv("SPEED")
        speed = 0

        if velocity is None or velocity == "":
            speed = 2
            print(f"\n{WARNING_CLR}[WARNING]: The default speed "
                  "is applied because the search for the appropriate "
                  f"variable returned no results.{RESET_CLR}\n")
        else:
            try:
                speed = int(velocity)
            except ValueError as e:
                raise VelocityError(
                    "The 'SPEED' value must be an integer "
                    "or be convertible to an integer.") from e

            if speed <= 0:
                raise VelocityError(
                    "The 'SPEED' value must be a positive integer; therefore, "
                    "it cannot be equal to or less than zero.")

        parser = FlyInParser(filename)
        network = parser.parse()

        graph = Graph.build_graph(network)
        if network.start_hub and network.end_hub:
            # print(paths)
            paths = graph.yen(network.start_hub.name, network.end_hub.name, 20)
            if not paths:
                raise BlockedZone("No valid route from start_hub to end_hub")

        simulation = Simulation(network, paths)

        events = simulation.run_from_all_path()
        turn = max(events)
        if render is not None:
            if render == "True" or render == "true":
                print(f"{color_ascii}{ascii_art}{RESET_CLR}")

                from render import Lancer
                lancer = Lancer(network,
                                simulation.scheduled_routes,
                                filename,
                                turn,
                                speed)
                lancer.run()
                simulation.render_terminal(events)

            elif render == "False" or render == "false":
                print(f"{color_ascii}{ascii_art}{RESET_CLR}")
                simulation.render_terminal(events)
            else:
                raise RenderError("The 'RENDER' value in the configuration "
                                  "(.env/environment variable) must be "
                                  "'True', 'False', or entirely lowercase.")
        else:
            print(f"{color_ascii}{ascii_art}{RESET_CLR}")
            simulation.render_terminal(events)

    except DotenvError as e:
        print(f"{ERROR_CLR}[DOTENV ERROR]: {e}{RESET_CLR}\n")
    except ParseError as e:
        print(f"[PARSE ERROR]: {e}{RESET_CLR}\n")
    except BlockedZone as e:
        print(f"{ERROR_CLR}[ZONE ERROR]: {e}{RESET_CLR}\n")
    except RenderError as e:
        print(f"{ERROR_CLR}[RENDER FLAG ERROR]: {e}{RESET_CLR}\n")
    except VelocityError as e:
        print(f"{ERROR_CLR}[VELOCITY ERROR]: {e}{RESET_CLR}\n")
    except ValueError as e:
        print(f"{ERROR_CLR}[VALUE ERROR]: {e}{RESET_CLR}\n")
    except ImportError as e:
        print(f"{ERROR_CLR}[IMPORTATION ERROR]: {e}{RESET_CLR}\n")
    except KeyboardInterrupt:
        print(f"{ERROR_CLR}[PROGRAM INTERRUPTED]{RESET_CLR}\n")
    except Exception as e:
        print(f"{ERROR_CLR}[ERROR]: {e}{RESET_CLR}\n")


if __name__ == "__main__":
    main()
