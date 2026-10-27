PYTHON ?= python3
PYTHONFLAGS ?= -W error

PROGRAMS := \
	00-hello-world/hello.py \
	01-objects-names-types/objects.py \
	02-expressions/expressions.py \
	03-control-flow/control.py \
	04-functions/functions.py \
	05-containers-iteration/containers.py \
	05-containers-iteration/iteration.py \
	06-strings-text/strings.py \
	07-classes/classes.py \
	08-modules-packages/run_imports.py \
	09-exceptions/exceptions.py \
	10-typing/typing_demo.py \
	11-capstone/calc.py

.PHONY: all run check clean

all:
	$(PYTHON) $(PYTHONFLAGS) -m compileall -q $(PROGRAMS) 08-modules-packages/shapes

run: all
	@set -e; for program in $(PROGRAMS); do \
		printf '\n===== %s =====\n' "$$program"; \
		$(PYTHON) $(PYTHONFLAGS) "$$program"; \
	done

check:
	$(MAKE) clean
	$(MAKE) run

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
