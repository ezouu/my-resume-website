# Progressive Website Updater

This project consists of a personal portfolio website and a Python script that automates its project updates. The website showcases my projects, experience, and skills, while the script automatically fetches and displays new projects from my GitHub repositories.

## Website Overview

The portfolio website features:
- Clean, responsive design with modern UI elements
- Sections for Projects, Experience, Education, and Skills
- Interactive project showcases with GitHub links
- Professional experience timeline
- Technical skills and expertise display
- Optimized image loading and smooth transitions

## Automation Script

The Python script automates the process of updating the website by dynamically fetching project information from GitHub repositories. It retrieves repository metadata, generates a description of the project, and parses details such as the project title, year, description, and associated image.

### How It Works

The script uses the GitHub API to:
1. Fetch all public repositories from a specified GitHub account
2. Look for a `description.txt` file in each repository
3. Parse the contents of the description file to extract:
   - Project title
   - Year/date
   - Project description
   - Associated image (with fallback to default.jpg)
4. Update the website's HTML file by:
   - Finding the projects section
   - Adding new projects that don't already exist
   - Maintaining consistent formatting with existing projects
   - Adding GitHub links to both images and titles

The script uses BeautifulSoup to parse and modify the HTML, ensuring that the website's structure and styling remain intact while adding new content.

## Technical Details

- Uses GitHub's REST API for repository data
- Implements HTML parsing with BeautifulSoup
- Handles image fallbacks gracefully
- Preserves existing project entries
- Maintains consistent HTML structure and styling