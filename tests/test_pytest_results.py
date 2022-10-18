"""
Checks report/test_results.txt for number of passes and failures
"""

import get_pytest_results as pt_results
import pytest

pt_results.get_general_test_results()

# TODO:
# write a script to call test_general_requirements.py and
# test_html_requirements and store the results in variables
# NOTE: keep this as pytest, but have the script that runs pytest
# be its own script


def general_results(overall_results):
    data = overall_results[1:3]
    output = []
    output = get_results_list(data)
    return output


def html_results(overall):
    data = overall[4:]
    output = []
    output = get_results_list(data)
    return output


def get_results_list(data):
    results = []
    for description, number in data:
        for i in range(number):
            if "passed" in description.lower():
                results.append("Pass")
            else:
                results.append("failed")
    return results


results = pt_results.overall_results()
general = general_results(results)
html = html_results(results)


@pytest.mark.parametrize("item", general)
def test_general_requirements(item):
    if "Pass" == item:
        print("We have a passed general requirements test.")
        assert True
    else:
        print("We have a failed general requirements test.")
        assert False


@pytest.mark.parametrize("test", html)
def test_html_requirements(test):
    if "Pass" == test:
        print("We have a passed HTML requirements test.")
        assert True
    else:
        print("We have a failed HTML requirements test.")
        assert False
