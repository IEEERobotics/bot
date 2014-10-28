#!/usr/bin/env bash

# Check source file for PEP8 conformance.

cd ../bot2014 &> /dev/null
cd_return=$?
if [ $cd_return -ne "0" ]
then
    cd ../../bot2014 &> /dev/null
    cd2_return=$?
    if [ $cd2_return -ne "0" ]
    then
        echo "Error: Failed to cd to bot dir. Run from bot/ or bot/*."
        exit 1
    fi
fi

which pep8 &> /dev/null
have_pep8=$?
if [ $have_pep8 -ne 0 ]
then
    echo "You need pep8. Install it with your package manager."
    exit 1
fi

pep8 `find ./* -name "*.py" | grep -v "doc/"`
