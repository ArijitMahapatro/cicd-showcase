#!/usr/bin/env python3
"""
pipeline_status.py — Check GitHub Actions pipeline status via API
Demonstrates: Python CLI tooling for developer workflows

Usage:
  python scripts/pipeline_status.py --repo YOUR_USERNAME/cicd-showcase
  python scripts/pipeline_status.py --repo YOUR_USERNAME/cicd-showcase --branch main
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime


def get_workflow_runs(repo: str, branch: str, token: str) -> list:
    url = f"https://api.github.com/repos/{repo}/actions/runs?branch={branch}&per_page=5"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "cicd-showcase-cli")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())["workflow_runs"]
    except Exception as e:
        print(f"Error fetching runs: {e}")
        return []


STATUS_ICON = {
    "success":   "\033[92m✓\033[0m",
    "failure":   "\033[91m✗\033[0m",
    "in_progress": "\033[93m●\033[0m",
    "cancelled": "\033[90m○\033[0m",
    "skipped":   "\033[90m–\033[0m",
}


def main():
    parser = argparse.ArgumentParser(description="Check GitHub Actions pipeline status")
    parser.add_argument("--repo",   required=True, help="GitHub repo (owner/name)")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--token",  default=os.environ.get("GITHUB_TOKEN", ""))
    args = parser.parse_args()

    if not args.token:
        print("Error: set GITHUB_TOKEN env var or pass --token")
        sys.exit(1)

    runs = get_workflow_runs(args.repo, args.branch, args.token)
    if not runs:
        print("No runs found.")
        sys.exit(0)

    print(f"\n\033[1mPipeline Status — {args.repo} ({args.branch})\033[0m")
    print(f"{'Name':<35} {'Status':<15} {'Conclusion':<12} {'Time'}")
    print("─" * 80)

    for run in runs:
        conclusion = run.get("conclusion") or run.get("status", "unknown")
        icon = STATUS_ICON.get(conclusion, "?")
        created = run["created_at"][:16].replace("T", " ")
        print(f"{run['name']:<35} {icon} {run['status']:<13} {conclusion:<12} {created}")

    print()
    latest = runs[0]
    if latest.get("conclusion") == "success":
        print("\033[92mLatest pipeline: PASSED\033[0m")
        sys.exit(0)
    elif latest.get("status") == "in_progress":
        print("\033[93mLatest pipeline: IN PROGRESS\033[0m")
        sys.exit(0)
    else:
        print("\033[91mLatest pipeline: FAILED\033[0m")
        sys.exit(1)


if __name__ == "__main__":
    main()
