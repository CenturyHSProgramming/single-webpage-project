"""
Tests all HTML project requirements
"""

import pytest
from webanalyst import report

path = "project/"

# Generate report for testing
my_report = report.Report(path)
my_report.generate_report()
report_details = my_report.html_report.report_details
required_elements_found = report_details['required_elements_found']
html5_essential_elements = required_elements_found['HTML5_essential_elements_found']

html5_essential_results = list(html5_essential_elements.items())


@pytest.mark.parametrize("required_html5_elements", html5_essential_results)
def test_for_essential_html5_elements(required_html5_elements):
    results = required_html5_elements[1][-1]
    assert results
