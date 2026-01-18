// Conversation Management Module

const API_BASE = window.location.hostname === 'localhost'
    ? '/api'
    : '';

class ConversationManager {
    constructor() {
        this.currentModel = 'gpt-4o';
        this.messages = [];
        this.sessionId = this.generateSessionId();
        this.conversationId = null; // Firestore conversation ID
    }

    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    addMessage(role, content, metadata = {}) {
        const message = {
            role,
            content,
            timestamp: new Date().toISOString(),
            model: this.currentModel,
            ...metadata
        };
        this.messages.push(message);
        return message;
    }

    getConversationData() {
        const title = this.generateTitle();
        return {
            session_id: this.sessionId,
            title,
            messages: this.messages,
            model: this.currentModel,
            created_at: this.messages[0]?.timestamp || new Date().toISOString(),
            message_count: this.messages.length
        };
    }

    generateTitle() {
        // Generate title from first user message
        if (this.messages.length > 0) {
            const firstUserMessage = this.messages.find(m => m.role === 'user');
            if (firstUserMessage) {
                return firstUserMessage.content.substring(0, 50) +
                       (firstUserMessage.content.length > 50 ? '...' : '');
            }
        }
        return `Conversation ${new Date().toLocaleDateString()}`;
    }

    async autoSaveConversation() {
        /**
         * Silent auto-save after each assistant response.
         * Saves with user_saved=false (not visible in user's saved list).
         */
        try {
            const conversationData = this.getConversationData();
            const response = await fetch(`${API_BASE}/auto-save-conversation`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    conversation_id: this.conversationId,
                    messages: this.messages,
                    metadata: {
                        session_id: this.sessionId,
                        model: this.currentModel
                    }
                })
            });

            if (!response.ok) {
                console.warn('Failed to auto-save conversation (non-critical)');
                return null;
            }

            const result = await response.json();
            if (result.success && !this.conversationId) {
                // Store conversation ID for subsequent saves
                this.conversationId = result.conversation_id;
            }
            return result;
        } catch (error) {
            console.warn('Error auto-saving conversation (non-critical):', error);
            return null;
        }
    }

    async saveConversation() {
        /**
         * User-initiated save: sets user_saved=true and adds title.
         * Called when user clicks 'Save' button.
         */
        try {
            const conversationData = this.getConversationData();
            const response = await fetch(`${API_BASE}/save_conversation`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    conversation_id: this.conversationId,
                    title: conversationData.title,
                    messages: this.messages,
                    metadata: {
                        session_id: this.sessionId,
                        model: this.currentModel
                    }
                })
            });

            if (!response.ok) {
                throw new Error('Failed to save conversation');
            }

            const result = await response.json();
            if (result.success && !this.conversationId) {
                this.conversationId = result.conversation_id;
            }
            return result;
        } catch (error) {
            console.error('Error saving conversation:', error);
            throw error;
        }
    }

    async loadConversations() {
        try {
            const response = await fetch(`${API_BASE}/conversations`);
            if (!response.ok) {
                throw new Error('Failed to load conversations');
            }
            const data = await response.json();
            return data.conversations || [];
        } catch (error) {
            console.error('Error loading conversations:', error);
            return [];
        }
    }

    async loadConversation(conversationId) {
        try {
            const response = await fetch(`${API_BASE}/conversations/${conversationId}`);
            if (!response.ok) {
                throw new Error('Failed to load conversation');
            }
            const conversation = await response.json();

            // Restore conversation state
            this.messages = conversation.messages || [];
            this.conversationId = conversation.conversation_id;

            return conversation;
        } catch (error) {
            console.error('Error loading conversation:', error);
            throw error;
        }
    }

    clear() {
        this.messages = [];
        this.sessionId = this.generateSessionId();
        this.conversationId = null; // Reset conversation ID for new conversation
    }

    setModel(model) {
        this.currentModel = model;
    }
}

// Model Management
class ModelManager {
    constructor(conversationManager) {
        this.conversationManager = conversationManager;
        this.currentModel = 'gpt-4o';
        this.repriming = false;
    }

    async switchModel(newModel) {
        if (this.repriming) return;

        this.currentModel = newModel;
        this.conversationManager.setModel(newModel);

        // Show re-priming modal
        const modal = document.getElementById('reprime-modal');
        const logContainer = document.getElementById('reprime-log');
        const progressBar = document.getElementById('reprime-progress');
        const closeBtn = document.getElementById('reprime-close');

        modal.classList.remove('hidden');
        logContainer.innerHTML = '';
        progressBar.classList.add('hidden');
        closeBtn.disabled = true;
        this.repriming = true;

        try {
            const response = await fetch(`${API_BASE}/reprime`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ model: newModel })
            });

            if (!response.ok) {
                throw new Error('Failed to reprime knowledge base');
            }

            // Process SSE stream
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

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
                            this.handleReprimeEvent(event, logContainer, progressBar);
                        } catch (e) {
                            console.error('Error parsing reprime event:', e);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error repriming:', error);
            this.addLogEntry(logContainer, `❌ Error: ${error.message}`, 'error');
        } finally {
            this.repriming = false;
            closeBtn.disabled = false;
            this.addLogEntry(logContainer, '\n✅ Re-priming complete!', 'success');
        }
    }

    handleReprimeEvent(event, logContainer, progressBar) {
        switch (event.type) {
            case 'REPRIME_START':
                this.addLogEntry(logContainer, `🚀 Starting re-prime with model: ${event.data.model}`, 'info');
                break;

            case 'REPRIME_LOG':
                this.addLogEntry(logContainer, event.data.message);
                break;

            case 'REPRIME_PROGRESS':
                const percent = Math.round((event.data.current / event.data.total) * 100);
                progressBar.classList.remove('hidden');
                progressBar.querySelector('.progress-fill').style.width = `${percent}%`;
                progressBar.querySelector('.progress-text').textContent = `${percent}% - ${event.data.file}`;
                this.addLogEntry(logContainer, event.data.message);
                break;

            case 'REPRIME_ERROR':
                this.addLogEntry(logContainer, `❌ ${event.data.error}`, 'error');
                break;

            case 'REPRIME_COMPLETE':
                progressBar.querySelector('.progress-fill').style.width = '100%';
                progressBar.querySelector('.progress-text').textContent = '100% Complete';
                this.addLogEntry(logContainer, `✓ Analyzed ${event.data.documents_analyzed} documents`, 'success');
                break;
        }
    }

    addLogEntry(container, message, type = '') {
        const entry = document.createElement('div');
        entry.className = `log-entry ${type}`;
        entry.textContent = message;
        container.appendChild(entry);
        container.scrollTop = container.scrollHeight;
    }
}

// Export for use in main app
window.ConversationManager = ConversationManager;
window.ModelManager = ModelManager;