#!/bin/bash

if [ -f report/test_results.txt ]; then
    echo "report/test_results.txt exists."
    echo "removing old results."

    rm report/test_results.txt
    echo "creating new pytest results."
    pytest --tb=no >> report/test_results.txt
    echo "pytest results are saved in report/test_results.txt."
    exit 0
else
    echo "creating new pytest results."
    pytest --tb=no >> report/test_results.txt
    echo "pytest results are saved in report/test_results.txt."
    exit 0
fi

echo "Something went wrong!"
exit 1