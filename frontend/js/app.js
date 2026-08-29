// ============================================
// API Configuration
// ============================================
const API_BASE = 'http://localhost:5000/api';

// ============================================
// State Management
// ============================================
let selectedFiles = [];
let selectedScreenshot = null;

// ============================================
// DOM Elements
// ============================================
const elements = {
    // Tabs
    tabBtns: document.querySelectorAll('.tab-btn'),
    tabContents: document.querySelectorAll('.tab-content'),

    // GitHub
    githubUrl: document.getElementById('github-url'),
    analyzeGithubBtn: document.getElementById('analyze-github-btn'),

    // File Upload
    fileDropZone: document.getElementById('file-drop-zone'),
    fileInput: document.getElementById('file-input'),
    fileList: document.getElementById('file-list'),
    analyzeFilesBtn: document.getElementById('analyze-files-btn'),

    // Screenshot
    screenshotDropZone: document.getElementById('screenshot-drop-zone'),
    screenshotInput: document.getElementById('screenshot-input'),
    screenshotPreview: document.getElementById('screenshot-preview'),
    analyzeScreenshotBtn: document.getElementById('analyze-screenshot-btn'),

    // Loading
    loadingOverlay: document.getElementById('loading-overlay'),
    loadingStatus: document.getElementById('loading-status'),

    // Results
    resultsSection: document.getElementById('results-section'),
    projectSummary: document.getElementById('project-summary'),
    techUsedContent: document.getElementById('tech-used-content'),
    skillsContent: document.getElementById('skills-content'),
    relatedTechContent: document.getElementById('related-tech-content'),
    upgradeContent: document.getElementById('upgrade-content'),
    learningPathContent: document.getElementById('learning-path-content'),
    codeTipsContent: document.getElementById('code-tips-content'),
    newAnalysisBtn: document.getElementById('new-analysis-btn'),

    // Error
    errorToast: document.getElementById('error-toast'),
    errorMessage: document.getElementById('error-message')
};

// ============================================
// Tab Navigation
// ============================================
elements.tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tabId = btn.dataset.tab;

        // Update tab buttons
        elements.tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Update tab content
        elements.tabContents.forEach(content => content.classList.remove('active'));
        document.getElementById(`tab-${tabId}`).classList.add('active');
    });
});

// ============================================
// GitHub Analysis
// ============================================
elements.analyzeGithubBtn.addEventListener('click', async () => {
    const url = elements.githubUrl.value.trim();
    if (!url) {
        showError('Please enter a GitHub repository URL');
        return;
    }

    showLoading('Fetching repository data from GitHub...');

    try {
        const response = await fetch(`${API_BASE}/analyze/github`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ repo_url: url })
        });

        const data = await response.json();

        if (!response.ok || data.error) {
            throw new Error(data.error || 'Analysis failed');
        }

        hideLoading();
        displayResults(data);

    } catch (error) {
        hideLoading();
        showError(error.message);
    }
});

// Enter key support
elements.githubUrl.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        elements.analyzeGithubBtn.click();
    }
});

// ============================================
// File Upload
// ============================================

// Click to browse
elements.fileDropZone.addEventListener('click', () => {
    elements.fileInput.click();
});

// Drag and drop handlers
elements.fileDropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    elements.fileDropZone.classList.add('drag-over');
});

elements.fileDropZone.addEventListener('dragleave', () => {
    elements.fileDropZone.classList.remove('drag-over');
});

elements.fileDropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    elements.fileDropZone.classList.remove('drag-over');
    handleFileSelect(e.dataTransfer.files);
});

elements.fileInput.addEventListener('change', (e) => {
    handleFileSelect(e.target.files);
});

function handleFileSelect(files) {
    for (const file of files) {
        if (!selectedFiles.find(f => f.name === file.name)) {
            selectedFiles.push(file);
        }
    }
    updateFileList();
}

