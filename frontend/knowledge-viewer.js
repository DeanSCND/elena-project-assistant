/**
 * Knowledge Viewer Module
 * Handles displaying and managing learned knowledge
 */

class KnowledgeViewer {
    constructor() {
        this.knowledgeData = {};
        this.currentEditingId = null;
        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        // Create modal HTML if not exists
        if (!document.getElementById('knowledge-modal')) {
            this.createModal();
        }

        // Query elements AFTER modal is created
        this.modal = document.getElementById('knowledge-modal');
        this.closeBtn = document.getElementById('knowledge-close');
        this.searchInput = document.getElementById('knowledge-search');
        this.filterButtons = document.querySelectorAll('.knowledge-filter');
        this.contentArea = document.getElementById('knowledge-content');
        this.exportBtn = document.getElementById('knowledge-export');
        this.refreshBtn = document.getElementById('knowledge-refresh');
        this.addBtn = document.getElementById('knowledge-add');
        this.addForm = document.getElementById('knowledge-add-form');
        this.saveNewBtn = document.getElementById('knowledge-save-new');
        this.cancelAddBtn = document.getElementById('knowledge-cancel-add');

        console.log('Add button found:', this.addBtn);
        console.log('Add form found:', this.addForm);
        console.log('Cancel button found:', this.cancelAddBtn);

        // Ensure form is hidden on initialization
        if (this.addForm) {
            this.addForm.classList.add('hidden');
            console.log('Form hidden on init');
        }
        if (this.contentArea) {
            this.contentArea.classList.remove('hidden');
            console.log('Content area shown on init');
        }
    }

