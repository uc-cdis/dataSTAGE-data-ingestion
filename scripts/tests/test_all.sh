git clone https://github.com/bats-core/bats-core.git
cd bats-core
sudo ./install.sh /usr/local

cd ..
bats *.bats

pip install --user pipenv
pipenv install --dev
pipenv run python -m pytest tests.py

exit
