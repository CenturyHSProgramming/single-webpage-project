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
        min = details.get("min")
        if max == "NA":
            if goals == "Styles Applied":
                msg += f", at least {min} styletag or sheet must be applied "
                msg += "to all pages."
            if goals == "Styles Applied consistently":
                msg += ", all pages must have the same styles applied "
                msg += "consistently. What this means is the link tags and style tags"
                msg += " must appear in the same order on each page. NOTE: "
                msg += "actual styles in each style tag may be unique on each"
                msg += "page."
        else:
            msg += ", there should be no "
            if max:
                msg += f"more than {max} "
        msg += "errors."
        results.append((msg, max))

    return results


def get_css_general_results(data):
    results = []
    for details, result in data.items():
        details = "No " + details.lower()
        if result == "Passed":
            meets = True
        else:
            meets = False
        results.append((details, meets))
    return results


def get_standard_results(goals: list, results: dict) -> list:
    """compares the goals to the results and returns a list of
    description and result to be processed as test results."""
    output = []
    # for each goal description, append description and results
    goal_index = 0
    for result in results.items():
        passed = result[1]
        # make sure passed is a boolean type
        the_type = str(type(passed))
        if "bool" not in the_type:
            if passed.lower() == "failed":
                passed = False
            elif passed.lower() == "passed":
                passed = True
        message = goals[goal_index][0]
        output.append((message, passed))
        goal_index += 1

    return output


# Generate report for testing
my_report = report.Report(path)
my_report.generate_report()
report_details = my_report.css_report.report_details
general_req_results = report_details["general_styles_goals"]
standard_req_results = report_details["standard_requirements_results"]
standard_req_goals = get_css_goals(
    report_details["standard_requirements_goals"]
)
general_results = get_css_general_results(general_req_results)
standard_results = get_standard_results(
    standard_req_goals, standard_req_results
)


@pytest.mark.parametrize("description,results", general_results)
def test_for_general_css_requirements(description, results):
    print(description)
    assert results


@pytest.mark.parametrize("description,results", standard_results)
def test_for_standard_css_requirements(description, results):
    print(description)
    assert results
