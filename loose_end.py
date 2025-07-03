import os
import subprocess
import typer
from github import Github

app = typer.Typer()

def check_if_git_repo() -> bool:
    """Check if the current directory is a Git repository"""
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def get_remote_url() -> str:
    """Fetch the remote URL (GitHub) for the current repository"""
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""

def get_projects_for_repo(gh: Github, owner: str, repo: str) -> list:
    """Fetch projects for the repository from the GitHub API"""
    try:
        repository = gh.get_repo(f"{owner}/{repo}")
        projects = repository.get_projects()
        return [{"id": p.id, "name": p.name, "number": p.number} for p in projects]
    except Exception as e:
        return []

def get_github_token() -> str:
    """Get GitHub token from environment or ask user for input"""
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token
    
    # If the token is not set, prompt the user to input it
    token = typer.prompt("Please enter your GitHub Personal Access Token", type=str, hide_input=True)
    os.environ["GITHUB_TOKEN"] = token  # Set it as an environment variable for future use
    return token

@app.command()
def loose_end():
    """Interactive command to create a GitHub issue linked to a project"""
    # Step 1: Check if we're inside a git repo
    if not check_if_git_repo():
        typer.echo("❌ This is not a Git repository.", err=True)
        raise typer.Exit(1)
    
    # Step 2: Get the remote URL and parse owner/repo from it
    remote_url = get_remote_url()
    if not remote_url:
        typer.echo("❌ No remote URL found. Make sure the repo has a remote set.", err=True)
        raise typer.Exit(1)

    # Step 3: Extract owner and repo from the remote URL
    parts = remote_url.split("/")
    owner, repo = parts[-2], parts[-1].replace(".git", "")

    # Step 4: Get GitHub token and authenticate
    token = get_github_token()
    gh = Github(token)
    
    # Step 5: List available projects for the repo
    projects = get_projects_for_repo(gh, owner, repo)
    project_names = [project["name"] for project in projects]

    # Step 6: Prompt user for input
    link_project = typer.confirm("Would you like to link this to a project?", default=True)
    
    if link_project and project_names:
        project = typer.prompt(f"Choose a project ({', '.join(project_names)})", type=str)
    else:
        project = None

    title = typer.prompt("Issue Title")
    description = typer.prompt("Issue Description")

    # Step 7: Create the issue on GitHub
    try:
        repository = gh.get_repo(f"{owner}/{repo}")
        issue = repository.create_issue(
            title=title,
            body=description,
        )

        # Step 8: If linked to project, add the issue to the project board
        if project and projects:
            project_data = next((p for p in projects if p["name"] == project), None)
            if project_data:
                try:
                    project_obj = gh.get_project(project_data["id"])
                    # Get the first column (typically "To Do" or similar)
                    columns = list(project_obj.get_columns())
                    if columns:
                        columns[0].create_card(content_id=issue.id, content_type="Issue")
                except Exception as e:
                    typer.echo(f"⚠️  Issue created but failed to add to project: {str(e)}", err=True)
        
        # Step 9: Success message
        typer.echo(f"✅ Issue created successfully! {issue.html_url}")

    except Exception as e:
        typer.echo(f"❌ Failed to create issue: {str(e)}", err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    app()

