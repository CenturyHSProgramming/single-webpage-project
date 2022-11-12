#!/bin/bash
NEW_TEST_RESULTS=$(pytest --tb=no | grep -v '====\|FAILED\|test_pytest_results.py')

# store test results in report folder
echo $NEW_TEST_RESULTS > report/test_results.txt

ERRORS_COLLECTING=$(cat report/test_results.txt)
ERROR_MSG="!!! Interrupted"

if [[ $ERRORS_COLLECTING == *"$ERROR_MSG"* ]];
then
    echo $'\e[1;31m'!!! NOTICE: Pytest was interrupted. !!!$'\e[0m'
    echo -e "\nYour commit was interrupted as well."
    echo -e "This is most likely due to first time creation of test_results.txt file.\n"
    echo $'\e[1;33m'Please re-stage and re-run your last commit.$'\e[0m'

else
    echo "Pytest results successfully captured."
    git add *
    exit 0
fi

if [[ -f report/test_results.txt ]]; then
    echo "Test results successfully saved."
    git add report/test_results.txt
    exit 0
else
    echo "Having trouble saving test results."

    exit 21
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