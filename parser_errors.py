#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   parser_errors.py                                     :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/18 11:35:49 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/20 10:52:59 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #


class ParseError(Exception):
    """Triggered primarily when a parsing error occurs."""


class DotenvError(Exception):
    """Triggered primarily when a dotenv error occurs."""


class GraphError(Exception):
    """Triggered primarily when a graph error occurs."""


class BlockedZone(Exception):
    """Triggered primarily by a zone error or a blockage."""

class RenderError(Exception):
    """Triggered primarily by a render flag error."""
