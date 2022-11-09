#!/bin/bash
NEW_TEST_RESULTS=$(pytest --tb=no | grep -v '====')


if [ -f report/test_results.txt ]; then
    echo "\nreport/test_results.txt exists."
else
    echo "FAILURE: test results do not exist."
    echo "Creating new test results (report/test_results.txt)"
    echo $NEW_TEST_RESULTS > report/test_results.txt
    exit 19
fi


old_test_results=$(report/test_results.txt)
echo "Old test results are as follows..."
echo $old_test_results

if [ "$new_results_top" = "$old_test_results" ]; then
    echo "Test results are up to date!"
    exit 0
else
    #echo "FAILURE: report/test_results.txt is not up to date!"
    #> report/test_results.txt
    #pytest --tb=no >> report/test_results.txt
    exit 11
fi