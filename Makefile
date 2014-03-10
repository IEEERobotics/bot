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
	@rm -rf build *.egg *.egg-info 
	@find . -name '*.log' -print0 | xargs -0 rm -f
	@find . -name '*.log.[0-9]*' -print0 | xargs -0 rm -f
	@find . -name "*.pyc" -print0 | xargs -0 rm -f
	@rm -rf simulator/pins/*/*

# vim: set noexpandtab:
