*This project has been created as part of the 42 curriculum by hery-rak.*

# Description

Fly-in routes a fleet of drones through a bidirectional network of hubs. The
parser validates the map format, the graph uses Dijkstra and Yen's algorithm
to find weighted alternatives, and the scheduler assigns departures while
respecting hub and connection capacities.

# Instructions

Python 3.10 or later is required. The program accepts a map path directly:

```bash
python3 main.py maps/easy/01_linear_path.txt
```

The same path can be supplied with `MAP`. The Makefile provides `run`,
`debug`, `clean`, `lint`, and `lint-strict` targets; use `MAP=... make run`.

# Algorithm

Edges are weighted by the destination zone: normal and priority hubs cost one
turn, while restricted hubs cost two. Blocked hubs are excluded from the graph.
Yen's algorithm produces alternative simple paths. Drones are distributed over
these paths, then scheduled with time reservations for every edge traversal
and every intermediate hub arrival. A restricted move emits its connection on
the first turn and its destination on the second turn.

# Visual Representation

The mandatory terminal representation is one space-separated movement line per
turn. The existing optional Pygame renderer remains available for future visual
work, while the terminal output is deterministic and easy to validate in tests.

# Example

Input: `maps/easy/01_linear_path.txt`

```text
D1-waypoint1
D1-waypoint2 D2-waypoint1
D1-goal D2-waypoint2
D2-goal
```

# Resources

- [Yen's k-shortest paths algorithm](https://www.linchenguang.com/2018/01/30/Yen-s-algorithm/)
- [Python heap queue documentation](https://docs.python.org/3/library/heapq.html)
- [Pygame documentation](https://www.pygame.org/docs/)

AI was used to review the existing control flow, identify parser and scheduler
bugs, and help structure focused validation. The implementation was inspected
and tested against the supplied maps before being retained.
