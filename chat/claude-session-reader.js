/**
 * Leitor de Sessões do Claude Code SDK
 * Lê e interpreta arquivos .jsonl do diretório de projetos
 */

class ClaudeSessionReader {
    constructor() {
        this.projectPath = '/Users/2a/.claude/projects/-Users-2a-Desktop-neo4j-agent-claude-code-sdk';
        this.sessions = new Map();
        this.currentSessionId = null;
    }

    /**
     * Analisa a URL e determina qual sessão carregar
     */
    async initFromURL() {
        const path = window.location.pathname;

        // Formatos suportados:
        // / -> lista todas as sessões
        // /session/[uuid] -> visualiza sessão específica
        // /-Users-2a-Desktop-neo4j-agent-claude-code-sdk/[uuid] -> compatível com cc-sdk-chat

        const sessionMatch = path.match(/\/(?:session\/)?(?:-Users-2a-Desktop-neo4j-agent-claude-code-sdk\/)?([a-f0-9-]{36})/);

        if (sessionMatch) {
            this.currentSessionId = sessionMatch[1];
            await this.loadSession(this.currentSessionId);
        } else {
            await this.loadAllSessions();
        }
    }

    /**
     * Lista todas as sessões disponíveis
     */
    async loadAllSessions() {
        try {
            const response = await fetch('/api/sessions/list');
            if (response.ok) {
                const sessions = await response.json();
                this.displaySessionList(sessions);
            }
        } catch (error) {
            console.log('Erro ao carregar sessões:', error);
            this.displayOfflineMessage();
        }
    }

    /**
     * Carrega uma sessão específica
     */
    async loadSession(sessionId) {
        try {
            // Tenta carregar do backend
            const response = await fetch(`/api/sessions/read/${sessionId}`);
            if (response.ok) {
                const data = await response.json();
                this.parseSessionData(data);
                this.displaySession();
            }
        } catch (error) {
            console.log('Erro ao carregar sessão:', error);

            // Fallback: tenta carregar do localStorage se existir
            const cached = localStorage.getItem(`claude_session_${sessionId}`);
            if (cached) {
                this.parseSessionData(JSON.parse(cached));
                this.displaySession();
            } else {
                this.displayNotFound();
            }
        }
    }

    /**
     * Parseia dados da sessão do formato JSONL
     */
    parseSessionData(jsonlData) {
        const messages = [];
        const lines = jsonlData.split ? jsonlData.split('\n') : jsonlData;

        lines.forEach(line => {
            if (!line.trim()) return;

            try {
                const entry = JSON.parse(line);

                // Extrai mensagem baseado no tipo
                if (entry.type === 'user' && entry.message) {
                    messages.push({
                        id: entry.uuid,
                        role: 'user',
                        content: typeof entry.message.content === 'string'
                            ? entry.message.content
                            : entry.message.content[0]?.text || '',
                        timestamp: entry.timestamp
                    });
                } else if (entry.type === 'assistant' && entry.message) {
                    // Processa mensagens do assistant
                    let content = '';

                    if (entry.message.content) {
                        entry.message.content.forEach(block => {
                            if (block.type === 'text') {
                                content += block.text;
                            } else if (block.type === 'tool_use') {
                                content += `\n[🔧 Usando ferramenta: ${block.name}]\n`;
                            }
                        });
                    }

                    if (content) {
                        messages.push({
                            id: entry.uuid,
                            role: 'assistant',
                            content: content,
                            timestamp: entry.timestamp,
                            tokens: entry.message.usage
                        });
                    }
                }
            } catch (e) {
                console.error('Erro ao parsear linha:', e);
            }
        });

        this.sessions.set(this.currentSessionId, {
            id: this.currentSessionId,
            messages: messages,
            metadata: {
                totalMessages: messages.length,
                firstMessage: messages[0]?.timestamp,
                lastMessage: messages[messages.length - 1]?.timestamp
            }
        });
    }

