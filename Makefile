SHELL := /bin/bash

.PHONY: help install install-dev install-min install-plot install-hyperopt install-freqai install-freqai-rl update reset config plot install-ui version clean-venv doctor

help:
	@echo "Common tasks:"
	@echo "  make install            # Interactive install (runs ./setup.sh -i)"
	@echo "  make install-dev        # Non-interactive full dev install"
	@echo "  make install-min        # Non-interactive minimal install"
	@echo "  make install-plot       # Minimal + plotting"
	@echo "  make install-hyperopt   # Minimal + hyperopt"
	@echo "  make install-freqai     # Minimal + FreqAI"
	@echo "  make install-freqai-rl  # Minimal + FreqAI-RL (PyTorch)"
	@echo "  make update             # Update code and deps"
	@echo "  make reset              # Hard reset develop/stable and recreate venv"
	@echo "  make config             # Generate user_data/config.json"
	@echo "  make plot               # Install plotting dependencies"
	@echo "  make install-ui         # Install Web UI"
	@echo "  make version            # Show freqtrade version"
	@echo "  make clean-venv         # Remove .venv"
	@echo "  make doctor             # Quick environment checks"

install:
	./setup.sh -i

install-dev:
	FT_NON_INTERACTIVE=1 FT_DEV=1 ./setup.sh -i

install-min:
	FT_NON_INTERACTIVE=1 ./setup.sh -i

install-plot:
	FT_NON_INTERACTIVE=1 FT_WITH_PLOT=1 ./setup.sh -i

install-hyperopt:
	FT_NON_INTERACTIVE=1 FT_WITH_HYPEROPT=1 ./setup.sh -i

install-freqai:
	FT_NON_INTERACTIVE=1 FT_WITH_FREQAI=1 ./setup.sh -i

install-freqai-rl:
	FT_NON_INTERACTIVE=1 FT_WITH_FREQAI_RL=1 ./setup.sh -i

update:
	./setup.sh -u

reset:
	./setup.sh -r

config:
	source .venv/bin/activate && freqtrade new-config -c user_data/config.json

plot:
	./setup.sh -p

install-ui:
	source .venv/bin/activate && freqtrade install-ui

version:
	source .venv/bin/activate && freqtrade --version

clean-venv:
	rm -rf .venv

# Simple environment doctor
# Checks python version and ta-lib presence without modifying the system
# Note: This does not install anything.
doctor:
	@echo "Checking python..." && \
	if command -v python3 >/dev/null 2>&1; then \
	  pyv=$$(python3 - <<'PYCHK'\
import sys; print("%d.%d.%d" % sys.version_info[:3])\
PYCHK\
	  ); echo "python3: $$pyv"; else echo "python3: NOT FOUND"; fi; \
	echo "Checking ta-lib libs..."; \
	if [ -f /usr/local/lib/libta_lib.a ] || [ -f /usr/local/lib/libta_lib.so ] || [ -f /usr/lib/libta_lib.so ]; then \
	  echo "TA-Lib: FOUND"; \
	else \
	  echo "TA-Lib: NOT FOUND (will be built by setup if needed)"; \
	fi
