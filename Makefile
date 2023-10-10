SOURCES := music_inbox
INSTALL_STAMP := .install.stamp
UV := $(shell command -v uv 2> /dev/null)

.PHONY: help clean lint format check

help:
	@echo "Please use 'make <target>' where <target> is one of the following commands.\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo "\nCheck the Makefile to know exactly what each target is doing."

install: $(INSTALL_STAMP)  ## Install dependencies
$(INSTALL_STAMP): pyproject.toml uv.lock
	@if [ -z $(UV) ]; then echo "uv could not be found. See https://docs.astral.sh/uv/"; exit 2; fi
	$(UV) --version
	$(UV) sync
	touch $(INSTALL_STAMP)

clean:  ## Delete cache files
	find . -type d -name "__pycache__" | xargs rm -rf {};
	rm -rf .install.stamp

lint: $(INSTALL_STAMP)  ## Analyze code base
	$(UV) run ruff check $(SOURCES)
	$(UV) run ruff format --check $(SOURCES)
	$(UV)x ty check $(SOURCES)

format: $(INSTALL_STAMP)  ## Format code base
	$(UV) run ruff check --fix $(SOURCES)
	$(UV) run ruff format $(SOURCES)
