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

## 🚦 Getting Started

```bash
# Set required environment variables
export GITHUB_TOKEN=your_github_token
export OPENAI_API_KEY=your_openai_api_key

# Generate a blog post
python src/cli.py --repo owner/repo --pr 123 --enhance
```

## 📋 Command Options

- `--repo`: Repository in format owner/name
- `--pr`: Pull request number
- `--direction`: Custom direction for blog post focus
- `--output`: Custom output file path
- `--enhance`: Add web research to enrich content
- `--update`: Path to existing blog post to update
