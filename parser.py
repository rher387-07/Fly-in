#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   parser.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/18 11:36:11 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/29 12:02:05 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #


"""Analyze the provided file.

Extract the data, and convert it into a format that can be manipulated.
"""

from sys import maxsize
from parser_errors import ParseError
from parser_models import Connection, Hub, Network


VALID_ZONE_TYPES = {
    "normal",
    "blocked",
    "restricted",
    "priority",
}

VALID_MTD_HUB = {
    "zone",
    "color",
    "max_drones",
}

VALID_MTD_CONNEC = {
    "max_link_capacity"
}


class FlyInParser:
    """Parses a map configuration file into a manipulable `Network` object."""

    def __init__(self, filename: str) -> None:
        """Initialize the parser.

        Args:
            filename (str): Path to the configuration file (MAP) to parse.
        """
        self.filename = filename
        self.network = Network(nb_drones=0)

    def parse(self) -> Network:
        """Parse the configuration file and builds the network.

        Raises:
            ParseError: If the input file or map is empty.

        Returns:
            Network: The fully initialized and validated network object.
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
        """Read the configuration file and returns its content.

        Strips inline comments (anything after `#`) and skips blank or
        comment-only lines.

        Raises:
            ParseError: If the file cannot be opened or read.

        Returns:
            list[tuple[int, str]]: The remaining, non-empty lines paired
            with their original (1-based) line numbers.
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
        """Parse the number of drones from the first line of the file.

        Args:
            line_info (tuple[int, str]): The first file line, as a
                (line_number, line) pair. Must start with "nb_drones:".

        Raises:
            ParseError: If the line does not start with "nb_drones:".
            ParseError: If the `nb_drones` value cannot be converted to
                an integer.
            ParseError: If the value of `nb_drones` is not positive.
            ParseError: If the value of `nb_drones` exceeds 1,000.
        """
        line_number, line = line_info
        if not line.startswith("nb_drones:"):
            raise ParseError(
                f"Line {line_number}: "
                "first line must be nb_drones.")

        _, value = line.split(":", 1)
        self._chech_special_character(value, line_number)
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
                "nb_drones must be positive.")

        if nb_drones > 1500:
            warning_color = '\033[33m'
            reset_color = '\033[0m'
            print(
                f"{warning_color}[WARNING] The number of drones exceeds 1500, "
                f"and it takes a little time.{reset_color}\n")

            if nb_drones > 3000:
                raise ParseError(
                    f"Line {line_number}: "
                    "The number of drones must not exceed 3,000 "
                    "to avoid memory issues and processor overload.")

        self.network.nb_drones = nb_drones

    def _chech_special_character(self, value: str, line_number: int) -> None:
        """Check that a numeric value does not contain an underscore.

        Python allows `_` as a digit grouping separator in int literals
        (e.g. `1_000`), which would otherwise silently pass `int()`. This
        rejects that syntax so numeric fields only accept plain digits.

        Args:
            value (str): Value to check for an underscore character.
            line_number (int): Line number, used for the error message.

        Raises:
            ParseError: If `value` contains an underscore character.
        """
        if "_" in value:
            raise ParseError(
                    f"Line {line_number}: "
                    "The number of drones must be a valid number; "
                    f"no special character '_'. Perhaps '{int(value)}' "
                    f"instead of '{value}'?")

    def _check_color_valid(self, name_color: str, line_number: int) -> None:
        """Check that a color name is valid.

        Accepts the special value "rainbow", or any single-word CSS color
        name resolvable by the `webcolors` module.

        Args:
            name_color (str): Color name to validate.
            line_number (int): Line number, used for the error message.

        Raises:
            ImportError: If the `webcolors` module is not installed.
            ParseError: If `name_color` is not "rainbow" and is not a
                valid, recognized color name.
        """
        if name_color != "rainbow":
            try:
                from importlib import import_module
                webcolors = import_module("webcolors")
                webcolors.name_to_hex(name_color)
            except ImportError as error:
                raise ImportError("module not found") from error
            except ValueError as error:
                raise ParseError(
                    f"Line {line_number}: "
                    "Accepted color values are colors supported by Pygame "
                    "and valid single-word strings (e.g., red, blue, gray)."
                    f"Check your '{name_color}' value."
                ) from error

    def _parse_line(
        self,
        line: str,
        line_number: int,
    ) -> None:
        """Dispatches a configuration line to the appropriate parser.

        Routes the line based on its instruction prefix ("start_hub:",
        "end_hub:", "hub:", or "connection:").

        Args:
            line (str): The configuration line to parse (already
                stripped of comments and whitespace).
            line_number (int): Line number, used for error messages.

        Raises:
            ParseError: If the line does not match any known
                instruction prefix.
        """
        if line.startswith("start_hub:"):
            self._parse_special_hub(
                line,
                line_number,
                "start")
        elif line.startswith("end_hub:"):
            self._parse_special_hub(
                line,
                line_number,
                "end")
        elif line.startswith("hub:"):
            self._parse_regular_hub(
                line,
                line_number)
        elif line.startswith("connection:"):
            self._parse_connection(
                line,
                line_number)
        else:
            raise ParseError(
                f"Line {line_number}: "
                f"unknown instruction '{line}'.")

    def _parse_special_hub(
        self,
        line: str,
        line_number: int,
        name: str,
    ) -> None:
        """Parse a `start_hub:` or `end_hub:` line and registers it.

        Args:
            line (str): The configuration line to parse.
            line_number (int): Line number, used for error messages.
            name (str): Which special hub is being parsed: "start" for
                `start_hub`, anything else for `end_hub`.

        Raises:
            ParseError: If the parsed hub duplicates the name of an
                already-registered hub.
            ParseError: If `name` is "start" and `start_hub` has already
                been defined.
            ParseError: If `name` is not "start" and `end_hub` has
                already been defined.
        """
        hub = self._create_hub(line, line_number)

        if hub.name in self.network.hubs:
            raise ParseError(
                f"Line {line_number}: "
                f"duplicate hub '{hub.name}'.")

        if name == "start":
            if self.network.start_hub is not None:
                raise ParseError(
                    f"Line {line_number}: "
                    "multiple start_hub definitions.")
            self.network.start_hub = hub

        else:
            if self.network.end_hub is not None:
                raise ParseError(
                    f"Line {line_number}: "
                    "multiple end_hub definitions.")

            self.network.end_hub = hub
        self.network.hubs[hub.name] = hub

    def _parse_regular_hub(
        self,
        line: str,
        line_number: int,
    ) -> None:
        """Parse a `hub:` line and registers it as a regular hub.

        Args:
            line (str): The configuration line to parse.
            line_number (int): Line number, used for error messages.

        Raises:
            ParseError: If the parsed hub duplicates the name of an
                already-registered hub.
        """
        hub = self._create_hub(line, line_number, False)

        if hub.name in self.network.hubs:
            raise ParseError(
                f"Line {line_number}: "
                f"duplicate hub '{hub.name}'.")

        self.network.hubs[hub.name] = hub

    def _create_hub(
        self,
        line: str,
        line_number: int,
        flag: bool = True
    ) -> Hub:
        """Build a `Hub` object from a `hub:`/`start_hub:`/`end_hub:` line.

        Expects a "name x y" triplet, optionally followed by a
        "[key=value ...]" metadata block (zone, color, max_drones). The
        parsed y coordinate is stored negated, so the map's vertical axis
        grows downward as written.

        Args:
            line (str): The configuration line to parse.
            line_number (int): Line number, used for error messages.
            flag (bool, optional): Whether this hub is a special hub
                (start or end). If True, `max_drones` is set to the
                maximum possible value instead of being read from
                metadata. Defaults to True.

        Raises:
            ParseError: If the line does not contain exactly a name, x,
                and y value.
            ParseError: If the x or y coordinate is not a valid integer.
            ParseError: If the hub name contains a hyphen or a space.
            ParseError: If the `zone` metadata value is not a recognized
                zone type.

        Returns:
            Hub: The newly constructed hub.
        """
        _, content = line.split(":", 1)
        content = content.strip()
        metadata = self._extract_metadata(
            content,
            "hub",
            line_number)

        main_content = content.split("[", 1)[0].strip()
        parts = main_content.split()

        if len(parts) != 3:
            raise ParseError(
                f"Line {line_number}: "
                "hub requires name, x and y.")

        name, x_value, y_value = parts
        self._chech_special_character(x_value, line_number)
        self._chech_special_character(y_value, line_number)

        try:
            x = int(x_value)
            y = int(y_value)
        except ValueError as e:
            raise ParseError(
                f"Line {line_number}: "
                "coordinates must be integers."
            ) from e

        if "-" in name or " " in name:
            raise ParseError(
                f"Line {line_number}: "
                f"invalid hub name '{name}'.")

        zone_type = metadata.get("zone", "normal",)
        if zone_type not in VALID_ZONE_TYPES:
            raise ParseError(
                f"Line {line_number}: "
                f"invalid zone type '{zone_type}'.")

        if flag:
            max_drones = maxsize
        else:
            max_drones = self._positive_int(
                metadata.get("max_drones", "1"),
                "max_drones",
                line_number)

        color = metadata.get("color")
        if color:
            self._check_color_valid(color, line_number)

        return Hub(
            name=name,
            x=x,
            y=y * -1,
            zone_type=zone_type,
            color=color,
            max_drones=max_drones)

    def _parse_connection(
        self,
        line: str,
        line_number: int,
    ) -> None:
        """Parse a `connection:` line and registers the resulting link.

        Expects a "hub1-hub2" pair, optionally followed by a
        "[key=value ...]" metadata block (max_link_capacity).

        Args:
            line (str): The configuration line to parse.
            line_number (int): Line number, used for error messages.

        Raises:
            ParseError: If the line does not contain exactly two
                hyphen-separated hub names.
            ParseError: If either hub name is empty.
            ParseError: If either hub name refers to an unregistered hub.
            ParseError: If both hub names are the same.
            ParseError: If this connection already exists (in either
                direction).
        """
        _, content = line.split(":", 1)
        content = content.strip()

        metadata = self._extract_metadata(content, "connect", line_number)

        connection_text = content.split("[", 1)[0].strip()
        parts = connection_text.split("-")

        if len(parts) != 2:
            raise ParseError(
                f"Line {line_number}: "
                "invalid connection format.")

        hub1, hub2 = parts

        if not hub1 or not hub2:
            raise ParseError(
                f"Line {line_number}: "
                "connection contains an empty hub.")

        if hub1 not in self.network.hubs:
            raise ParseError(
                f"Line {line_number}: "
                f"unknown hub '{hub1}'.")

        if hub2 not in self.network.hubs:
            raise ParseError(
                f"Line {line_number}: "
                f"unknown hub '{hub2}'.")

        if hub1 == hub2:
            raise ParseError(
                f"Line {line_number}: "
                "a hub cannot connect to itself.")

        if self._connection_exists(hub1, hub2):
            raise ParseError(
                f"Line {line_number}: "
                f"duplicate connection "
                f"'{hub1}-{hub2}'.")

        capacity = self._positive_int(
            metadata.get("max_link_capacity", "1"),
            "max_link_capacity",
            line_number)

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
        data: str,
        line_number: int,
    ) -> dict[str, str]:
        """Extract and validates a "[key=value ...]" metadata block.

        Args:
            content (str): The line content (after the instruction
                prefix) that may contain a trailing metadata block.
            data (str): Which field set to validate keys against: "hub"
                (uses `VALID_METADATA_HUB`) or "connect" (uses
                `VALID_METADATA_CONNEC`).
            line_number (int): Line number, used for error messages.

        Raises:
            ParseError: If a `[` is present but the content does not end
                with `]`.
            ParseError: If an entry in the metadata block does not
                contain `=`.
            ParseError: If a key or value is empty, or the key is not
                valid for the given `data` type.
            ParseError: If the same key appears more than once.

        Returns:
            dict[str, str]: The parsed metadata as a key-value mapping.
            Returns an empty dict if there is no metadata block, or an
            empty one.
        """
        if "[" not in content:
            return {}

        if not content.endswith("]"):
            raise ParseError(
                f"Line {line_number}: "
                "invalid metadata block.")

        metadata_text = content.split("[", 1)[1][:-1].strip()
        if not metadata_text:
            return {}

        result: dict[str, str] = {}

        for item in metadata_text.split():
            if "=" not in item:
                raise ParseError(
                    f"Line {line_number}: "
                    f"invalid metadata '{item}'.")

            key, value = item.split("=", 1)

            if data == "hub":
                if (not key or not value) or not (key in VALID_MTD_HUB):
                    raise ParseError(
                        f"Line {line_number}: "
                        f"invalid metadata '{item}'.")

            elif data == "connect":
                if (not key or not value) or not (key in VALID_MTD_CONNEC):
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
        """Parse and validate a strictly positive integer field.

        Args:
            value (str): The raw string value to parse.
            name (str): Name of the field being parsed, used in error
                messages.
            line_number (int): Line number, used for error messages.

        Raises:
            ParseError: If `value` cannot be converted to an integer.
            ParseError: If the resulting integer is not positive.

        Returns:
            int: The parsed, validated positive integer.
        """
        self._chech_special_character(value, line_number)
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
        """Check whether a connection between two hubs already exists.

        The check is direction-agnostic: a connection "A-B" is
        considered to already exist for the pair ("B", "A") too.

        Args:
            hub1 (str): Name of the first hub.
            hub2 (str): Name of the second hub.

        Returns:
            bool: True if a connection between `hub1` and `hub2` (in
            either direction) is already registered, False otherwise.
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
        """Validate that the network has both a start and an end hub.

        Raises:
            ParseError: If `start_hub` was never defined.
            ParseError: If `end_hub` was never defined.
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
        """Validate that no two hubs share the same coordinates.

        Raises:
            ParseError: If any two hubs in the network have identical
                (x, y) coordinates.
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
