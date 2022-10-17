#!/bin/bash

if [ -f report/test_results.txt ]; then
    echo "report/test_results.txt exists."
    echo "removing old results."
    rm report/test_results.txt
    echo "creating new pytest results."
    pytest --tb=no >> report/test_results.txt
    exit 0
else
    echo "creating new pytest results."
    pytest --tb=no >> report/test_results.txt
    exit 0
fi

echo "Something went wrong...or did it?"
exit 1