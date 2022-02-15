all: package

test:
	PYTHONPATH=$(PWD)/py python py/strato/common/log/tests/test.py

check_convention:
	pep8 py --max-line-length=109

clean:
	rm -rf dist

package: setup.py strato_common
	python -m setup sdist
	rm -rf strato_common.egg-info