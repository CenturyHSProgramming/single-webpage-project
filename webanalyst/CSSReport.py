import logging
import os
import re

import file_clerk.clerk as clerk
import webcode_tk.color_keywords as keywords
import webcode_tk.colortools as colors
import webcode_tk.css as CSSinator
import webcode_tk.html as html
import webcode_tk.validator as val
from bs4 import BeautifulSoup

import webanalyst.report as rep

logging.basicConfig(
    format="%(asctime)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S"
)
report_template_path = "webanalyst/report_template.html"
report_path = "report/report.html"


class CSSReport:
    def __init__(self, readme_list, dir_path):
        self.__dir_path = dir_path
        self.at_import_url_errors = []
        self.html_level = "0"
        self.readme_list = readme_list
        self.html_files = []
        self.project_css_by_html_file = {}
        self.font_families_used = []
        self.min_num_css_files = 0
        self.max_num_css_files = 0
        self.css_errors = {}
        self.css_file_data = []
        self.css_files = []
        self.style_tag_contents = []
        self.num_style_tags = 0
        self.linked_stylesheets = {}
        self.meets_requirements = False
        self.order_of_css_by_file = {}
        self.pages_contain_same_css_files = False
        self.repeat_selectors = {}
        self.repeat_declarations_blocks = {}
        self.set_readme_list()
        self.styles_applied_consistently = False
        self.styles_applied_to_all_pages = False
        self.stylesheet_objects = []
        self.report_details = {
            "css_level": "",
            "css_level_attained": False,
            "css_validator_goals": 0,
            "css_validator_results": {},
            "num_css_files": 0,
            "style_tags": [],
            "repeat_selectors": 0,
            "repeat_declaration_blocks": 0,
            "general_styles_goals": {},
            "standard_requirements_goals": {},
            "standard_requirements_results": {},
            "project_specific_goals": {},
            "project_specific_results": {},
            "meets_requirements": False,
        }

    def set_css_validation(self, css_validation_results):
        self.report_details["css_validator_results"] = css_validation_results
        self.css_errors.update(css_validation_results)
        self.report_details["css_validator_errors"] = len(
            css_validation_results
        )

    def generate_report(self, html_files):
        self.html_files = html_files
        self.get_project_css_by_file(html_files)
        self.get_order_of_css_by_file(html_files)
        self.get_num_css_files()
        self.get_style_tags()
        self.get_num_style_tags()
        self.get_css_code()
        self.check_pages_for_same_css_files()
        self.set_repeat_selectors()
        self.validate_css()
        self.set_repeat_declaration_blocks()
        self.get_standard_requirements()
        self.get_standard_requirements_results()
        self.get_general_styles_goals()
        self.get_general_styles_results()
        self.get_css_results()
        self.publish_results()

    def get_general_styles_goals(self):
        try:
            start = self.readme_list.index("* General Styles:") + 1
        except ValueError:
            # There's no general styles goals
            warning = "There's no General Styles Goals in README."
            warning += "Look into it."
            logging.warning(warning)
            return
        if "* Project-specific Requirements:" in self.readme_list:
            stop = self.readme_list.index("* Project-specific Requirements:")
        else:
            stop = len(self.readme_list)

        # take a slice in between for reqs
        requirements = self.readme_list[start:stop]
        details = {}
        for req in requirements:
            if "    * Font Families" in req:
                response = rep.Report.get_header_details(req)
                details = response
            elif "+ minimum" in req.lower() or "+ min" in req.lower():
                min = req.split(":")[1].strip()
                details["details"]["minimum"] = min
            elif "+ maximum" in req.lower() or "+ max" in req.lower():
                max = req.split(":")[1].strip()
                details["details"]["maximum"] = max
            elif "* color settings" in req.lower():
                # If we had already gathered requirements,
                # Let's add them before clearing them out for the next round
                if details:
                    # add details to report_details
                    item = details.pop("title")
                    self.report_details["general_styles_goals"][item] = details

                    # reset details
                    details = {"Color Settings": {}}

            elif "+ entire page colors set" in req.lower():
                description, title = self.get_title_and_description(req)
                details["Color Settings"]["details"] = {
                    "description": req.strip()
                }
                (
                    self.report_details["general_styles_goals"][
                        "Color Settings"
                    ]
                ) = details["Color Settings"]
            elif "+ headers" in req.lower():
                description, title = self.get_title_and_description(req)
                details["Color Settings"][title] = description
            elif "+ color contrast" in req.lower():
                description, title = self.get_title_and_description(req)
                details["Color Settings"][title] = {"description": description}
            elif "- normal" in req.lower():
                description, title = self.get_title_and_description(req)
                details["Color Settings"]["Color Contrast (readability)"][
                    title
                ] = description
            elif "- large" in req.lower():
                description, title = self.get_title_and_description(req)
                (
                    details["Color Settings"]["Color Contrast (readability)"][
                        title
                    ]
                ) = description
        self.report_details["general_styles_goals"][
            "Color Settings"
        ] = details["Color Settings"]

    def get_title_and_description(self, req):
        full_details = req.split(": ")
        title = full_details[0].strip()[2:]
        description = full_details[1].strip()
        return description, title

    def get_general_styles_results(self):
        goals = list(self.report_details["general_styles_goals"].items())
        all_styles_in_order = self.get_all_styles_in_order()

        # if there are no styles, we have a major failure
        if not all_styles_in_order:
            print("Oh where have all the styles gone?")

        for goal, details in goals:
            if goal == "Font Families":
                # get actual # of font families and compare to range (min max)
                font_families = self.get_font_families()
                font_count = self.get_font_count(font_families)
                min = int(details["details"]["minimum"])
                max = int(details["details"]["maximum"])
                meets = font_count >= min and font_count <= max
                self.report_details["general_styles_goals"]["Font Families"][
                    "details"
                ]["actual"] = str(font_count)
                self.report_details["general_styles_goals"]["Font Families"][
                    "details"
                ]["meets"] = meets
            elif goal == "Color Settings":
                color_settings_results = ""

                # we meet settings until we don't
                meets_color = True

                # Check for global colors
                needs_global_colors = self.needs_global_colors_set()
                global_colors = []
                if needs_global_colors:
                    # We have all styles in order let's check for global
                    # are they set?
                    global_colors = self.get_final_global_colors(
                        all_styles_in_order
                    )
                    global_colors_results = self.get_global_colors_results(
                        global_colors
                    )
                    color_settings_results += global_colors_results
                    if "fail" in global_colors_results.lower():
                        meets_color = False

                # check for headers for contrast setting and goal message
                global_headers, goal_msg = self.get_global_headers_goals(goals)
                if global_headers != "NA":
                    # we can process rules for headers
                    global_headers_colors = self.get_final_header_colors(
                        all_styles_in_order, global_colors
                    )
                    global_headers_results = self.get_global_headers_results(
                        global_headers_colors, goal_msg
                    )
                    if "fail" in global_headers_results.lower():
                        meets_color = False
                    color_settings_results += global_headers_results

                # check for color contrast
                goal_key = "Color Contrast (readability)"
                contrast_goals = goals[1][1][goal_key]
                contrast_description = str(contrast_goals).split(
                    "description': '"
                )[1][:-1]
                description_list = contrast_description.split("', '")
                contrast_description = description_list[0].capitalize() + ": "
                contrast_description += description_list[1].replace("'", "")
                contrast_description += (
                    "; " + description_list[2].replace("'", "") + "."
                )
                normal_goal = contrast_goals.get("Normal")
                large_goal = contrast_goals.get("Large")

                for page, stylesheet in all_styles_in_order:
                    color_contrasts = self.get_color_contrast_results(
                        stylesheet, normal_goal, large_goal
                    )
                    print(color_contrasts)
                # Get contrast of header colors

                self.report_details["general_styles_goals"]["Color Settings"][
                    "details"
                ]["meets"] = meets_color
                self.report_details["general_styles_goals"]["Color Settings"][
                    "results"
                ] = color_settings_results

    def get_color_contrast_results(self, styles, normal, large):
        results = {}
        global_results = CSSinator.get_global_color_details(styles.rulesets)
        self.get_color_data()
        header_results = CSSinator.get_header_color_details(styles.rulesets)

        results["Normal"] = global_results
        results["Large"] = header_results
        return results

    def get_global_headers_goals(self, goals):
        message = ""
        try:
            color_details = goals[1][1]["Headers"]
            message = "Headers must set " + color_details + " colors "
            contrast_goal = goals[1][1]["Color Contrast (readability)"][
                "Large"
            ]
            message += "at a " + contrast_goal + " level.\n"
        except IndexError:
            return "NA", "IndexError"
        except KeyError:
            return "NA", "KeyError"
        except Exception as e:
            return "NA", str(e)
        return contrast_goal, message

    def get_global_headers_results(self, global_headers_data, goals):
        """returns results on whether global headers color goals are met"""
        results = ""
        # Parse goals to identify each goal
        # Check to see if required headings are present and meet
        # Get all heading matches from goals
        # if not specified in README, it's all headings (h1 - h6)
        to_heading = "h6"
        all_headings = ["h1", "h2", "h3", "h4", "h5", "h6"]
        required = re.findall("h[1-6]", goals)
        if required:
            to_heading = required[-1]
            to_pos = all_headings.index(to_heading) + 1
            required_headings = all_headings[:to_pos]
        else:
            required_headings = all_headings

        # Check whether all HTML files address header colors
        applies_headers_results = ""
        pages_addressed = self.get_html_pages_addressed(global_headers_data)
        if len(pages_addressed) < len(self.html_files):
            for file in self.html_files:
                filename = file.split("\\")[-1]
                if filename not in pages_addressed:
                    applies_headers_results += (
                        "<li>"
                        + filename
                        + " did not apply styles to headings</li>\n"
                    )
            if applies_headers_results:
                intro = "Goal: all HTML files address header colors\n<ul>\n"
                applies_headers_results = intro + applies_headers_results
                applies_headers_results += "\n</ul>"
        # Get pertinent data on applied header colors by page and selector
        applied_colors = self.get_applied_header_colors(
            global_headers_data, pages_addressed
        )

        if "background and foreground" in goals.lower():
            # use a dictionary to store info (and possibly override at times)
            both_applied_results = ""
            for page in applied_colors.keys():
                for selector, data in applied_colors[page].items():
                    color = data.get("color")
                    bg_color = data.get("bg-color")
                    if not color or not bg_color:
                        both_applied_results += "<li>In page: " + page + " - "
                        if not color:
                            both_applied_results += "color was not applied "
                        else:
                            both_applied_results += (
                                "background color was not applied "
                            )
                        both_applied_results += (
                            "by the " + selector + " selector</li>\n"
                        )
            if both_applied_results:
                intro = (
                    "Headers must set background and foreground colors\n<ul>\n"
                )
                both_applied_results = intro + both_applied_results + "</ul>\n"

        # Check whether all required headers
        required_heading_results = self.get_required_headers_results(
            required_headings, global_headers_data, pages_addressed
        )
        if required_heading_results:
            intro = (
                "Required Headers are NOT addressed. See the following:\n<ul>"
            )
            required_heading_results = intro + required_heading_results
            required_heading_results += "</ul>"

        # Check color contrast of all global headers
        color_contrast_results = self.get_header_color_contrast(
            applied_colors, goals
        )
        # Final check of all global headers goals
        if (
            applies_headers_results
            or both_applied_results
            or required_heading_results
            or color_contrast_results
        ):
            results = "<b>Header Colors Applied: Fail</b><br>\n "
            results += applies_headers_results + both_applied_results
            results += required_heading_results + color_contrast_results

        return results

    def get_required_headers_results(self, required, data, pages):
        results = ""
        # were all required headers present on each page?
        for page in pages:
            # get a copy of required headers
            target_headers = required[:]

            for item in data:
                item.get("html_file")

                # remove any header selector from copy of required
                if item.get("html_file") == page:
                    selector = item.get("selector")

                    if selector in target_headers:
                        target_headers.remove(selector)

                    if not target_headers:
                        break

            # check to see if all header selectors have been applied
            if target_headers:
                for header_selector in target_headers:
                    results += "<li>In " + page + ": "
                    results += header_selector + " was not applied.</li>\n"

        # If we have results, it's a fail
        if results:
            result = "Fail: not all required heading selectors are present"
            results = result + "\n<ul>" + results + "</ul>\n"

        return results

    def get_applied_header_colors(self, global_headers_data, pages_addressed):
        background_foreground = {}

        # make sure both are set on all headers
        # while checking, see if all required headers are present
        for page in pages_addressed:
            background_foreground[page] = {}
            for datum in global_headers_data:
                if datum.get("html_file") == page:
                    selector = datum.get("selector")
                    specificity = datum.get("specificity")
                    bg = datum.get("bg-color")
                    col = datum.get("color")
                    both_set = bool(datum.get("bg-color")) and bool(
                        datum.get("color")
                    )
                    global_bg = datum.get("global-bg-color")
                    global_col = datum.get("global-color")
                    if selector not in background_foreground[page].keys():
                        background_foreground[page][selector] = {
                            "both_set": both_set,
                            "specificity": specificity,
                            "bg-color": bg,
                            "color": col,
                            "global-bg-color": global_bg,
                            "global-color": global_col,
                        }
                    else:
                        # override if specificity is greater
                        old_specificity = background_foreground[page][
                            selector
                        ].get("specificity")
                        if specificity > old_specificity:
                            my_selector = background_foreground[page][selector]
                            my_selector["specificity"] = specificity
                            # override bg &/or color
                            if bg:
                                my_selector["bg-color"] = bg
                            if col:
                                my_selector["color"] = col
                            background = my_selector.get("bg-color")
                            foreground = my_selector.get("color")
                            if background and foreground:
                                my_selector["both_set"] = True
                            my_selector["global-bg-color"] = global_bg
                            my_selector["global-color"] = global_col
        return background_foreground

    def get_html_pages_addressed(self, global_headers_data):
        pages_addressed = []
        for item in global_headers_data:
            if item.get("html_file") not in pages_addressed:
                pages_addressed.append(item.get("html_file"))
        return pages_addressed

    def get_global_colors_results(self, global_colors):
        """Are global colors set for each HTML file?"""
        results = ""
        num_files = len(self.html_files)
        num_global_set = len(global_colors)
        global_filenames = []
        for i in global_colors:
            global_filenames.append(i.get("html_file"))

        # Check to see if all HTML files have global colors set
        if num_global_set < num_files:
            results += "<li><b>Fail</b>: not all files have global "
            "colors applied.\n<ul>\n"
            for file in self.html_files:
                filename = file.split("\\")[-1]
                if filename not in global_filenames:
                    results += (
                        "<li>File: "
                        + filename
                        + " has no global colors set.</li>\n"
                    )
            results += "</ul></li>\n"
        # Were any global styles missing a declaration (color or bg-color):
        for setting in global_colors:
            color_set = setting.get("color")
            if not color_set:
                results += "<li><b>Fail</b>: in " + setting.get("html_file")
                results += " the color property was not set.</li>\n"
            bg_color_set = setting.get("bg-color")
            if not bg_color_set:
                results += "<li>Fail: in " + setting.get("html_file")
                results += " the background-color property was not set.</li>\n"

        # If no results and global colors set, there were no problems
        if not results and num_global_set:
            results = "<b>Global Colors Set</b>: "
            results += "<b>Success</b>! All files had global colors set.\n"
            return results
        else:
            results = (
                "<b>Global Colors Set</b>: <b>Fail</b>\n<ul>\n"
                + results
                + "</ul>\n"
            )
            return results

    def needs_global_colors_set(self):
        """returns whether global colors should be set"""
        general_styles_goals = self.report_details.get("general_styles_goals")
        if general_styles_goals:
            color_settings = general_styles_goals.get("Color Settings")
            if color_settings:
                description = color_settings.get("details")
                if "Entire Page" in description.get("description"):
                    return True

        return False

    def get_color_data(self):
        """Initialize background & foreground to white & black
        Get background & foreground colors for:
        * global styles
        * headers
        * anchors (default is blue and purple for hover)
        * any other selectors
        If any declarations leave out color or background-color, use the global setting
        NOTE: we will NOT worry about the context (like applying inheritance
              of an li from ul). That's beyond my paygrade
        """
        color_data = self.set_color_data_defaults()

        # TODO:
        # Check all stylesheet objects for color_rulesets
        all_styles = self.get_all_styles_in_order()

        # Override any stylesheet rulesets with matching styletag rulesets
        # we may also have to check specificity
        global_color_errors = ""
        global_colors = self.get_final_global_colors(all_styles)
        num_html_files = len(self.html_files)
        num_files_colors_set = len(global_colors)
        if num_files_colors_set < num_html_files:
            global_color_errors += "Global colors not set on all pages\n"
        global_results = self.get_global_color_contrast(global_colors)
        if "Failure" in global_results:
            color_data["global"]["passes"] = False
        else:
            color_data["global"]["passes"] = True
        color_data["global"]["message"] = global_results

        header_color_errors = ""
        header_colors = self.get_final_header_colors(all_styles, global_colors)
        num_files_colors_set = len(header_colors)
        if num_files_colors_set < num_html_files:
            header_color_errors += "Header colors not set on all pages\n"
        header_color_contrast = self.get_header_color_contrast(
            header_colors, global_colors
        )
        print(header_color_contrast)
        return color_data

    def get_header_color_contrast(
        self, header_colors, global_colors, goals=""
    ):
        results = ""
        # default target goal is AAA, but if it's just AA, change it
        if goals and "AAA" not in goals:
            # double check
            if "AA" in goals:
                pass
        for item in global_colors:
            html_file = item.get("html_file")
            css_file = item.get("css_file")
            global_bg = item.get("bg-color")
            global_color = item.get("color")
            for item in header_colors:
                filename = html_file.split("/")[-1]
                selector = item.get("selector")

                # only operate on same file
                if (
                    item.get("html_file") == html_file
                    and item.get("css_file") == css_file
                ):
                    # attempt all colors from selector, to global, to default
                    color = item.get("color")
                    if not color:
                        color = item.get("global-color")
                        if not color:
                            if not global_color:
                                color = "#000000"
                            else:
                                color = global_color
                    color = self.get_color_hex(color)
                    if "warning" in color.lower():
                        results += "WARNING for " + filename + ": "
                        results += color
                        continue

                    # check for BG going all the way to default if necessary
                    bg_color = item.get("bg-color")
                    if not bg_color:
                        bg_color = item.get("global-bg-color")
                        if not bg_color:
                            if not global_bg:
                                bg_color = "#ffffff"
                            else:
                                bg_color = global_bg
                    bg_color = self.get_color_hex(bg_color)
                    if "warning" in bg_color.lower():
                        results += "WARNING for " + filename + ": "
                        results += bg_color
                        continue
                    # Cannot yet deal with gradients, so check first before crashing
                    gradients = self.get_gradients(header_colors)
                    if gradients:
                        print(
                            "WARNING: we have gradients and should do something"
                        )
                        continue

                    # Test for contrast
                    contrast_report = colors.get_color_contrast_report(
                        color, bg_color
                    )
                    target = self.get_color_contrast_target("Large")
                    passes = contrast_report.get(target)
                    if passes == "Fail":
                        if not results:
                            results = "<b>Fail</b>: \n<ul>"
                        results += "<li>Page " + filename + ": " + selector
                        results += " fails color contrast report for " + target
                        results += "</li>\n"
                    else:
                        if not results:
                            results = "<b>Success</b>: \n<ul>"
                        results += "<li>Page " + filename + ": " + selector
                        results += (
                            " passes color contrast report for " + target
                        )
                        results += "</li>\n"
        if results:
            results += "</ul>"
        return results

    def get_gradients(self, color_data: list) -> list:
        """Returns a list of dictionaries of files that use gradients.

        Since any given color (background or text) could potentially be a gradient,
        we need to inspect each file that uses color data to determine if it uses a
        gradient.

        If the file uses a gradient, then we must identify the file name, which property
        uses a gradient (color or bg-color), and a list of the lightest and the darkest
        color for each property that uses a gradient.

        Args:
            color_data (list): a list of dictionaries that represent a file and
                its background and foreground colors.

        Returns:
            gradients (list): a list of files with gradient data"""
        gradients = []
        for file in color_data:
            gradient_data = {}
            filename = file.get("css_file")
            bg_color = file.get("bg-color")
            color = file.get("color")
            if CSSinator.is_gradient(bg_color):
                gradient_list = CSSinator.process_gradient(bg_color)
                gradient_data[filename] = {"bg_color_gradients": gradient_list}
            if CSSinator.is_gradient(color):
                gradient_list = CSSinator.process_gradient(color)
                gradient_data[filename] = {"color_gradients": gradient_list}
            if gradient_data:
                file["gradient_data"] = gradient_data
                gradients.append(gradient_data)
        return gradients

    def get_global_color_contrast(self, global_colors):
        results = ""
        contrast_report = {}
        for file in global_colors:
            color = file.get("color")
            color = self.get_color_hex(color)
            if "warning" in color.lower():
                results += "WARNING for " + file["file"] + ": "
                results += color
                continue
            bg_color = file.get("bg-color")
            bg_color = self.get_color_hex(bg_color)
            if "warning" in bg_color.lower():
                results += "WARNING for " + file["file"] + ": "
                results += color
                continue
            # Test for contrast but only if we have both colors
            if color or bg_color:
                if not color:
                    color = "#000000"
                if not bg_color:
                    bg_color = "#ffffff"
                contrast_report = colors.get_color_contrast_report(
                    color, bg_color
                )
            results += "Results for " + file["html_file"] + ": "

            target = self.get_color_contrast_target("Normal")
            if contrast_report:
                results += self.process_contrast_report(
                    contrast_report, target
                )
            else:
                results += "FAIL: "
        return results

    def get_color_contrast_target(self, size):
        gen_style_goals = self.report_details["general_styles_goals"]
        color_goals = gen_style_goals["Color Settings"]
        contrast_goals = color_goals.get("Color Contrast (readability)")
        target = contrast_goals.get(size)
        return size + " " + target

    def get_color_contrast_goals(self, type="global"):
        # TODO: double check to see if this is even necessary
        general_styles = self.report_details.get("general_styles_goals")
        color_settings = general_styles.get("Color Settings")
        contrast = color_settings.get("Color Contrast (readability)")
        if type == "global":
            return contrast["Normal"]
        if type == "headers":
            return contrast["Large"]

    def process_contrast_report(self, report, target):
        """checks to see if passes at best level or not"""
        results = ""

        # capture contrast_report to modify
        general_goals = self.report_details.get("general_styles_goals")
        contrast_key = "Color Contrast (readability)"
        contrast_report = general_goals["Color Settings"][contrast_key]

        # extract both size and rating
        size, rating = target.split()
        meets_key = "Meets " + target
        if report[target] == "Pass":
            results += "Success: page passes at a " + rating
            results += " rating for " + size.lower() + "-sized text.\n"
            contrast_report[meets_key] = True
        else:
            results += "Failure: page does NOT pass at a " + rating
            results += " rating for " + size.lower() + "-sized text.\n"
            contrast_report[meets_key] = False
        return results

    def get_color_hex(self, color):
        color_hex = ""
        if "#" in color:
            color_hex = color
        elif keywords.is_a_keyword(color):
            color_hex = keywords.get_hex_by_keyword(color)
        elif "rgb" in color:
            color_hex = colors.rgb_to_hex(color)
        elif "hsl(" in color:
            hsl = colors.get_hsl_from_string(color)
            rgb = colors.hsl_to_rgb(hsl)
            color_hex = colors.rgb_to_hex(rgb)
        elif "hsla(" in color:
            hsla = colors.get_hsl_from_string(color)
            a = hsla[-1]
            if len(hsla) == 4 and a < 1:
                results = "Warning: you are using HSLA with "
                results += "transparency applied. We cannot "
                results += "test contrast with transparency applied.\n"
                return results
            elif len(hsla) == 4 and a == 1:
                rgb = colors.hsl_to_rgb(color[:-1])
                color_hex = colors.rgb_to_hex(rgb)
        return color_hex

    def get_all_styles_in_order(self):
        """returns each stylesheet object in order of appearance"""
        # whether that's a styletag or external stylesheet
        all_styles = []

        # loop through CSS by file
        for file in self.order_of_css_by_file.keys():
            for item in self.order_of_css_by_file[file]:
                if item == "style tag":
                    # get the stylesheet
                    styletag = self.get_styletag_object(file)
                    if styletag:
                        all_styles.append((file, styletag))
                else:
                    stylesheet = self.get_stylesheet_object(item)
                    if stylesheet:
                        all_styles.append((file, stylesheet))

        # Loop through style tags and do the same
        for tag in self.style_tag_contents:
            file = tag.href
            all_styles.append((file, tag))
        return all_styles

    def get_styletag_object(self, file):
        for styletag in self.style_tag_contents:
            if styletag.href in file:
                return styletag
        return None

    def get_stylesheet_object(self, item):
        for object in self.stylesheet_objects:
            if object.href in item:
                return object
        return None

    def get_final_header_colors(self, all_styles, global_colors={}):
        """get header colors from each stylesheet and tag"""
        styles_checked = self.get_styles_checked(all_styles)
        header_color_data = {}
        # loop through all styles that have been used
        # if colors were set on headers, add the details to
        # header_color_data's stylesheet
        for styles in styles_checked.values():
            header_colors_set = CSSinator.get_header_color_details(
                styles.rulesets
            )

            if header_colors_set:
                header_color_data[styles.href] = header_colors_set

        # We have all header styles
        # Identify all unique headings applied for each HTML document
        applied_styles = []
        for page in self.html_files:
            filename = page.split("\\")[-1]
            # intialize applied_styles for each page
            applied = {
                "html_file": filename,
                "css_file": "",
                "applied": False,
                "selector": "",
                "specificity": "",
                "bg-color": "",
                "color": "",
                "global-bg-color": "",
                "global-color": "",
                "context-bg-color": "",
                "context-color": "",
            }
            for styles in all_styles:
                filename = filename.split("/")[-1]
                if filename in styles[0]:
                    href = styles[1].href

                    # check to see if the stylesheet has header colors
                    # applied
                    if href in header_color_data.keys():
                        # get all the selectors for that stylesheet
                        selectors = header_color_data[href]

                        if ".html" in href:
                            applied["css_file"] = "styletag"
                        else:
                            applied["css_file"] = href

                        # get global bg color and color
                        global_bg_color = ""
                        global_color = ""
                        for file in global_colors:
                            if file.get("html_file") == filename:
                                global_bg_color = file.get("bg-color")
                                global_color = file.get("color")

                        for selector in selectors:
                            details = selector
                            data = applied.copy()
                            data = self.set_header_color_details(
                                data, details, global_bg_color, global_color
                            )
                            applied_styles.append(data)
                    elif styles[0] in styles[1].href:
                        # We're in a styletag: see if we have header color data
                        if header_color_data.get(href):
                            selectors = header_color_data[href]
                            if ".html" in href:
                                applied["css_file"] = "styletag"
                            else:
                                applied["css_file"] = href

                            # get global bg color and color
                            global_bg_color = ""
                            global_color = ""
                            for file in global_colors:
                                if file.get("html_file") == filename:
                                    global_bg_color = file.get("bg-color")
                                    global_color = file.get("color")

                            for selector in selectors:
                                details = selector
                                data = applied.copy()
                                data = self.set_header_color_details(
                                    data,
                                    details,
                                    global_bg_color,
                                    global_color,
                                )
                                applied_styles.append(data)

        return applied_styles

    def get_final_global_colors(self, all_styles):
        """get global colors from each stylesheet and each style tag"""
        # track which stylesheets have already been checked,
        # so there are no repetitions
        styles_checked = self.get_styles_checked(all_styles)

        # get global styles from only the styles that are checked
        # so no duplicates
        global_color_data = {}
        for styles in styles_checked.values():
            global_colors_set = CSSinator.get_global_color_details(
                styles.rulesets
            )
            if global_colors_set:
                # we have global colors set - let's do something:
                global_color_data[styles.href] = global_colors_set

        # Process to determine whether and which files have global
        applied_styles = []
        for page in self.html_files:
            filename = page.split("\\")[-1]
            # initialize applied_styles for each page
            applied = {
                "html_file": filename,
                "css_file": "",
                "applied": False,
                "selector": "",
                "specificity": "",
                "bg-color": "",
                "color": "",
            }
            for styles in all_styles:
                if styles[0] in filename:
                    href = styles[1].href
                    if href in global_color_data.keys():
                        details = global_color_data[href]
                        if ".html" in href:
                            applied["css_file"] = "styletag"
                        else:
                            applied["css_file"] = href
                        applied = self.adjust_applied(applied, details)
                    elif styles[0] == styles[1].href:
                        details = global_color_data.get(href)
                        applied = self.adjust_applied(applied, details)
            if applied["applied"]:
                applied_styles.append(applied)

        return applied_styles

    def adjust_applied(self, old_styles, new_styles):
        """returns old_styles adjusted according to new styles"""
        old_styles["applied"] = True
        # but only if there are new styles
        if new_styles:
            for style in new_styles:
                new_selector = style["selector"]
                old_selector = old_styles["selector"]
                if old_selector:
                    # we need to adjust all that applies
                    # if selectors are the same OR
                    # old specificity is greater than new, we keep
                    # all old styles unless not set

                    new_specificity = CSSinator.get_specificity(new_selector)
                    if new_specificity >= old_styles["specificity"]:
                        # new wins out for everything present
                        old_styles["selector"] = style["selector"]
                        old_styles["specificity"] = new_specificity
                        if style.get("background-color"):
                            old_styles["bg-color"] = style["background-color"]
                        elif style.get("background"):
                            old_styles["bg-color"] = style["background"]
                        if style.get("color"):
                            old_styles["color"] = style["color"]
                    else:
                        # old specificity is greater, so only apply anything not set
                        if not old_styles["bg-color"]:
                            if style.get("background-color"):
                                old_styles["bg-color"] = style[
                                    "background-color"
                                ]
                            elif style.get("background"):
                                old_styles["bg-color"] = style["background"]
                        if not old_styles["color"] and style.get("color"):
                            old_styles["color"] = style["color"]
            else:
                # this is the first time, get all styles and apply
                old_selector = style["selector"]
                old_styles["selector"] = style["selector"]
                old_styles["specificity"] = CSSinator.get_specificity(
                    old_selector
                )
                if style.get("background-color"):
                    old_styles["bg-color"] = style["background-color"]
                elif style.get("background"):
                    old_styles["bg-color"] = style["background"]
                if style.get("color"):
                    old_styles["color"] = style["color"]
        return old_styles

    def set_header_color_details(self, applied, details, global_bg, global_c):
        """sets color details to applied and adds global colors if not set"""
        applied["applied"] = True

        applied["selector"] = details["selector"]
        applied["specificity"] = CSSinator.get_specificity(details["selector"])
        if details.get("background-color"):
            applied["bg-color"] = details["background-color"]
        elif details.get("background"):
            applied["bg-color"] = details["background"]
        else:
            # background color was never set
            applied["global-bg-color"] = global_bg
        if details.get("color"):
            applied["color"] = details["color"]
        else:
            applied["global-color"] = global_c
        return applied

    def get_styles_checked(self, all_styles):
        styles_checked = {}
        for page, styles in all_styles:
            stylename = None
            if ".html" in styles.href:
                # it's a styletag
                stylename = page + " - styletag"
            else:
                stylename = styles.href
            if stylename not in styles_checked.keys():
                styles_checked[stylename] = styles
        return styles_checked

    def set_color_data_defaults(self):
        default_colors = {"color": "#000000", "background": "#ffffff"}
        general_data = {"specificity": 1, "colors": {}, "contrast": ""}
        global_colors = {"name": "global", "selector": "body"}
        anchor_defaults = {"color": "#0000ff", "background": "#ffffff"}
        color_data = {"global": {}, "headers": {}, "anchors": {}, "others": {}}
        general_data["colors"] = default_colors
        color_data["global"] = global_colors.copy()
        color_data["headers"] = general_data.copy()
        color_data["anchors"] = general_data.copy()
        color_data["anchors"]["colors"] = anchor_defaults
        return color_data

    def meets_page_colors(self, goals):
        meets = False
        try:
            if goals["Entire Page colors set"] == "background and foreground":
                for sheet in self.style_tag_contents:
                    if sheet.color_rulesets:
                        if self.are_background_and_foreground_set(sheet):
                            return True
                for sheet in self.stylesheet_objects:
                    if sheet.color_rulesets:
                        if self.are_background_and_foreground_set(sheet):
                            return True
            return meets
        except Exception as e:
            print("We have an exception most likely with the key for goals.")
            print(e)
            return False

    def are_background_and_foreground_set(self, sheet):
        for rule in sheet.color_rulesets:
            if rule.selector in ("body", "html"):
                if (
                    "background-color:" in rule.declaration_block.text
                    and rule.declaration_block.text.count("color") > 1
                ):
                    # both are set
                    print(rule.declaration_block.text)
                    return True

    def get_font_count(self, font_families):
        # Make sure there are no duplicates
        for font in font_families:
            num = font_families.count(font)
            if num > 1:
                font_families.remove(font)
        return len(font_families)

    def get_font_families(self):
        font_families = []
        for declaration in self.style_tag_contents:
            families = self.get_families(declaration)
            if families:
                for fam in families:
                    font_families.append(fam)
        for declaration in self.stylesheet_objects:
            families = self.get_families(declaration)
            if families:
                for fam in families:
                    font_families.append(fam)
        return font_families

    def get_families(self, declaration):
        families = []
        for ruleset in declaration.rulesets:
            if ruleset.declaration_block:
                for declaration in ruleset.declaration_block.declarations:
                    if declaration.property.lower() in ("font", "font-family"):
                        families.append(declaration.value)
        return families

    def get_standard_requirements(self):
        """gets all standard css requirements from readme file and stores them in
        report details

        The language in the requirements is important. If at least or minimum is
        included, then we need a minimum. If max or 'no more than' is included, then
        we need a max. If None is listed, the the min and max is 0."""

        # get index position of Standard Req and General Styles headers
        try:
            start = self.readme_list.index("* Standard Requirements:") + 1
        except ValueError:
            # there's no Standard Requirements
            logging.warning(
                "There's no Standard Requirements in README? Is that intentional? Typo?"
            )
            return
        if "* General Styles:" in self.readme_list:
            stop = self.readme_list.index("* General Styles:")
        elif "* Project-specific Requirements:" in self.readme_list:
            stop = self.readme_list.index("* Project-specific Requirements:")
        else:
            stop = len(self.readme_list)
        # take a slice in between for reqs
        requirements = self.readme_list[start:stop]

        # get each req and put into standard reqs dictionary
        for req in requirements:
            req = req.strip()
            split_req = req.split(":", 1)
            description = split_req[0][2:]
            goal_raw = split_req[1]
            min = 0
            max = "NA"

            # language to determine min & max
            if "None" in goal_raw:
                min = 0
                max = 0
            else:
                # get minimum
                if "at least" in goal_raw:
                    min = goal_raw.split("at least")[1]
                    min = re.findall(r"\d+", min)
                    min = int(min[0])
                elif "min" in goal_raw:
                    min = goal_raw.split("min")[1]
                    min = re.findall(r"\d+", min)
                    min = int(min[0])
                else:
                    min = 0

                # get maximum
                if "max" in goal_raw:
                    # split using the word 'max'
                    max_goal = goal_raw.split("max")[1]
                    max = re.findall(r"\d+", max_goal)
                    max = int(max[0])
                elif "no more than" in goal_raw:
                    # No more than implies a minimum of 0
                    max_goal = goal_raw.split("no more than")[1]
                    max = re.findall(r"\d+", max_goal)
                    max = int(max[0])
                elif "at least" in goal_raw:
                    max = "NA"
                else:
                    max = min

            # add requirements to dictionary
            self.report_details["standard_requirements_goals"][description] = {
                "min": min,
                "max": max,
            }

    def get_standard_requirements_results(self):
        errors = self.get_css_errors()
        self.get_standard_requirements_results_by_key(errors, "CSS Errors")

        repeats = len(list(self.repeat_selectors.keys()))
        self.get_standard_requirements_results_by_key(
            repeats, "Repeat selectors"
        )

        repeats = len(list(self.repeat_declarations_blocks.keys()))
        self.get_standard_requirements_results_by_key(
            repeats, "Repeat declaration blocks"
        )

    def get_standard_requirements_results_by_key(self, results, key):
        try:
            range = self.report_details["standard_requirements_goals"][key]
            min = range["min"]
            max = range["max"]
            passed = results >= min and results <= max
            # NOTE: a passed means they are within the range
            # and there are styles being applied
            styles_applied = self.get_styles_applied()
            if passed and styles_applied:
                results = "Passed"
            else:
                results = "Failed"

            self.report_details["standard_requirements_results"][key] = results
        except KeyError:
            return None

    def get_styles_applied(self):
        """returns whether any styles have been applied"""
        applied = self.css_files or self.stylesheet_objects
        return bool(applied)

    def get_css_errors(self):
        number = 0
        for errors in self.css_errors.values():
            if errors != "No errors":
                number += len(errors)
        return number

    def set_repeat_selectors(self):
        all_selectors = []
        # get the names of all linked stylesheets
        linked_stylesheets = self.get_linked_stylesheets()
        filenames = self.get_filenames_from_paths(linked_stylesheets)
        implemented_selectors = self.get_implemented_selectors(
            all_selectors, filenames
        )
        # sort then get repeated selectors (if any)
        all_selectors.sort()
        self.get_repeated_selectors(all_selectors, implemented_selectors)

    def get_repeated_selectors(self, all_selectors, implemented_selectors):
        for selector in all_selectors:
            count = all_selectors.count(selector)
            if count > 1:
                # get the stylesheets that "own" the selector
                for page in implemented_selectors.keys():
                    if selector in implemented_selectors[page]:
                        pages = self.repeat_selectors.get(selector)
                        if not pages:
                            self.repeat_selectors[selector] = [
                                page,
                            ]
                        elif page not in pages:
                            self.repeat_selectors[selector].append(page)
                        else:
                            # At this point, only append if we have not
                            # yet matched the number of pages to the count
                            if len(self.repeat_selectors[selector]) < count:
                                self.repeat_selectors[selector].append(page)

                # sort the pages
                self.repeat_selectors[selector].sort()

    def get_implemented_selectors(self, all_selectors, filenames):
        implemented_selectors = (
            self.get_selectors_from_implemented_stylesheets(
                all_selectors, filenames
            )
        )
        # get selectors from style_tag_contents
        self.get_selectors_from_style_tags(
            all_selectors, implemented_selectors
        )
        return implemented_selectors

    def get_selectors_from_style_tags(
        self, all_selectors, implemented_selectors
    ):
        for stylesheet in self.style_tag_contents:
            for selector in stylesheet.selectors:
                all_selectors.append(selector)
                try:
                    implemented_selectors[stylesheet.href].append(selector)
                except KeyError:
                    implemented_selectors[stylesheet.href] = [
                        selector,
                    ]

    def get_selectors_from_implemented_stylesheets(
        self, all_selectors, filenames
    ):
        implemented_selectors = {}
        for stylesheet_object in self.stylesheet_objects:
            if stylesheet_object.href in filenames:
                for selector in stylesheet_object.selectors:
                    if (selector, stylesheet_object.href) not in all_selectors:
                        all_selectors.append(selector)
                        try:
                            implemented_selectors[
                                stylesheet_object.href
                            ].append(selector)
                        except KeyError:
                            implemented_selectors[stylesheet_object.href] = [
                                selector,
                            ]
        return implemented_selectors

    def get_filenames_from_paths(self, linked_stylesheets):
        filenames = []
        for filename in linked_stylesheets:
            filename = clerk.get_file_name(filename)
            filenames.append(filename)
        return filenames

    def set_repeat_declaration_blocks(self):
        # no repeat blocks (per page)
        # any repeat blocks from a style tag?
        declaration_blocks = self.get_all_declaration_blocks()
        for block, sheets in declaration_blocks.items():
            count = len(sheets)
            if count > 1:
                self.repeat_declarations_blocks[block] = sheets

    def get_all_declaration_blocks(self):
        declaration_blocks = {}
        for sheet in self.style_tag_contents:
            for ruleset in sheet.rulesets:
                if ruleset.declaration_block:
                    declaration_block = "{" + ruleset.declaration_block.text
                    source = sheet.href
                    try:
                        if declaration_blocks[declaration_block]:
                            declaration_blocks[declaration_block].append(
                                source
                            )
                        else:
                            declaration_blocks[declaration_block] = [
                                source,
                            ]
                    except KeyError:
                        declaration_blocks[declaration_block] = [
                            source,
                        ]
                if "@import" in ruleset._Ruleset__text:
                    continue
        for sheet in self.stylesheet_objects:
            for ruleset in sheet.rulesets:
                # it's possible someone places html, so only process
                # if the declaration block is NOT a None type
                if ruleset.declaration_block:
                    declaration_block = "{" + ruleset.declaration_block.text
                else:
                    continue
                source = sheet.href
                try:
                    if declaration_blocks[declaration_block]:
                        declaration_blocks[declaration_block].append(source)
                    else:
                        declaration_blocks[declaration_block] = [
                            source,
                        ]
                except KeyError:
                    declaration_blocks[declaration_block] = [
                        source,
                    ]
        return declaration_blocks

    def get_linked_stylesheets(self):
        stylesheets = []
        try:
            for file, sheets in self.linked_stylesheets.items():
                for sheet in sheets:
                    if sheet not in stylesheets:
                        stylesheets.append(sheet)
        except TypeError:
            print("no stylesheet found in {}".format(file))
        return stylesheets

    def set_readme_list(self):
        readme_list = self.readme_list[:]
        for i in range(len(self.readme_list)):
            if self.readme_list[i] == "### CSS":
                break
        self.readme_list = readme_list[i:]

    def get_project_css_by_file(self, html_files):
        # create a dictionary of files in the project
        # each with a list of CSS applied
        file_dict = {}
        for file in html_files:
            filename = clerk.get_file_name(file)
            file_dict[filename] = []
            head_children = self.get_children(file, "head")
            styles = self.get_css_elements(head_children)
            body_children = self.get_children(file, "body")
            styles += self.get_css_elements(body_children)
            file_dict[filename] = styles
        self.project_css_by_html_file = file_dict

    def get_order_of_css_by_file(self, html_files):
        file_dict = {}
        for file in html_files:
            filename = clerk.get_file_name(file)
            file_dict[filename] = {"link_order": [], "stylesheets": []}
            head_children = self.get_children(file, "head")
            if head_children:
                for element in head_children:
                    tag = element.name
                    if tag == "link" or tag == "style":
                        source = element.attrs.get("href")
                        if source:
                            if "http" not in source and ".css" in source[-4:]:
                                file_dict[filename]["link_order"].append(
                                    source
                                )
                        else:
                            file_dict[filename]["link_order"].append(
                                "style tag"
                            )
        self.order_of_css_by_file = file_dict

    def check_pages_for_same_css_files(self):
        """determine if styles are applied on all pages and applied consistently"""
        # Assume it's all done correctly until proven otherwise
        applies_styles = True
        styles_list = list(self.order_of_css_by_file.values())
        for styles in styles_list:
            if not styles:
                applies_styles = False

        applied_consistently = all(
            elem == styles_list[0] for elem in styles_list
        )
        self.styles_applied_to_all_pages = applies_styles
        self.styles_applied_consistently = applied_consistently

    def extract_only_style_tags_from_css_files(self, files_with_css):
        results = {}
        for page, styles in files_with_css.items():
            results[page] = []
            for style in styles:
                if "style_tag=" not in style:
                    results[page].append(style)
        return results

    def get_children(self, path, parent):
        code = html.get_html(path)
        try:
            head = code.find(parent)
            children = head.findChildren()
            return children
        except Exception:
            return None

    def get_css_elements(self, nodes):
        styles = []
        if not nodes:
            return styles
        for el in nodes:
            if el.name == "link":
                if el.attrs["href"] and el.attrs["href"][-4:] == ".css":
                    styles.append(el.attrs["href"])
            if el.name == "style":
                # append styles to file_dict
                css_string = el.string
                css_string = str(css_string)
                styles.append("style_tag=" + css_string)
        return styles

    def get_num_css_files(self):
        css_files = clerk.get_all_files_of_type(self.__dir_path, "css")
        num_css_files = len(css_files)
        self.report_details["num_css_files"] = num_css_files
        return num_css_files

    def get_style_tags(self):
        # get HTML files
        html_files = clerk.get_all_files_of_type(self.__dir_path, "html")
        # get the contents of any style tag in each html doc
        for file in html_files:
            style_tags = html.get_elements("style", file)
            for tag in style_tags:
                filename = os.path.basename(file)
                # get tag string and check for relative @imports
                tag_string = tag.string
                if "@import" in tag_string:
                    tag_split = tag_string.split("@import")

                    # reset tag_string and rebuild by including the imported code
                    tag_string = ""
                    for code in tag_split:
                        code = code.strip()
                        if code:
                            if "url(" not in code:
                                tag_string += code
                            else:
                                import_result = self.get_at_import_code(
                                    code, filename
                                )
                                if "ERROR" in import_result:
                                    self.at_import_url_errors.append(
                                        import_result
                                    )
                                else:
                                    tag_string += import_result

                css_object = CSSinator.Stylesheet(filename, tag_string)
                self.style_tag_contents.append(css_object)
            self.report_details["style_tags"].append((file, len(style_tags)))
        return self.report_details["style_tags"]

    def get_at_import_code(self, at_import_string: str, filename: str) -> str:
        """returns CSS from at_import_string, but only if it's a locally imported
        file"""
        code = ""
        string_parts = re.split("['\"]", at_import_string)
        if len(string_parts) > 1:
            code = string_parts[1]
            if "../" in code:
                # get path while going back a folder
                filepath = self._CSSReport__dir_path
                filepath = filepath.split("/")
                if not filepath[-1]:
                    filepath = filepath[:-2]
                else:
                    filepath = filepath[:-1]
                filepath = "/".join(filepath)
                code = code.split("/")[1]
                filepath += "/" + code
                try:
                    code = clerk.file_to_string(filepath)
                except FileNotFoundError:
                    code = "<b>ERROR in {}</b>".format(filename)
                    code += ": the link to {}".format(filepath)
                    code += ", does not exist."
                    code += "Check the @import url path."
                    return code
            if "http" not in code:
                filepath = self._CSSReport__dir_path
                if "/" in code:
                    code = code.split("/")[1]
                filepath += code
                code = clerk.file_to_string(filepath)
        return code

    def get_num_style_tags(self):
        self.num_style_tags = len(self.report_details["style_tags"])
        return self.num_style_tags

    def get_css_code(self):
        """extract content from all CSS files

        Loop through order_of_css_by_file. At each file, get the position of the style
        tag. If the style tag is NOT at the end, then get all code together as a string
        and convert it into 1 stylesheet.

        If, however, the style tag is at the end, get all CSS code from the stylesheets
        and convert them to a stylesheet object, then convert styletag to a stylesheet
        object (unless I already did that, then why reinvent the wheel."""
        for file, css_list in self.order_of_css_by_file.items():
            if css_list:
                has_one_sheet = len(css_list) == 1
                if self.styletag_at_end(css_list):
                    combined_style_code = ""
                    for sheet in css_list["link_order"]:
                        if sheet != "style tag":
                            filepath = self.__dir_path + sheet
                            combined_style_code += clerk.file_to_string(
                                filepath
                            )
                        else:
                            # we've combined all link tag strings
                            # it's time to make a stylesheet (if there is code)
                            if combined_style_code:
                                combined_stylesheet = CSSinator.Stylesheet(
                                    file, combined_style_code
                                )
                                css_file_data = self.order_of_css_by_file[file]
                                css_file_data["stylesheets"].append(
                                    combined_stylesheet
                                )
                                styletag_code = self.get_combined_css(
                                    file, css_list
                                )
                                styletag_sheet = CSSinator.Stylesheet(
                                    file, styletag_code, "style tag"
                                )
                                css_file_data["stylesheets"].append(
                                    styletag_sheet
                                )
                        # Only loop one time if there is only css sheet or tag
                        if has_one_sheet:
                            break
                else:
                    combined_css = self.get_combined_css(file, css_list)
                    combined_stylesheet = CSSinator.Stylesheet(
                        file, combined_css, "combined"
                    )
                    print("Do I need to change self directly?")
                    css_list["stylesheets"].append(combined_stylesheet)

    def get_combined_css(self, file, css_list):
        combined_style_code = ""
        filenames = css_list.get("link_order")
        for sheet in filenames:
            if sheet == "style tag":
                for tag in self.style_tag_contents:
                    if tag.href == file:
                        combined_style_code += tag.text
            else:
                filepath = self.__dir_path + sheet
                combined_style_code += clerk.file_to_string(filepath)
        return combined_style_code

    def styletag_at_end(self, css_list: list) -> bool:
        return css_list.get("link_order")[-1] == "style tag"

    def file_is_linked(self, filename):
        for sheets in self.linked_stylesheets.values():
            if sheets:
                for sheet in sheets:
                    if filename in sheet:
                        return True
        return False

    def validate_css(self):
        # Get CSS validation on CSS files
        errors = 0
        for file_path in self.css_files:
            # Run css code through validator
            # Get code
            code = clerk.file_to_string(file_path)
            errors_in_file = val.validate_css(code)
            if errors_in_file:
                for error in errors_in_file:
                    print(error.contents)
            # Add to number of errors
            errors += len(errors_in_file)
            page_name = clerk.get_file_name(file_path)
            if errors > 0:
                self.process_errors(page_name, errors_in_file)
        # Get CSS validation from style tag
        for tag in self.style_tag_contents:
            tag_errors = val.validate_css(tag.text)
            # No need to process an error if we have none
            if "Congratulations!" in tag_errors[0].text:
                continue
            errors += len(tag_errors)
            if len(tag_errors) > 0:
                self.process_errors(tag.href, tag_errors)

        # add any errors to css_errors
        self.css_errors = self.report_details["css_validator_results"]

    def process_errors(self, page_name, errors):
        """receives errors and records warnings and errors"""
        errors_dict = {}
        warnings_dict = {}

        # Loop through all the errors and separate
        # error from warning
        # Must use try/except whenever adding an item
        # because it will crash if we try and append it
        # to a non-existant list
        for item in errors:
            # We need to grab all tr.error contents for errors
            error_rows = self.get_error_rows(item)

            # process errors
            if error_rows:
                errors_dict[page_name] = []
                for row in error_rows:
                    row_dict = self.get_results_details("error", row)
                    errors_dict[page_name].append(row_dict)

            # process warnings
            warning_rows = self.get_warning_rows(item)
            if warning_rows:
                warnings_dict[page_name] = []
                for row in warning_rows:
                    row_dict = self.get_results_details("warning", row)
                    warnings_dict[page_name].append(row_dict)

        if errors_dict:
            self.report_details["css_validator_results"][
                page_name
            ] = errors_dict[page_name]
        else:
            self.report_details["css_validator_results"][
                page_name
            ] = "No errors"
        if warnings_dict:
            self.report_details["css_validator_results"][
                page_name
            ] = warnings_dict[page_name]

    def get_error_rows(self, item):
        item_string = item.contents
        item_string = "".join([str(elem) for elem in item_string])
        error_soup = BeautifulSoup(item_string, "html.parser")
        error_rows = error_soup.find_all("tr", {"class": "error"})
        return error_rows

    def get_results_details(self, type, tag):
        details = {}
        # check for warning or error
        details[type] = type
        line_number = tag.contents[1]["title"]
        details["line_number"] = line_number
        context = tag.contents[3].text
        details["context"] = context
        message = tag.contents[5].text
        message = clerk.clear_extra_text(message)
        details["error_msg"] = message
        code = tag.contents[5].find("span")
        details["extract"] = code
        return details

    def get_warning_rows(self, item):
        item_string = item.contents
        item_string = "".join([str(elem) for elem in item_string])
        error_soup = BeautifulSoup(item_string, "html.parser")
        rows = error_soup.find_all("tr", {"class": "warning"})
        return rows

    def publish_results(self):
        # Get report
        report_content = html.get_html(report_path)
        # TODO Process all the CSS info into our CSS tables

        # Generate Validator Reports
        general_results = ""
        specific_results = ""
        cumulative_errors = 0
        has_errors = self.has_css_errors(self.css_errors)
        if not has_errors:
            # first of all check to make sure ANY CSS has been applied
            num_css_files = self.report_details.get("num_css_files")
            try:
                num_style_tags = self.report_details.get("style_tags")[0][1]
            except IndexError:
                num_style_tags = 0
            if num_css_files + num_style_tags == 0:
                fail = (
                    "<b>Fail</b>: No CSS styles were applied in the project."
                )
                general_results = (
                    '<tr><td colspan="4">' + fail + "</td></tr>\n"
                )
            else:
                congrats = "Congratulations, no errors were found."
                general_results = (
                    '<tr><td colspan="4">' + congrats + "</td></tr>\n"
                )
            pages = self.css_errors.keys()
            for page in pages:
                specific_results += "<tr><td>" + page + "</td>"
                specific_results += "<td>No errors found</td>"
                specific_results += "<td>NA</td>" * 2 + "</tr>\n"
        else:
            specific_results = ""
            general_results = '<tr><td colspan="4"><ul>'
            for page, errors in self.css_errors.items():
                # Process general results
                num_errors = len(errors)
                general_results += "<p>The file <b>" + page + "</b> contains "
                general_results += str(num_errors) + " errors.</p>"

                # Process specific results
                cumulative_errors += num_errors

                # process specific results
                for error in errors:
                    # get page, message, location, and extract
                    message = error["error_msg"]
                    location = error["line_number"]
                    has_extract = error.get("extract")
                    if has_extract:
                        extract = error["extract"].contents[0].strip()
                    specific_results += "<tr><td>" + page + "</td>"
                    specific_results += "<td>" + message + "</td>"
                    specific_results += "<td>" + location + "</td>"
                    if has_extract:
                        specific_results += (
                            "<td><pre>" + extract.strip() + "</pre></td></tr>"
                        )
                    else:
                        specific_results += "<td>No extract</td></tr>"
            general_results += "</td></tr>"
        # create our tbody contents for general validation
        tr_contents = BeautifulSoup(general_results, "html.parser")
        tr_id = "css-errors-outcome"
        report_content.find(id=tr_id).replace_with(tr_contents)

        # create our tbody contents for css validation errors
        tbody_contents = BeautifulSoup(specific_results, "html.parser")
        tbody_id = "css-validation-specifics"
        report_content.find(id=tbody_id).replace_with(tbody_contents)

        # Generate CSS Goals Report
        # did it meet CSS validator goals? [goal | actual | results]
        css_errors_goal = self.report_details["standard_requirements_goals"][
            "CSS Errors"
        ]
        min = css_errors_goal["min"]
        max = css_errors_goal["max"]
        css_errors_goal = "<td>CSS Errors - Min: {} Max: {}</td>".format(
            min, max
        )
        css_validator_errors = "<td>Total CSS Errors: {}</td></tr>".format(
            cumulative_errors
        )
        css_validator_results = str(bool(cumulative_errors < max))
        css_validator_results = "<td>" + css_validator_results + "</td>"
        "<tr>" + css_validator_errors + "</tr>"

        # What about general styles goals?
        # Loop through general Styles Goals and get all goals and results
        general_styles_goals = ""
        for goal, details in self.report_details[
            "general_styles_goals"
        ].items():
            # Build out the table row
            goal_details = details["details"]
            goal_details.get("description")
            has_min_max = goal_details.get("minimum")
            if has_min_max:
                min = goal_details["minimum"]
                max = goal_details["maximum"]
                actual = goal_details["actual"]
                actual_string = "Minimum: {} Maximum: {} Actual: {}".format(
                    min, max, actual
                )
                results = str(goal_details.get("meets"))
            else:
                # probably we're looking at color details
                actual_string = details.get("results")
                results = str(goal_details.get("meets"))

                # convert boolean results to reader friendly text
                if results == "True":
                    results = "Passes!"
                elif results == "False":
                    results = "Fails!"
                else:
                    # something went wrong
                    print("hoo boy! We had a problem.")

            general_styles_goals += (
                "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                    goal, actual_string, results
                )
            )

        # create our tbody contents for css general results
        tbody_contents = BeautifulSoup(general_styles_goals, "html.parser")
        tbody_id = "css-general-styles"
        report_content.find(id=tbody_id).replace_with(tbody_contents)

        # Check standard requirements goals

        # Any project specific goals?

        # Save new HTML as report/report.html
        with open(report_path, "w") as f:
            f.write(str(report_content.contents[0]))

    def has_css_errors(self, css_errors):
        for page, item in css_errors.items():
            if isinstance(item, list):
                for el in item:
                    if isinstance(el, dict):
                        error = el.get("error")
                        if error:
                            return True
            else:
                if item == "error":
                    return True
        return False

    def get_css_validation_results(self):
        results = ""
        cumulative_errors = 0
        for page in self.report_details["css_validator_results"].values():
            if page != "No errors":
                errors = 0
                for item in page:
                    if "error" in item.keys():
                        errors += 1

        print(errors)
        if not self.validator_errors:
            return '<tr><td rowspan="4">Congratulations! No Errors Found</td></tr>'
        else:
            try:
                validation_report = self.validator_errors[
                    "validation_type"
                ].copy()
            except Exception as e:
                print("Whoah Nelly")
                print(e)
            cumulative_errors = 0
            for page, errors in validation_report.items():
                num_errors = len(errors)
                error_str = str(num_errors) + " error"
                if num_errors != 1:
                    error_str += "s"
                cumulative_errors += num_errors
                cumulative_errors_string = (
                    str(cumulative_errors) + " total errors"
                )
                meets = str(
                    cumulative_errors <= self.report_details["validator_goals"]
                )
                results += rep.Report.get_report_results_string(
                    "", page, error_str, cumulative_errors_string, meets
                )
            return results

    def get_css_results(self):
        """determines overall results for CSS goals"""
        # We meet until we don't
        meets = True
        report_details = self.report_details

        # check CSS validator results
        goals = report_details.get("css_validator_goals")
        actual = report_details.get("css_validator_errors")
        if actual > goals:
            meets = False

        self.meets_requirements = meets


if __name__ == "__main__":
    pass
