"""
Utilities for GitHub PR blog post generation
"""
import requests
import re
from typing import Dict, List, Optional, Tuple, Any
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def print_progress(message: str, emoji: str = "🔄", style: str = "bold", color: str = "blue") -> None:
    """
    Print a colorful progress message to the console
    
    Args:
        message: The message to print
        emoji: Emoji to prepend to the message
        style: Text style (bold, italic, underline)
        color: Text color (blue, green, yellow, red, magenta, cyan)
    """
    # ANSI escape codes for styling
    styles = {
        "bold": "\033[1m",
        "italic": "\033[3m",
        "underline": "\033[4m",
        "reset": "\033[0m"
    }
    
    colors = {
        "blue": "\033[94m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "magenta": "\033[95m",
        "cyan": "\033[96m"
    }
    
    # Apply styling
    style_code = styles.get(style.lower(), "")
    color_code = colors.get(color.lower(), "")
    reset = styles["reset"]
    
    # Print the message
    print(f"{color_code}{style_code}{emoji} {message}{reset}")
    sys.stdout.flush()  # Ensure the message is displayed immediately

def fetch_pr_data(repo_owner: str, repo_name: str, pr_number: int) -> Dict[str, Any]:
    """
    Fetch pull request data from GitHub API
    
    Args:
        repo_owner: Owner of the repository
        repo_name: Name of the repository
        pr_number: Pull request number
        
    Returns:
        Dictionary containing PR data
    """
    github_token = os.environ.get("GITHUB_TOKEN")
    headers = {"Authorization": f"token {github_token}"} if github_token else {}
    
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()

def fetch_pr_commits(repo_owner: str, repo_name: str, pr_number: int) -> List[Dict[str, Any]]:
    """
    Fetch commits for a pull request
    
    Args:
        repo_owner: Owner of the repository
        repo_name: Name of the repository
        pr_number: Pull request number
        
    Returns:
        List of commit data
    """
    github_token = os.environ.get("GITHUB_TOKEN")
    headers = {"Authorization": f"token {github_token}"} if github_token else {}
    
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/commits"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()

def fetch_pr_diff(repo_owner: str, repo_name: str, pr_number: int) -> str:
    """
    Fetch the diff for a pull request
    
    Args:
        repo_owner: Owner of the repository
        repo_name: Name of the repository
        pr_number: Pull request number
        
    Returns:
        Diff content as string
    """
    github_token = os.environ.get("GITHUB_TOKEN")
    headers = {
        "Authorization": f"token {github_token}" if github_token else "",
        "Accept": "application/vnd.github.v3.diff"
    }
    
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.text

def search_web(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """
    Search the web for related content
    
    Args:
        query: Search query
        num_results: Number of results to return
        
    Returns:
        List of search results with title and snippet, or empty list if search fails
    """
    try:
        # This is a placeholder. In a real implementation, you would use a search API
        # like Google Custom Search, Bing Search, or a similar service
        
        # TODO: Replace with actual search API implementation
        # For example, using Google Custom Search API:
        # from googleapiclient.discovery import build
        # service = build("customsearch", "v1", developerKey=os.environ.get("GOOGLE_API_KEY"))
        # res = service.cse().list(q=query, cx=os.environ.get("GOOGLE_CSE_ID"), num=num_results).execute()
        # results = []
        # if "items" in res:
        #     for item in res["items"]:
        #         results.append({
        #             "title": item.get("title", ""),
        #             "url": item.get("link", ""),
        #             "snippet": item.get("snippet", "")
        #         })
        # return results
        
        # For now, return an empty list to avoid dummy links
        print_progress("Web search functionality not implemented yet. Returning empty results.", "⚠️", "bold", "yellow")
        return []
        
    except Exception as e:
        print_progress(f"Error searching the web: {str(e)}", "❌", "bold", "red")
        return []

def parse_diff(diff_content: str) -> Dict[str, Any]:
    """
    Parse a git diff to extract meaningful information
    
    Args:
        diff_content: Git diff content
        
    Returns:
        Dictionary with parsed diff information
    """
    files_changed = re.findall(r'diff --git a/(.*?) b/', diff_content)
    
    additions = len(re.findall(r'^\+[^+]', diff_content, re.MULTILINE))
    deletions = len(re.findall(r'^-[^-]', diff_content, re.MULTILINE))
    
    # Extract file extensions to determine languages used
    extensions = [os.path.splitext(file)[1] for file in files_changed if os.path.splitext(file)[1]]
    languages = list(set([ext.lstrip('.') for ext in extensions if ext]))
    
    return {
        "files_changed": files_changed,
        "file_count": len(files_changed),
        "additions": additions,
        "deletions": deletions,
        "languages": languages
    }

def summarize_commits(commits: List[Dict[str, Any]]) -> str:
    """
    Summarize commit messages into a coherent narrative
    
    Args:
        commits: List of commit data
        
    Returns:
        Summary of commits
    """
    if not commits:
        return "No commits found."
    
    commit_messages = [commit.get("commit", {}).get("message", "").split("\n")[0] for commit in commits]
    
    # Simple summary for now - in a real implementation, you might use an LLM here
    summary = "The changes include:\n\n"
    for i, message in enumerate(commit_messages, 1):
        summary += f"{i}. {message}\n"
    
    return summary

def download_image(image_url: str, save_path: str) -> bool:
    """
    Download an image from a URL and save it to a local path
    
    Args:
        image_url: URL of the image to download
        save_path: Local path to save the image to
        
    Returns:
        True if download was successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Validate the URL
        if not image_url or not image_url.startswith(('http://', 'https://')):
            print_progress(f"Invalid image URL: {image_url}", "❌", "bold", "red")
            return False
            
        # Download the image with timeout and retries
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = requests.get(image_url, stream=True, timeout=30)
                response.raise_for_status()
                
                # Verify content type is an image
                content_type = response.headers.get('Content-Type', '')
                if not content_type.startswith('image/'):
                    print_progress(f"URL does not point to an image. Content-Type: {content_type}", "❌", "bold", "red")
                    return False
                
                # Save the image to the specified path
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Verify the file was created and has content
                if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                    print_progress(f"Image downloaded successfully to {save_path}", "✅", "bold", "green")
                    return True
                else:
                    print_progress(f"Image file is empty or not created", "❌", "bold", "red")
                    retry_count += 1
                    
            except requests.exceptions.Timeout:
                print_progress(f"Timeout downloading image, retry {retry_count+1}/{max_retries}", "⚠️", "bold", "yellow")
                retry_count += 1
            except requests.exceptions.RequestException as e:
                print_progress(f"Request error: {str(e)}, retry {retry_count+1}/{max_retries}", "⚠️", "bold", "yellow")
                retry_count += 1
                
        print_progress(f"Failed to download image after {max_retries} attempts", "❌", "bold", "red")
        return False
        
    except Exception as e:
        print_progress(f"Failed to download image: {str(e)}", "❌", "bold", "red")
        return False
