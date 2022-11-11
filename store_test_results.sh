#!/bin/bash
NEW_TEST_RESULTS=$(pytest --tb=no | grep -v '====\|FAILED\|test_pytest_results.py')

# store test results in report folder
echo $NEW_TEST_RESULTS > report/test_results.txt

ERRORS_COLLECTING=$(cat report/test_results.txt | grep '!!!')
echo $ERRORS_COLLECTING

if [[ -f report/test_results.txt ]]; then
    echo "Test results successfully saved."
    # TODO: Need to test for errors during test collection
    # 1 error during collection
    git add report/test_results.txt
    exit 0
else
    echo "Having trouble saving test results."

    exit 11
fi

# # We have our new test
# OLD_TEST=$(cat report/old_test_results.txt)
# NEW_TEST=$(cat report/test_results.txt)

# if [ "$NEW_TEST" = "$OLD_TEST" ]; then
#     echo "Test results are up to date!"
#     exit 0
# else
#     echo "FAILURE: report/test_results.txt is not up to date!"
#     echo $NEW_TEST > report/old_test_results.txt
#     # echo $NEW_TEST_RESULTS > report/test_results.txt
#     exit 11
# fi