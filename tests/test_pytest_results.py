"""
Checks report/test_results.txt for number of passes and failures
"""

import pytest


@pytest.fixture
def results():
    """Generates a report on all relevant project files"""
    results = {
        "general requirements": {
            "passed": 0,
            "failed": 0,
        },
        "HTML requirements": {
            "passed": 0,
            "failed": 0,
        },
    }
    with open("report/test_results.txt") as f:
        lines = f.readlines()
    for line in lines:
        if "tests\\" in line:
            test_results = line.split(".py")[1]
            passed = test_results.count(".")
            failed = test_results.count("F")
            if "general_requirements" in line:
                results["general requirements"]["passed"] = passed
                results["general requirements"]["failed"] = failed
            else:
                results["HTML requirements"]["passed"] = passed
                results["HTML requirements"]["failed"] = failed
        if "short test summary" in line:
            break
    yield results


def test_for_number_of_passes(results):
    # TODO: Mark parametrize the loops here
    # Also: split test functions into each category of tests
    assert True
