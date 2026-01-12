// Enhanced Construction Agent POC - Frontend V2 with Reasoning Display

const API_BASE = window.location.hostname === 'localhost' && window.location.port === '5173'
    ? '/api'
    : 'http://localhost:8100';

// State management
const state = {
    connected: false,
    messages: [],
    currentStreamingMessage: null,
    reasoningSteps: [],
    showReasoning: true,
    currentModel: 'gpt-5'
};

// Manager instances
let voiceManager = null;
let conversationManager = null;
let modelManager = null;

// DOM elements
const elements = {
    messages: document.getElementById('messages'),
    messageInput: document.getElementById('message-input'),
    chatForm: document.getElementById('chat-form'),
    connectionStatus: document.getElementById('connection-status'),
    thinkingIndicator: document.getElementById('thinking-indicator'),
    reasoningToggle: document.getElementById('reasoning-toggle'),
    docStatus: document.getElementById('doc-status'),
    reasoningPanel: document.getElementById('reasoning-panel'),
    saveConversationBtn: document.getElementById('save-conversation'),
    newConversationBtn: document.getElementById('new-conversation')
};

// Initialize enhanced app
async function init() {
    console.log('🚀 Initializing Enhanced Construction Agent V2...');

    // Set dark mode by default
    document.body.classList.add('dark-mode');
    localStorage.setItem('theme', 'dark');

    // Initialize managers
    if (window.ConversationManager) {
        conversationManager = new ConversationManager();
    }
    if (window.ModelManager) {
        modelManager = new ModelManager(conversationManager);
    }

    // Check backend health
    await checkBackendStatus();

    // Setup event listeners
    setupEventListeners();

    // Voice disabled for now

    // Add initial welcome message
    addMessage('assistant',
        `Hello! I'm Elena, your construction assistant with deep reasoning and learning capabilities.

**What I can do:**
- Analyze complex patterns in shop drawings
- Identify base components and dimensional relationships
- Provide detailed technical analysis with source references
- Learn and remember project-specific knowledge

**Try asking me:**
- "Analyze the trellis shop drawings and identify the base components"
- "What patterns exist in the trellis dimensions?"
- "Are there conflicts between HVAC and trellis systems?"

**Teaching me new things:**
You can teach me project-specific knowledge using natural language:
- "Remember that the trellis clearance is 24 inches"
- "I want you to remember that the HVAC units are on the roof"
- "Learn that all beams must have 2-inch spacing"
- "Never use metric measurements in reports"

**View my knowledge:**
Click the "📖 Knowledge" button above to view, edit, or delete things I've learned.

I'll show you my reasoning process as I analyze your questions, including the source PDFs I reference.`, false, true);

    // Focus the message input for immediate typing
    if (elements.messageInput) {
        elements.messageInput.focus();
    }
}

// Check enhanced backend status
async function checkBackendStatus() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const health = await response.json();

        state.connected = true;
        updateConnectionStatus(true);

        // Update with enhanced status
        if (elements.docStatus) {
            elements.docStatus.innerHTML = `
                <div class="status-item">
                    <span class="status-label">📄 Documents:</span>
                    <span class="status-value">${health.documents_loaded || 0}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">🔧 Components:</span>
                    <span class="status-value">${health.components_identified || 0}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">📊 Base Types:</span>
                    <span class="status-value">${health.base_component_types?.length || 0}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">🔍 Patterns:</span>
                    <span class="status-value">${health.patterns_found || 0}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">🤖 Model:</span>
                    <span class="status-value">${health.openai_configured ? state.currentModel.toUpperCase() : '❌'}</span>
                </div>
            `;
        }

        // Load knowledge base preview
        await loadKnowledgePreview();

    } catch (error) {
        console.error('Backend not reachable:', error);
        state.connected = false;
        updateConnectionStatus(false);
        if (elements.docStatus) {
            elements.docStatus.innerHTML = '<p class="error">❌ Backend not connected</p>';
        }
    }
}

// Load knowledge base preview
async function loadKnowledgePreview() {
    try {
        const response = await fetch(`${API_BASE}/knowledge`);
        const knowledge = await response.json();

        // Display base components if found
        if (knowledge.base_components && Object.keys(knowledge.base_components).length > 0) {
            console.log('Base components loaded:', knowledge.base_components);
        }

    } catch (error) {
        console.error('Error loading knowledge base:', error);
    }
}

