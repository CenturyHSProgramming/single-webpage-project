# Single Web Page Project
Students are asked to create a single web page designed to give information about a student-selected topic using Headings (h1 & h2), paragraphs, links, images, and bold and italics.

Students are also asked to apply basic CSS styles for fonts, colors, and images.

## Instructions
### Setting up the Project
1. Clone this project.
2. Open the cloned project folder on your computer
3. Double-click on the file `single-html-page-project.code-workspace`
4. Open the Terminal in VS Code (`File > Terminal`)
5. Run `poetry install`
6. Run `poetry shell`
    1. This will show where the virtual environment is.
    2. It will start with the text: `Spawning shell within C:\...`
    3. Note the odd characters after `single-html-page-project-` that will help you know the exact virtual environment for the next step.
7. Set the Python interpreter...
    1. Click View > Command Palette
    2. Type `Python: Select Interpreter`
    3. Select the option that shows both the repo name in parentheses and a path that begins with `~\.virtualenvs\...` trailing after it.
    4. Select the path that matches the spawned shell path created by the previous step.
8. Setup up the pre-commit hooks by typing `pre-commit install`
9. Test it all out by typing: `pytest` it should show a lot of output that ends with a number that passed, failed, or were skipped.
10. If you don't see test results, see the teacher.
11. You are now ready to begin work on your project.

### Working and testing your work.
2. Create a new html file named index.html in the project folder (***It must go into the project folder, or you will not be able to pass this assignment.***)
3. Select a topic for your web page project.
4. Title your web page in the `title` tag of the head and the `h1` tag in the body.
5. Divide your topic into a minimum of 2 sections using a `h2` tag.
6. Throughout working on this project, track your changes and updates on an ongoing basis through well-written commits. ***NOTE THE FOLLOWING***
    a. Whenever you try to commit your work, there will be some pre-commit tests run
    b. You want to see everything Pass or get skipped (that's good)
    c. If anything fails, you'll need to run the `add *` and `commit -m "your message"` one more time.
    d. It should work the 2nd time
7. Add content to fill out each section being sure to include all required elements (paragraphs, lists, images).
8. Use the `figure` tag for each image and be sure to add appropriate credits and captions using the `figcaption` tag.
9. Test your project at any point by ...
    a. running pytest by typing: `pytest`
    b. doing a commit and pushing it to the repo
10. Once you run pytest or commit your changes, there should be two files you can explore to see if you had any errors in the report folder:
    a. `report.html`
    b. `test_results.txt`
11. If you are not sure what to do about anything, contact your teacher to get help.
12. Keep working on your project, committing your work until you both...
    a. no longer fail any tests.
    b. think your project is ready for your teacher to review.
13. Make one final push to the repo and check GitHub Classroom (or Google classroom) to see your grade (pts/4).

## How to test your work as you go
This project uses the Python programming language to test your project to make sure you have met all requirements (see below).

### Pre-reqs
If you wish to test your project locally, be sure to have the following installed on your machine:
* [Python v3.6 or higher](https://www.python.org/downloads/)
* [Poetry](https://python-poetry.org/) - you can install poetry using pip (once you have Python installed on your machine) using the following command from the [Installation Instructions](https://python-poetry.org/docs/#installation)
    * `curl -sSL https://install.python-poetry.org | python3 -` for Linxu, macOS, and Windows (WSL)
    * `(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -` - for Windows (in Powershell)

### Testing your project
1. Activate your Pip environment: In the terminal (or Git BASH), enter the following commands:
    * `poetry install`
    * `poetry shell`
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
