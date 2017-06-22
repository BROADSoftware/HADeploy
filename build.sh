python setup.py clean --all
rm -rf dist/*
rm -rf build/*
rm -rf HADeploy.egg-info
plugins/setup.sh
python setup.py sdist
python setup.py bdist_wheel
rm -rf build/*

# To upload to test pip site
# python setup.py register -r https://testpypi.python.org/pypi
# twine upload dist/* -r testpypi

# To install from test pip site
# pip install -i https://testpypi.python.org/pypi HADeploy
# (Does not works, due to dependencies version pb)

 # To upload to pypi
 #
 # twine register dist/HADeploy-0.3.0rc1-py2-none-any.whl
 # twine register dist/HADeploy-0.3.0rc1.tar.gz
 # twine upload dist/*