function updateFileList() {
    elements.fileList.innerHTML = '';

    selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div class="file-item-info">
                <i class="fas fa-file-code"></i>
                <span class="file-item-name">${file.name}</span>
                <span class="file-item-size">${formatFileSize(file.size)}</span>
            </div>
            <button class="file-remove" onclick="removeFile(${index})">
                <i class="fas fa-times"></i>
            </button>
        `;
        elements.fileList.appendChild(fileItem);
    });

    elements.analyzeFilesBtn.disabled = selectedFiles.length === 0;
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFileList();
}

// Make removeFile available globally
window.removeFile = removeFile;

elements.analyzeFilesBtn.addEventListener('click', async () => {
    if (selectedFiles.length === 0) {
        showError('Please select files to analyze');
        return;
    }

    showLoading('Reading and analyzing your code files...');

    try {
        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });

        const response = await fetch(`${API_BASE}/analyze/file`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok || data.error) {
            throw new Error(data.error || 'Analysis failed');
        }

        hideLoading();
        displayResults(data);

    } catch (error) {
        hideLoading();
        showError(error.message);
    }
});

// ============================================
// Screenshot Upload
// ============================================

elements.screenshotDropZone.addEventListener('click', () => {
    elements.screenshotInput.click();
});

elements.screenshotDropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    elements.screenshotDropZone.classList.add('drag-over');
});

elements.screenshotDropZone.addEventListener('dragleave', () => {
    elements.screenshotDropZone.classList.remove('drag-over');
});

elements.screenshotDropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    elements.screenshotDropZone.classList.remove('drag-over');
    if (e.dataTransfer.files.length > 0) {
        handleScreenshotSelect(e.dataTransfer.files[0]);
    }
});

elements.screenshotInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleScreenshotSelect(e.target.files[0]);
    }
});

function handleScreenshotSelect(file) {
    const validTypes = ['image/png', 'image/jpeg', 'image/gif', 'image/bmp', 'image/webp'];
    if (!validTypes.includes(file.type)) {
        showError('Please select a valid image file (PNG, JPG, GIF, BMP, WebP)');
        return;
    }

    selectedScreenshot = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        elements.screenshotPreview.innerHTML = `
            <img src="${e.target.result}" alt="Code screenshot preview">
            <p style="margin-top: 8px; font-size: 0.85rem; color: var(--text-muted);">
                ${file.name} (${formatFileSize(file.size)})
            </p>
        `;
    };
    reader.readAsDataURL(file);

    elements.analyzeScreenshotBtn.disabled = false;
}

elements.analyzeScreenshotBtn.addEventListener('click', async () => {
    if (!selectedScreenshot) {
        showError('Please select a screenshot to analyze');
        return;
    }

    showLoading('Analyzing your code screenshot...');

    try {
        const formData = new FormData();
        formData.append('screenshot', selectedScreenshot);

        const response = await fetch(`${API_BASE}/analyze/screenshot`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok || data.error) {
            throw new Error(data.error || 'Analysis failed');
        }

        hideLoading();
        displayResults(data);

    } catch (error) {
        hideLoading();
        showError(error.message);
    }
});

// ============================================
// Display Results
// ============================================
function displayResults(data) {
    if (!data.success) {
        showError(data.error || 'Analysis failed. Please try again.');
        return;
    }

    // Scroll to results
    elements.resultsSection.classList.remove('hidden');

    // Project Summary
    renderProjectSummary(data.project_summary);

    // Technologies Used
    renderTechnologiesUsed(data.technologies_used);

    // Skills Learned
    renderSkillsLearned(data.skills_learned);

    // Related Technologies
    renderRelatedTech(data.related_technologies);

    // Upgrade Suggestions
    renderUpgradeSuggestions(data.upgrade_suggestions);

    // Learning Path
    renderLearningPath(data.learning_path);

    // Code Quality Tips
    renderCodeTips(data.code_quality_tips);

    // Smooth scroll to results
    setTimeout(() => {
        elements.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 200);
}

function renderProjectSummary(summary) {
    if (!summary) return;

    elements.projectSummary.innerHTML = `
        <div class="summary-grid">
            <div class="summary-item">
                <div class="summary-label">Project Name</div>
                <div class="summary-value">${escapeHtml(summary.name || 'Unknown')}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Project Type</div>
                <div class="summary-value">${escapeHtml(summary.project_type || 'Unknown')}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Complexity</div>
                <div class="summary-value">${escapeHtml(summary.complexity_level || 'Unknown')}</div>
            </div>
        </div>
        ${summary.description ? `
            <div class="summary-description">
                ${escapeHtml(summary.description)}
            </div>
        ` : ''}
    `;
}

function renderTechnologiesUsed(technologies) {
    if (!technologies || technologies.length === 0) {
        elements.techUsedContent.innerHTML = '<p style="color: var(--text-muted);">No technologies detected.</p>';
        return;
    }

    elements.techUsedContent.innerHTML = `
        <div class="tech-grid">
            ${technologies.map(tech => `
                <div class="tech-tag">
                    <span class="tech-tag-icon">${tech.icon || '🔧'}</span>
                    <span class="tech-tag-name">${escapeHtml(tech.name)}</span>
                    <span class="tech-tag-category">${escapeHtml(tech.category || '')}</span>
                </div>
            `).join('')}
        </div>
    `;
}

function renderSkillsLearned(skills) {
    if (!skills || skills.length === 0) {
        elements.skillsContent.innerHTML = '<p style="color: var(--text-muted);">No skills identified.</p>';
        return;
    }

    elements.skillsContent.innerHTML = `
        <div class="skills-list">
            ${skills.map(skill => `
                <div class="skill-item">
                    <div class="skill-icon">
                        <i class="fas fa-check"></i>
                    </div>
                    <div class="skill-info">
                        <span class="skill-category">${escapeHtml(skill.category || '')}</span>
                        <h4>${escapeHtml(skill.skill)}</h4>
                        <p>${escapeHtml(skill.description || '')}</p>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function renderRelatedTech(technologies) {
    if (!technologies || technologies.length === 0) {
        elements.relatedTechContent.innerHTML = '<p style="color: var(--text-muted);">No related technologies found.</p>';
        return;
    }

    elements.relatedTechContent.innerHTML = `
        <div class="related-grid">
            ${technologies.map(tech => `
                <div class="related-card">
                    <div class="related-card-header">
                        <div class="related-card-title">
                            <span>${tech.icon || '🔧'}</span>
                            <h4>${escapeHtml(tech.name)}</h4>
                        </div>
                        <span class="difficulty-badge difficulty-${(tech.difficulty || 'medium').toLowerCase()}">
                            ${escapeHtml(tech.difficulty || 'Medium')}
                        </span>
                    </div>
                    <p>${escapeHtml(tech.description || '')}</p>
                    <p style="font-size: 0.8rem; color: var(--text-muted); font-style: italic;">
                        ${escapeHtml(tech.relation || '')}
                    </p>
                    ${tech.learning_time ? `
                        <div class="learning-time">
                            <i class="fas fa-clock"></i> ${escapeHtml(tech.learning_time)}
                        </div>
                    ` : ''}
                </div>
            `).join('')}
        </div>
    `;
}

function renderUpgradeSuggestions(suggestions) {
    if (!suggestions || suggestions.length === 0) {
        elements.upgradeContent.innerHTML = '<p style="color: var(--text-muted);">No upgrade suggestions available.</p>';
        return;
    }

    elements.upgradeContent.innerHTML = `
        <div class="upgrade-list">
            ${suggestions.map(item => `
                <div class="upgrade-item">
                    <div class="upgrade-header">
                        <div class="upgrade-arrow">
                            <span class="upgrade-from">${escapeHtml(item.current_tech || '')}</span>
                            <i class="fas fa-arrow-right upgrade-icon"></i>
                            <span class="upgrade-to">${escapeHtml(item.suggested_tech || '')}</span>
                        </div>
                        <span class="priority-badge priority-${(item.priority || 'medium').toLowerCase()}">
                            ${escapeHtml(item.priority || 'Medium')} Priority
                        </span>
                    </div>
                    <p class="upgrade-reason">${escapeHtml(item.reason || '')}</p>
                    ${item.benefits && item.benefits.length > 0 ? `
                        <div class="upgrade-benefits">
                            ${item.benefits.map(b => `
                                <span class="benefit-tag">
                                    <i class="fas fa-check-circle"></i> ${escapeHtml(b)}
                                </span>
                            `).join('')}
                        </div>
                    ` : ''}
                    ${item.learning_resources && item.learning_resources.length > 0 ? `
                        <div class="learning-resources">
                            ${item.learning_resources.map(r => `
                                <a href="${escapeHtml(r.url || '#')}" target="_blank" class="resource-link">
                                    <i class="fas fa-external-link-alt"></i>
                                    ${escapeHtml(r.title || 'Resource')}
                                </a>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            `).join('')}
        </div>
    `;
}

function renderLearningPath(path) {
    if (!path) {
        elements.learningPathContent.innerHTML = '<p style="color: var(--text-muted);">No learning path available.</p>';
        return;
    }

    let html = '<div class="learning-path-grid">';

    if (path.next_steps && path.next_steps.length > 0) {
        html += `
            <div class="path-section">
                <h4><i class="fas fa-shoe-prints"></i> Next Steps</h4>
                <ul class="path-list">
                    ${path.next_steps.map(step => `<li>${escapeHtml(step)}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    if (path.short_term_goals && path.short_term_goals.length > 0) {
        html += `
            <div class="path-section">
                <h4><i class="fas fa-bullseye"></i> Short-Term Goals</h4>
                <ul class="path-list">
                    ${path.short_term_goals.map(goal => `<li>${escapeHtml(goal)}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    if (path.long_term_goals && path.long_term_goals.length > 0) {
        html += `
            <div class="path-section">
                <h4><i class="fas fa-mountain"></i> Long-Term Goals</h4>
                <ul class="path-list">
                    ${path.long_term_goals.map(goal => `<li>${escapeHtml(goal)}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    html += '</div>';

    // Recommended projects
    if (path.recommended_projects && path.recommended_projects.length > 0) {
        html += `
            <div class="recommended-projects">
                <h4><i class="fas fa-lightbulb"></i> Recommended Projects to Build</h4>
                <div class="project-suggestions">
                    ${path.recommended_projects.map(proj => `
                        <div class="project-card">
                            <h5>${escapeHtml(proj.name || '')}</h5>
                            <p>${escapeHtml(proj.description || '')}</p>
                            ${proj.technologies && proj.technologies.length > 0 ? `
                                <div class="project-techs">
                                    ${proj.technologies.map(t => `
                                        <span class="project-tech-tag">${escapeHtml(t)}</span>
                                    `).join('')}
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    elements.learningPathContent.innerHTML = html;
}

function renderCodeTips(tips) {
    if (!tips || tips.length === 0) {
        elements.codeTipsContent.innerHTML = '<p style="color: var(--text-muted);">No code quality tips available.</p>';
        return;
    }

    elements.codeTipsContent.innerHTML = `
        <div class="tips-list">
            ${tips.map(tip => `
                <div class="tip-item tip-${(tip.priority || 'medium').toLowerCase()}">
                    <div class="tip-icon">
                        <i class="fas fa-lightbulb"></i>
                    </div>
                    <div class="tip-info">
                        <h4>${escapeHtml(tip.area || '')}</h4>
                        <p>${escapeHtml(tip.tip || '')}</p>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// ============================================
// New Analysis
// ============================================
elements.newAnalysisBtn.addEventListener('click', () => {
    elements.resultsSection.classList.add('hidden');

    // Reset forms
    elements.githubUrl.value = '';
    selectedFiles = [];
    updateFileList();
    selectedScreenshot = null;
    elements.screenshotPreview.innerHTML = '';
    elements.analyzeScreenshotBtn.disabled = true;

    // Scroll to upload section
    document.getElementById('upload-section').scrollIntoView({ behavior: 'smooth' });
});

// ============================================
// Loading State
// ============================================
const loadingMessages = [
    'Scanning your project...',
    'Identifying technologies...',
    'Analyzing code patterns...',
    'Detecting frameworks and libraries...',
    'Generating upgrade suggestions...',
    'Building your learning path...',
    'Almost there...'
];

let loadingInterval = null;

function showLoading(initialMessage) {
    elements.loadingOverlay.classList.remove('hidden');
    elements.loadingStatus.textContent = initialMessage || loadingMessages[0];

    let msgIndex = 0;
    loadingInterval = setInterval(() => {
        msgIndex = (msgIndex + 1) % loadingMessages.length;
        elements.loadingStatus.textContent = loadingMessages[msgIndex];
    }, 3000);
}

function hideLoading() {
    elements.loadingOverlay.classList.add('hidden');
    if (loadingInterval) {
        clearInterval(loadingInterval);
        loadingInterval = null;
    }
}

// ============================================
// Error Handling
// ============================================
function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorToast.classList.remove('hidden');

    // Auto-hide after 6 seconds
    setTimeout(() => {
        hideError();
    }, 6000);
}

function hideError() {
    elements.errorToast.classList.add('hidden');
}

// Make hideError globally accessible
window.hideError = hideError;

// ============================================
// Utility Functions
// ============================================
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// Smooth scroll for nav links
// ============================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// ============================================
// Health check on load
// ============================================
window.addEventListener('load', async () => {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        console.log('API Status:', data.message);
    } catch (error) {
        console.warn('API not reachable. Make sure the backend is running on port 5000.');
    }
});
