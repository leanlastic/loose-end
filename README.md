
# Loose-End CLI Tool

The **Loose-End CLI Tool** helps you create GitHub issues directly from your terminal, with the option to link the issue to a specific project board. It prompts you for all the necessary information (like issue type, title, description, and project association) and handles the authentication to GitHub using your **Personal Access Token (PAT)**.

---

## Requirements

- **Python 3.6+**: Ensure Python is installed on your system.
- **PyGithub**: To interact with GitHub's API.
- **Typer**: To build the interactive CLI tool.

---

## Installation

### 1. Install Python

Ensure that Python 3.6 or later is installed. You can check your Python version by running:

```bash
python3 --version
```

If Python is not installed, you can download and install it from [here](https://www.python.org/downloads/).

---

### 2. Install the Loose-End CLI Tool

To install the **Loose-End CLI Tool** globally (or within a virtual environment), follow these steps:

1. **Clone the Repository or Download the Files**

   Clone the repository (or download the ZIP) and navigate to the project folder:

   ```bash
   git clone https://github.com/yourusername/loose-end-cli.git
   cd loose-end-cli
   ```

2. **Create a Virtual Environment (Optional)**

   It’s recommended to create a virtual environment to isolate dependencies for your project:

   ```bash
   # Install virtualenv if it's not already installed
   pip install virtualenv

   # Create a virtual environment
   virtualenv venv

   # Activate the virtual environment
   # On Linux/macOS
   source venv/bin/activate

   # On Windows
   venv\Scriptsctivate
   ```

3. **Install Dependencies**

   Install the required dependencies using `pip`:

   ```bash
   pip install typer[all] PyGithub
   ```

4. **Install the CLI Tool**

   Now, install the tool globally (or within your virtual environment):

   ```bash
   pip install .
   ```

   This will install the `loose-end` command and make it available globally (or within your virtual environment).

---

### 3. Running the CLI Tool

Once the tool is installed, you can run it from anywhere in your terminal:

```bash
loose-end
```

The CLI tool will prompt you for the necessary information to create a GitHub issue, including:

- **Issue or Draft**: Whether this is a new issue or a draft.
- **Link to Project**: If you want to link the issue to an existing GitHub project board.
- **Title**: The title of the issue.
- **Description**: The detailed description of the issue.

The tool will create the issue on GitHub and optionally link it to a project board if selected.

---

## Authentication

The CLI tool requires authentication with GitHub to create issues. The easiest way to authenticate is by using a **Personal Access Token (PAT)**.

- **Generate a PAT**: Follow GitHub's documentation to create a **Personal Access Token**: [Creating a personal access token](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token).
- **Enter the Token**: If the `GITHUB_TOKEN` environment variable is not set, the CLI will prompt you to enter your PAT when you run the `loose-end` command.

---

### Optional: Install as a Global Command

If you’d like to run the tool from anywhere without navigating to the project folder, you can install it globally by running:

```bash
pip install .
```

Now you can run the `loose-end` command from any directory in your terminal.

---

## Troubleshooting

1. **No GitHub Token Set**: If you don’t set the `GITHUB_TOKEN` environment variable, the tool will prompt you for the token when you run the command.
2. **Git Not Found**: Make sure you’re running the tool from within a valid Git repository.
3. **Missing Dependencies**: Run `pip install -r requirements.txt` if the dependencies are not installed.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Feel free to fork the repository and submit pull requests for new features or bug fixes!