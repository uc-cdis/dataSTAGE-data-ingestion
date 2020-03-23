git clone https://github.com/bats-core/bats-core.git
cd bats-core
sudo ./install.sh /usr/local

cd ..
bats *.bats

curl https://raw.githubusercontent.com/kennethreitz/pipenv/master/get-pipenv.py | python || pip install pipenv
pipenv install --dev
pipenv run python -m pytest tests.py

exit
