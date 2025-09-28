/**
 * Sistema de Gerenciamento de Sessão Unificada
 * Compatível com Claude Code SDK (.jsonl)
 */

class SessionManager {
    constructor() {
        this.currentSessionId = null;
        this.projectPath = null;
        this.messages = [];
        this.metadata = {
            created: new Date().toISOString(),
            lastModified: new Date().toISOString(),
            messageCount: 0
        };
    }

    /**
     * Inicializa sessão baseada na URL ou cria nova
     */
    async initialize() {
        const path = window.location.pathname;

        // Extrai projeto e sessão da URL
        // Formato: /project-path/session-id ou /
        const pathMatch = path.match(/^\/(.+?)\/([a-f0-9-]{36})$/);

        if (pathMatch) {
            // URL com projeto e sessão
            this.projectPath = pathMatch[1];
            this.currentSessionId = pathMatch[2];

            // Carregar histórico existente
            await this.loadSession();
        } else if (path !== '/' && path.length > 1) {
            // URL com apenas projeto - criar nova sessão
            this.projectPath = path.substring(1);
            this.currentSessionId = this.generateSessionId();

            // Redirecionar para URL completa
            window.history.replaceState(null, '', `/${this.projectPath}/${this.currentSessionId}`);
        } else {
            // Página inicial - usar sessão padrão
            this.projectPath = '-Users-2a-Desktop-neo4j-agent-claude-code-sdk';
            this.currentSessionId = this.getOrCreateDefaultSession();

            // Atualizar URL sem recarregar
            window.history.replaceState(null, '', `/${this.projectPath}/${this.currentSessionId}`);
        }

        this.updateUI();
        return this.currentSessionId;
    }

    /**
     * Gera ID de sessão no formato UUID
     */
    generateSessionId() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    /**
     * Obtém ou cria sessão padrão do localStorage
     */
    getOrCreateDefaultSession() {
        const storageKey = `session_${this.projectPath}`;
        let sessionId = localStorage.getItem(storageKey);

        if (!sessionId) {
            sessionId = this.generateSessionId();
            localStorage.setItem(storageKey, sessionId);
        }

        return sessionId;
    }

    /**
     * Carrega sessão do backend ou localStorage
     */
    async loadSession() {
        try {
            // Primeiro tenta carregar do localStorage (cache local)
            const localData = this.loadFromLocalStorage();
            if (localData) {
                this.messages = localData.messages || [];
                this.metadata = localData.metadata || this.metadata;
            }

            // Depois tenta sincronizar com backend
            const response = await fetch(`/api/sessions/${this.currentSessionId}`);
            if (response.ok) {
                const data = await response.json();
                this.messages = data.messages || this.messages;
                this.metadata = data.metadata || this.metadata;

                // Atualiza cache local
                this.saveToLocalStorage();
            }
        } catch (error) {
            console.log('Usando cache local:', error);
        }

        // Renderiza mensagens existentes
        this.renderMessages();
    }

    /**
     * Salva sessão no localStorage
     */
    saveToLocalStorage() {
        const storageKey = `session_data_${this.currentSessionId}`;
        const data = {
            sessionId: this.currentSessionId,
            projectPath: this.projectPath,
            messages: this.messages,
            metadata: this.metadata
        };

        try {
            localStorage.setItem(storageKey, JSON.stringify(data));
        } catch (e) {
            console.warn('localStorage cheio, limpando sessões antigas...');
            this.cleanOldSessions();
        }
    }

    /**
     * Carrega sessão do localStorage
     */
    loadFromLocalStorage() {
        const storageKey = `session_data_${this.currentSessionId}`;
        const data = localStorage.getItem(storageKey);

        if (data) {
            try {
                return JSON.parse(data);
            } catch (e) {
                console.error('Erro ao parsear dados da sessão:', e);
            }
        }

        return null;
    }

    /**
     * Limpa sessões antigas (mais de 7 dias)
     */
    cleanOldSessions() {
        const now = Date.now();
        const maxAge = 7 * 24 * 60 * 60 * 1000; // 7 dias

        for (let i = localStorage.length - 1; i >= 0; i--) {
            const key = localStorage.key(i);
            if (key?.startsWith('session_data_')) {
                try {
                    const data = JSON.parse(localStorage.getItem(key));
                    const age = now - new Date(data.metadata?.lastModified || 0).getTime();

                    if (age > maxAge) {
                        localStorage.removeItem(key);
                    }
                } catch (e) {
                    // Remove item corrompido
                    localStorage.removeItem(key);
                }
            }
        }
    }

