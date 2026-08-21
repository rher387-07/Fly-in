from parser.errors import ParseError, DotenvError
from parser.parser import FlyInParser
from parser.dotenv_parser import dot_parse
# from graph.graph import Graph
from z import Graph
import os
import sys


def main() -> None:

    if len(sys.argv) != 2:
        print("Usage: python main.py <map_file>")
        return
    # if fals
    try:
        # load, find_path = dot_parse()
        # path = find_path()
        # if path == "":
        #     print("[WARNING] Dotenv could not find the file '.env'.\n")
        #     flag_load = load()
        #     map = os.getenv("MAP") is not None
        #     if map is False and flag_load is False:
        #         print(
        #               "[ERROR] Error loading environment variable\n"
        #               "Use 'cp .env_example .env'\n"
        #               "Or use the environment variable e.g.: MAP=<path>"
        #         )
        #         return
        # load()
        # filename = str(os.getenv("MAP"))
        # if filename == "":
        #     print("[INVALID] The map path must not be empty")
        #     return
        dict_graph = {}
        list_hub = []
        turn = 0
        parser = FlyInParser(sys.argv[1])
        network = parser.parse()
        graph = Graph(turn, dict_graph)
        # graph.add_summit()

        # print(f"nb drone: {network.nb_drones}")
        # print(f"start   : {network.start_hub}")
        # print(f"end     : {network.end_hub}")
        # print("hubs    :")
        for value in network.hubs.values():
            # print(f"    {value}")
            list_hub.append(value)


        start = list_hub[0].name
        end = list_hub[len(list_hub) - 1].name
        # print("Connection:")
        for y in network.connections:
            # print(f"    {y}")
            graph.add_summit(y.hub1, y.hub2, list_hub)

        for key, dict_val in dict_graph.copy().items():
            for val in dict_val:
                if val == end:
                    graph.add_summit(val, key, list_hub)
        # print(f"graph: {dict_graph}")

        path = graph.yen(start, end, 20 )
        print(path)

        # print(f"Path:")
        # for y in path:
        #     print(f"    {y}")
        # tmp_turn = float("inf")
        # for x in path:
        #     turn, path = x
        #     # print(turn)
        #     if turn < tmp_turn:
        #         tmp_turn = turn

        # print(tmp_turn)

        # print(f"Turn: {turn}")
        # for x in dict_graph:
        #     print(x)
        # print(start)
        # print(type(end))
        # dis, prec = graph.shortest_distances(start)
        # # print(f"distance: {dis}")
        # distance = dis[end]
        # print(f"turn: {distance}")
        # print(f"pred: {prec}")
        # print()
    except DotenvError as error:
        print(f"Dotenv error: {error}")
    except ParseError as error:
        print(f"Parse error: {error}")
    # except Exception as error:
    #     print(f"Error: {error}")

if __name__ == "__main__":
    main()

# d  ={
#     "d":4,
#     "f":1
# }
