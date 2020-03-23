git clone https://github.com/bats-core/bats-core.git
cd bats-core
sudo ./install.sh /usr/local

bats *.bats

pipenv install --dev
python -m pytest tests.py

exit
