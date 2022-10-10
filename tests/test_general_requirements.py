"""
Tests all general project requirements
"""

import pytest
import report

path = "project/"


@pytest.fixture
def general_report():
    """ Generates a report on all relevant project files """
    my_report = report.Report(path)
    my_report.generate_report()
    yield my_report.general_report.report_details


@pytest.fixture
def writing_goal_results(general_report):
    yield general_report['writing_goal_results']


def test_for_required_html_files(general_report):
    results = general_report['num_files_results']
    assert results['Meets HTML']


def test_for_average_words_per_sentence(writing_goal_results):
    assert writing_goal_results['meets_WPS']


def test_for_average_sentences_per_paragraph(writing_goal_results):
    assert writing_goal_results["meets_SPP"]
