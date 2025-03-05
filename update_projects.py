import os
import requests
from datetime import datetime
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# GitHub API configuration
GITHUB_USERNAME = "ezouu"
GITHUB_API_BASE = "https://api.github.com"
WEBSITE_REPO = "resumewebsite"

def get_github_token():
    """Get GitHub token from .env file"""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        raise ValueError("Please set GITHUB_TOKEN in your .env file")
    return token

def get_repositories():
    """Fetch all public repositories from GitHub"""
    headers = {
        'Authorization': f'token {get_github_token()}',
        'Accept': 'application/vnd.github.v3+json'
    }
    response = requests.get(f"{GITHUB_API_BASE}/users/{GITHUB_USERNAME}/repos", headers=headers)
    return response.json()

def get_description_file_content(repo_name):
    """Fetch description.txt content from a repository"""
    headers = {
        'Authorization': f'token {get_github_token()}',
        'Accept': 'application/vnd.github.v3+json'
    }
    try:
        response = requests.get(
            f"{GITHUB_API_BASE}/repos/{GITHUB_USERNAME}/{repo_name}/contents/description.txt",
            headers=headers
        )
        if response.status_code == 200:
            content = response.json()['content']
            return content
    except:
        return None
    return None

def parse_description(content):
    """Parse description.txt content into project details"""
    lines = content.split('\n')
    project = {
        'title': '',
        'year': '',
        'description': '',
        'image': 'images/default.jpg'  # Default image
    }
    
    for line in lines:
        if line.startswith('title:'):
            project['title'] = line.replace('title:', '').strip()
        elif line.startswith('year:'):
            project['year'] = line.replace('year:', '').strip()
        elif line.startswith('image:'):
            project['image'] = line.replace('image:', '').strip()
        elif line.startswith('description:'):
            project['description'] = line.replace('description:', '').strip()
    
    return project

def update_html(projects):
    """Update the HTML file with new projects"""
    with open('index.html', 'r') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the projects table
    projects_table = soup.find('table', {'style': 'width:100%;border:0px;border-spacing:0px;border-collapse:separate;margin-right:auto;margin-left:auto;'})
    if not projects_table:
        return
    
    # Clear existing project entries
    for tr in projects_table.find_all('tr'):
        if tr.find('td', {'style': 'padding:20px;width:25%;vertical-align:middle'}):
            tr.decompose()
    
    # Add new projects
    for project in projects:
        new_tr = soup.new_tag('tr')
        
        # Image cell
        img_cell = soup.new_tag('td', attrs={'style': 'padding:20px;width:25%;vertical-align:middle'})
        img_div = soup.new_tag('div', attrs={'class': 'one'})
        img = soup.new_tag('img', attrs={'src': project['image'], 'width': '160'})
        img_div.append(img)
        img_cell.append(img_div)
        new_tr.append(img_cell)
        
        # Content cell
        content_cell = soup.new_tag('td', attrs={'style': 'padding:20px;width:75%;vertical-align:middle'})
        
        # Title
        title = soup.new_tag('span', attrs={'class': 'papertitle'})
        title.string = project['title']
        content_cell.append(title)
        content_cell.append(soup.new_tag('br'))
        
        # Year
        year = soup.new_tag('em')
        year.string = project['year']
        content_cell.append(year)
        content_cell.append(soup.new_tag('br'))
        
        # Description
        desc = soup.new_tag('p')
        desc.string = project['description']
        content_cell.append(desc)
        
        new_tr.append(content_cell)
        projects_table.append(new_tr)
    
    # Write updated HTML back to file
    with open('index.html', 'w') as f:
        f.write(str(soup))

def main():
    try:
        # Get all repositories
        repos = get_repositories()
        
        # Filter out the website repository itself
        repos = [repo for repo in repos if repo['name'] != WEBSITE_REPO]
        
        projects = []
        for repo in repos:
            content = get_description_file_content(repo['name'])
            if content:
                project = parse_description(content)
                if project['title'] and project['description']:
                    projects.append(project)
        
        # Update the HTML file
        update_html(projects)
        print("Successfully updated projects section!")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 