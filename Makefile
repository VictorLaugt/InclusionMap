build:
	python3 setup.py sdist bdist_wheel

install_dev:
	python3 -m pip install --editable .

upload_test:
	twine upload -r testpypi "dist/*"

upload:
	twine upload "dist/*"

clean:
	rm -rf build dist *.egg-info

.PHONY: build install_dev upload_test upload clean
