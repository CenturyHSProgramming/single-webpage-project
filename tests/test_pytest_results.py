"""
Checks report/test_results.txt for number of passes and failures
"""

import pytest


@pytest.fixture
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
    yield results


# @pytest.fixture
# def general_results(overall_results):
#     data = overall_results
#     output = []
#     for description, number in data:
#         for i in range(number):
#             if "passed" in description.lower():
#                 output.append("Pass")
#             else:
#                 output.append("failed")
#     return output


# @pytest.mark.parametrize("item", general_results)
# def test_general_requirements(item):
#     if "passed" == item:
#         assert True
#     else:
#         assert False
