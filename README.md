# 🚀 PR-to-Blog: Transform Pull Requests into Engaging Blog Posts

Turn your GitHub pull requests into polished, professional blog posts with this AI-powered tool!

## ✨ Features

- **Smart PR Analysis**: Automatically extracts code diffs, commit messages, PR titles and descriptions
- **AI-Powered Content Generation**: Creates well-structured technical blog posts using OpenAI's GPT models
- **Web Research Integration**: Enhances posts with relevant content from across the web
- **Customizable Output**: Take control with user-defined direction for the tone and focus
- **Flexible Updates**: Easily revise and enhance existing blog posts with new information
- **Comprehensive PR Stats**: Includes file counts, additions/deletions, and language breakdowns
- **Markdown-Ready Output**: Posts are formatted in Markdown, ready for publishing

## 🛠️ Technical Details

- Built with Python 3
- Uses GitHub API for PR data extraction
- Leverages OpenAI's API for content generation
- Command-line interface for easy integration into workflows
- Modular architecture with separate utilities for GitHub interactions, content generation, and web search

## 🧩 Code Implementation

### Core Components

- **BlogGenerator Class**: The main class that orchestrates the entire process
  - Collects PR information from GitHub
  - Generates blog content using OpenAI's GPT models
  - Enhances content with web research
  - Updates existing blog posts with new information

- **Utility Functions**:
  - GitHub API interactions (`fetch_pr_data`, `fetch_pr_commits`, `fetch_pr_diff`)
  - Diff parsing and analysis (`parse_diff`)
  - Commit summarization (`summarize_commits`)
  - Web search integration (`search_web`)
  - Progress reporting (`print_progress`)

### Workflow Process

1. **Data Collection**: 
   - Fetch PR metadata (title, description, author, dates)
   - Retrieve commit history and messages
   - Download and parse code diffs
   - Extract statistics (files changed, additions/deletions, languages)

2. **Content Generation**:
   - Create a detailed prompt for the AI model
   - Include PR metadata, commit summaries, and diff analysis
   - Generate structured blog post with OpenAI's GPT models

3. **Content Enhancement** (optional):
   - Search the web for related resources
   - Enhance the blog post with additional context and information
   - Add a "Related Resources" section with relevant links

4. **Content Update** (when updating existing posts):
   - Read existing blog post content
   - Incorporate new information or follow new direction
   - Preserve the original structure while adding new content

## 🚦 Getting Started

```bash
# Create a .env file with your API keys
echo "GITHUB_TOKEN=your_github_token" > .env
echo "OPENAI_API_KEY=your_openai_api_key" >> .env

# Or set environment variables directly
export GITHUB_TOKEN=your_github_token
export OPENAI_API_KEY=your_openai_api_key

# Install required dependencies
pip install -r requirements.txt

# Generate a blog post
python src/cli.py --repo owner/repo --pr 123 --enhance
```

### Environment Setup

1. **API Keys**:
   - GitHub Token: Required for accessing PR data (especially for private repositories)
   - OpenAI API Key: Required for content generation

2. **Dependencies**:
   - Python 3.7+
   - OpenAI Python client
   - Requests library for API calls
   - dotenv for environment variable management

## 📋 Command Options

- `--repo`: Repository in format owner/name
- `--pr`: Pull request number
- `--direction`: Custom direction for blog post focus
- `--output`: Custom output file path
- `--no-enhance`: Skip adding web research to enrich content (enhancement is on by default)
- `--update`: Path to existing blog post to update

## 🔄 Example Workflows

### Basic Blog Generation

Generate a blog post from a pull request (includes web research by default):

```bash
python src/cli.py --repo facebook/react --pr 12345 --output blog_react_hooks.md
```

### Blog Without Web Research

Create a simpler post without web research integration:

```bash
python src/cli.py --repo tensorflow/tensorflow --pr 54321 --no-enhance --output tensorflow_feature.md
```

### Focused Content Direction

Guide the AI to focus on specific aspects of the PR:

```bash
python src/cli.py --repo kubernetes/kubernetes --pr 98765 \
  --direction "Focus on security implications and best practices" \
  --output k8s_security_post.md
```

### Update Existing Content

Update a previously generated blog post with new information:

```bash
python src/cli.py --repo django/django --pr 24680 \
  --update previous_django_post.md \
  --direction "Include the new performance benchmarks"
```

### Complete Workflow Example

A comprehensive workflow that combines multiple features:

```bash
# First, generate an initial blog post
python src/cli.py --repo pytorch/pytorch --pr 13579 --output pytorch_feature.md

# Later, update it with new information
python src/cli.py --repo pytorch/pytorch --pr 13579 \
  --update pytorch_feature.md \
  --direction "Add information about the new benchmarks and community feedback"
```

## 🏗️ Internal Architecture

### File Structure

```
pr-to-blog/
├── src/
│   ├── cli.py           # Command-line interface entry point
│   ├── gen_blog.py      # Main BlogGenerator class and workflow
│   └── utils.py         # Utility functions for GitHub API, parsing, etc.
├── .env                 # Environment variables (API keys)
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```

### Data Flow

1. **Command Parsing** (`cli.py`):
   - Parse command-line arguments
   - Call the main function in `gen_blog.py`

2. **PR Data Collection** (`gen_blog.py` → `utils.py`):
   - Fetch PR metadata, commits, and diffs from GitHub API
   - Parse and analyze the collected data

3. **Content Generation** (`gen_blog.py`):
   - Create prompts for OpenAI's GPT models
   - Generate initial blog post content
   - Optionally enhance with web research
   - Optionally update existing content

4. **Output** (`gen_blog.py`):
   - Save the generated blog post to a file
   - Display progress and completion messages

### Extensibility

The modular design allows for easy extensions:
- Add support for additional code hosting platforms (GitLab, Bitbucket)
- Integrate different AI models for content generation
- Implement more sophisticated web research capabilities
- Add support for different output formats (HTML, PDF, etc.)
