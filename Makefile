build:
	python3 setup.py sdist bdist_wheel

test:
	pytest

install_dev:
	python3 -m pip install --editable .

upload_test:
	twine upload -r testpypi "dist/*"

upload:
	twine upload "dist/*"

clean:
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache
	find . -mindepth 1 -type d -name __pycache__ -exec rm -rf {} +

.PHONY: build install_dev upload_test upload clean
