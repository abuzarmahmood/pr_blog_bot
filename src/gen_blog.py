"""
Main workflow for generating blog posts from GitHub pull requests
"""
import argparse
import json
import os
from typing import Dict, List, Optional, Any
from openai import OpenAI

from datetime import datetime
from dotenv import load_dotenv

from utils import (
    fetch_pr_data,
    fetch_pr_commits,
    fetch_pr_diff,
    parse_diff,
    summarize_commits,
    search_web
)

class BlogGenerator:
    """
    Generate blog posts from GitHub pull requests
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the blog generator
        
        Args:
            openai_api_key: OpenAI API key (optional, will use environment variable if not provided)
        """
        # Load environment variables from .env file
        load_dotenv()
        openai_api_key = os.environ.get("OPENAI_API_KEY")

        if openai_api_key:
            self.client = OpenAI(api_key=openai_api_key)
        else:
            raise ValueError("OpenAI API key is required. Provide it as an argument or set OPENAI_API_KEY environment variable.")

    def collect_pr_info(self, repo_owner: str, repo_name: str, pr_number: int) -> Dict[str, Any]:
        """
        Collect all information about a pull request
        
        Args:
            repo_owner: Owner of the repository
            repo_name: Name of the repository
            pr_number: Pull request number
            
        Returns:
            Dictionary with PR information
        """
        # Fetch PR data
        pr_data = fetch_pr_data(repo_owner, repo_name, pr_number)

        # Fetch commits
        commits = fetch_pr_commits(repo_owner, repo_name, pr_number)

        # Fetch and parse diff
        diff_content = fetch_pr_diff(repo_owner, repo_name, pr_number)
        diff_summary = parse_diff(diff_content)

        # Summarize commits
        commit_summary = summarize_commits(commits)

        return {
            "pr_title": pr_data.get("title", ""),
            "pr_description": pr_data.get("body", ""),
            "pr_author": pr_data.get("user", {}).get("login", ""),
            "pr_created_at": pr_data.get("created_at", ""),
            "pr_updated_at": pr_data.get("updated_at", ""),
            "pr_url": pr_data.get("html_url", ""),
            "commits": commits,
            "commit_summary": commit_summary,
            "diff_summary": diff_summary,
            "diff_content": diff_content
        }

    def generate_blog_post(self, pr_info: Dict[str, Any], user_direction: Optional[str] = None) -> str:
        """
        Generate a blog post based on PR information
        
        Args:
            pr_info: Dictionary with PR information
            user_direction: Optional user input on the direction of the blog post
            
        Returns:
            Generated blog post content
        """
        # Prepare the prompt for the LLM
        prompt = self._create_blog_prompt(pr_info, user_direction)

        # Call OpenAI API to generate the blog post
        response = self.client.chat.completions.create(model="gpt-4",  # or another appropriate model
        messages=[
            {"role": "system", "content": "You are a technical writer creating a blog post about code changes."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.7)

        return response.choices[0].message.content

    def _create_blog_prompt(self, pr_info: Dict[str, Any], user_direction: Optional[str] = None) -> str:
        """
        Create a prompt for the LLM to generate a blog post
        
        Args:
            pr_info: Dictionary with PR information
            user_direction: Optional user input on the direction of the blog post
            
        Returns:
            Prompt for the LLM
        """
        prompt = f"""
        Write a technical blog post about the following GitHub pull request:
        
        Title: {pr_info['pr_title']}
        
        Description:
        {pr_info['pr_description']}
        
        Author: {pr_info['pr_author']}
        Created: {pr_info['pr_created_at']}
        URL: {pr_info['pr_url']}
        
        Summary of changes:
        - Files changed: {pr_info['diff_summary']['file_count']}
        - Additions: {pr_info['diff_summary']['additions']}
        - Deletions: {pr_info['diff_summary']['deletions']}
        - Languages: {', '.join(pr_info['diff_summary']['languages'])}
        
        Commit summary:
        {pr_info['commit_summary']}
        
        Key files changed:
        {', '.join(pr_info['diff_summary']['files_changed'][:5])}
        """

        if user_direction:
            prompt += f"\n\nAdditional direction for the blog post:\n{user_direction}"

        prompt += """
        
        The blog post should:
        1. Have a catchy title
        2. Include an introduction explaining the purpose of the changes
        3. Highlight the key technical aspects of the changes
        4. Explain the impact or benefits of these changes
        5. Include code examples where relevant
        6. End with a conclusion
        
        Format the blog post in Markdown.
        """

        return prompt

    def enhance_with_web_content(self, blog_post: str, pr_info: Dict[str, Any]) -> str:
        """
        Enhance the blog post with related content from the web
        
        Args:
            blog_post: Original blog post content
            pr_info: Dictionary with PR information
            
        Returns:
            Enhanced blog post content
        """
        # Create a search query based on PR info
        search_query = f"{pr_info['pr_title']} {' '.join(pr_info['diff_summary']['languages'])}"

        # Search the web
        search_results = search_web(search_query)

        if not search_results:
            return blog_post

        # Create a prompt to enhance the blog post
        prompt = f"""
        Here is a blog post:
        
        {blog_post}
        
        Here are some related resources from the web:
        
        {json.dumps(search_results, indent=2)}
        
        Enhance the blog post by incorporating relevant information from these resources.
        Add a "Related Resources" section at the end with links to the most relevant resources.
        Keep the blog post in Markdown format.
        """

        # Call OpenAI API to enhance the blog post
        response = self.client.chat.completions.create(model="gpt-4",  # or another appropriate model
        messages=[
            {"role": "system", "content": "You are a technical writer enhancing a blog post with additional information."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.7)

        return response.choices[0].message.content

    def update_blog_post(self, blog_post: str, new_input: str) -> str:
        """
        Update an existing blog post with new information or direction
        
        Args:
            blog_post: Original blog post content
            new_input: New information or direction
            
        Returns:
            Updated blog post content
        """
        prompt = f"""
        Here is an existing blog post:
        
        {blog_post}
        
        Update this blog post based on the following new information or direction:
        
        {new_input}
        
        Keep the blog post in Markdown format.
        """

        # Call OpenAI API to update the blog post
        response = self.client.chat.completions.create(model="gpt-4",  # or another appropriate model
        messages=[
            {"role": "system", "content": "You are a technical writer updating a blog post with new information."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.7)

        return response.choices[0].message.content

def main():
    """
    Main entry point for the blog generator
    """
    parser = argparse.ArgumentParser(description="Generate a blog post from a GitHub pull request")
    parser.add_argument("--repo", required=True, help="Repository in the format owner/name")
    parser.add_argument("--pr", required=True, type=int, help="Pull request number")
    parser.add_argument("--direction", help="Direction for the blog post")
    parser.add_argument("--output", help="Output file path (default: blog_post_{pr_number}_{date}.md)")
    parser.add_argument("--enhance", action="store_true", help="Enhance the blog post with web content")
    parser.add_argument("--update", help="Update an existing blog post with new information")

    args = parser.parse_args()

    # Parse repository owner and name
    repo_parts = args.repo.split("/")
    if len(repo_parts) != 2:
        parser.error("Repository must be in the format owner/name")

    repo_owner, repo_name = repo_parts

    # Initialize the blog generator
    generator = BlogGenerator()

    # If updating an existing blog post
    if args.update:
        if not os.path.exists(args.update):
            parser.error(f"Blog post file {args.update} does not exist")

        with open(args.update, "r") as f:
            existing_blog_post = f.read()

        updated_blog_post = generator.update_blog_post(existing_blog_post, args.direction or "")

        output_file = args.update
        with open(output_file, "w") as f:
            f.write(updated_blog_post)

        print(f"Updated blog post saved to {output_file}")
        return

    # Collect PR information
    pr_info = generator.collect_pr_info(repo_owner, repo_name, args.pr)

    # Generate blog post
    blog_post = generator.generate_blog_post(pr_info, args.direction)

    # Enhance with web content if requested
    if args.enhance:
        blog_post = generator.enhance_with_web_content(blog_post, pr_info)

    # Save to file
    if args.output:
        output_file = args.output
    else:
        date_str = datetime.now().strftime("%Y%m%d")
        output_file = f"blog_post_{args.pr}_{date_str}.md"

    with open(output_file, "w") as f:
        f.write(blog_post)

    print(f"Blog post saved to {output_file}")

if __name__ == "__main__":
    main()
