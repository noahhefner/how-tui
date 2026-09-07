.PHONY: lint format format-check typecheck test check fix
lint:
	uv run ruff check ./src

format:
	uv run ruff format ./src

format-check:
	uv run ruff format --check ./src

typecheck:
	uv run ty check ./src

test:
	uv run pytest

check:
	@printf '\n=== Linting ===\n'
	uv run ruff check $(PYTHON_SRC)

	@printf '\n=== Checking Formatting ===\n'
	uv run ruff format --check $(PYTHON_SRC)

	@printf '\n=== Type Checking ===\n'
	uv run ty check $(PYTHON_SRC)

	@printf '\n✓ All checks passed!\n'

fix:
	@printf '\n=== Linting and Formatting ===\n'
	uv run ruff check --fix $(PYTHON_SRC)
	uv run ruff format $(PYTHON_SRC)

	@printf '\n✓ Formatting complete!\n'