// Update connection status
function updateConnectionStatus(connected) {
    if (elements.connectionStatus) {
        if (connected) {
            elements.connectionStatus.textContent = '● Connected';
            elements.connectionStatus.className = 'status-indicator connected';
        } else {
            elements.connectionStatus.textContent = '● Disconnected';
            elements.connectionStatus.className = 'status-indicator disconnected';
        }
    }
}

// Setup enhanced event listeners
function setupEventListeners() {
    // Chat form submission
    if (elements.chatForm) {
        elements.chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const message = elements.messageInput.value.trim();
            if (message) {
                await sendMessage(message);
            }
        });
    }

    // Model selector
    const modelSelector = document.getElementById('model-selector');
    if (modelSelector) {
        modelSelector.addEventListener('change', async (e) => {
            const newModel = e.target.value;
            if (newModel !== state.currentModel) {
                state.currentModel = newModel;
                if (modelManager) {
                    await modelManager.switchModel(newModel);
                }
            }
        });
    }

    // Save conversation button (new location)
    if (elements.saveConversationBtn) {
        elements.saveConversationBtn.addEventListener('click', async () => {
            if (conversationManager && conversationManager.messages.length > 0) {
                try {
                    const result = await conversationManager.saveConversation();
                    // Show brief confirmation instead of alert
                    showNotification('Conversation saved!');
                } catch (error) {
                    showNotification('Failed to save conversation', 'error');
                }
            } else {
                showNotification('No messages to save', 'warning');
            }
        });
    }

    // New conversation button
    if (elements.newConversationBtn) {
        elements.newConversationBtn.addEventListener('click', () => {
            if (conversationManager && conversationManager.messages.length > 0) {
                if (confirm('Start a new conversation? Current conversation will be cleared.')) {
                    // Clear conversation
                    conversationManager.clear();
                    // Clear UI
                    if (elements.messages) {
                        elements.messages.innerHTML = '';
                    }
                    // Add welcome message
                    addMessage('assistant', 'Ready for a new conversation! How can I help you with the Aurora project?', false, true);
                    // Hide buttons again
                    elements.saveConversationBtn.classList.add('hidden');
                    elements.newConversationBtn.classList.add('hidden');
                }
            }
        });
    }

    // History button
    const historyBtn = document.getElementById('history-btn');
    if (historyBtn) {
        historyBtn.addEventListener('click', async () => {
            await showHistoryModal();
        });
    }

    // Knowledge base button
    const knowledgeBtn = document.getElementById('knowledge-btn');
    if (knowledgeBtn) {
        knowledgeBtn.addEventListener('click', async () => {
            if (window.knowledgeViewer) {
                await window.knowledgeViewer.open();
            }
        });
    }

    // Theme toggle button
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            themeToggle.textContent = isDark ? '🌙' : '☀️';
        });
    }

    // History modal close
    const historyClose = document.getElementById('history-close');
    if (historyClose) {
        historyClose.addEventListener('click', () => {
            document.getElementById('history-modal').classList.add('hidden');
        });
    }

    // Reprime modal close
    const reprimeClose = document.getElementById('reprime-close');
    if (reprimeClose) {
        reprimeClose.addEventListener('click', () => {
            document.getElementById('reprime-modal').classList.add('hidden');
        });
    }

    // Quick query links
    document.querySelectorAll('.quick-query').forEach(link => {
        link.addEventListener('click', async (e) => {
            e.preventDefault();
            const query = e.target.textContent;
            if (elements.messageInput) {
                elements.messageInput.value = query;
            }
            await sendMessage(query);
        });
    });

    // Reasoning toggle
    if (elements.reasoningToggle) {
        elements.reasoningToggle.addEventListener('click', () => {
            state.showReasoning = !state.showReasoning;
            elements.reasoningToggle.textContent = state.showReasoning ? '🧠 Reasoning On' : '🧠 Reasoning Off';
            elements.reasoningToggle.classList.toggle('active', state.showReasoning);

            // Toggle reasoning panel visibility
            if (elements.reasoningPanel) {
                elements.reasoningPanel.style.display = state.showReasoning ? 'block' : 'none';
            }
        });
    }

    // Voice controls
    if (elements.voiceToggle) {
        elements.voiceToggle.addEventListener('click', () => {
            if (voiceManager) {
                voiceManager.toggleVoice();
            }
        });
    }

    if (elements.voiceInputBtn) {
        // Mouse events
        elements.voiceInputBtn.addEventListener('mousedown', (e) => {
            e.preventDefault();
            if (voiceManager && voiceManager.voiceEnabled) {
                voiceManager.startRecording();
            }
        });

        elements.voiceInputBtn.addEventListener('mouseup', (e) => {
            e.preventDefault();
            if (voiceManager && voiceManager.isRecording) {
                voiceManager.stopRecording();
            }
        });

        elements.voiceInputBtn.addEventListener('mouseleave', () => {
            if (voiceManager && voiceManager.isRecording) {
                voiceManager.stopRecording();
            }
        });

        // Touch events
        elements.voiceInputBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            if (voiceManager && voiceManager.voiceEnabled) {
                voiceManager.startRecording();
            }
        });

        elements.voiceInputBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            if (voiceManager && voiceManager.isRecording) {
                voiceManager.stopRecording();
            }
        });
    }

    // Analyze button for specific topics
    const analyzeBtn = document.getElementById('analyze-trellis-btn');
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', async () => {
            await analyzeTrelliComponents();
        });
    }
}

