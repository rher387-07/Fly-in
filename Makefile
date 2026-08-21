# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: hery-rak <hery-rak@student.42antananari    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/14 13:42:54 by hery-rak          #+#    #+#              #
#    Updated: 2026/08/21 14:46:39 by hery-rak         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

RESET = \033[0m
BOLD_ITALIC = \033[1;3m
BG_GREEN = \033[42m
BG_BLUE = \033[44m
CLR_RED = \033[31m
CLR_GREEN = \033[32m
CLR_WHITE = \033[37m

DEPENDENCE=pyproject.toml
SRC=main.py

POETRY=poetry
ENV=env
LIST=list
REMOVE=remove


PYTHON=python
RUN=run
DEBUG=pdb

RM=rm
FLAG_RM= -rf

FLAKE8=flake8
MYPY=mypy
FLAG_MYPY=--warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
FLAG_MYPY_STRICT=--strict


install: $(DEPENDENCY)
	@echo "$(BG_GREEN)$(CLR_WHITE)$(BOLD_ITALIC)	Run virtual environment with poetry$(RESET)";
	@$(POETRY) install
	@echo ""

run: install $(SRC)
	@echo "$(CLR_GREEN)$(BOLD_ITALIC)	run the program with poetry$(RESET)"
	@$(POETRY) $(RUN) $(PYTHON) $(SRC)
	@echo ""

debug: install $(SRC)
	@echo "$(CLR_GREEN)$(BOLD_ITALIC)	Run debug with pdb$(RESET)"
	@$(POETRY) $(RUN) $(PYTHON) -m $(DEBUG) $(SRC)
	@echo ""

clean:
	@echo "$(CLR_RED)$(BOLD_ITALIC)	Run cleanup$(RESET)"
	@$(RM) $(FLAG_RM) __pycache__ .pytest_cache .mypy_cache
	@find . -type d -name "__pycache__" -exec $(RM) $(FLAG_RM) {} + -prune 2>/dev/null || true
	@echo ""

lint: install
	@echo "$(CLR_RED)$(BOLD_ITALIC)		Code verification with flake8 and mypy$(RESET)"

	@echo "$(BG_BLUE)$(CLR_WHITE)	flake8$(RESET)"
	$(POETRY) $(RUN) $(PYTHON) -m $(FLAKE8) .
	@echo ""


	@echo "$(BG_BLUE)$(CLR_WHITE)	mypy$(RESET)"
	$(POETRY) $(RUN) $(PYTHON) -m $(MYPY) . $(FLAG_MYPY)
	@echo ""


lint-strict: install
	@echo "$(CLR_RED)$(BOLD_ITALIC)		Code verification with flake8 and mypy using the "--strict" option$(RESET)"

# 	@if ![-z "${}"]
	@echo "$(BG_BLUE)$(CLR_WHITE)	flake8$(RESET)"
	$(POETRY) $(RUN) $(PYTHON) -m $(FLAKE8) .
	@echo ""

	@echo "$(BG_BLUE)$(CLR_WHITE)	mypy$(RESET)"
	$(POETRY) $(RUN) $(PYTHON) -m $(MYPY) . $(FLAG_MYPY_STRICT)
	@echo ""


.PHONY: install run debug clean lint lint-strict
