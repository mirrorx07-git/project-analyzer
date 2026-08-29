# ProjectLens

ProjectLens is an AI-powered project analyzer for students and developers. Analyze a public GitHub repository, upload source files, or upload a code screenshot to receive a project summary, detected technologies, skills learned, upgrade suggestions, a learning path, and code-quality tips.

## Features

- Analyze public GitHub repositories
- Analyze uploaded code files across common programming languages
- Extract code from screenshots with OCR and analyze it
- Identify technologies and developer skills
- Generate suggested technology upgrades and learning paths
- Provide practical code-quality recommendations

## Built with

- **Backend:** Python, Flask, Gunicorn
- **Frontend:** HTML, CSS, JavaScript
- **AI:** OpenAI API
- **Repository data:** GitHub REST API
- **OCR:** Tesseract via `pytesseract`

## Project structure

```text
project-analyzer/
├── backend/
│   ├── app.py                 # Flask app and API endpoints
│   ├── analyzer.py            # OpenAI-powered analysis logic
│   ├── github_handler.py      # GitHub API integration
│   ├── file_handler.py        # File and OCR handling
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
├── .env                       # Local secrets — do not commit
└── README.md
```

## Prerequisites

- Python 3.11 or later
- An [OpenAI API key](https://platform.openai.com/api-keys)
- A GitHub personal access token (recommended, to avoid low unauthenticated API limits)
- Tesseract OCR installed locally if you want to use screenshot analysis

## Local setup

1. Clone the repository and open the project folder:

   ```bash
   git clone https://github.com/YOUR-USERNAME/project-analyzer.git
   cd project-analyzer
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```bash
   pip install -r backend/requirements.txt
   ```

4. Create a `.env` file in the project root:

   ```env
   OPENAI_API_KEY=your_openai_api_key
   GITHUB_TOKEN=your_github_token
   SECRET_KEY=a_long_random_secret
   ```

5. Run the app:

   ```bash
   python backend/app.py
   ```

6. Open [http://localhost:5000](http://localhost:5000) in your browser.

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Serves the web application |
| `GET` | `/api/health` | Checks whether the API is running |
| `POST` | `/api/analyze/github` | Analyzes a public GitHub repository |
| `POST` | `/api/analyze/file` | Analyzes uploaded code files |
| `POST` | `/api/analyze/screenshot` | Analyzes a code screenshot |

## Deploy from GitHub to Render

GitHub Pages cannot run this application because it has a Python/Flask backend. Use GitHub to store the source code and deploy the full application as a Render web service.

1. Add a `.gitignore` file before publishing:

   ```gitignore
   .env
   .venv/
   backend/uploads/
   backend/__pycache__/
   *.pyc
   ```

2. Create a repository on GitHub, then push the project:

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/project-analyzer.git
   git push -u origin main
   ```

3. In Render, select **New → Web Service**, connect the GitHub repository, and enter:

   | Setting | Value |
   | --- | --- |
   | Build Command | `pip install -r backend/requirements.txt` |
   | Start Command | `gunicorn --chdir backend app:app` |
   | Health Check Path | `/api/health` |

4. Add these environment variables in Render's **Environment** settings:

   ```text
   OPENAI_API_KEY
   GITHUB_TOKEN
   SECRET_KEY
   PYTHON_VERSION=3.11.11
   ```

5. Deploy. Render provides a public `onrender.com` URL and can redeploy automatically whenever you push to `main`.

## Security

- Never commit `.env`, API keys, or GitHub tokens.
- If a key is pushed to a public repository, revoke and replace it immediately.
- Use a GitHub token with the smallest permissions necessary. Public-repository access is sufficient for the current repository-analysis feature.

## Notes

- Screenshot analysis requires the Tesseract executable in addition to the Python package. Configure it on the host if you need that feature in production.
- The default request upload limit is 16 MB.

## License

Add a license file before publishing if you want others to reuse or contribute to the project.
