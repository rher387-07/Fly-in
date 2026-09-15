# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: hery-rak <hery-rak@student.42antananari    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/09/15 09:13:09 by hery-rak          #+#    #+#              #
#    Updated: 2026/09/15 11:29:17 by hery-rak         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

POETRY = poetry
PYTHON = python
INSTALL = install
RUN = run
VISUAL = --render

DEBUG = pdb
DEPENDENCIE = pyproject.toml

SOURCE = main.py

FLAKE = flake8
MYPY = mypy
FLAG_STRICt = --strict
FLAG_MYPY = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

FIND = find .

install: $(DEPENDENCIE)
	@echo "Dependencies are managed by pyproject.toml"
	@$(POETRY) $(INSTALL)

run: install
	@$(POETRY) $(RUN) $(PYTHON) $(SOURCE)

debug:
	$(POETRY) $(RUN) $(PYTHON) -m $(DEBUG) $(SOURCE) $(MAP)

clean:
	$(FIND) -type d \( -name __pycache__ -o -name .mypy_cache -o -name .pytest_cache \) -prune -exec rm -rf {} +

lint:
	$(POETRY) $(RUN) $(PYTHON) -m $(FLAKE) .
	$(POETRY) $(RUN) $(PYTHON) -m $(MYPY) . $(FLAG_MYPY)

lint-strict:
	$(POETRY) $(RUN) $(PYTHON) -m $(FLAKE) .
	$(POETRY) $(RUN) $(PYTHON) -m $(MYPY) . $(FLAG_STRICt)

.PHONY: install run debug clean lint lint-strict
