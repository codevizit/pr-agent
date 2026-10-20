from agent.clients.github import GitHubClient


def fetch_diff(state: dict) -> dict:
    files = GitHubClient().list_pr_files(state["pr_number"])
    return {
        "diff_files": [
            {
                "path": f["filename"],
                "status": f["status"],
                "additions": f["additions"],
                "deletions": f["deletions"],
                "patch": f.get("patch"),  # missing for binary or very large files
            }
            for f in files
        ]
    }