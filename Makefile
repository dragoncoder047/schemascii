.PHONY: docs must_specify

must_specify:
	@echo "there is no default makefile rule"
	@exit 1

docs:
	python3 scripts/docs.py
