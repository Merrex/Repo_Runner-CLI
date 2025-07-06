#!/usr/bin/env python3
"""
Git Repository Update Manager

This script helps manage git updates for the repo_runner project.
It can pull latest changes, check for updates, and manage the repository state.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

class GitManager:
    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path).resolve()
        self.git_path = self.repo_path / ".git"
        
    def is_git_repo(self):
        """Check if the directory is a git repository"""
        return self.git_path.exists()
    
    def get_current_branch(self):
        """Get the current branch name"""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def get_remote_url(self):
        """Get the remote URL"""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def check_for_updates(self):
        """Check if there are updates available"""
        try:
            # Fetch latest changes
            subprocess.run(
                ["git", "fetch", "origin"],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            # Check if local is behind remote
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD..origin/main"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commits_behind = int(result.stdout.strip())
            return commits_behind > 0, commits_behind
            
        except subprocess.CalledProcessError as e:
            print(f"Error checking for updates: {e}")
            return False, 0
    
    def pull_updates(self):
        """Pull latest updates from remote"""
        try:
            print("Pulling latest updates...")
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            print("Updates pulled successfully!")
            print(f"Output: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error pulling updates: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    def get_status(self):
        """Get current git status"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""
    
    def has_uncommitted_changes(self):
        """Check if there are uncommitted changes"""
        status = self.get_status()
        return bool(status.strip())
    
    def commit_changes(self, message="Auto-commit changes"):
        """Commit any uncommitted changes"""
        if not self.has_uncommitted_changes():
            print("No uncommitted changes to commit.")
            return True
        
        try:
            # Add all changes
            subprocess.run(
                ["git", "add", "."],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            # Commit changes
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            print(f"Changes committed: {message}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error committing changes: {e}")
            return False
    
    def push_changes(self):
        """Push committed changes to remote"""
        try:
            result = subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            print("Changes pushed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error pushing changes: {e}")
            return False
    
    def update_repository(self, auto_commit=True):
        """Complete repository update process"""
        print("=== Repository Update Process ===")
        
        if not self.is_git_repo():
            print("Error: Not a git repository!")
            return False
        
        current_branch = self.get_current_branch()
        remote_url = self.get_remote_url()
        
        print(f"Repository: {self.repo_path}")
        print(f"Current branch: {current_branch}")
        print(f"Remote URL: {remote_url}")
        
        # Check for uncommitted changes
        if self.has_uncommitted_changes():
            print("Found uncommitted changes:")
            print(self.get_status())
            
            if auto_commit:
                if self.commit_changes():
                    self.push_changes()
                else:
                    print("Failed to commit changes. Please handle manually.")
                    return False
            else:
                print("Please commit or stash changes before updating.")
                return False
        
        # Check for updates
        has_updates, commits_behind = self.check_for_updates()
        
        if has_updates:
            print(f"Found {commits_behind} commits behind remote.")
            if self.pull_updates():
                print("Repository updated successfully!")
                return True
            else:
                print("Failed to pull updates.")
                return False
        else:
            print("Repository is up to date.")
            return True

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Git Repository Update Manager")
    parser.add_argument("--path", default=".", help="Repository path")
    parser.add_argument("--check", action="store_true", help="Only check for updates")
    parser.add_argument("--pull", action="store_true", help="Pull updates")
    parser.add_argument("--commit", action="store_true", help="Commit changes")
    parser.add_argument("--push", action="store_true", help="Push changes")
    parser.add_argument("--auto", action="store_true", help="Auto-commit and update")
    
    args = parser.parse_args()
    
    git_manager = GitManager(args.path)
    
    if args.check:
        has_updates, commits_behind = git_manager.check_for_updates()
        if has_updates:
            print(f"Updates available: {commits_behind} commits behind")
        else:
            print("Repository is up to date")
    
    elif args.pull:
        git_manager.pull_updates()
    
    elif args.commit:
        git_manager.commit_changes()
    
    elif args.push:
        git_manager.push_changes()
    
    elif args.auto:
        git_manager.update_repository(auto_commit=True)
    
    else:
        # Default: full update process
        git_manager.update_repository(auto_commit=True)

if __name__ == "__main__":
    main() 