    createModal() {
        const modalHTML = `
            <div id="knowledge-modal" class="modal hidden">
                <div class="modal-content modal-wide">
                    <div class="modal-header">
                        <h2>📖 Knowledge Base</h2>
                        <button class="modal-close" id="knowledge-modal-close">×</button>
                    </div>
                    <div class="modal-body">
                        <div class="knowledge-controls">
                            <input
                                type="text"
                                id="knowledge-search"
                                placeholder="Search knowledge..."
                                class="knowledge-search"
                            />
                            <div class="knowledge-filters">
                                <button class="knowledge-filter active" data-type="all">All</button>
                                <button class="knowledge-filter" data-type="rule">📋 Rules</button>
                                <button class="knowledge-filter" data-type="fact">📌 Facts</button>
                                <button class="knowledge-filter" data-type="calculation">🔢 Calculations</button>
                                <button class="knowledge-filter" data-type="reference">🔗 References</button>
                                <button class="knowledge-filter" data-type="correction">✏️ Corrections</button>
                            </div>
                            <div class="knowledge-actions">
                                <button id="knowledge-add" class="action-btn action-btn-primary" title="Add Knowledge">➕ Add</button>
                                <button id="knowledge-refresh" class="action-btn" title="Refresh">🔄</button>
                                <button id="knowledge-export" class="action-btn" title="Export">💾</button>
                            </div>
                        </div>
                        <div id="knowledge-stats" class="knowledge-stats hidden">
                            <span class="stat">Total: <strong id="stat-total">0</strong></span>
                            <span class="stat">Rules: <strong id="stat-rules">0</strong></span>
                            <span class="stat">Facts: <strong id="stat-facts">0</strong></span>
                            <span class="stat">Most Used: <strong id="stat-most-used">-</strong></span>
                        </div>
                        <div id="knowledge-add-form" class="knowledge-add-form hidden">
                            <h3>➕ Add New Knowledge</h3>
                            <div class="form-group">
                                <label for="add-knowledge-text">Knowledge:</label>
                                <textarea id="add-knowledge-text" placeholder="Enter the knowledge you want to add..." rows="3"></textarea>
                            </div>
                            <div class="form-group">
                                <label for="add-knowledge-type">Type:</label>
                                <select id="add-knowledge-type">
                                    <option value="fact">📌 Fact</option>
                                    <option value="rule">📋 Rule</option>
                                    <option value="calculation">🔢 Calculation</option>
                                    <option value="reference">🔗 Reference</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="add-knowledge-tags">Tags (comma separated):</label>
                                <input type="text" id="add-knowledge-tags" placeholder="e.g., trellis, dimensions, hvac" />
                            </div>
                            <div class="form-buttons">
                                <button id="knowledge-save-new" class="btn-primary">Save</button>
                                <button id="knowledge-cancel-add" class="btn-secondary">Cancel</button>
                            </div>
                        </div>
                        <div id="knowledge-content" class="knowledge-list">
                            <p class="placeholder">Loading knowledge base...</p>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button id="knowledge-close" class="btn-secondary">Close</button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    attachEventListeners() {
        // Close button
        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', () => this.close());
        }

        // Modal close button (X)
        const modalCloseBtn = document.getElementById('knowledge-modal-close');
        if (modalCloseBtn) {
            modalCloseBtn.addEventListener('click', () => this.close());
        }

        // Search input
        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => {
                this.filterKnowledge(e.target.value);
            });
        }

        // Filter buttons
        this.filterButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setActiveFilter(e.target);
                this.displayKnowledge(e.target.dataset.type);
            });
        });

        // Export button
        if (this.exportBtn) {
            this.exportBtn.addEventListener('click', () => this.exportKnowledge());
        }

        // Refresh button
        if (this.refreshBtn) {
            this.refreshBtn.addEventListener('click', () => this.loadKnowledge());
        }

        // Add button
        if (this.addBtn) {
            this.addBtn.addEventListener('click', () => this.showAddForm());
        }

        // Save new knowledge button
        if (this.saveNewBtn) {
            this.saveNewBtn.addEventListener('click', () => this.saveNewKnowledge());
        }

        // Cancel add button
        if (this.cancelAddBtn) {
            this.cancelAddBtn.addEventListener('click', () => this.hideAddForm());
        }

        // Click outside to close
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });
    }

    async open() {
        this.modal.classList.remove('hidden');
        await this.loadKnowledge();
    }

    close() {
        this.modal.classList.add('hidden');
    }

    async loadKnowledge() {
        try {
            const response = await fetch('http://localhost:8100/learned-knowledge');
            if (!response.ok) throw new Error('Failed to load knowledge');

            this.knowledgeData = await response.json();
            this.updateStats();
            this.displayKnowledge('all');

            // Ensure add form is hidden when loading knowledge
            this.hideAddForm();
        } catch (error) {
            console.error('Error loading knowledge:', error);
            this.contentArea.innerHTML = '<p class="error">Failed to load knowledge base</p>';
        }
    }

    updateStats() {
        let total = 0;
        let rules = 0;
        let facts = 0;
        let mostUsed = { knowledge: '-', count: 0 };

        Object.entries(this.knowledgeData).forEach(([type, entries]) => {
            total += entries.length;
            if (type === 'rule') rules = entries.length;
            if (type === 'fact') facts = entries.length;

            entries.forEach(entry => {
                if (entry.usage_count > mostUsed.count) {
                    mostUsed = { knowledge: entry.knowledge.substring(0, 30) + '...', count: entry.usage_count };
                }
            });
        });

        const statsEl = document.getElementById('knowledge-stats');
        if (statsEl) {
            statsEl.classList.remove('hidden');
            document.getElementById('stat-total').textContent = total;
            document.getElementById('stat-rules').textContent = rules;
            document.getElementById('stat-facts').textContent = facts;
            document.getElementById('stat-most-used').textContent = mostUsed.knowledge;
        }
    }

    displayKnowledge(filterType = 'all') {
        let html = '';
        let hasEntries = false;

        Object.entries(this.knowledgeData).forEach(([type, entries]) => {
            if (filterType !== 'all' && type !== filterType) return;
            if (entries.length === 0) return;

            hasEntries = true;
            const typeLabels = {
                'rule': '📋 Rules',
                'fact': '📌 Facts',
                'calculation': '🔢 Calculations',
                'reference': '🔗 References',
                'correction': '✏️ Corrections'
            };

            html += `<div class="knowledge-section">
                <h3>${typeLabels[type] || type}</h3>
                <div class="knowledge-entries">`;

            entries.forEach(entry => {
                const date = new Date(entry.created_at).toLocaleDateString();
                const tags = entry.tags.map(tag => `<span class="tag">${tag}</span>`).join('');

                html += `
                    <div class="knowledge-entry" data-id="${entry.id}">
                        <div class="entry-header">
                            <span class="entry-type">${type}</span>
                            <span class="entry-date">${date}</span>
                            <span class="entry-usage">Used ${entry.usage_count}x</span>
                            <div class="entry-actions">
                                <button class="edit-btn" onclick="knowledgeViewer.editEntry('${entry.id}')" title="Edit">✏️</button>
                                <button class="delete-btn" onclick="knowledgeViewer.deleteEntry('${entry.id}')" title="Delete">🗑️</button>
                            </div>
                        </div>
                        <div class="entry-content">
                            <div class="entry-knowledge">${this.escapeHtml(entry.knowledge)}</div>
                            ${entry.trigger !== entry.knowledge ? `<div class="entry-trigger">Original: "${this.escapeHtml(entry.trigger)}"</div>` : ''}
                            ${tags ? `<div class="entry-tags">${tags}</div>` : ''}
                            ${entry.examples && entry.examples.length > 0 ?
                                `<div class="entry-examples">Examples: ${entry.examples.join(', ')}</div>` : ''}
                        </div>
                        <div class="entry-edit hidden">
                            <textarea class="edit-textarea">${entry.knowledge}</textarea>
                            <div class="edit-buttons">
                                <button onclick="knowledgeViewer.saveEdit('${entry.id}')">Save</button>
                                <button onclick="knowledgeViewer.cancelEdit('${entry.id}')">Cancel</button>
                            </div>
                        </div>
                    </div>`;
            });

            html += '</div></div>';
        });

        if (!hasEntries) {
            html = '<p class="placeholder">No knowledge entries found</p>';
        }

        this.contentArea.innerHTML = html;

        // Ensure content area is visible and form is hidden after displaying
        if (this.contentArea) {
            this.contentArea.classList.remove('hidden');
        }
    }

    filterKnowledge(searchTerm) {
        if (!searchTerm) {
            this.displayKnowledge(this.getCurrentFilterType());
            return;
        }

        const filtered = {};
        Object.entries(this.knowledgeData).forEach(([type, entries]) => {
            filtered[type] = entries.filter(entry =>
                entry.knowledge.toLowerCase().includes(searchTerm.toLowerCase()) ||
                entry.trigger.toLowerCase().includes(searchTerm.toLowerCase()) ||
                entry.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
            );
        });

        // Temporarily replace data and display
        const originalData = this.knowledgeData;
        this.knowledgeData = filtered;
        this.displayKnowledge(this.getCurrentFilterType());
        this.knowledgeData = originalData;
    }

    getCurrentFilterType() {
        const activeFilter = document.querySelector('.knowledge-filter.active');
        return activeFilter ? activeFilter.dataset.type : 'all';
    }

    setActiveFilter(button) {
        this.filterButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
    }

    editEntry(entryId) {
        // Hide all other edit forms
        document.querySelectorAll('.entry-edit').forEach(el => el.classList.add('hidden'));
        document.querySelectorAll('.entry-content').forEach(el => el.classList.remove('hidden'));

        const entry = document.querySelector(`[data-id="${entryId}"]`);
        if (entry) {
            entry.querySelector('.entry-content').classList.add('hidden');
            entry.querySelector('.entry-edit').classList.remove('hidden');
            this.currentEditingId = entryId;
        }
    }

    cancelEdit(entryId) {
        const entry = document.querySelector(`[data-id="${entryId}"]`);
        if (entry) {
            entry.querySelector('.entry-content').classList.remove('hidden');
            entry.querySelector('.entry-edit').classList.add('hidden');
        }
        this.currentEditingId = null;
    }

    async saveEdit(entryId) {
        const entry = document.querySelector(`[data-id="${entryId}"]`);
        const newKnowledge = entry.querySelector('.edit-textarea').value;

        try {
            const response = await fetch(`http://localhost:8100/learned-knowledge/${entryId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    updates: { knowledge: newKnowledge }
                })
            });

            if (!response.ok) throw new Error('Failed to update knowledge');

            // Refresh the display
            await this.loadKnowledge();
            this.showNotification('Knowledge updated successfully', 'success');
        } catch (error) {
            console.error('Error updating knowledge:', error);
            this.showNotification('Failed to update knowledge', 'error');
        }
    }

    async deleteEntry(entryId) {
        if (!confirm('Are you sure you want to delete this knowledge entry?')) return;

        try {
            const response = await fetch(`http://localhost:8100/learned-knowledge/${entryId}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Failed to delete knowledge');

            // Refresh the display
            await this.loadKnowledge();
            this.showNotification('Knowledge deleted successfully', 'success');
        } catch (error) {
            console.error('Error deleting knowledge:', error);
            this.showNotification('Failed to delete knowledge', 'error');
        }
    }

    async exportKnowledge() {
        try {
            const response = await fetch('http://localhost:8100/learned-knowledge/export', {
                method: 'POST'
            });

            if (!response.ok) throw new Error('Failed to export knowledge');

            const result = await response.json();
            this.showNotification(`Knowledge exported to: ${result.path}`, 'success');
        } catch (error) {
            console.error('Error exporting knowledge:', error);
            this.showNotification('Failed to export knowledge', 'error');
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    showAddForm() {
        console.log('showAddForm called');
        if (this.addForm && this.contentArea) {
            this.addForm.classList.remove('hidden');
            this.contentArea.classList.add('hidden');
            // Clear form
            const textField = document.getElementById('add-knowledge-text');
            const typeField = document.getElementById('add-knowledge-type');
            const tagsField = document.getElementById('add-knowledge-tags');
            if (textField) textField.value = '';
            if (typeField) typeField.value = 'fact';
            if (tagsField) tagsField.value = '';
        }
    }

    hideAddForm() {
        console.log('hideAddForm called');
        if (this.addForm && this.contentArea) {
            this.addForm.classList.add('hidden');
            this.contentArea.classList.remove('hidden');
        }
    }

    async saveNewKnowledge() {
        const knowledgeText = document.getElementById('add-knowledge-text').value.trim();
        const knowledgeType = document.getElementById('add-knowledge-type').value;
        const tagsInput = document.getElementById('add-knowledge-tags').value;

        if (!knowledgeText) {
            this.showNotification('Please enter knowledge text', 'warning');
            return;
        }

        // Parse tags
        const tags = tagsInput.split(',').map(t => t.trim()).filter(t => t);

        try {
            // Create knowledge entry via backend
            const response = await fetch('http://localhost:8100/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: `Remember, ${knowledgeText}`,
                    reasoning_mode: false
                })
            });

            if (!response.ok) throw new Error('Failed to save knowledge');

            this.showNotification('Knowledge added successfully!', 'success');
            this.hideAddForm();
            await this.loadKnowledge();
        } catch (error) {
            console.error('Error saving knowledge:', error);
            this.showNotification('Failed to add knowledge', 'error');
        }
    }
}

// Initialize knowledge viewer
const knowledgeViewer = new KnowledgeViewer();

// Export for use in other modules
window.knowledgeViewer = knowledgeViewer;