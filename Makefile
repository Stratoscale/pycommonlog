.PHONY: all test build test_py2 test_py3 lint_py2 lint_py3
ARTIFACT=dist/strato_common_log-*-py2.py3-none-any.whl
all: lint test build

test: test_py2 test_py3

test_py3:
	PYTHONPATH=$(PWD)/py python3 py/strato/common/log/tests/test.py

test_py2:
	PYTHONPATH=$(PWD)/py python2.7 py/strato/common/log/tests/test.py

lint: lint_py2 lint_py3

lint_py3:
	python3 -m pep8 py --max-line-length=120

lint_py2:
	python2.7 -m pep8 py --max-line-length=120

build: $(ARTIFACT)

clean:
	find . -name *.pyc -delete
	find . -name __pycache__ -delete
	rm -rf dist */*.egg-info build *.stratolog

$(ARTIFACT):
	python3 -m build --wheel
