import os


class FileHandler:
    def __init__(self):
        pass

    def extract_text_from_image(self, filepath):
        """Extract text from an image using pytesseract OCR"""
        try:
            from PIL import Image
            import pytesseract

            image = Image.open(filepath)
            text = pytesseract.image_to_string(image)
            return text if text.strip() else "Could not extract text from image. The AI will analyze the image directly."

        except ImportError:
            return "OCR libraries not available. The image will be analyzed using AI vision instead."
        except Exception as e:
            return f"OCR extraction failed: {str(e)}. The image will be analyzed using AI vision instead."

    def detect_language(self, filename, content):
        """Detect programming language from filename and content"""
        ext_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React JSX',
            '.tsx': 'React TSX',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.sass': 'Sass',
            '.less': 'Less',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.go': 'Go',
            '.rs': 'Rust',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.r': 'R',
            '.sql': 'SQL',
            '.vue': 'Vue.js',
            '.svelte': 'Svelte'
        }

        ext = os.path.splitext(filename)[1].lower()
        return ext_map.get(ext, 'Unknown')

    def get_file_info(self, filename, content):
        """Get basic info about a file"""
        return {
            'filename': filename,
            'language': self.detect_language(filename, content),
            'lines': len(content.split('\n')),
            'size': len(content),
            'extension': os.path.splitext(filename)[1].lower()
        }