    /**
     * Adiciona mensagem à sessão
     */
    addMessage(role, content, metadata = {}) {
        const message = {
            id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            role: role,
            content: content,
            timestamp: new Date().toISOString(),
            ...metadata
        };

        this.messages.push(message);
        this.metadata.lastModified = new Date().toISOString();
        this.metadata.messageCount = this.messages.length;

        // Salva localmente
        this.saveToLocalStorage();

        // Tenta salvar no backend (fire-and-forget)
        this.saveToBackend().catch(console.error);

        return message;
    }

    /**
     * Salva sessão no backend
     */
    async saveToBackend() {
        try {
            await fetch(`/api/sessions/${this.currentSessionId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sessionId: this.currentSessionId,
                    projectPath: this.projectPath,
                    messages: this.messages,
                    metadata: this.metadata
                })
            });
        } catch (error) {
            console.log('Salvando apenas localmente:', error);
        }
    }

    /**
     * Exporta sessão para formato .jsonl (Claude Code SDK)
     */
    exportToJSONL() {
        const lines = this.messages.map(msg => {
            return JSON.stringify({
                id: msg.id,
                type: 'message',
                role: msg.role,
                content: msg.content,
                timestamp: msg.timestamp,
                model: msg.model || 'claude-3-opus-20240229'
            });
        });

        return lines.join('\n');
    }

    /**
     * Renderiza mensagens existentes
     */
    renderMessages() {
        const messagesDiv = document.getElementById('messages');
        if (!messagesDiv) return;

        messagesDiv.innerHTML = '';

        this.messages.forEach(msg => {
            const isUser = msg.role === 'user';
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'info' : 'success'}`;

            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';

            if (isUser) {
                contentDiv.innerHTML = `<span style="color: #00ffff">👤 USER:</span><br>${this.escapeHtml(msg.content)}`;
            } else {
                contentDiv.innerHTML = `<span style="color: #00ff00">🤖 CLAUDE:</span><br>${this.renderMarkdown(msg.content)}`;
            }

            messageDiv.appendChild(contentDiv);
            messagesDiv.appendChild(messageDiv);
        });

        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    /**
     * Atualiza UI com informações da sessão
     */
    updateUI() {
        // Adiciona informações da sessão no status
        const statusPanel = document.getElementById('status');
        if (statusPanel) {
            statusPanel.title = `Sessão: ${this.currentSessionId}\nProjeto: ${this.projectPath}`;
        }

        // Adiciona breadcrumb
        this.createBreadcrumb();
    }

    /**
     * Cria breadcrumb de navegação
     */
    createBreadcrumb() {
        let breadcrumb = document.getElementById('session-breadcrumb');
        if (!breadcrumb) {
            breadcrumb = document.createElement('div');
            breadcrumb.id = 'session-breadcrumb';
            breadcrumb.style.cssText = `
                padding: 8px;
                background: rgba(0, 255, 0, 0.1);
                border-bottom: 1px solid #00ff00;
                font-size: 12px;
                color: #00ff00;
                font-family: monospace;
            `;

            const container = document.querySelector('.container');
            if (container) {
                container.insertBefore(breadcrumb, container.firstChild);
            }
        }

        breadcrumb.innerHTML = `
            📁 <a href="/" style="color: #00ff00">Home</a> /
            <span>${this.projectPath}</span> /
            <span style="color: #00ffff">${this.currentSessionId}</span>
            <span style="float: right">
                💬 ${this.messages.length} mensagens
                <button onclick="sessionManager.exportSession()" style="margin-left: 10px; font-size: 11px;">
                    📥 Exportar .jsonl
                </button>
            </span>
        `;
    }

    /**
     * Exporta e baixa sessão
     */
    exportSession() {
        const jsonl = this.exportToJSONL();
        const blob = new Blob([jsonl], { type: 'application/jsonl' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.currentSessionId}.jsonl`;
        a.click();

        URL.revokeObjectURL(url);
    }

    /**
     * Helpers
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    renderMarkdown(text) {
        return text
            .replace(/^### (.*?)$/gm, '<h3>$1</h3>')
            .replace(/^## (.*?)$/gm, '<h2>$1</h2>')
            .replace(/^# (.*?)$/gm, '<h1>$1</h1>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/```([\s\S]*?)```/g, '<pre style="background:#0a0a0a;padding:10px;border:1px solid #00ff00;">$1</pre>')
            .replace(/`([^`]+)`/g, '<code style="background:#0a0a0a;padding:2px 4px;border:1px solid #00ff00;">$1</code>')
            .replace(/\n/g, '<br>');
    }
}

// Instância global
window.sessionManager = new SessionManager();