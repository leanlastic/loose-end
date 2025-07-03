import os
import subprocess
import typer
import requests
from github import Github
from typing import Optional

app = typer.Typer(
    help="🚀 Loose-End CLI Tool - Create GitHub issues with intelligent project linking",
    epilog="Examples:\n  loose-end\n  loose-end 'Bug fix' 'Fixed login issue' -p\n  loose-end 'Feature' 'Add dark mode' -p 'My Project'\n  loose-end --debug"
)

def debug_print(message: str, debug_enabled: bool = False):
    """Print debug message only if debug is enabled"""
    if debug_enabled:
        typer.echo(f"🔍 {message}", err=True)

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

def get_projects_for_repo(token: str, owner: str, repo: str, debug: bool = False) -> list:
    """Fetch projects for the repository using GitHub GraphQL API"""
    try:
        # GraphQL query to get projects linked to the repository
        query = """
        query($owner: String!, $repo: String!) {
          repository(owner: $owner, name: $repo) {
            projectsV2(first: 20) {
              nodes {
                id
                title
                number
              }
            }
          }
        }
        """
        
        debug_print("GraphQL query for repository projects", debug)
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": {"owner": owner, "repo": repo}},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if "data" in data and data["data"]["repository"]:
                projects = data["data"]["repository"]["projectsV2"]["nodes"]
                project_list = [{"id": p["id"], "name": p["title"], "number": p["number"]} for p in projects]
                debug_print(f"Repository projects response: {len(project_list)} projects found", debug)
                
                # If no repository projects, try organization projects
                if len(project_list) == 0:
                    return get_org_projects(token, owner)
                
                return project_list
            else:
                debug_print("No repository data found or access denied", debug)
                return get_org_projects(token, owner)
        else:
            debug_print(f"GraphQL request failed: {response.status_code}", debug)
            return []
    except Exception as e:
        debug_print(f"Error fetching projects: {str(e)}", debug)
        return []

def add_issue_to_project(token: str, project_id: str, issue_node_id: str, debug: bool = False) -> bool:
    """Add an issue to a project using GitHub GraphQL API"""
    try:
        mutation = """
        mutation($projectId: ID!, $contentId: ID!) {
          addProjectV2ItemById(input: {
            projectId: $projectId
            contentId: $contentId
          }) {
            item {
              id
            }
          }
        }
        """
        
        debug_print("Adding issue to project via GraphQL", debug)
        debug_print(f"Project ID: {project_id}", debug)
        debug_print(f"Issue Node ID: {issue_node_id}", debug)
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": mutation, "variables": {"projectId": project_id, "contentId": issue_node_id}},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if "data" in data and data["data"]["addProjectV2ItemById"]:
                typer.echo(typer.style("✅ Issue successfully added to project!", fg=typer.colors.GREEN))
                return True
            else:
                debug_print(f"GraphQL response: {data}", debug)
                return False
        else:
            debug_print(f"GraphQL mutation failed: {response.status_code}", debug)
            return False
    except Exception as e:
        debug_print(f"Error adding issue to project: {str(e)}", debug)
        return False

