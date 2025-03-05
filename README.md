# Project Automation for Personal Website

This script automatically updates the projects section of your personal website by fetching information from your GitHub repositories.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a GitHub Personal Access Token:
   - Go to GitHub Settings > Developer Settings > Personal Access Tokens
   - Generate a new token with `repo` scope
   - Copy the token

3. Set the GitHub token as an environment variable:
```bash
export GITHUB_TOKEN='your_token_here'
```

## Adding New Projects

To add a new project to your website:

1. Create a new GitHub repository for your project
2. Add a `description.txt` file in the root of your repository with the following format:
```
title: Project Title
year: 2024 -- Present
image: images/project-image.jpg
description: Your project description goes here. This can be multiple lines long.
```

## Running the Script

To update your website's projects section:

```bash
python update_projects.py
```

The script will:
1. Fetch all your public GitHub repositories
2. Look for `description.txt` files in each repository
3. Parse the project information
4. Update your website's HTML file with the new projects

## Notes

- Make sure to add project images to your website's `images` directory
- The script will maintain the same styling and format as your existing projects
- Projects without a valid `description.txt` file will be ignored
- The website repository itself is excluded from the projects list