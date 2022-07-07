# Single Web Page Project
Students are asked to create a single web page designed to give information about a student-selected topic using Headings (h1 & h2), paragraphs, links, images, and bold and italics.

Students are also asked to apply basic CSS styles for fonts, colors, and images.

## Instructions
1. Clone or Fork this project.
2. Create a new html file named index.html in the project folder.
3. Select a topic for your web page project.
4. Title your web page in the `title` tag of the head and the `h1` tag in the body.
5. Divide your topic into a minimum of 2 sections using a `h2` tag.
6. Throughout working on this project, track your changes and updates on an ongoing basis through well-written commits.
7. Add content to fill out each section being sure to include all required elements (paragraphs, lists, images).
8. Use the `figure` tag for each image and be sure to add appropriate credits and captions using the `figcaption` tag.
9. Run your HTML through the ***[w3c online validator](https://validator.w3.org/#validate_by_upload)*** 
10. Fix any errors
11. Style your page by adding colors and fonts.
12. Make sure the colors go well together and provide a high contrast between light and dark.
13. Test your colors using the ***[WebAIM Color Contrast Checker](https://webaim.org/resources/contrastchecker/)*** and fix the colors if necessary.
14. Run your CSS through the ***[W3C CSS Validation Service](https://jigsaw.w3.org/css-validator/#validate_by_upload)*** and fix any errors.
15. Once you have met all requirements and are satisfied with your work, make one last commit of your project. 

## How to test your work as you go
This project uses the Python programming language to test your project to make sure you have met all requirements (see below). 

### Pre-reqs
If you wish to test your project locally, be sure to have the following installed on your machine: 
* [Python v3.6 or higher](https://www.python.org/downloads/) 
* [Pipenv](https://pypi.org/project/pipenv/) - you can install pipenv using pip (once you have Python installed on your machine)

### Testing your project
1. Activate your Pip environment: In the terminal (or Git BASH), enter `pipenv shell`
2. If using a text editor, you might have to set the Python Interpreter
    * In VSCode:
      1. Click View > Command Palette
      2. Type `Python: Select Interpreter`
      3. Select the option that shows both the repo name in parentheses and a path that begins with `~\.virtualenvs\...` trailing after it.
3. Run the tests by entering `pytest` in the terminal (or GitBASH or command prompt, etc.)
    * To get more details, you can enter `pytest -v` instead
4. Read the names of the tests you failed to get an idea which requirement/s you did not meet.
5. For a more user-friendly format, check the file: `report/report.html`
6. You may continue working on your project and committing your changes until you pass all tests.

## Style Guidelines
When selecting skills and practices, we will be using the [Mozilla Developer Network](https://developer.mozilla.org/) as the final arbiter of styles and best practices.

## IMPORTANT
For this to work correctly, you must 
* only place your web project files in the project folder.
* leave the README.md file in the project folder alone.

## Project Structure & Architecture
Python® is used as the scripting language for performing tests and reports.
We are still selecting license and folder structure.

## Student Proficiency Ranking (levels)
### 101 (Entry Level)
#### HTML
At this level, students are just getting started. They can make single web pages, albeit with some errors.
Elements that students should be proficient at before moving on are as follows:
* headers
* paragraphs
* style
* links
* images
#### CSS
Students at this level only need to demonstrate basic CSS syntax and adjusting colors, background colors, and fonts (at a minimum a font applied to body (or html)). In addition, color and background color must be applied to body or html and meet color contrast analyzer