// Show history modal
async function showHistoryModal() {
    const modal = document.getElementById('history-modal');
    const listContainer = document.getElementById('conversation-list');
    const viewer = document.getElementById('conversation-viewer');

    modal.classList.remove('hidden');
    viewer.classList.add('hidden');

    // Load conversations
    if (conversationManager) {
        const conversations = await conversationManager.loadConversations();

        if (conversations.length === 0) {
            listContainer.innerHTML = '<p style="text-align: center; color: #6b7280;">No saved conversations</p>';
        } else {
            listContainer.innerHTML = conversations.map(conv => `
                <div class="conversation-item" data-filename="${conv.filename}">
                    <div class="conversation-title">${conv.title || 'Untitled'}</div>
                    <div class="conversation-meta">
                        <span>📅 ${new Date(conv.saved_at).toLocaleString()}</span>
                        <span>💬 ${conv.message_count} messages</span>
                    </div>
                </div>
            `).join('');

            // Add click handlers
            listContainer.querySelectorAll('.conversation-item').forEach(item => {
                item.addEventListener('click', async () => {
                    const filename = item.dataset.filename;
                    const conversation = await conversationManager.loadConversation(filename);

                    // Show in viewer
                    viewer.innerHTML = `
                        <h3>${conversation.title || 'Conversation'}</h3>
                        <div class="conversation-messages">
                            ${conversation.messages.map(msg => `
                                <div class="message ${msg.role}">
                                    <div class="message-header">${msg.role === 'user' ? '👤 You' : '🤖 Assistant'}</div>
                                    <div class="message-content">${msg.content}</div>
                                </div>
                            `).join('')}
                        </div>
                    `;
                    viewer.classList.remove('hidden');

                    // Highlight selected
                    listContainer.querySelectorAll('.conversation-item').forEach(i =>
                        i.classList.remove('selected'));
                    item.classList.add('selected');
                });
            });
        }
    }
}

// Close history modal helper
window.closeHistoryModal = function() {
    document.getElementById('history-modal').classList.add('hidden');
};

// Show notification helper
function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    // Style it
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 12px 20px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#f59e0b'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Send enhanced message with reasoning
async function sendMessage(message) {
    if (!state.connected) {
        alert('Backend not connected. Please ensure the server is running.');
        return;
    }

    // Clear input
    if (elements.messageInput) {
        elements.messageInput.value = '';
    }

    // Add user message
    addMessage('user', message);

    // Track in conversation manager
    if (conversationManager) {
        conversationManager.addMessage('user', message);
    }

    // Show save/new buttons after first message
    if (elements.saveConversationBtn && elements.newConversationBtn) {
        elements.saveConversationBtn.classList.remove('hidden');
        elements.newConversationBtn.classList.remove('hidden');
    }

    // Show thinking indicator
    if (elements.thinkingIndicator) {
        elements.thinkingIndicator.classList.remove('hidden');
    }

    // Clear reasoning panel
    if (elements.reasoningPanel && state.showReasoning) {
        elements.reasoningPanel.innerHTML = '<div class="reasoning-step">🔄 Starting analysis...</div>';
    }

    // Create assistant message container
    const assistantMessage = addMessage('assistant', '', true);

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message,
                reasoning_mode: state.showReasoning,
                model: state.currentModel
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Process enhanced SSE stream
        await processEnhancedSSEStream(response, assistantMessage);

    } catch (error) {
        console.error('Error sending message:', error);
        assistantMessage.querySelector('.message-content').textContent =
            'Sorry, there was an error processing your request. Please try again.';
    } finally {
        if (elements.thinkingIndicator) {
            elements.thinkingIndicator.classList.add('hidden');
        }
        if (elements.messageInput) {
            elements.messageInput.focus();
        }
    }
}

