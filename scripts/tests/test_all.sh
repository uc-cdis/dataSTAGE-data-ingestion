# Run this file from within the scripts/tests/ directory with ./test_all.sh

unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    CYGWIN*)    machine=Cygwin;;
    MINGW*)     machine=MinGw;;
    *)          machine="UNKNOWN:${unameOut}"
esac
echo "Running on ${machine}"

pipenv --version
if [ $? != 0 ]; then
    curl https://raw.githubusercontent.com/kennethreitz/pipenv/master/get-pipenv.py | python || pip install pipenv
fi
pipenv install --dev
pipenv run python -m pytest tests.py

bats -v
if [ $? != 0 ] && [ $machine != 'Mac' ]; then
    git clone https://github.com/bats-core/bats-core.git
    cd bats-core
    sudo ./install.sh /usr/local
    cd ..
fi

bats -v
if [ $? != 0 ] && [ $machine == 'Mac' ]; then
    brew install bats-core
fi

cd ..
bats tests/*.bats

exit
