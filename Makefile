PYTHON ?= python3
MAP ?= maps/easy/01_linear_path.txt

install:
	@echo "Dependencies are managed by pyproject.toml"

run:
	$(PYTHON) main.py $(MAP)

debug:
	$(PYTHON) -m pdb main.py $(MAP)

clean:
	find . -type d \( -name __pycache__ -o -name .mypy_cache -o -name .pytest_cache \) -prune -exec rm -rf {} +

lint:
	$(PYTHON) -m flake8 . --exclude=venv,.venv
	$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(PYTHON) -m flake8 . --exclude=venv,.venv
	$(PYTHON) -m mypy . --strict

.PHONY: install run debug clean lint lint-strict