// Process enhanced SSE stream with reasoning steps
async function processEnhancedSSEStream(response, messageElement) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let fullText = '';
    let reasoningSteps = [];

    const messageContent = messageElement.querySelector('.message-content');
    messageElement.classList.add('streaming');

    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');

            buffer = lines.pop();

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') continue;

                    try {
                        const event = JSON.parse(data);

                        switch (event.type) {
                            case 'REASONING_START':
                                if (elements.reasoningPanel && state.showReasoning) {
                                    elements.reasoningPanel.innerHTML = `
                                        <div class="reasoning-header">
                                            🧠 Reasoning Process (${event.data.steps_count} steps)
                                        </div>`;
                                }
                                break;

                            case 'REASONING_STEP':
                                if (elements.reasoningPanel && state.showReasoning) {
                                    const stepDiv = document.createElement('div');
                                    stepDiv.className = 'reasoning-step';

                                    // Parse JSON in result if it's Information Retrieval step
                                    let resultContent = event.data.result;
                                    if (event.data.title === 'Information Retrieval') {
                                        try {
                                            console.log('Parsing Information Retrieval data:', event.data.result);
                                            const retrieval = JSON.parse(event.data.result);
                                            console.log('Parsed retrieval:', retrieval);

                                            // Extract just the PDF filenames from the full paths
                                            const extractPdfName = (path) => {
                                                // Get the last part of the path
                                                const parts = path.split('/');
                                                const filename = parts[parts.length - 1];
                                                // Remove .pdf extension for cleaner display
                                                return filename.replace('.pdf', '');
                                            };

                                            // Format the source PDFs nicely
                                            if (retrieval.source_pdfs && retrieval.source_pdfs.length > 0) {
                                                console.log('Found source_pdfs:', retrieval.source_pdfs);
                                                const pdfNames = retrieval.source_pdfs.map(extractPdfName);
                                                resultContent = `
                                                    <div class="retrieval-details">
                                                        <div class="pdf-sources">
                                                            <strong>📄 Source PDFs:</strong>
                                                            ${pdfNames.map(pdf => `<div class="source-pdf-item">• ${pdf}</div>`).join('')}
                                                        </div>
                                                    </div>
                                                `;
                                                console.log('Formatted PDF content:', resultContent);
                                            } else if (retrieval.data_sources_count > 0) {
                                                console.log('No PDFs, but found documents:', retrieval.data_sources_count);
                                                // Fallback if no PDFs but documents were found
                                                resultContent = `
                                                    <div class="retrieval-details">
                                                        <div>📊 Analyzed ${retrieval.data_sources_count} document${retrieval.data_sources_count > 1 ? 's' : ''}</div>
                                                    </div>
                                                `;
                                            } else {
                                                console.log('No relevant documents found');
                                                resultContent = 'No relevant documents found';
                                            }
                                        } catch (e) {
                                            console.error('Failed to parse Information Retrieval JSON:', e);
                                            console.error('Raw data was:', event.data.result);

                                            // FALLBACK: Extract ONLY from source_pdfs field in JSON
                                            const sourcePdfsMatch = event.data.result.match(/"source_pdfs":\s*\[(.*?)\]/);
                                            if (sourcePdfsMatch) {
                                                const pdfMatches = sourcePdfsMatch[1].match(/"([^"]+)"/g);
                                                if (pdfMatches && pdfMatches.length > 0) {
                                                    const pdfFiles = pdfMatches.map(m => m.replace(/"/g, '').replace('.pdf', ''));
                                                    resultContent = `
                                                        <div class="retrieval-details">
                                                            <div class="pdf-sources">
                                                                <strong>📄 Source PDFs:</strong>
                                                                ${pdfFiles.map(pdf => `<div class="source-pdf-item">• ${pdf}</div>`).join('')}
                                                            </div>
                                                        </div>
                                                    `;
                                                    console.log('Used fallback regex extraction for PDFs:', pdfFiles);
                                                }
                                            }
                                        }
                                    }

                                    stepDiv.innerHTML = `
                                        <div class="step-number">Step ${event.data.step_number}</div>
                                        <div class="step-title">${event.data.title}</div>
                                        <div class="step-result">${resultContent}</div>
                                    `;
                                    elements.reasoningPanel.appendChild(stepDiv);

                                    // Animate in
                                    setTimeout(() => stepDiv.classList.add('visible'), 50);
                                }
                                reasoningSteps.push(event.data);
                                break;

                            case 'TEXT_MESSAGE_CHUNK':
                                if (event.data?.content) {
                                    fullText += event.data.content;
                                    messageContent.textContent = fullText;
                                    // Auto-scroll
                                    if (elements.messages) {
                                        elements.messages.scrollTop = elements.messages.scrollHeight;
                                    }
                                }
                                break;

                            case 'ANALYSIS_METADATA':
                                if (event.data) {
                                    // Add metadata badge to message (without source PDFs - those go in reasoning panel)
                                    const metadataDiv = document.createElement('div');
                                    metadataDiv.className = 'message-metadata';

                                    let metadataContent = `
                                        <span class="confidence">Confidence: ${Math.round(event.data.confidence * 100)}%</span>
                                        <span class="sources">Sources: ${event.data.sources_used}</span>
                                        <span class="components">Components: ${event.data.total_components}</span>
                                    `;

                                    metadataDiv.innerHTML = metadataContent;
                                    messageElement.appendChild(metadataDiv);
                                }
                                break;

                            case 'TEXT_MESSAGE_END':
                                console.log('Message complete');
                                break;
                        }
                    } catch (e) {
                        console.error('Error parsing SSE event:', e);
                    }
                }
            }
        }
    } finally {
        messageElement.classList.remove('streaming');

        // Speak response if voice enabled
        if (voiceManager && voiceManager.voiceEnabled && fullText) {
            await voiceManager.speakText(fullText);
        }

        // Save assistant response to conversation manager
        if (conversationManager && fullText) {
            conversationManager.addMessage('assistant', fullText, {
                reasoning_steps: reasoningSteps
            });
        }

        // Store reasoning steps
        state.reasoningSteps = reasoningSteps;
    }
}

