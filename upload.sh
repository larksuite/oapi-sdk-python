rm -rf dist
python setup.py bdist_wheel sdist
twine upload dist/*