# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: hery-rak <hery-rak@student.42antananari    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/09/15 09:13:09 by hery-rak          #+#    #+#              #
#    Updated: 2026/09/21 00:42:37 by hery-rak         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

INSTALL = install
POETRY = poetry
PYTHON = python
RUN = run

DEBUGGER = pdb

SOURCE = main.py

FLAKE = flake8
MYPY = mypy
FLAG_STRICT = --strict
FLAG_MYPY = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

FIND = find .

BOLD_ITALIC = \033[1;3m
	
CLR_BLUE = \033[34m
CLR_RED = \033[31m
CLR_GREEN = \033[32m

RESET = \033[0m

install:
	@echo "$(CLR_BLUE)$(BOLD_ITALIC)	Installation or Update of dependencies$(RESET)"
	@$(POETRY) $(INSTALL)
	@echo ""

run: install
	@echo "$(CLR_GREEN)$(BOLD_ITALIC)	Run project: Fly-In$(RESET)"
	@$(POETRY) $(RUN) $(PYTHON) $(SOURCE)

debug:
	@echo "$(CLR_BLUE)$(BOLD_ITALIC)	Run Debug$(RESET)"
	@$(POETRY) $(RUN) $(PYTHON) -m $(DEBUGGER) $(SOURCE)
	@echo ""

clean:
	@echo "$(CLR_RED)$(BOLD_ITALIC)		Run Cleanup$(RESET)"
	$(FIND) -type d \( -name __pycache__ -o -name .mypy_cache -o -name .pytest_cache \) -prune -exec rm -rf {} +
	@echo ""

flake:
	@$(POETRY) $(RUN) $(PYTHON) -m $(FLAKE) .

lint: flake
	@echo "$(CLR_RED)$(BOLD_ITALIC)		Verification of code quality and consistency$(RESET)"
	@$(POETRY) $(RUN) $(PYTHON) -m $(MYPY) . $(FLAG_MYPY)

lint-strict: flake
	@echo "$(CLR_RED)$(BOLD_ITALIC)		Verification of code quality and consistency$(RESET)"
	@$(POETRY) $(RUN) $(PYTHON) -m $(MYPY) . $(FLAG_STRICT)

.PHONY: install run debug clean flake lint lint-strict