#!/usr/bin/env bash

cd ./doc &> /dev/null
cd_return=$?
if [ $cd_return -ne "0" ]
then
    cd ../doc &> /dev/null
    cd2_return=$?
    if [ $cd2_return -ne "0" ]
    then
        echo "Error: Failed to cd to doc dir. Run from bot/ or bot/scripts/."
        exit 1
    fi
fi

which sphinx-apidoc
have_sphinx=$?
if [ $have_sphinx -ne 0 ]
then
    echo "You need Sphinx. Run \"pip install sphinx\"."
    exit 1
fi

make clean
sphinx-apidoc -o . .. -f

# I don't know what the modules.rst file does, and it throws warnings.
rm modules.rst

make html

echo
echo "Open doc/.build/html/index.html in a browser for docs."
