#!/usr/bin/env python3
"""
Script to check workflow status using GitHub API.
"""

import requests
import json
import time
from datetime import datetime


def get_latest_workflow_runs(repo_owner, repo_name):
    """Get latest workflow runs for a repository."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/runs"
    
    try:
        response = requests.get(url, headers={
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Pi-Pages-Workflow-Checker'
        })
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get workflow runs: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching workflow runs: {e}")
        return None


def display_workflow_status(runs_data):
    """Display workflow status in a readable format."""
    if not runs_data or 'workflow_runs' not in runs_data:
        print("❌ No workflow runs found")
        return
    
    runs = runs_data['workflow_runs']
    
    print(f"📊 Found {len(runs)} recent workflow runs:")
    print("=" * 80)
    
    for run in runs[:10]:  # Show last 10 runs
        workflow_name = run.get('name', 'Unknown')
        status = run.get('status', 'unknown')
        conclusion = run.get('conclusion', 'unknown')
        created_at = run.get('created_at', 'unknown')
        updated_at = run.get('updated_at', 'unknown')
        
        # Convert timestamps
        try:
            created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            updated_dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            created_str = created_dt.strftime('%Y-%m-%d %H:%M:%S')
            updated_str = updated_dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            created_str = created_at
            updated_str = updated_at
        
        # Status emoji
        if status == 'completed':
            if conclusion == 'success':
                status_emoji = '✅'
            elif conclusion == 'failure':
                status_emoji = '❌'
            elif conclusion == 'cancelled':
                status_emoji = '⏹️'
            else:
                status_emoji = '❓'
        elif status == 'in_progress':
            status_emoji = '🔄'
        elif status == 'queued':
            status_emoji = '⏳'
        else:
            status_emoji = '❓'
        
        print(f"{status_emoji} {workflow_name}")
        print(f"   Status: {status} | Conclusion: {conclusion}")
        print(f"   Created: {created_str} | Updated: {updated_str}")
        print(f"   Run ID: {run.get('id', 'N/A')}")
        print(f"   Branch: {run.get('head_branch', 'N/A')}")
        print("-" * 80)


def check_specific_workflow(repo_owner, repo_name, workflow_name):
    """Check status of a specific workflow."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/{workflow_name}/runs"
    
    try:
        response = requests.get(url, headers={
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Pi-Pages-Workflow-Checker'
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('workflow_runs'):
                latest_run = data['workflow_runs'][0]
                status = latest_run.get('status', 'unknown')
                conclusion = latest_run.get('conclusion', 'unknown')
                
                print(f"📋 Latest run of '{workflow_name}':")
                print(f"   Status: {status}")
                print(f"   Conclusion: {conclusion}")
                print(f"   Run ID: {latest_run.get('id', 'N/A')}")
                
                return status, conclusion
            else:
                print(f"❌ No runs found for workflow '{workflow_name}'")
                return None, None
        else:
            print(f"❌ Failed to get workflow info: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error checking workflow: {e}")
        return None, None


def main():
    """Main function."""
    print("🚀 Pi-Pages Workflow Status Checker")
    print("=" * 50)
    
    # Repository information
    repo_owner = "1devspace"  # Replace with actual owner
    repo_name = "office-screen"  # Replace with actual repo name
    
    print(f"🔍 Checking workflows for: {repo_owner}/{repo_name}")
    print()
    
    # Get all workflow runs
    runs_data = get_latest_workflow_runs(repo_owner, repo_name)
    
    if runs_data:
        display_workflow_status(runs_data)
        
        print("\n🎯 Checking specific workflows:")
        print("-" * 30)
        
        # Check specific workflows
        workflows_to_check = [
            "ci.yml",
            "test-simple.yml",
            "test.yml",
            "security.yml"
        ]
        
        for workflow in workflows_to_check:
            status, conclusion = check_specific_workflow(repo_owner, repo_name, workflow)
            if status:
                if status == 'completed' and conclusion == 'success':
                    print(f"✅ {workflow}: SUCCESS")
                elif status == 'completed' and conclusion == 'failure':
                    print(f"❌ {workflow}: FAILED")
                elif status == 'in_progress':
                    print(f"🔄 {workflow}: RUNNING")
                else:
                    print(f"❓ {workflow}: {status} ({conclusion})")
            else:
                print(f"⚠️  {workflow}: No runs found")
    
    print("\n📊 Next Steps:")
    print("1. Check the GitHub Actions tab in your repository")
    print("2. Look for any failed workflows and check their logs")
    print("3. If workflows are failing, check the error messages")
    print("4. You can manually trigger workflows from the Actions tab")


if __name__ == "__main__":
    main() 