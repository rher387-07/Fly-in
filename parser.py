#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   parser.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/18 11:36:11 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/19 13:57:59 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #


from parser_errors import ParseError
from parser_models import Connection, Hub, Network


VALID_ZONE_TYPES = {
    "normal",
    "blocked",
    "restricted",
    "priority",
}

VALID_METADATA = {
    "zone",
    "color",
    "max_drones",
    "max_link_capacity"
}


class FlyInParser:
    """_summary_
    """

    def __init__(self, filename: str) -> None:
        """_summary_

        Args:
            filename (str): _description_
        """
        self.filename = filename
        self.network = Network(nb_drones=0)

    def parse(self) -> Network:
        """_summary_

        Raises:
            ParseError: _description_

        Returns:
            Network: _description_
        """
        lines = self._read_file()

        if not lines:
            raise ParseError("The map is empty.")

        self._parse_nb_drones(lines[0])

        for line_number, line in lines[1:]:
            self._parse_line(line, line_number)

        self._validate_network()
        self._validate_cordo()

        return self.network

    def _read_file(self) -> list[tuple[int, str]]:
        """_summary_

        Raises:
            ParseError: _description_

        Returns:
            list[tuple[int, str]]: _description_
        """
        try:
            with open(self.filename, "r") as file:
                result: list[tuple[int, str]] = []

                for number, raw_line in enumerate(file, 1):
                    line = raw_line.split("#", 1)[0].strip()

                    if not line or line.startswith("#"):
                        continue

                    result.append((number, line))
                return result

        except OSError as e:
            raise ParseError(
                f"Cannot open '{self.filename}'."
            ) from e

    def _parse_nb_drones(
        self,
        line_info: tuple[int, str],
    ) -> None:
        """_summary_

        Args:
            line_info (tuple[int, str]): _description_

        Raises:
            ParseError: _description_
            ParseError: _description_
            ParseError: _description_
        """

        line_number, line = line_info

        if not line.startswith("nb_drones:"):
            raise ParseError(
                f"Line {line_number}: "
                "first line must be nb_drones."
            )

        _, value = line.split(":", 1)

        try:
            nb_drones = int(value.strip())
        except ValueError as e:
            raise ParseError(
                f"Line {line_number}: "
                "nb_drones must be an integer."
            ) from e

        if nb_drones <= 0:
            raise ParseError(
                f"Line {line_number}: "
                "nb_drones must be positive."
            )
        if nb_drones > 1000:
            raise ParseError(
                f"Line {line_number}: "
                "The number of drones must not exceed 1,000 to avoid memory overload and other errors."
            )

        self.network.nb_drones = nb_drones

    def _parse_line(
        self,
        line: str,
        line_number: int,
    ) -> None:
        """_summary_

        Args:
            line (str): _description_
            line_number (int): _description_

        Raises:
            ParseError: _description_
        """

        if line.startswith("start_hub:"):
            self._parse_special_hub(
                line,
                line_number,
                "start",
            )

        elif line.startswith("end_hub:"):
            self._parse_special_hub(
                line,
                line_number,
                "end",
            )

        elif line.startswith("hub:"):
            self._parse_regular_hub(
                line,
                line_number,
            )

        elif line.startswith("connection:"):
            self._parse_connection(
                line,
                line_number,
            )

        else:
            raise ParseError(
                f"Line {line_number}: "
                f"unknown instruction '{line}'."
            )

    def _parse_special_hub(
        self,
        line: str,
        line_number: int,
        name: str,
    ) -> None:
        """_summary_

        Args:
            line (str): _description_
            line_number (int): _description_
            name (str): _description_

        Raises:
            ParseError: _description_
            ParseError: _description_
            ParseError: _description_
        """

        hub = self._create_hub(line, line_number)

        if hub.name in self.network.hubs:
            raise ParseError(
                f"Line {line_number}: "
                f"duplicate hub '{hub.name}'."
            )

        if name == "start":
            if self.network.start_hub is not None:
                raise ParseError(
                    f"Line {line_number}: "
                    "multiple start_hub definitions."
                )

            self.network.start_hub = hub

        else:
            if self.network.end_hub is not None:
                raise ParseError(
                    f"Line {line_number}: "
                    "multiple end_hub definitions."
                )

            self.network.end_hub = hub

        self.network.hubs[hub.name] = hub

    def _parse_regular_hub(
        self,
        line: str,
        line_number: int,
    ) -> None:
        """_summary_

        Args:
            line (str): _description_
            line_number (int): _description_

        Raises:
            ParseError: _description_
        """

        hub = self._create_hub(line, line_number)

        if hub.name in self.network.hubs:
            raise ParseError(
                f"Line {line_number}: "
                f"duplicate hub '{hub.name}'."
            )

        self.network.hubs[hub.name] = hub

    def _create_hub(
        self,
        line: str,
        line_number: int,
    ) -> Hub:
        """_summary_

        Args:
            line (str): _description_
            line_number (int): _description_

        Raises:
            ParseError: _description_
            ParseError: _description_
            ParseError: _description_
            ParseError: _description_

        Returns:
            Hub: _description_
        """

        _, content = line.split(":", 1)
        content = content.strip()

        metadata = self._extract_metadata(
            content,
            line_number,
        )

        main_content = content.split("[", 1)[0].strip()
        parts = main_content.split()

        if len(parts) != 3:
            raise ParseError(
                f"Line {line_number}: "
                "hub requires name, x and y."
            )

        name, x_value, y_value = parts

        try:
            x = int(x_value)
            y = int(y_value)
        except ValueError as e:
            raise ParseError(
                f"Line {line_number}: "
                "coordinates must be integers."
            ) from e

        # if x > 10 or y > 10 or x < -10 or y < -10:
        #     raise ParseError(
        #         f"Line {line_number}: "
        #         f"The coordinates must not exceed -10|10 on the y and x axes"
        #     )

        if "-" in name or " " in name:
            raise ParseError(
                f"Line {line_number}: "
                f"invalid hub name '{name}'."
            )

        zone_type = metadata.get(
            "zone",
            "normal",
        )

        if zone_type not in VALID_ZONE_TYPES:
            raise ParseError(
                f"Line {line_number}: "
                f"invalid zone type '{zone_type}'."
            )
        max_drones = self._positive_int(
            metadata.get("max_drones", "1"),
            "max_drones",
            line_number,
        )

        color = metadata.get("color")

        return Hub(
            name=name,
            x=x,
            y=y * -1,
            zone_type=zone_type,
            color=color,
            max_drones=max_drones,
            # max_drones=5,

        )

    def _parse_connection(
        self,
        line: str,
        line_number: int,
    ) -> None:
        """_summary_

        Args:
            line (str): _description_
            line_number (int): _description_

        Raises:
            ParseError: _description_
            ParseError: _description_
            ParseError: _description_
            ParseError: _description_
            ParseError: _description_
            ParseError: _description_
        """

        _, content = line.split(":", 1)
        content = content.strip()

        metadata = self._extract_metadata(
            content,
            line_number,
        )

        connection_text = content.split("[", 1)[0].strip()

        parts = connection_text.split("-")

        if len(parts) != 2:
            raise ParseError(
                f"Line {line_number}: "
                "invalid connection format."
            )

        hub1, hub2 = parts

        if not hub1 or not hub2:
            raise ParseError(
                f"Line {line_number}: "
                "connection contains an empty hub."
            )

        if hub1 not in self.network.hubs:
            raise ParseError(
                f"Line {line_number}: "
                f"unknown hub '{hub1}'."
            )

        if hub2 not in self.network.hubs:
            raise ParseError(
                f"Line {line_number}: "
                f"unknown hub '{hub2}'."
            )

        if hub1 == hub2:
            raise ParseError(
                f"Line {line_number}: "
                "a hub cannot connect to itself."
            )

        if self._connection_exists(hub1, hub2):
            raise ParseError(
                f"Line {line_number}: "
                f"duplicate connection "
                f"'{hub1}-{hub2}'."
            )

        capacity = self._positive_int(
            metadata.get("max_link_capacity", "1"),
            "max_link_capacity",
            line_number,
        )

        self.network.connections.append(
            Connection(
                hub1=hub1,
                hub2=hub2,
                max_capacity=capacity,
            )
        )

    def _extract_metadata(
        self,
        content: str,
        line_number: int,
    ) -> dict[str, str]:
        """_summary_

        Args:
            content (str): _description_
            line_number (int): _description_

        Raises:
            ParseError: _description_
            ParseError: _description_
            ParseError: _description_
            ParseError: _description_

        Returns:
            dict[str, str]: _description_
        """

        if "[" not in content:
            return {}

        if not content.endswith("]"):
            raise ParseError(
                f"Line {line_number}: "
                "invalid metadata block."
            )

        metadata_text = content.split("[", 1)[1][:-1].strip()

        if not metadata_text:
            return {}

        result: dict[str, str] = {}

        for item in metadata_text.split():
            if "=" not in item:
                raise ParseError(
                    f"Line {line_number}: "
                    f"invalid metadata '{item}'."
                )

            key, value = item.split("=", 1)

            if (not key or not value) or not (key in VALID_METADATA):
                raise ParseError(
                    f"Line {line_number}: "
                    f"invalid metadata '{item}'."
                )

            if key in result:
                raise ParseError(
                    f"Line {line_number}: "
                    f"duplicate metadata '{key}'."
                )

            result[key] = value

        return result

    def _positive_int(
        self,
        value: str,
        name: str,
        line_number: int,
    ) -> int:
        """_summary_

        Args:
            value (str): _description_
            name (str): _description_
            line_number (int): _description_

        Raises:
            ParseError: _description_
            ParseError: _description_

        Returns:
            int: _description_
        """

        try:
            result = int(value)
        except ValueError as e:
            raise ParseError(
                f"Line {line_number}: "
                f"{name} must be an integer."
            ) from e

        if result <= 0:
            raise ParseError(
                f"Line {line_number}: "
                f"{name} must be positive."
            )

        return result

    def _connection_exists(
        self,
        hub1: str,
        hub2: str,
    ) -> bool:
        """_summary_

        Args:
            hub1 (str): _description_
            hub2 (str): _description_

        Returns:
            bool: _description_
        """

        return any(
            {
                connection.hub1,
                connection.hub2,
            }
            == {hub1, hub2}
            for connection in self.network.connections
        )

    def _validate_network(self) -> None:
        """_summary_

        Raises:
            ParseError: _description_
            ParseError: _description_
        """

        if self.network.start_hub is None:
            raise ParseError(
                "Missing start_hub."
            )

        if self.network.end_hub is None:
            raise ParseError(
                "Missing end_hub."
            )

    def _validate_cordo(self) -> None:
        """_summary_

        Raises:
            ParseError: _description_
        """
        tuple_coord = []
        res = self.network.hubs.values()
        for x in res:
            tuple_coord += [(x.x, x.y)]

        for i, coord in enumerate(tuple_coord):
            for next_coord in tuple_coord[i + 1:]:
                if coord == next_coord:
                    raise ParseError(
                        "There must be no duplication"
                        " in the coordination of the hubs. "
                        "Check your hubs coordinate."
                    )
