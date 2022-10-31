"""
Tests all HTML project requirements
"""

import pytest

import webanalyst.report as report

path = "webanalyst/"


def get_assigned_tags_results(data):
    results = []
    for tag, info in data.items():
        if "HTML5" in tag:
            continue
        message = f"Expecting {info[0]} <{tag}> tags. "
        message += f"Found {info[1]} <{tag}> tags."
        passed = info[-1]
        results.append((message, passed))
    return results


# Generate report for testing
my_report = report.Report(path)
my_report.generate_report()
report_details = my_report.html_report.report_details
required_elements_found = report_details["required_elements_found"]
html5_essential_elements = required_elements_found[
    "HTML5_essential_elements_found"
]

html5_essential_results = list(html5_essential_elements.items())
assigned_tags_results = get_assigned_tags_results(required_elements_found)


@pytest.mark.parametrize("required_html5_elements", html5_essential_results)
def test_for_essential_html5_elements(required_html5_elements):
    results = required_html5_elements[1][-1]
    assert results


@pytest.mark.parametrize("actual,results", assigned_tags_results)
def test_for_assigned_tag_requirements(actual, results):
    # todo: make sure I indicate at each failed test which element is gone
    print(actual)
    assert results
