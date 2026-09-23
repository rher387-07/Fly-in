#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   parser_errors.py                                     :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/18 11:35:49 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/23 15:28:11 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""specific classes of errors."""


class Error(Exception):
    """Base exception for Fly-in configuration, parsing, and simulation errors.

    Args:
        msg (str): Human-readable error message.
    """

    def __init__(self, msg: str):
        """Initialize an error with a human-readable message.

        Args:
            msg (str): Message describing the error.
        """
        super().__init__(msg)
        ERROR_CLR = '\033[31m'
        error = """
░▒▓████████▓▒░▒▓███████▓▒░░▒▓███████▓▒░ ░▒▓██████▓▒░░▒▓███████▓▒░
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░
░▒▓██████▓▒░ ░▒▓███████▓▒░░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░
░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░

"""
        print(f"{ERROR_CLR}{error}")


class ParseError(Error):
    """Triggered primarily when a parsing error occurs."""


class DotenvError(Error):
    """Triggered primarily when a dotenv error occurs."""


class GraphError(Error):
    """Triggered primarily when a graph error occurs."""


class BlockedZone(Error):
    """Triggered primarily by a zone error or a blockage."""


class RenderError(Error):
    """Triggered primarily by a render flag error."""


class VelocityError(Error):
    """Raised when the configured simulation speed is invalid."""
