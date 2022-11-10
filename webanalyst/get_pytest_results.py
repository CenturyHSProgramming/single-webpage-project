"""
Calls pytest scripts (not test_pytest though) and stores results
"""

# TODO:
# write a script to call test_general_requirements.py and
# test_html_requirements.py and store the results in variables
# to be used later


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


def get_general_test_results(all_results) -> list:
    """returns a list of the pytest general test results"""
    results = []
    prep = all_results[1:3]
    for result, num in prep:
        if "Passed" in result:
            for i in range(num):
                results.append("passed")
        else:
            for i in range(num):
                results.append("failed")
    return results


def get_html_test_results(all_results) -> list:
    results = []
    prep = all_results[4:]
    for result, num in prep:
        if "Passed" in result:
            for i in range(num):
                results.append("passed")
        else:
            for i in range(num):
                results.append("failed")
    return results


def get_css_test_results(all_results) -> list:
    """ extracts all test data from test_css_requirements """
    results = []
    return results


if __name__ == "__main__":
    overall = overall_results()
    general_results = get_general_test_results(overall)
    html_results = get_html_test_results(overall)
    print(html_results)