def get_org_projects(token: str, owner: str, debug: bool = False) -> list:
    """Fetch organization projects using GitHub GraphQL API"""
    try:
        query = """
        query($owner: String!) {
          organization(login: $owner) {
            projectsV2(first: 20) {
              nodes {
                id
                title
                number
              }
            }
          }
        }
        """
        
        debug_print("GraphQL query for organization projects", debug)
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": {"owner": owner}},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if "data" in data and data["data"]["organization"]:
                projects = data["data"]["organization"]["projectsV2"]["nodes"]
                project_list = [{"id": p["id"], "name": p["title"], "number": p["number"]} for p in projects]
                debug_print(f"Organization projects response: {len(project_list)} projects found", debug)
                return project_list
            else:
                debug_print("No organization data found or access denied", debug)
                return []
        else:
            debug_print(f"GraphQL request failed: {response.status_code}", debug)
            return []
    except Exception as e:
        debug_print(f"Error fetching org projects: {str(e)}", debug)
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
def loose_end(
    title: Optional[str] = typer.Argument(None, help="Issue title"),
    description: Optional[str] = typer.Argument(None, help="Issue description"),
    project: Optional[str] = typer.Option(None, "-p", "--project", help="Project name to link to, or use first project if -p without value"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug output")
):
    """
    Create a GitHub issue and optionally link it to a project.
    
    Run without arguments for interactive mode, or provide title and description for fast mode.
    Use -p to auto-link to first project, or -p "Project Name" for specific project.
    """
    # Step 1: Check if we're inside a git repo
    if not check_if_git_repo():
        typer.echo(typer.style("❌ This is not a Git repository.", fg=typer.colors.RED), err=True)
        raise typer.Exit(1)
    
    # Step 2: Get the remote URL and parse owner/repo from it
    remote_url = get_remote_url()
    if not remote_url:
        typer.echo(typer.style("❌ No remote URL found. Make sure the repo has a remote set.", fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    # Step 3: Extract owner and repo from the remote URL
    if remote_url.startswith("git@github.com:"):
        # SSH URL format: git@github.com:owner/repo.git
        repo_part = remote_url.replace("git@github.com:", "").replace(".git", "")
        owner, repo = repo_part.split("/")
    elif "github.com" in remote_url:
        # HTTPS URL format: https://github.com/owner/repo.git
        parts = remote_url.split("/")
        owner, repo = parts[-2], parts[-1].replace(".git", "")
    else:
        typer.echo(typer.style("❌ Unsupported remote URL format. Only GitHub URLs are supported.", fg=typer.colors.RED), err=True)
        raise typer.Exit(1)
    
    # Debug logging
    debug_print(f"Remote URL: {remote_url}", debug)
    debug_print(f"Owner: {owner}, Repo: {repo}", debug)
    debug_print(f"Will attempt to access: {owner}/{repo}", debug)

    # Step 4: Get GitHub token and authenticate
    token = get_github_token()
    gh = Github(token)
    
    # Step 5: List available projects for the repo
    projects = get_projects_for_repo(token, owner, repo, debug)
    project_names = [project["name"] for project in projects]
    
    # Debug logging for projects
    debug_print(f"Found {len(projects)} projects for {owner}/{repo}", debug)
    for i, proj in enumerate(projects):
        debug_print(f"Project {i+1}: {proj}", debug)
    debug_print(f"Project names: {project_names}", debug)

    # Step 6: Handle project selection based on available projects and CLI args
    selected_project = None
    
    # Handle -p flag
    if project is not None:  # -p flag was used
        if project == "":  # -p without value, use first project
            if projects:
                selected_project = projects[0]["name"]
                typer.echo(typer.style(f"📋 Auto-selected first project: {selected_project}", fg=typer.colors.GREEN))
            else:
                typer.echo(typer.style("❌ No projects found to auto-select", fg=typer.colors.RED), err=True)
        else:  # -p with specific project name
            matching_projects = [p for p in projects if p["name"].lower() == project.lower()]
            if matching_projects:
                selected_project = matching_projects[0]["name"]
                typer.echo(typer.style(f"📋 Selected project: {selected_project}", fg=typer.colors.GREEN))
            else:
                typer.echo(typer.style(f"❌ Project '{project}' not found", fg=typer.colors.RED), err=True)
                raise typer.Exit(1)
    elif projects:
        # Interactive mode - ask about project linking
        link_project = typer.confirm(typer.style("🔗 Would you like to link this to a project?", fg=typer.colors.BLUE), default=True)
        if link_project:
            if len(projects) == 1:
                # Auto-select if only one project
                selected_project = projects[0]["name"]
                typer.echo(typer.style(f"📋 Auto-selected project: {selected_project}", fg=typer.colors.GREEN))
            else:
                # Multiple projects - show numbered list
                typer.echo(typer.style("📋 Available projects:", fg=typer.colors.BLUE))
                for i, p in enumerate(projects, 1):
                    typer.echo(f"  {typer.style(str(i), fg=typer.colors.YELLOW)}. {p['name']}")
                
                while True:
                    try:
                        choice = typer.prompt("Select project (number) or 'n' to skip", type=str)
                        if choice.lower() == 'n':
                            selected_project = None
                            break
                        choice_num = int(choice)
                        if 1 <= choice_num <= len(projects):
                            selected_project = projects[choice_num - 1]["name"]
                            break
                        else:
                            typer.echo(typer.style(f"Please enter a number between 1 and {len(projects)}", fg=typer.colors.RED))
                    except ValueError:
                        typer.echo(typer.style("Please enter a valid number or 'n'", fg=typer.colors.RED))
    else:
        typer.echo(typer.style("📋 No projects found for this repository", fg=typer.colors.YELLOW))

    # Handle title and description (fast mode vs interactive)
    if title is None:
        title = typer.prompt(typer.style("📝 Issue Title", fg=typer.colors.BLUE))
    if description is None:
        description = typer.prompt(typer.style("📄 Issue Description", fg=typer.colors.BLUE))

    # Step 7: Show confirmation overview
    typer.echo("\n" + typer.style("="*50, fg=typer.colors.CYAN))
    typer.echo(typer.style("📋 SUMMARY", fg=typer.colors.CYAN, bold=True))
    typer.echo(typer.style("="*50, fg=typer.colors.CYAN))
    typer.echo(f"{typer.style('Title:', fg=typer.colors.BLUE, bold=True)} {title}")
    typer.echo(f"{typer.style('Description:', fg=typer.colors.BLUE, bold=True)} {description}")
    typer.echo(f"{typer.style('Repository:', fg=typer.colors.BLUE, bold=True)} {typer.style(f'{owner}/{repo}', fg=typer.colors.GREEN)}")
    typer.echo(f"{typer.style('Project:', fg=typer.colors.BLUE, bold=True)} {typer.style(selected_project if selected_project else 'None', fg=typer.colors.GREEN if selected_project else typer.colors.YELLOW)}")
    typer.echo(typer.style("="*50, fg=typer.colors.CYAN))
    
    if not typer.confirm(typer.style("✨ Create this issue?", fg=typer.colors.GREEN, bold=True), default=True):
        typer.echo(typer.style("❌ Issue creation cancelled", fg=typer.colors.RED))
        raise typer.Exit(0)

    # Step 8: Create the issue on GitHub
    try:
        debug_print(f"Attempting to access repository: {owner}/{repo}", debug)
        repository = gh.get_repo(f"{owner}/{repo}")
        debug_print("Repository found successfully", debug)
        debug_print(f"Creating issue with title: '{title}'", debug)
        debug_print(f"API call: POST /repos/{owner}/{repo}/issues", debug)
        
        debug_print(f"Payload: {{\"title\": \"{title}\", \"body\": \"{description}\"}}", debug)
        issue = repository.create_issue(
            title=title,
            body=description
        )

        # Step 8: If linked to project, add the issue to the project board
        if selected_project and projects:
            project_data = next((p for p in projects if p["name"] == selected_project), None)
            if project_data:
                try:
                    success = add_issue_to_project(token, project_data["id"], issue.node_id, debug)
                    if not success:
                        typer.echo(typer.style("⚠️  Issue created but failed to add to project", fg=typer.colors.YELLOW), err=True)
                except Exception as e:
                    typer.echo(typer.style(f"⚠️  Issue created but failed to add to project: {str(e)}", fg=typer.colors.YELLOW), err=True)
        
        # Step 9: Success message
        typer.echo(typer.style(f"✅ Issue created successfully! {issue.html_url}", fg=typer.colors.GREEN, bold=True))

    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg and "personal access token" in error_msg:
            typer.echo(typer.style(f"❌ Failed to create issue: {error_msg}", fg=typer.colors.RED), err=True)
            typer.echo(typer.style("💡 Token permission issue. Check your token type:", fg=typer.colors.YELLOW), err=True)
            typer.echo(typer.style("   • Classic token: needs 'repo' scope", fg=typer.colors.YELLOW), err=True)
            typer.echo(typer.style("   • Fine-grained token: needs 'Issues' write permission", fg=typer.colors.YELLOW), err=True)
            typer.echo(typer.style("💡 Update at: https://github.com/settings/tokens", fg=typer.colors.BLUE), err=True)
        else:
            typer.echo(typer.style(f"❌ Failed to create issue: {error_msg}", fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    app()

