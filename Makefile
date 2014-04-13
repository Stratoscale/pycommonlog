all: test check_convention

test:
	PYTHONPATH=$(PWD)/py python py/strato/common/log/tests/test.py

check_convention:
	pep8 py --max-line-length=109