// Analyze trellis components specifically
async function analyzeTrelliComponents() {
    try {
        const response = await fetch(`${API_BASE}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ topic: 'trellis_base_components' })
        });

        const analysis = await response.json();

        // Display analysis results
        const analysisMessage = `
Trellis Component Analysis:
- Total trellis components: ${analysis.total_trellis_components}
- Unique dimension groups: ${analysis.dimension_groups}
- Base component types: ${analysis.base_components?.length || 0}

Dimension Groups Found:
${Object.entries(analysis.groups || {}).map(([dim, count]) =>
    `  • ${dim}: ${count} components`).join('\n')}
        `;

        addMessage('assistant', analysisMessage);

    } catch (error) {
        console.error('Error analyzing trellis components:', error);
        addMessage('assistant', 'Error performing trellis analysis. Please try again.');
    }
}

// Add message to chat with enhanced styling
function addMessage(role, content, streaming = false, isInitial = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}${streaming ? ' streaming' : ''}${isInitial ? ' initial' : ''}`;

    const headerDiv = document.createElement('div');
    headerDiv.className = 'message-header';
    headerDiv.textContent = role === 'user' ? '👤 You' : '🤖 Assistant (Enhanced)';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Support markdown-style formatting
    if (!streaming) {
        contentDiv.innerHTML = formatMessageContent(content);
    } else {
        contentDiv.textContent = content;
    }

    messageDiv.appendChild(headerDiv);
    messageDiv.appendChild(contentDiv);

    if (elements.messages) {
        elements.messages.appendChild(messageDiv);
        elements.messages.scrollTop = elements.messages.scrollHeight;
    }

    return messageDiv;
}

// Format message content with basic markdown support
function formatMessageContent(content) {
    return content
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/^- (.+)$/gm, '<li>$1</li>')
        .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
}

// Hook for voice manager
if (window.VoiceManager) {
    VoiceManager.prototype.sendMessageWithVoice = async function(text) {
        await sendMessage(text);
    };
}

// Periodic health check
setInterval(checkBackendStatus, 30000);

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}