$(shell mkdir -p .local)
requirements = .local/requirements

$(requirements): Makefile
	pip install pip==22.0.4 pip-tools==6.6.0 wheel==0.37.1
	touch $(requirements)


compile-requirements: $(requirements)
	pip-compile --generate-hashes requirements.in
	pip-compile --generate-hashes --output-file=requirements-dev.txt requirements-dev.in requirements.in


install-requirements-dev: $(requirements)
	pip-sync requirements-dev.txt
	pip install -e .


install-requirements: $(requirements)
	pip-sync requirements.txt
	pip install -e .


check-style: $(requirements)
	@flake8 src tests && echo "Flake8 OK"
	@isort --check-only --diff src/ tests/ || exit_on_error "Run 'make isort' to fix"


isort:
	isort src/ tests/
