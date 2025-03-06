import os
import requests
from datetime import datetime
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import base64

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
    repos = response.json()
    print(f"\nFound {len(repos)} repositories:")
    for repo in repos:
        print(f"- {repo['name']}")
    return repos

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
            content = base64.b64decode(response.json()['content']).decode('utf-8')
            print(f"\nFound description.txt in {repo_name}")
            return content, f"https://github.com/{GITHUB_USERNAME}/{repo_name}"
        elif response.status_code == 404:
            print(f"No description.txt found in {repo_name}")
        else:
            print(f"Error checking {repo_name}: {response.status_code}")
    except Exception as e:
        print(f"Error checking {repo_name}: {str(e)}")
    return None, None

def parse_description(content, github_url):
    """Parse description.txt content into project details"""
    lines = content.split('\n')
    default_image = 'images/default.jpg'
    project = {
        'title': '',
        'year': '',
        'description': '',
        'image': default_image,  # Default image path
        'github_url': github_url
    }
    
    current_field = None
    description_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:  # Skip empty lines
            continue
            
        if line.startswith('title:'):
            project['title'] = line.replace('title:', '').strip()
            current_field = None
        elif line.startswith('year:'):
            project['year'] = line.replace('year:', '').strip()
            current_field = None
        elif line.startswith('image:'):
            # Get the specified image path
            image_path = line.replace('image:', '').strip()
            # If it doesn't start with 'images/', add it
            if not image_path.startswith('images/'):
                image_path = f'images/{image_path}'
            # Only use the specified image if it exists
            if os.path.exists(image_path):
                project['image'] = image_path
            else:
                print(f"Image not found: {image_path}, using {default_image}")
                project['image'] = default_image
        elif line.startswith('description:'):
            current_field = 'description'
            description_lines.append(line.replace('description:', '').strip())
        elif current_field == 'description':
            description_lines.append(line)
    
    project['description'] = '\n'.join(description_lines)
    
    print(f"Parsed project: {project['title']}")
    print(f"Year: {project['year']}")
    print(f"Image: {project['image']}")
    print(f"Description length: {len(project['description'])} characters")
    
    return project

def update_html(projects):
    """Update the HTML file with new projects"""
    with open('index.html', 'r') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find and remove the duplicate project entry (the one before the Projects section)
    first_project_table = soup.find('table', {'style': 'width:100%;border:0px;border-spacing:0px;border-collapse:separate;margin-right:auto;margin-left:auto;'})
    if first_project_table and first_project_table.find('span', {'class': 'papertitle'}):
        first_project_table.decompose()
    
    # Find the projects table (the one after the "Projects" heading)
    projects_heading = soup.find('h2', string='Projects')
    if not projects_heading:
        return
    
    # Find the table that contains the projects (it's after the heading)
    projects_table = projects_heading.find_next('table')
    if not projects_table:
        return
    
    # Keep track of existing project titles to avoid duplicates
    existing_titles = set()
    for tr in projects_table.find_all('tr'):
        title_span = tr.find('span', {'class': 'papertitle'})
        if title_span:
            existing_titles.add(title_span.text.strip())
    
    # Add new projects that don't already exist
    for project in projects:
        if project['title'] not in existing_titles:
            new_tr = soup.new_tag('tr')
            
            # Image cell
            img_cell = soup.new_tag('td', attrs={'style': 'padding:20px;width:25%;vertical-align:middle'})
            img_div = soup.new_tag('div', attrs={'class': 'one'})
            
            # Add GitHub link if available
            if project.get('github_url'):
                link = soup.new_tag('a', href=project['github_url'])
                img = soup.new_tag('img', src=project['image'], attrs={'width': '160'})
                link.append(img)
                img_div.append(link)
            else:
                img = soup.new_tag('img', src=project['image'], attrs={'width': '160'})
                img_div.append(img)
                
            img_cell.append(img_div)
            new_tr.append(img_cell)
            
            # Content cell
            content_cell = soup.new_tag('td', attrs={'style': 'padding:20px;width:75%;vertical-align:middle'})
            
            # Title with GitHub link if available
            if project.get('github_url'):
                title_link = soup.new_tag('a', href=project['github_url'])
                title = soup.new_tag('span', attrs={'class': 'papertitle'})
                title.string = project['title']
                title_link.append(title)
                content_cell.append(title_link)
            else:
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
    
    # Format the HTML with proper indentation and line breaks
    formatted_html = str(soup)
    formatted_html = formatted_html.replace('</tbody><tr>', '</tbody>\n<tr>')
    formatted_html = formatted_html.replace('</tr></table>', '</tr>\n</table>')
    formatted_html = formatted_html.replace('><tr>', '>\n<tr>')
    formatted_html = formatted_html.replace('</tr><', '</tr>\n<')
    formatted_html = formatted_html.replace('><td', '>\n<td')
    formatted_html = formatted_html.replace('</td><', '</td>\n<')
    formatted_html = formatted_html.replace('><div', '>\n<div')
    formatted_html = formatted_html.replace('</div><', '</div>\n<')
    formatted_html = formatted_html.replace('><p>', '>\n<p>')
    formatted_html = formatted_html.replace('</p><', '</p>\n<')
    
    # Write updated HTML back to file
    with open('index.html', 'w') as f:
        f.write(formatted_html)

def main():
    try:
        # Get all repositories
        repos = get_repositories()
        
        # Filter out the website repository itself
        repos = [repo for repo in repos if repo['name'] != WEBSITE_REPO]
        
        projects = []
        for repo in repos:
            content, github_url = get_description_file_content(repo['name'])
            if content:
                project = parse_description(content, github_url)
                if project['title'] and project['description']:
                    projects.append(project)
        
        print(f"\nFound {len(projects)} valid projects to display")
        
        # Update the HTML file
        update_html(projects)
        print("Successfully updated projects section!")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 