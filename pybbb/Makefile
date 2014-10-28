VENV_DIR=~/.virtualenvs
VENV_CONF=.venv
VENV=$(VENV_DIR)/$(shell cat ${VENV_CONF})

default: build

.PHONY: build test devinst install clean

build:
	python setup.py build

test:
	python setup.py test

devinst:
	python setup.py develop

install:
	python setup.py install

venv:
	virtualenv --clear --system-site-packages $(VENV)
	@echo Activate with \"source $(VENV)/bin/activate\"

clean:
	@rm -rf build *.egg *.egg-info *.log *.log.[0-9]*
	@find . -name "*.pyc" -print0 | xargs -0 rm -f

# vim: set noexpandtab:
