#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   dotenv_parser.py                                     :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/18 14:54:05 by hery-rak            #+#    #+#            #
#   Updated: 2026/08/19 09:07:28 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from collections.abc import Callable
from importlib import import_module
# from parser.errors import DotenvError
from typing import Any


def dot_parse() -> list[Callable[..., Any]]:
    dotenv = import_module("dotenv")

    load_dotenv = dotenv.load_dotenv
    find_dotenv = dotenv.find_dotenv

    return [load_dotenv, find_dotenv]


# def load_dotenv() -> Callable[..., list[Callable[..., Any]]]:
#     return _import()

# def parser_dotenv() -> None:
#     load_dot, find_dot = load_dotenv()

#     path = find_dot()

#     if path == "":
#         print(
#             "[WARNING] Dotenv could not find the file '.env'. "
#             "Use 'cp .env_example .env'\n"
#             )
#     else:
#         load_dot()
#         map = os.getenv("MAP")
# def parser_dotenv() -> list[bool, str]:
#     load_dot, find_dot = _import()
#     return [load_dot, find_dot]

# parser_dotenv()
