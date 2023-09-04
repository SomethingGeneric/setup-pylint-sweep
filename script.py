import os
import subprocess
import requests
import shutil
import json
import subprocess
from git import Repo
from time import sleep
from random import randint

def clone_repositories(username):
    # Step 1: Get a list of the user's repositories using the GitHub API
    url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve repositories for user {username}.")
        return
    
    repositories = response.json()
    
    # git@github.com:SomethingGeneric/emailscript.git

    # Step 2: Clone each repository using Git and SSH
    for repo in repositories:
        repo_name = repo["name"]

        if not os.path.exists(repo_name):
            if not repo["archived"] and not repo["fork"]:
                ssh_url = repo["ssh_url"]
                print(f"Cloning {repo_name}...")
                # Clone the repository
                os.system(f"git clone {ssh_url}")
                print("Cloning complete.")
                with open(f"{repo_name}.json", "w") as f:
                    f.write(json.dumps(repo))
                sleep(0.002+randint(0,3))
            else:
                print(f"Skipping archived repository {repo_name}.")
        else:
            print(f"{repo_name}: repository already exists. Skipping.")

def get_repo_json(name):
    try:
        with open(f"../{name}.json") as f:
            return json.load(f.read().strip().replace("'", "\""))
    except:
        return None

def loop_through_files(username):
    # Loop through all directories (repositories)
    for repository in os.listdir():
        if os.path.isdir(repository):
            print(f"Repository: {repository}")
            
            # Loop through all files in the repository
            for root, dirs, files in os.walk(repository):
                for file in files:
                    file_path = os.path.join(root, file)
                    print(f"File: {file_path}")

def check_is_python(repo_name):
    # Check if a repository contains Python files
    for root, dirs, files in os.walk(repo_name):
        for file in files:
            if file.endswith(".py"):
                return True
    return False

def add_pylint_workflow(repo_name):
    os.chdir(repo_name)
    os.makedirs(".github/workflows", exist_ok=True)
    if not os.path.exists(".github/workflows/pylint.yml"):
        shutil.copy("../pylint.yml", ".github/workflows/pylint.yml")
    os.chdir("../")

def add_sweep_yaml(repo_name):
    os.chdir(repo_name)
    if not os.path.exists("sweep.yaml"):
        sweep_text = open("../sweep_GENERIC.yaml", "r").read()

        repo = get_repo_json(repo_name)
        existing = None

        if repo is not None:
            existing = repo["description"]

        if existing is None:
            existing = "Couldn't load existing description."
        
        if input(f"Use existing description ({existing}) for {repo_name}? (y/n): ") == "y":
            my_text = sweep_text.replace("REPODESC", existing)
        else:
            my_text = sweep_text.replace("REPODESC", input(f"Add a description of {repo_name} for sweep: "))

        with open("sweep.yaml", "w") as f:
            f.write(my_text)
    os.chdir("../")

def commit_if_changes(repo_name):
    os.chdir(repo_name)
    os.system("git add . -v")
    os.system("git commit -m \"Added sweep.yaml\"")
    os.system("git push")
    os.chdir("../")

if __name__ == "__main__":
    github_username = "SomethingGeneric"
    
    # Step 1: Clone repositories
    clone_repositories(github_username)

    for repository in os.listdir():
        if os.path.isdir(repository):
            print(f"Repository: {repository}")
            if check_is_python(repository):
                print(f"Repository {repository} contains Python files.")
                add_pylint_workflow(repository)
            add_sweep_yaml(repository)
            commit_if_changes(repository)