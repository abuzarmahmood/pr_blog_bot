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
    search_web,
    print_progress
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
        print_progress(f"Fetching PR #{pr_number} data from {repo_owner}/{repo_name}", "🔍", "bold", "blue")
        # Fetch PR data
        pr_data = fetch_pr_data(repo_owner, repo_name, pr_number)

        print_progress("Retrieving commit history", "📜", "bold", "cyan")
        # Fetch commits
        commits = fetch_pr_commits(repo_owner, repo_name, pr_number)

        print_progress("Downloading and analyzing code changes", "📊", "bold", "magenta")
        # Fetch and parse diff
        diff_content = fetch_pr_diff(repo_owner, repo_name, pr_number)
        diff_summary = parse_diff(diff_content)

        print_progress("Summarizing commit messages", "📝", "bold", "green")
        # Summarize commits
        commit_summary = summarize_commits(commits)
        
        # Extract all contributors from commits
        contributors = set()
        for commit in commits:
            author = commit.get("commit", {}).get("author", {}).get("name", "")
            committer = commit.get("commit", {}).get("committer", {}).get("name", "")
            if author:
                contributors.add(author)
            if committer and committer != author:
                contributors.add(committer)
        
        # Add PR author if not already in contributors
        pr_author = pr_data.get("user", {}).get("login", "")
        if pr_author:
            contributors.add(pr_author)
            
        # Format date for better readability
        created_date = pr_data.get("created_at", "")
        if created_date:
            try:
                # Convert ISO format to more readable format
                created_date_obj = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                formatted_date = created_date_obj.strftime("%B %d, %Y")
            except:
                formatted_date = created_date
        else:
            formatted_date = ""

        return {
            "pr_title": pr_data.get("title", ""),
            "pr_description": pr_data.get("body", ""),
            "pr_author": pr_author,
            "pr_created_at": pr_data.get("created_at", ""),
            "pr_formatted_date": formatted_date,
            "pr_updated_at": pr_data.get("updated_at", ""),
            "pr_url": pr_data.get("html_url", ""),
            "commits": commits,
            "commit_summary": commit_summary,
            "diff_summary": diff_summary,
            "diff_content": diff_content,
            "contributors": list(contributors)
        }

    def generate_image(self, prompt: str, size: str = "1024x1024", model: str = "dall-e-3") -> Optional[str]:
        """
        Generate an image using OpenAI's DALL-E API
        
        Args:
            prompt: Text description of the desired image
            size: Size of the image (1024x1024, 1792x1024, or 1024x1792 for dall-e-3)
            model: Model to use (dall-e-2 or dall-e-3)
            
        Returns:
            URL of the generated image, or None if generation failed
        """
        print_progress("Generating custom image with DALL-E", "🎨", "bold", "magenta")
        try:
            response = self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality="standard",
                n=1,
            )
            
            # Extract the image URL from the response
            image_url = response.data[0].url
            print_progress("Image generated successfully", "✅", "bold", "green")
            return image_url
        except Exception as e:
            print_progress(f"Failed to generate image: {str(e)}", "⚠️", "bold", "red")
            return None

    def generate_blog_post(self, pr_info: Dict[str, Any], user_direction: Optional[str] = None) -> str:
        """
        Generate a blog post based on PR information
        
        Args:
            pr_info: Dictionary with PR information
            user_direction: Optional user input on the direction of the blog post
            
        Returns:
            Generated blog post content
        """
        print_progress("Creating blog post prompt", "✨", "bold", "yellow")
        # Prepare the prompt for the LLM
        prompt = self._create_blog_prompt(pr_info, user_direction)

        print_progress("Generating blog post content with AI", "🤖", "bold", "cyan")
        # Call OpenAI API to generate the blog post
        response = self.client.chat.completions.create(model="gpt-4",  # or another appropriate model
        messages=[
            {"role": "system", "content": "You are a technical writer creating a blog post about code changes. Always include at least one relevant image in your blog posts."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.7)
        
        blog_content = response.choices[0].message.content
        
        # Generate a custom image for the blog post
        image_prompt = f"Create a technical illustration for a blog post about: {pr_info['pr_title']}. " \
                       f"The changes involve {', '.join(pr_info['diff_summary']['languages'])} code. " \
                       f"Make it visually appealing and professional."
        
        image_url = self.generate_image(image_prompt)
        
        # Add the generated image to the blog post if it doesn't already have one
        if image_url and ("![" not in blog_content or "](" not in blog_content):
            print_progress("Adding generated image to blog post", "🖼️", "bold", "yellow")
            
            # Create image caption based on PR title
            image_caption = f"Visual representation of {pr_info['pr_title']}"
            
            # Add the image at the beginning of the blog post, after the title if present
            if blog_content.startswith("#"):
                # Find the end of the title line
                title_end = blog_content.find("\n")
                if title_end != -1:
                    blog_content = blog_content[:title_end+1] + f"\n![{image_caption}]({image_url})\n\n" + blog_content[title_end+1:]
            else:
                # If no title, add the image at the very beginning
                blog_content = f"![{image_caption}]({image_url})\n\n" + blog_content
        
        # If we couldn't generate an image or add it properly, fall back to the old method
        elif "![" not in blog_content or "](" not in blog_content:
            print_progress("Adding image to blog post (fallback method)", "🖼️", "bold", "yellow")
            # If no image is present, add a request to include one
            follow_up_prompt = f"""
            The blog post you generated doesn't include an image. Please add at least one relevant image using Markdown syntax.
            
            Here's the blog post:
            
            {blog_content}
            
            You can use images from:
            - https://unsplash.com/ (for high-quality free stock photos)
            - https://shields.io/ (for badges and status shields)
            - https://mermaid.live/ (for diagrams)
            - https://carbon.now.sh/ (for code screenshots)
            
            Return the complete blog post with at least one image added.
            """
            
            # Call OpenAI API again to add an image
            image_response = self.client.chat.completions.create(model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a technical writer enhancing a blog post with images."},
                {"role": "user", "content": follow_up_prompt}
            ],
            max_tokens=2000,
            temperature=0.7)
            
            blog_content = image_response.choices[0].message.content

        return blog_content

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
        Created: {pr_info['pr_formatted_date']} ({pr_info['pr_created_at']})
        URL: {pr_info['pr_url']}
        
        Contributors: {', '.join(pr_info['contributors'])}
        
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
        
        Format the blog post in Markdown. Don't worry about including images - I'll handle that separately.
        Focus on creating high-quality, informative content about the technical changes.
        
        For technical topics, consider including code snippets, explanations of algorithms, or architectural decisions.
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
        print_progress("Searching the web for related content", "🌐", "bold", "blue")
        # Create a search query based on PR info
        search_query = f"{pr_info['pr_title']} {' '.join(pr_info['diff_summary']['languages'])}"

        # Search the web
        search_results = search_web(search_query)

        if not search_results:
            print_progress("No relevant web content found", "⚠️", "bold", "yellow")
            return blog_post

        # Check if the blog post already contains an image
        has_image = "![" in blog_post and "](" in blog_post
        
        # Create a prompt to enhance the blog post
        prompt = f"""
        Here is a blog post:
        
        {blog_post}
        
        Here are some related resources from the web:
        
        {json.dumps(search_results, indent=2)}
        
        Enhance the blog post by incorporating relevant information from these resources.
        Add a "Related Resources" section at the end with links to the most relevant resources.
        
        {"" if has_image else "IMPORTANT: The blog post MUST include at least one relevant image. Add an appropriate image using Markdown image syntax (![alt text](image_url))."}
        
        Keep the blog post in Markdown format.
        """

        print_progress("Enhancing blog post with web content", "🔍", "bold", "magenta")
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
        print_progress("Preparing to update existing blog post", "📝", "bold", "cyan")
        prompt = f"""
        Here is an existing blog post:
        
        {blog_post}
        
        Update this blog post based on the following new information or direction:
        
        {new_input}
        
        Keep the blog post in Markdown format.
        """

        print_progress("Updating blog post content with AI", "🤖", "bold", "green")
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
    from utils import print_progress
    
    print_progress("Starting PR-to-Blog Generator", "🚀", "bold", "green")
    
    parser = argparse.ArgumentParser(description="Generate a blog post from a GitHub pull request")
    parser.add_argument("--repo", required=True, help="Repository in the format owner/name")
    parser.add_argument("--pr", required=True, type=int, help="Pull request number")
    parser.add_argument("--direction", help="Direction for the blog post")
    parser.add_argument("--output", help="Output file path (default: blog_post_{pr_number}_{date}.md)")
    parser.add_argument("--no-enhance", action="store_true", help="Skip enhancing the blog post with web content")
    parser.add_argument("--update", help="Update an existing blog post with new information")

    args = parser.parse_args()
    print_progress("Parsed command line arguments", "✅", "bold", "blue")

    # Parse repository owner and name
    repo_parts = args.repo.split("/")
    if len(repo_parts) != 2:
        parser.error("Repository must be in the format owner/name")

    repo_owner, repo_name = repo_parts
    print_progress(f"Target repository: {repo_owner}/{repo_name}", "📦", "bold", "cyan")

    # Initialize the blog generator
    print_progress("Initializing blog generator", "⚙️", "bold", "magenta")
    generator = BlogGenerator()

    # If updating an existing blog post
    if args.update:
        if not os.path.exists(args.update):
            parser.error(f"Blog post file {args.update} does not exist")

        print_progress(f"Reading existing blog post from {args.update}", "📄", "bold", "blue")
        with open(args.update, "r") as f:
            existing_blog_post = f.read()

        updated_blog_post = generator.update_blog_post(existing_blog_post, args.direction or "")

        output_file = args.update
        print_progress(f"Saving updated blog post", "💾", "bold", "green")
        with open(output_file, "w") as f:
            f.write(updated_blog_post)

        print_progress(f"Updated blog post saved to {output_file}", "🎉", "bold", "green")
        return

    # Collect PR information
    pr_info = generator.collect_pr_info(repo_owner, repo_name, args.pr)

    # Generate blog post
    blog_post = generator.generate_blog_post(pr_info, args.direction)

    # Enhance with web content by default, unless --no-enhance is specified
    if not args.no_enhance:
        print_progress("Enhancing blog post with web research", "🔎", "bold", "blue")
        blog_post = generator.enhance_with_web_content(blog_post, pr_info)

    # Save to file
    if args.output:
        output_file = args.output
    else:
        date_str = datetime.now().strftime("%Y%m%d")
        output_file = f"blog_post_{args.pr}_{date_str}.md"

    print_progress(f"Saving blog post to {output_file}", "💾", "bold", "cyan")
    with open(output_file, "w") as f:
        f.write(blog_post)

    print_progress(f"Blog post successfully saved to {output_file}", "🎉", "bold", "green")

if __name__ == "__main__":
    main()
