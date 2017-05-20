python setup.py clean --all
rm -rf dist/*
rm -rf build/*
rm -rf HADeploy.egg-info
plugins/setup.sh
python setup.py sdist
python setup.py bdist_wheel
rm -rf build/*

