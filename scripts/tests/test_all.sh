git clone https://github.com/bats-core/bats-core.git
cd bats-core
sudo ./install.sh /usr/local

cd ..
bats tests/*.bats

cd tests
pipenv install --dev
python -m pytest tests.py

exit
