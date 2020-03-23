brew install bats-core

cd ..
bats tests/*.bats

cd tests
pipenv shell python -m pytest tests.py

exit