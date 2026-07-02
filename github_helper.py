import requests

def get_repo_contents(username, repo, github_token=""):
    headers = {}
    if github_token:
        headers['Authorization'] = f'Bearer {github_token}'

    # 1. Find the default branch (e.g., main or master)
    repo_url = f"https://api.github.com/repos/{username}/{repo}"
    repo_resp = requests.get(repo_url, headers=headers)
    
    # --- NEW: Check specifically for expired/invalid tokens ---
    if repo_resp.status_code == 401:
        return None, "TOKEN_EXPIRED"
    
    if repo_resp.status_code != 200:
        error_msg = repo_resp.json().get('message', 'Unknown error')
        return None, f"GitHub Error {repo_resp.status_code}: {error_msg}"

    default_branch = repo_resp.json().get('default_branch', 'main')

    # 2. Get the full repository tree recursively
    tree_url = f"https://api.github.com/repos/{username}/{repo}/git/trees/{default_branch}?recursive=1"
    tree_resp = requests.get(tree_url, headers=headers)

    # --- NEW: Check token expiration on tree fetch too ---
    if tree_resp.status_code == 401:
        return None, "TOKEN_EXPIRED"

    if tree_resp.status_code != 200:
        error_msg = tree_resp.json().get('message', 'Unknown error')
        return None, f"Error fetching tree {tree_resp.status_code}: {error_msg}"
    
    # Extract the tree data from the response
    tree = tree_resp.json().get('tree', [])
            
    # 3. Filter for text-based code files
    allowed_extensions = {
        '.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', 
        '.cpp', '.c', '.h', '.java', '.sh', '.toml'
    }

    files_data = ""
    for item in tree:
        if item['type'] == 'blob':  # 'blob' means it's a file, not a folder
            path = item['path']
            if any(path.endswith(ext) for ext in allowed_extensions):
                # Fetch the raw text of the file
                raw_url = f"https://raw.githubusercontent.com/{username}/{repo}/{default_branch}/{path}"
                raw_resp = requests.get(raw_url, headers=headers)
                
                if raw_resp.status_code == 200:
                    files_data += f"\n\n{'='*40}\nFile: {path}\n{'='*40}\n"
                    files_data += raw_resp.text

    if not files_data:
        return None, "No readable code files found in the repository."

    return files_data, "Success"