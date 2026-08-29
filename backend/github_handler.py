import os
import re
import requests
import base64
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


class GitHubHandler:
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        self.api_base = 'https://api.github.com'
        self.headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'

    def parse_repo_url(self, url):
        """Parse a GitHub URL to extract owner and repo name"""
        patterns = [
            r'github\.com/([^/]+)/([^/\s\?#]+)',
            r'^([^/]+)/([^/\s]+)$'
        ]

        url = url.strip().rstrip('/')
        # Remove .git suffix
        if url.endswith('.git'):
            url = url[:-4]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return {
                    'owner': match.group(1),
                    'repo': match.group(2)
                }
        return None

    def fetch_repo_data(self, owner, repo):
        """Fetch repository metadata from GitHub API"""
        try:
            # Get repo info
            repo_response = requests.get(
                f'{self.api_base}/repos/{owner}/{repo}',
                headers=self.headers,
                timeout=15
            )

            if repo_response.status_code == 404:
                return {'error': 'Repository not found. Make sure it exists and is public.'}
            elif repo_response.status_code == 403:
                return {'error': 'API rate limit exceeded. Please try again later or add a GitHub token.'}
            elif repo_response.status_code != 200:
                return {'error': f'GitHub API error: {repo_response.status_code}'}

            repo_data = repo_response.json()

            # Get languages
            lang_response = requests.get(
                f'{self.api_base}/repos/{owner}/{repo}/languages',
                headers=self.headers,
                timeout=10
            )
            languages = lang_response.json() if lang_response.status_code == 200 else {}

            # Get topics
            topics_headers = self.headers.copy()
            topics_headers['Accept'] = 'application/vnd.github.mercy-preview+json'
            topics_response = requests.get(
                f'{self.api_base}/repos/{owner}/{repo}/topics',
                headers=topics_headers,
                timeout=10
            )
            topics = topics_response.json().get('names', []) if topics_response.status_code == 200 else []

            return {
                'name': repo_data.get('name', ''),
                'description': repo_data.get('description', ''),
                'language': repo_data.get('language', ''),
                'languages': languages,
                'topics': topics,
                'has_wiki': repo_data.get('has_wiki', False),
                'has_pages': repo_data.get('has_pages', False),
                'stargazers_count': repo_data.get('stargazers_count', 0),
                'forks_count': repo_data.get('forks_count', 0),
                'default_branch': repo_data.get('default_branch', 'main'),
                'created_at': repo_data.get('created_at', ''),
                'updated_at': repo_data.get('updated_at', ''),
                'size': repo_data.get('size', 0)
            }

        except requests.exceptions.Timeout:
            return {'error': 'Request timed out. Please try again.'}
        except requests.exceptions.RequestException as e:
            return {'error': f'Failed to connect to GitHub: {str(e)}'}

    def fetch_repo_files(self, owner, repo, path='', depth=0, max_depth=3):
        """Recursively fetch important files from the repository"""
        if depth > max_depth:
            return {}

        important_files = {
            'package.json', 'requirements.txt', 'Pipfile', 'Cargo.toml',
            'go.mod', 'build.gradle', 'pom.xml', 'Gemfile', 'composer.json',
            'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
            '.env.example', 'Makefile', 'CMakeLists.txt',
            'tsconfig.json', 'webpack.config.js', 'vite.config.js',
            'next.config.js', 'nuxt.config.js', 'angular.json',
            'setup.py', 'setup.cfg', 'pyproject.toml',
            'README.md', 'readme.md'
        }

        important_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c',
            '.cs', '.rb', '.php', '.go', '.rs', '.swift', '.kt',
            '.html', '.css', '.scss', '.vue', '.svelte', '.sql'
        }

        file_contents = {}
        max_files = 15  # Limit total files to analyze

        try:
            response = requests.get(
                f'{self.api_base}/repos/{owner}/{repo}/contents/{path}',
                headers=self.headers,
                timeout=10
            )

            if response.status_code != 200:
                return {}

            items = response.json()
            if not isinstance(items, list):
                return {}

            for item in items:
                if len(file_contents) >= max_files:
                    break

                name = item.get('name', '')
                item_type = item.get('type', '')
                item_path = item.get('path', '')

                # Skip common non-essential directories
                skip_dirs = {'node_modules', '.git', '__pycache__', 'venv', 'env',
                             '.venv', 'dist', 'build', '.next', '.nuxt', 'vendor',
                             'target', 'bin', 'obj', '.idea', '.vscode', 'coverage'}

                if item_type == 'dir':
                    if name not in skip_dirs:
                        sub_files = self.fetch_repo_files(owner, repo, item_path, depth + 1, max_depth)
                        file_contents.update(sub_files)

                elif item_type == 'file':
                    ext = os.path.splitext(name)[1].lower()
                    size = item.get('size', 0)

                    # Only fetch important or code files, skip large files
                    if (name in important_files or ext in important_extensions) and size < 50000:
                        try:
                            file_response = requests.get(
                                item.get('url', ''),
                                headers=self.headers,
                                timeout=10
                            )
                            if file_response.status_code == 200:
                                file_data = file_response.json()
                                content = file_data.get('content', '')
                                encoding = file_data.get('encoding', '')

                                if encoding == 'base64' and content:
                                    decoded = base64.b64decode(content).decode('utf-8', errors='ignore')
                                    file_contents[item_path] = decoded
                        except Exception:
                            continue

        except Exception:
            pass

        return file_contents