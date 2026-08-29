import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from analyzer import TechAnalyzer
from github_handler import GitHubHandler
from file_handler import FileHandler

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = Flask(__name__, static_folder='../frontend')
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {
    'py', 'js', 'ts', 'jsx', 'tsx', 'html', 'css', 'java', 'cpp', 'c',
    'cs', 'rb', 'php', 'go', 'rs', 'swift', 'kt', 'scala', 'r',
    'sql', 'json', 'xml', 'yaml', 'yml', 'toml', 'md', 'txt',
    'dockerfile', 'sh', 'bat', 'ps1', 'vue', 'svelte',
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'
}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

analyzer = TechAnalyzer()
github_handler = GitHubHandler()
file_handler = FileHandler()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/css/<path:path>')
def serve_css(path):
    return send_from_directory(os.path.join(app.static_folder, 'css'), path)


@app.route('/js/<path:path>')
def serve_js(path):
    return send_from_directory(os.path.join(app.static_folder, 'js'), path)


@app.route('/api/analyze/github', methods=['POST'])
def analyze_github():
    """Analyze a GitHub repository"""
    try:
        data = request.get_json()
        repo_url = data.get('repo_url', '').strip()

        if not repo_url:
            return jsonify({'error': 'Repository URL is required'}), 400

        # Extract repo info from URL
        repo_info = github_handler.parse_repo_url(repo_url)
        if not repo_info:
            return jsonify({'error': 'Invalid GitHub repository URL'}), 400

        # Fetch repository data
        repo_data = github_handler.fetch_repo_data(repo_info['owner'], repo_info['repo'])
        if 'error' in repo_data:
            return jsonify({'error': repo_data['error']}), 400

        # Get file contents for analysis
        file_contents = github_handler.fetch_repo_files(repo_info['owner'], repo_info['repo'])

        # Analyze with AI
        analysis = analyzer.analyze_project(
            source_type='github',
            repo_data=repo_data,
            file_contents=file_contents,
            repo_url=repo_url
        )

        return jsonify(analysis)

    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/api/analyze/file', methods=['POST'])
def analyze_file():
    """Analyze uploaded code files"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400

        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({'error': 'No files selected'}), 400

        file_contents = {}
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[1].lower()

                if ext in {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}:
                    # Handle image files - extract text via OCR
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    extracted_text = file_handler.extract_text_from_image(filepath)
                    file_contents[filename] = extracted_text
                    os.remove(filepath)
                else:
                    # Handle code files
                    content = file.read().decode('utf-8', errors='ignore')
                    file_contents[filename] = content

        if not file_contents:
            return jsonify({'error': 'No valid files to analyze'}), 400

        # Analyze with AI
        analysis = analyzer.analyze_project(
            source_type='file',
            file_contents=file_contents
        )

        return jsonify(analysis)

    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/api/analyze/screenshot', methods=['POST'])
def analyze_screenshot():
    """Analyze a screenshot of code"""
    try:
        if 'screenshot' not in request.files:
            return jsonify({'error': 'No screenshot uploaded'}), 400

        file = request.files['screenshot']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

        if ext not in {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}:
            return jsonify({'error': 'Invalid image format'}), 400

        # Save temporarily
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Use AI vision to analyze the screenshot
        import base64
        with open(filepath, 'rb') as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode('utf-8')

        os.remove(filepath)

        # Analyze with AI vision
        analysis = analyzer.analyze_screenshot(image_base64, ext)

        return jsonify(analysis)

    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'API is running'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)