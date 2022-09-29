"""
Tests all HTML project requirements
"""

import pytest
from webanalyst import report
import webcode_tk.css as css

path = "project/"


# Generate report for testing
my_report = report.Report(path)
my_report.generate_report()
report_details = my_report.html_report.report_details