    /**
     * Exibe lista de sessões disponíveis
     */
    displaySessionList(sessions) {
        const container = document.getElementById('messages') || document.querySelector('.container');

        container.innerHTML = `
            <div style="padding: 20px;">
                <h2 style="color: #00ff00;">📁 Sessões do Claude Code SDK</h2>
                <p style="color: #00ffff;">Projeto: -Users-2a-Desktop-neo4j-agent-claude-code-sdk</p>

                <div style="margin-top: 20px;">
                    ${sessions.map(session => `
                        <div style="
                            border: 1px solid #00ff00;
                            padding: 15px;
                            margin: 10px 0;
                            background: rgba(0, 255, 0, 0.05);
                            cursor: pointer;
                        " onclick="window.location.href='/session/${session.id}'">
                            <div style="color: #00ff00; font-weight: bold;">
                                💬 ${session.id}
                            </div>
                            <div style="color: #999; font-size: 12px; margin-top: 5px;">
                                📅 ${new Date(session.modified).toLocaleString('pt-BR')}
                                | 📝 ${session.messageCount || '?'} mensagens
                                | 📦 ${(session.size / 1024).toFixed(1)} KB
                            </div>
                            ${session.preview ? `
                                <div style="color: #ccc; font-size: 11px; margin-top: 8px;
                                           padding: 8px; background: rgba(0,0,0,0.3);
                                           border-left: 2px solid #00ff00;">
                                    "${session.preview}"
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    /**
     * Exibe sessão carregada
     */
    displaySession() {
        const session = this.sessions.get(this.currentSessionId);
        if (!session) return;

        const messagesDiv = document.getElementById('messages');
        if (!messagesDiv) return;

        // Limpa e adiciona breadcrumb
        messagesDiv.innerHTML = `
            <div style="
                padding: 10px;
                background: rgba(0, 255, 0, 0.1);
                border-bottom: 1px solid #00ff00;
                margin-bottom: 10px;
            ">
                <a href="/" style="color: #00ff00;">← Todas as Sessões</a>
                <span style="color: #00ffff; margin-left: 10px;">
                    Sessão: ${this.currentSessionId}
                </span>
                <span style="float: right; color: #999;">
                    ${session.messages.length} mensagens
                </span>
            </div>
        `;

        // Renderiza mensagens
        session.messages.forEach(msg => {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${msg.role === 'user' ? 'info' : 'success'}`;

            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';

            const timestamp = new Date(msg.timestamp).toLocaleTimeString('pt-BR');

            if (msg.role === 'user') {
                contentDiv.innerHTML = `
                    <span style="color: #00ffff">👤 USER [${timestamp}]:</span><br>
                    ${this.escapeHtml(msg.content)}
                `;
            } else {
                contentDiv.innerHTML = `
                    <span style="color: #00ff00">🤖 CLAUDE [${timestamp}]:</span>
                    ${msg.tokens ? `<span style="font-size: 10px; color: #666;">
                        (${msg.tokens.input_tokens}→${msg.tokens.output_tokens} tokens)
                    </span>` : ''}
                    <br>
                    ${this.renderMarkdown(msg.content)}
                `;
            }

            messageDiv.appendChild(contentDiv);
            messagesDiv.appendChild(messageDiv);
        });

        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    /**
     * Exibe mensagem quando offline
     */
    displayOfflineMessage() {
        const container = document.getElementById('messages') || document.querySelector('.container');
        container.innerHTML = `
            <div style="padding: 20px; text-align: center;">
                <h2 style="color: #ffff00;">⚠️ Modo Offline</h2>
                <p style="color: #ccc;">
                    Para visualizar as sessões do Claude Code SDK,
                    inicie o servidor backend:
                </p>
                <pre style="background: #111; padding: 10px; margin: 20px auto; display: inline-block;">
npm run serve:sessions
                </pre>
                <p style="color: #999; font-size: 12px; margin-top: 20px;">
                    Ou continue usando o chat normalmente para criar novas conversas.
                </p>
            </div>
        `;
    }

    /**
     * Exibe mensagem de não encontrado
     */
    displayNotFound() {
        const container = document.getElementById('messages') || document.querySelector('.container');
        container.innerHTML = `
            <div style="padding: 20px; text-align: center;">
                <h2 style="color: #ff0000;">❌ Sessão Não Encontrada</h2>
                <p style="color: #ccc;">
                    Sessão ${this.currentSessionId} não existe.
                </p>
                <a href="/" style="color: #00ff00;">← Voltar para Lista de Sessões</a>
            </div>
        `;
    }

    /**
     * Helpers
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text || '';
        return div.innerHTML;
    }

    renderMarkdown(text) {
        if (!text) return '';
        return text
            .replace(/^### (.*?)$/gm, '<h3>$1</h3>')
            .replace(/^## (.*?)$/gm, '<h2>$1</h2>')
            .replace(/^# (.*?)$/gm, '<h1>$1</h1>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/```([\s\S]*?)```/g, '<pre style="background:#0a0a0a;padding:10px;border:1px solid #00ff00;overflow-x:auto;">$1</pre>')
            .replace(/`([^`]+)`/g, '<code style="background:#0a0a0a;padding:2px 4px;border:1px solid #00ff00;">$1</code>')
            .replace(/\[🔧[^\]]*\]/g, match => `<span style="color:#ffff00;">${match}</span>`)
            .replace(/\n/g, '<br>');
    }
}

// Instância global
window.claudeReader = new ClaudeSessionReader();