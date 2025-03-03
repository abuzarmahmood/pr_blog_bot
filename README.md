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
# Create a .env file with your API keys
echo "GITHUB_TOKEN=your_github_token" > .env
echo "OPENAI_API_KEY=your_openai_api_key" >> .env

# Or set environment variables directly
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

## 🔄 Example Workflows

### Basic Blog Generation

Generate a simple blog post from a pull request:

```bash
python src/cli.py --repo facebook/react --pr 12345 --output blog_react_hooks.md
```

### Enhanced Blog with Research

Create a more comprehensive post with web research integration:

```bash
python src/cli.py --repo tensorflow/tensorflow --pr 54321 --enhance --output tensorflow_feature.md
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
python src/cli.py --repo pytorch/pytorch --pr 13579 --enhance --output pytorch_feature.md

# Later, update it with new information
python src/cli.py --repo pytorch/pytorch --pr 13579 \
  --update pytorch_feature.md \
  --direction "Add information about the new benchmarks and community feedback"
```
