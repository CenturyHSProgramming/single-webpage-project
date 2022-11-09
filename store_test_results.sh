#!/bin/bash
NEW_TEST_RESULTS=$(pytest --tb=no | grep -v '====\|FAILED\|test_pytest_results.py')


if [[ -f report/test_results.txt && -f report/old_test_results.txt ]]; then
    echo "both tests exist."
    echo $NEW_TEST_RESULTS > report/test_results.txt
else
    echo "FAILURE: one or more test results do not exist."
    echo "Storing new test results in both test_results.txt and old_test_results.txt"
    echo $NEW_TEST_RESULTS > report/test_results.txt
    echo $NEW_TEST_RESULTS > report/old_test_results.txt
    exit 19
fi

# wE HAVE OUR NEW TEST
OLD_TEST=$(cat report/old_test_results.txt)
NEW_TEST=$(cat report/test_results.txt)

if [ "$NEW_TEST" = "$OLD_TEST" ]; then
    echo "Test results are up to date!"
    exit 0
else
    echo "FAILURE: report/test_results.txt is not up to date!"
    echo $NEW_TEST > report/old_test_results.txt
    # echo $NEW_TEST_RESULTS > report/test_results.txt
    exit 11
fi