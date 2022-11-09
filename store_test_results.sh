#!/bin/bash
NEW_TEST_RESULTS=$(pytest --tb=no | grep -v '====\|FAILED\|test_pytest_results.py')


if [[ -f report/test_results.txt && -f report/old_test_results.txt ]]; then
    echo "both tests exist."
    echo $NEW_TEST > report/test_results.txt
    echo $OLD_TEST > report/old_test_results.txt
elif [ -f report/test_results.txt ]; then
    echo "Copying new test as old test results (first time)"
    echo $NEW_TEST_RESULTS > report/old_test_results.txt
    exit 0
else
    echo "FAILURE: test results do not exist."
    echo "Creating new test results (report/test_results.txt)"
    echo $NEW_TEST > report/test_results.txt
    exit 19
fi


OLD_TEST=$(cat report/test_results.txt)
# echo "Old test is as follows..."
# echo $OLD_TEST

if [ "$NEW_TEST" = "$OLD_TEST" ]; then
    echo "Test results are up to date!"
    exit 0
else
    echo "FAILURE: report/test_results.txt is not up to date!"
    echo $OLD_TEST > report/old_test_results.txt
    echo $NEW_TEST_RESULTS > report/test_results.txt
    exit 11
fi