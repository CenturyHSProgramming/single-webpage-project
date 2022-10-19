"""
Checks report/test_results.txt for number of passes and failures
"""

import pytest

from webanalyst import get_pytest_results as pt_results

# Get general and HTML results
total_results = pt_results.overall_results()
general_results = pt_results.get_general_test_results(total_results)
html_results = pt_results.get_html_test_results(total_results)


@pytest.mark.parametrize("item", general_results)
def test_general_requirements(item):
    if "Pass" == item:
        print("We have a passed general requirements test.")
        assert True
    else:
        print("We have a failed general requirements test.")
        assert False


@pytest.mark.parametrize("test", html_results)
def test_html_requirements(test):
    if "Pass" == test:
        print("We have a passed HTML requirements test.")
        assert True
    else:
        print("We have a failed HTML requirements test.")
        assert False
