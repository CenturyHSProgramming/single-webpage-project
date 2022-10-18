"""
Checks report/test_results.txt for number of passes and failures
"""

import pytest


def overall_results():
    """Generates a report on all relevant project files"""
    results = []
    with open("report/test_results.txt") as f:
        lines = f.readlines()
    for line in lines:
        if "tests\\" in line:
            test_results = line.split(".py")[1]
            passed = test_results.count(".")
            failed = test_results.count("F")
            total_tests = passed + failed
            if "general_requirements" in line:
                results.append(("General Requirements", total_tests))
            else:
                results.append(("HTML requirements", total_tests))
            results.append(("Tests Passed: ", passed))
            results.append(("Tests Failed: ", failed))
        if "short test summary" in line:
            break
    return results


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


results = overall_results()
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
