"""
Tests all CSS project requirements
"""

import pytest

from webanalyst import report

path = "project/"


def get_css_goals(data):
    results = []
    for goals, details in data.items():
        msg = "For " + goals
        max = details.get("max")
        msg += ", there should be no "
        if max:
            msg += f"more than {max} "
        msg += "errors."
        results.append((msg, max))

    return results


def get_css_general_results(data, description):
    results = []
    for details, result in data.items():
        details = "No " + details.lower()
        if result == "Passed":
            meets = True
        else:
            meets = False
        results.append((details, meets))
    return results


# Generate report for testing
my_report = report.Report(path)
my_report.generate_report()
report_details = my_report.css_report.report_details
standard_req_results = report_details["general_styles_goals"]
standard_req_goals = get_css_goals(
    report_details["standard_requirements_goals"]
)
general_results = get_css_general_results(
    standard_req_results, standard_req_goals
)


@pytest.mark.parametrize("description,results", general_results)
def test_for_general_css_requirements(description, results):
    print(description)
    assert results
