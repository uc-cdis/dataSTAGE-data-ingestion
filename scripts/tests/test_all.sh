git clone https://github.com/bats-core/bats-core.git
cd bats-core
sudo ./install.sh /usr/local

cd ..
bats *.bats

pip install pipenv || curl https://raw.githubusercontent.com/kennethreitz/pipenv/master/get-pipenv.py | python
pipenv install --dev
python -m pytest tests.py

exit
