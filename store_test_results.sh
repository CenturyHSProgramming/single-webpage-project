#!/bin/bash
NEW_TEST_RESULTS=$(pytest --tb=no)


if [ -f report/test_results.txt ]; then
    echo "report/test_results.txt exists."
    pytest --tb=no >> report/test_results.txt
else
    echo "FAILURE: test results do not exist."
    echo "Creating new test results (report/test_results.txt)"
    pytest --tb=no >> report/test_results.txt
    exit 19
fi

OLD_TEST_RESULTS=$(cat report/test_results.txt)

if [ "$NEW_TEST_REQUIREMENTS" = "$OLD_TEST_REQUIREMENTS" ]; then
    echo "Test results are up to date!"
    echo "$NEW_TEST_REQUIREMENTS" > report/test_results.txt
    exit 0
else
    echo "FAILURE: report/test_results.txt is not up to date!"
    pytest --tb=no >> report/test_results.txt
    exit 11
fi