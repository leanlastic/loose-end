
# Loose-End CLI Tool 🚀

The **Loose-End CLI Tool** helps you create GitHub issues directly from your terminal, with intelligent project linking and a beautiful colored interface. Supports both interactive and fast CLI modes for maximum productivity.

## ✨ Features

- 🎨 **Beautiful colored interface** with intuitive prompts
- ⚡ **Fast mode**: Create issues instantly with command-line arguments
- 🔗 **Smart project linking**: Auto-select single projects, numbered selection for multiple
- 📋 **Confirmation summary** before creating issues
- 🐛 **Debug mode** for troubleshooting
- 🔐 **Secure authentication** using GitHub Personal Access Tokens

---

## Requirements

- **Python 3.6+**: Ensure Python is installed on your system.
- **PyGithub**: To interact with GitHub's API.
- **Typer**: To build the interactive CLI tool.
- **Requests**: For GitHub GraphQL API calls.

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
   pip install typer[all] PyGithub requests
   ```

4. **Install the CLI Tool**

   Now, install the tool globally (or within your virtual environment):

   ```bash
   pip install .
   ```

   This will install the `loose-end` command and make it available globally (or within your virtual environment).

---

### 3. Running the CLI Tool

## 🚀 Usage

**⚠️ Important**: The CLI must be run from within your Git project directory (the repository where you want to create issues).

### Interactive Mode
Run the tool interactively with guided prompts:
```bash
cd /path/to/your/git-project
loose-end
```

### Fast Mode
Create issues instantly with command-line arguments:
```bash
cd /path/to/your/git-project

# Basic issue creation
loose-end "Bug in login form" "The login form doesn't validate email addresses properly"

# With automatic project linking (links to first available project)
loose-end "Feature request" "Add dark mode support" -p

# With specific project linking
loose-end "Bug fix" "Fixed authentication issue" -p "My Project"
```

### Debug Mode
Enable debug output for troubleshooting:
```bash
cd /path/to/your/git-project
loose-end --debug
```

## 🎯 Command Options

| Option | Description |
|--------|-------------|
| `title` | Issue title (positional argument) |
| `description` | Issue description (positional argument) |
| `-p, --project` | Link to project (auto-select first if no name given) |
| `--debug` | Enable debug output |
| `--help` | Show help message |

## 🔄 Interactive Features

- **Smart project selection**: 
  - Auto-selects if only one project exists
  - Shows numbered menu for multiple projects
  - Option to skip project linking
- **Confirmation summary**: Review all details before creating
- **Colorful interface**: Easy-to-read colored prompts and messages

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

## 🎉 Examples

### Interactive Mode Flow
```bash
$ cd /path/to/your/git-project
$ loose-end
🔗 Would you like to link this to a project? [Y/n]: Y
📋 Auto-selected project: My Project
📝 Issue Title: Bug in user registration
📄 Issue Description: Users can't register with special characters in email

==================================================
📋 SUMMARY
==================================================
Title: Bug in user registration
Description: Users can't register with special characters in email
Repository: myorg/myapp
Project: My Project
==================================================
✨ Create this issue? [Y/n]: Y
✅ Issue created successfully! https://github.com/myorg/myapp/issues/42
```

### Fast Mode Examples
```bash
cd /path/to/your/git-project

# Quick issue without project
loose-end "Fix login bug" "Login form validation is broken"

# With auto project linking
loose-end "Add feature" "Implement dark mode" -p

# With specific project
loose-end "Update docs" "Add API documentation" -p "Documentation"
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Feel free to fork the repository and submit pull requests for new features or bug fixes!