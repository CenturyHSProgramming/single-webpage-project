#!/bin/bash
NEW_TEST_RESULTS=$(pytest --tb=no | grep -v '====')
echo $NEW_TEST_RESULTS


if [ -f report/test_results.txt ]; then
    echo "\nreport/test_results.txt exists."
else
    echo "FAILURE: test results do not exist."
    echo "Creating new test results (report/test_results.txt)"
    pytest --tb=no >> report/test_results.txt
    exit 19
fi


old_test_results=$(head -n 10 report/test_results.txt)

if [ "$new_results_top" = "$old_test_results" ]; then
    echo "Test results are up to date!"
    exit 0
else
    echo "FAILURE: report/test_results.txt is not up to date!"
    > report/test_results.txt
    pytest --tb=no >> report/test_results.txt
    exit 11
fi