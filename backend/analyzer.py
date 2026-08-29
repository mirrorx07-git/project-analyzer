import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


class TechAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o"

    def _build_analysis_prompt(self, source_type, repo_data=None, file_contents=None, repo_url=None):
        """Build the prompt for AI analysis"""

        prompt = """You are an expert software engineering mentor and technology advisor. 
Analyze the following student project and provide a comprehensive technology analysis.

Return your response as a valid JSON object with this exact structure:
{
    "project_summary": {
        "name": "Project name or description",
        "description": "Brief description of what the project does",
        "complexity_level": "Beginner/Intermediate/Advanced",
        "project_type": "Web App/Mobile App/CLI Tool/API/Game/Data Science/etc."
    },
    "technologies_used": [
        {
            "name": "Technology name",
            "category": "Language/Framework/Library/Database/Tool/Platform",
            "icon": "emoji icon",
            "proficiency_indicator": "Basic/Intermediate/Advanced",
            "usage_description": "How it's used in the project"
        }
    ],
    "skills_learned": [
        {
            "skill": "Skill name",
            "category": "Frontend/Backend/Database/DevOps/Design/Testing/etc.",
            "description": "What the student learned by using this"
        }
    ],
    "related_technologies": [
        {
            "name": "Technology name",
            "category": "Language/Framework/Library/Database/Tool",
            "icon": "emoji icon",
            "relation": "How it relates to current tech stack",
            "difficulty": "Easy/Medium/Hard",
            "learning_time": "Estimated time to learn",
            "description": "Why this is worth learning"
        }
    ],
    "upgrade_suggestions": [
        {
            "current_tech": "What they're currently using",
            "suggested_tech": "What they could upgrade to",
            "category": "Frontend/Backend/Database/DevOps/Testing/Deployment",
            "icon": "emoji icon",
            "priority": "High/Medium/Low",
            "reason": "Why this upgrade would help",
            "benefits": ["benefit1", "benefit2", "benefit3"],
            "learning_resources": [
                {"title": "Resource name", "url": "URL", "type": "Documentation/Tutorial/Course/Video"}
            ]
        }
    ],
    "learning_path": {
        "next_steps": ["Step 1", "Step 2", "Step 3"],
        "short_term_goals": ["Goal 1", "Goal 2"],
        "long_term_goals": ["Goal 1", "Goal 2"],
        "recommended_projects": [
            {"name": "Project idea", "description": "Brief description", "technologies": ["tech1", "tech2"]}
        ]
    },
    "code_quality_tips": [
        {
            "area": "Area of improvement",
            "tip": "Specific actionable tip",
            "priority": "High/Medium/Low"
        }
    ]
}

"""

        if source_type == 'github' and repo_data:
            prompt += f"\n--- GITHUB REPOSITORY INFO ---\n"
            if repo_url:
                prompt += f"Repository URL: {repo_url}\n"
            prompt += f"Repository Name: {repo_data.get('name', 'Unknown')}\n"
            prompt += f"Description: {repo_data.get('description', 'No description')}\n"
            prompt += f"Primary Language: {repo_data.get('language', 'Unknown')}\n"
            prompt += f"Languages Used: {json.dumps(repo_data.get('languages', {}))}\n"
            prompt += f"Topics/Tags: {', '.join(repo_data.get('topics', []))}\n"
            prompt += f"Has Wiki: {repo_data.get('has_wiki', False)}\n"
            prompt += f"Has Pages: {repo_data.get('has_pages', False)}\n"
            prompt += f"Stars: {repo_data.get('stargazers_count', 0)}\n"
            prompt += f"Forks: {repo_data.get('forks_count', 0)}\n"

        if file_contents:
            prompt += f"\n--- FILE CONTENTS ---\n"
            for filename, content in file_contents.items():
                # Truncate very large files
                truncated = content[:3000] if len(content) > 3000 else content
                prompt += f"\n=== {filename} ===\n{truncated}\n"
                if len(content) > 3000:
                    prompt += f"... (truncated, full file is {len(content)} characters)\n"

        prompt += "\nAnalyze the project thoroughly and return ONLY the JSON response, no additional text."

        return prompt

    def analyze_project(self, source_type, repo_data=None, file_contents=None, repo_url=None):
        """Analyze a project using OpenAI API"""
        try:
            prompt = self._build_analysis_prompt(source_type, repo_data, file_contents, repo_url)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert software engineering mentor. Always respond with valid JSON only, no markdown formatting, no code blocks, just pure JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000
            )

            result_text = response.choices[0].message.content.strip()

            # Clean up response - remove markdown code blocks if present
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.startswith('```'):
                result_text = result_text[3:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            result_text = result_text.strip()

            analysis = json.loads(result_text)
            analysis['success'] = True
            return analysis

        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'Failed to parse AI response: {str(e)}',
                'raw_response': result_text if 'result_text' in dir() else 'No response'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'AI analysis failed: {str(e)}'
            }

    def analyze_screenshot(self, image_base64, image_ext):
        """Analyze a screenshot using OpenAI Vision"""
        try:
            mime_map = {
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'gif': 'image/gif',
                'bmp': 'image/bmp',
                'webp': 'image/webp'
            }
            mime_type = mime_map.get(image_ext, 'image/png')

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert software engineering mentor. Analyze code screenshots and identify technologies, patterns, and provide suggestions. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this screenshot of code. Identify the programming languages, frameworks, 
libraries, and technologies visible. Then provide suggestions for improvements and related technologies to learn.

Return your response as a valid JSON object with this exact structure:
{
    "project_summary": {
        "name": "Code from screenshot",
        "description": "Description of what the code does",
        "complexity_level": "Beginner/Intermediate/Advanced",
        "project_type": "Type of project"
    },
    "technologies_used": [
        {
            "name": "Technology name",
            "category": "Language/Framework/Library/Database/Tool",
            "icon": "emoji",
            "proficiency_indicator": "Basic/Intermediate/Advanced",
            "usage_description": "How it's used"
        }
    ],
    "skills_learned": [
        {"skill": "Skill name", "category": "Category", "description": "Description"}
    ],
    "related_technologies": [
        {
            "name": "Tech name",
            "category": "Category",
            "icon": "emoji",
            "relation": "How it relates",
            "difficulty": "Easy/Medium/Hard",
            "learning_time": "Estimated time",
            "description": "Why learn this"
        }
    ],
    "upgrade_suggestions": [
        {
            "current_tech": "Current",
            "suggested_tech": "Suggested",
            "category": "Category",
            "icon": "emoji",
            "priority": "High/Medium/Low",
            "reason": "Why upgrade",
            "benefits": ["benefit1", "benefit2"],
            "learning_resources": [{"title": "Resource", "url": "URL", "type": "Type"}]
        }
    ],
    "learning_path": {
        "next_steps": ["Step 1", "Step 2"],
        "short_term_goals": ["Goal 1"],
        "long_term_goals": ["Goal 1"],
        "recommended_projects": [{"name": "Project", "description": "Desc", "technologies": ["tech1"]}]
    },
    "code_quality_tips": [
        {"area": "Area", "tip": "Tip", "priority": "Priority"}
    ]
}

Return ONLY the JSON, no additional text."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4000
            )

            result_text = response.choices[0].message.content.strip()

            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.startswith('```'):
                result_text = result_text[3:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            result_text = result_text.strip()

            analysis = json.loads(result_text)
            analysis['success'] = True
            return analysis

        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'Failed to parse AI response: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Screenshot analysis failed: {str(e)}'
            }