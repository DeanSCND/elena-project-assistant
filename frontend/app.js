// Construction Agent POC - Frontend Client

// Use relative path when behind Vite proxy, or direct URL for standalone
const API_BASE = window.location.hostname === 'localhost' && window.location.port === '5173'
    ? '/api'  // Vite proxy
    : 'http://localhost:8100';  // Direct access

// State management
const state = {
    connected: false,
    messages: [],
    currentStreamingMessage: null
};

// Voice manager instance
let voiceManager = null;

// DOM elements
const elements = {
    messages: document.getElementById('messages'),
    messageInput: document.getElementById('message-input'),
    sendBtn: document.getElementById('send-btn'),
    chatForm: document.getElementById('chat-form'),
    connectionStatus: document.getElementById('connection-status'),
    thinkingIndicator: document.getElementById('thinking-indicator'),
    voiceToggle: document.getElementById('voice-toggle'),
    voiceInputBtn: document.getElementById('voice-input-btn'),
    docStatus: document.getElementById('doc-status')
};

// Initialize app
async function init() {
    console.log('🚀 Initializing Construction Agent...');

    // Check backend health
    await checkBackendStatus();

    // Setup event listeners
    setupEventListeners();

    // Initialize voice manager
    voiceManager = new VoiceManager();
    const voiceSupported = await voiceManager.init();
    if (!voiceSupported) {
        console.warn('Voice features not available');
        document.getElementById('voice-toggle').style.display = 'none';
        document.getElementById('voice-input-btn').style.display = 'none';
    }
}

// Check backend status
async function checkBackendStatus() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const health = await response.json();

        state.connected = true;
        updateConnectionStatus(true);

        // Update document status
        elements.docStatus.innerHTML = `
            <p>✅ ${health.documents_loaded} documents loaded</p>
            <p>📊 Context size: ${(health.total_context_size / 1000).toFixed(0)}K chars</p>
            <p>🤖 LLM: ${health.openai_configured ? 'OpenAI GPT-4o' : '❌ Not configured'}</p>
        `;
    } catch (error) {
        console.error('Backend not reachable:', error);
        state.connected = false;
        updateConnectionStatus(false);
        elements.docStatus.innerHTML = '<p>❌ Backend not connected</p>';
    }
}

// Update connection status indicator
function updateConnectionStatus(connected) {
    if (connected) {
        elements.connectionStatus.textContent = '● Connected';
        elements.connectionStatus.className = 'status-indicator connected';
    } else {
        elements.connectionStatus.textContent = '● Disconnected';
        elements.connectionStatus.className = 'status-indicator disconnected';
    }
}

// Setup event listeners
function setupEventListeners() {
    // Chat form submission
    elements.chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = elements.messageInput.value.trim();
        if (message) {
            await sendMessage(message);
        }
    });

    // Quick query links
    document.querySelectorAll('.quick-query').forEach(link => {
        link.addEventListener('click', async (e) => {
            e.preventDefault();
            const query = e.target.textContent;
            elements.messageInput.value = query;
            await sendMessage(query);
        });
    });

    // Voice toggle button
    elements.voiceToggle.addEventListener('click', () => {
        if (voiceManager) {
            voiceManager.toggleVoice();
        }
    });

    // Voice input button (push-to-talk)
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

    // Touch events for mobile
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

// Send message to backend
async function sendMessage(message) {
    if (!state.connected) {
        alert('Backend not connected. Please ensure the server is running.');
        return;
    }

    // Clear input
    elements.messageInput.value = '';
    elements.sendBtn.disabled = true;

    // Add user message to chat
    addMessage('user', message);

    // Show thinking indicator
    elements.thinkingIndicator.classList.remove('hidden');

    // Create assistant message container
    const assistantMessage = addMessage('assistant', '', true);

    try {
        // Use Server-Sent Events for streaming
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Process SSE stream
        await processSSEStream(response, assistantMessage);

    } catch (error) {
        console.error('Error sending message:', error);
        assistantMessage.querySelector('.message-content').textContent =
            'Sorry, there was an error processing your request. Please try again.';
    } finally {
        elements.thinkingIndicator.classList.add('hidden');
        elements.sendBtn.disabled = false;
        elements.messageInput.focus();
    }
}

// Process Server-Sent Events stream
async function processSSEStream(response, messageElement) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let fullText = '';

    const messageContent = messageElement.querySelector('.message-content');
    messageElement.classList.add('streaming');

    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');

            // Keep the last incomplete line in buffer
            buffer = lines.pop();

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') continue;

                    try {
                        const event = JSON.parse(data);
                        handleSSEEvent(event, messageContent, fullText);

                        // Update fullText if we have a chunk
                        if (event.type === 'TEXT_MESSAGE_CHUNK' && event.data?.content) {
                            fullText += event.data.content;
                            messageContent.textContent = fullText;
                        }
                    } catch (e) {
                        console.error('Error parsing SSE event:', e);
                    }
                }
            }
        }
    } finally {
        messageElement.classList.remove('streaming');

        // If voice is enabled, speak the response
        if (voiceManager && voiceManager.voiceEnabled && fullText) {
            await voiceManager.speakText(fullText);
        }
    }
}

// Handle different SSE event types (AG-UI protocol)
function handleSSEEvent(event, messageContent, currentText) {
    switch (event.type) {
        case 'RUN_STARTED':
            console.log('🏃 Run started:', event.data);
            break;

        case 'TEXT_MESSAGE_START':
            console.log('📝 Message start');
            break;

        case 'TEXT_MESSAGE_CHUNK':
            // Content is updated in processSSEStream
            break;

        case 'TEXT_MESSAGE_END':
            console.log('✅ Message complete');
            break;

        case 'RUN_FINISHED':
            console.log('🏁 Run finished');
            break;

        case 'RUN_ERROR':
            console.error('❌ Run error:', event.data);
            messageContent.textContent = 'An error occurred: ' + event.data.error;
            break;

        default:
            console.log('Unknown event type:', event.type);
    }
}

// Add message to chat
function addMessage(role, content, streaming = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}${streaming ? ' streaming' : ''}`;

    const headerDiv = document.createElement('div');
    headerDiv.className = 'message-header';
    headerDiv.textContent = role === 'user' ? '👤 You' : '🤖 Assistant';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;

    messageDiv.appendChild(headerDiv);
    messageDiv.appendChild(contentDiv);
    elements.messages.appendChild(messageDiv);

    // Scroll to bottom
    elements.messages.scrollTop = elements.messages.scrollHeight;

    return messageDiv;
}

// Hook for voice manager to send messages
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