/**
 * Neo4j Agent Chat - Versão Unificada com Visualizador de Sessões
 * Combina chat sem limitações + leitor de sessões Claude SDK
 */

// Configuração
const CONFIG = {
    API_URL: 'http://localhost:8080',
    RETRY_DELAYS: [1000, 2000, 4000, 8000],
    CONNECTION_TIMEOUT: 10 * 60 * 1000,
    CLAUDE_PROJECTS_PATH: '/Users/2a/.claude/projects/-Users-2a-Desktop-neo4j-agent-claude-code-sdk'
};

// Gerenciamento de requisições múltiplas
const activeRequests = new Map();
let requestIdCounter = 0;
let currentStreamingMessageDiv = null;

// Modo de operação
let operationMode = 'chat'; // 'chat' ou 'viewer'
let currentSessionData = null;

// =====================================================
// FUNÇÕES DO CHAT ORIGINAL
// =====================================================

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function log(message, type = 'info') {
    const debugPanel = document.getElementById('debug');
    const now = new Date().toLocaleTimeString();
    const entry = `[${now}] ${message}`;

    if (debugPanel) {
        debugPanel.textContent += '\n' + entry;
        debugPanel.scrollTop = debugPanel.scrollHeight;
    }
    console.log(entry);
}

function updateStatus(message, type = 'info') {
    const statusPanel = document.getElementById('status');
    if (statusPanel) {
        statusPanel.className = `debug-panel ${type}`;
        statusPanel.textContent = `[STATUS] ${message}`;
    }
}

function renderMarkdown(text) {
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

function addMessage(content, isUser = false, requestId = null) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'info' : 'success'}`;

    if (requestId) {
        messageDiv.setAttribute('data-request-id', requestId);
    }

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    if (isUser) {
        contentDiv.innerHTML = `<span style="color: #00ffff">👤 USER:</span><br>${escapeHtml(content)}`;
    } else {
        contentDiv.innerHTML = `<span style="color: #00ff00">🤖 CLAUDE:</span><br>${renderMarkdown(content)}`;
    }

    messageDiv.appendChild(contentDiv);
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    if (!isUser) {
        currentStreamingMessageDiv = messageDiv;
    }
}

function updateStreamingMessage(content) {
    if (!currentStreamingMessageDiv) {
        addMessage(content, false);
        return;
    }

    const contentDiv = currentStreamingMessageDiv.querySelector('.message-content');
    if (contentDiv) {
        contentDiv.innerHTML = `<span style="color: #00ff00">🤖 CLAUDE:</span><br>${renderMarkdown(content)}`;
    }
}

function updateActiveRequestsIndicator() {
    const count = activeRequests.size;
    const button = document.querySelector('button[onclick="cancelAllRequests()"]');
    if (button) {
        if (count > 0) {
            button.textContent = `⛔ Cancelar (${count})`;
            button.style.display = 'inline-block';
        } else {
            button.textContent = '⛔ Cancelar';
            button.style.display = 'none';
        }
    }
}

function cancelAllRequests() {
    if (activeRequests.size === 0) {
        log('ℹ️ Nenhuma requisição ativa para cancelar');
        updateStatus('Nenhuma requisição ativa', 'info');
        return;
    }

    const count = activeRequests.size;
    log(`🛑 Cancelando ${count} requisição(ões)...`);

    activeRequests.forEach((request, id) => {
        if (request.abortController) {
            request.abortController.abort();
        }
        if (request.timeout) {
            clearTimeout(request.timeout);
        }
    });

    activeRequests.clear();
    updateStatus(`${count} requisição(ões) cancelada(s)`, 'warn');
    updateActiveRequestsIndicator();
}

async function sendMessage() {
    if (operationMode !== 'chat') {
        log('⚠️ Chat desabilitado no modo visualização');
        return;
    }

    const input = document.getElementById('messageInput');
    const message = input.value.trim();

    if (!message) {
        log('⚠️ Mensagem vazia', 'error');
        return;
    }

    const requestId = ++requestIdCounter;
    const localAbortController = new AbortController();

    activeRequests.set(requestId, {
        abortController: localAbortController,
        timeout: null
    });

    log(`📤 #${requestId}: Enviando "${message}"`);
    addMessage(message, true, requestId);
    input.value = '';

    updateStatus(`Enviando mensagem #${requestId}...`, 'info');
    updateActiveRequestsIndicator();

    currentStreamingMessageDiv = null;

    try {
        const timeoutId = setTimeout(() => {
            const request = activeRequests.get(requestId);
            if (request) {
                log(`⚠️ Timeout da mensagem #${requestId}`);
                request.abortController.abort();
                activeRequests.delete(requestId);
                updateActiveRequestsIndicator();
            }
        }, CONFIG.CONNECTION_TIMEOUT);

        activeRequests.get(requestId).timeout = timeoutId;

        const response = await fetch(`${CONFIG.API_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message }),
            signal: localAbortController.signal
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        updateStatus(`Recebendo resposta #${requestId}...`, 'info');

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let fullResponse = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));

                        log(`🔍 Evento: ${data.type} - ${JSON.stringify(data).substring(0, 100)}`);

                        if (data.type === 'session_created') {
                            log(`📌 Sessão criada: ${data.session_id}`);
                        }
                        else if (data.type === 'processing') {
                            log('⏳ Processando...');
                            updateStatus('Claude está processando...', 'info');
                        }
                        else if (data.type === 'content') {
                            const content = data.content || '';
                            fullResponse += content;
                            updateStreamingMessage(fullResponse);

                            if (content.length > 0) {
                                const preview = content.substring(0, 50).replace(/\n/g, ' ');
                                log(`📝 Chunk recebido: "${preview}${content.length > 50 ? '...' : ''}"`);
                            }
                        } else if (data.type === 'done') {
                            log(`✅ Resposta #${requestId} completa`);
                            updateStatus('Resposta recebida', 'success');
                            currentStreamingMessageDiv = null;

                            const req = activeRequests.get(requestId);
                            if (req && req.timeout) {
                                clearTimeout(req.timeout);
                            }
                            activeRequests.delete(requestId);
                            updateActiveRequestsIndicator();
                            break;
                        }
                    } catch (err) {
                        console.error('Parse error:', err);
                    }
                }
            }
        }

    } catch (error) {
        if (error.name === 'AbortError') {
            log(`⚠️ Requisição #${requestId} cancelada`);
            updateStatus('Requisição cancelada', 'warn');
        } else {
            log(`❌ Erro #${requestId}: ${error.message}`);
            updateStatus(`Erro: ${error.message}`, 'error');
            addMessage(`Erro: ${error.message}`, false);
        }
    } finally {
        const req = activeRequests.get(requestId);
        if (req) {
            if (req.timeout) {
                clearTimeout(req.timeout);
            }
            activeRequests.delete(requestId);
            updateActiveRequestsIndicator();
        }
    }
}

async function testConnection() {
    log('🔍 Testando conexão com a API...');
    updateStatus('Testando conexão...', 'info');

    try {
        const response = await fetch(`${CONFIG.API_URL}/api/health`);
        const data = await response.json();

        if (data.status === 'healthy') {
            log('✅ API conectada e funcionando!');
            updateStatus('API conectada', 'success');
        } else {
            throw new Error('API não está saudável');
        }
    } catch (error) {
        log(`❌ Erro de conexão: ${error.message}`, 'error');
        updateStatus('Erro de conexão', 'error');
    }
}

// =====================================================
// FUNÇÕES DO VISUALIZADOR DE SESSÕES
// =====================================================

async function loadSessionsList() {
    updateStatus('Carregando sessões do Claude SDK...', 'info');

    try {
        // Detecta qual projeto carregar baseado na URL
        const path = window.location.pathname;
        let apiUrl = '/api/sessions'; // default

        if (path.includes('-Users-2a-Desktop-neo4j-agent-claude-code-sdk')) {
            apiUrl = '/api/projects/-Users-2a-Desktop-neo4j-agent-claude-code-sdk/sessions';
        }

        // Usa a nova API do servidor SPA
        const response = await fetch(apiUrl).catch(() => null);

        if (response && response.ok) {
            const sessions = await response.json();
            displaySessionsList(sessions);
        } else {
            // Fallback: mostra mensagem informativa
            displayOfflineSessionsList();
        }
    } catch (error) {
        log(`❌ Erro ao carregar sessões: ${error.message}`);
        displayOfflineSessionsList();
    }
}

function displaySessionsList(sessions) {
    const messagesDiv = document.getElementById('messages');
    const currentPath = window.location.pathname;

    // Atualiza URL se não estiver correta
    if (currentPath !== '/-Users-2a-Desktop-neo4j-agent-claude-code-sdk') {
        window.history.pushState(null, '', '/-Users-2a-Desktop-neo4j-agent-claude-code-sdk');
    }

    messagesDiv.innerHTML = `
        <div style="padding: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2 style="color: #00ff00; margin: 0;">📁 Sessões do Claude Code SDK</h2>
                <button onclick="backToChat()" style="
                    background: #00ff00;
                    color: #000;
                    padding: 8px 15px;
                    border: none;
                    cursor: pointer;
                    font-weight: bold;
                ">← Voltar ao Chat</button>
            </div>

            <p style="color: #00ffff; margin-bottom: 20px;">
                Projeto: ${CONFIG.CLAUDE_PROJECTS_PATH.split('/').pop()}
                <br>
                <span style="font-size: 12px; color: #666;">URL: ${window.location.href}</span>
            </p>

            ${sessions.length === 0 ? `
                <div style="color: #999; text-align: center; padding: 40px;">
                    <p>Nenhuma sessão encontrada</p>
                    <p style="font-size: 12px;">As sessões aparecem quando você conversa através do Claude Code SDK</p>
                </div>
            ` : `
                <div style="display: grid; gap: 10px;">
                    ${sessions.map(session => `
                        <div style="
                            border: 1px solid #00ff00;
                            padding: 15px;
                            background: rgba(0, 255, 0, 0.05);
                            cursor: pointer;
                            transition: all 0.2s;
                        "
                        onmouseover="this.style.background='rgba(0,255,0,0.1)'"
                        onmouseout="this.style.background='rgba(0,255,0,0.05)'"
                        onclick="viewSessionWithURL('${session.id}')">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span style="color: #00ff00; font-weight: bold;">
                                    💬 ${session.id.substring(0, 8)}...
                                </span>
                                <span style="color: #666; font-size: 12px;">
                                    ${new Date(session.modified).toLocaleString('pt-BR')}
                                </span>
                            </div>
                            ${session.preview ? `
                                <div style="
                                    color: #ccc;
                                    font-size: 13px;
                                    padding: 8px;
                                    background: rgba(0,0,0,0.3);
                                    border-left: 2px solid #00ff00;
                                    margin-top: 5px;
                                ">
                                    "${session.preview}"${session.preview.length >= 100 ? '...' : ''}
                                </div>
                            ` : ''}
                            <div style="color: #666; font-size: 11px; margin-top: 8px;">
                                📦 ${(session.size / 1024).toFixed(1)} KB
                            </div>
                        </div>
                    `).join('')}
                </div>
            `}
        </div>
    `;

    messagesDiv.scrollTop = 0;
    updateStatus('Sessões carregadas', 'success');
}

function displayOfflineSessionsList() {
    const messagesDiv = document.getElementById('messages');

    messagesDiv.innerHTML = `
        <div style="padding: 20px; text-align: center;">
            <h2 style="color: #00ff00;">📁 Visualizador de Sessões Claude SDK</h2>

            <div style="
                margin: 30px auto;
                padding: 20px;
                border: 1px solid #ffff00;
                background: rgba(255, 255, 0, 0.1);
                max-width: 600px;
            ">
                <h3 style="color: #ffff00;">ℹ️ Como Visualizar Sessões</h3>

                <p style="color: #ccc; text-align: left;">
                    As sessões do Claude Code SDK são salvas em:
                </p>

                <pre style="
                    background: #000;
                    padding: 10px;
                    color: #00ff00;
                    font-size: 11px;
                    overflow-x: auto;
                ">${CONFIG.CLAUDE_PROJECTS_PATH}</pre>

                <p style="color: #ccc; text-align: left; margin-top: 20px;">
                    Cada arquivo <code>.jsonl</code> representa uma sessão de conversa.
                    Para visualizá-las aqui:
                </p>

                <ol style="color: #ccc; text-align: left;">
                    <li>Inicie o servidor de sessões: <code>node simple-session-api.mjs</code></li>
                    <li>Ou acesse os arquivos diretamente no diretório</li>
                    <li>Ou continue conversando normalmente no chat abaixo</li>
                </ol>
            </div>

            <button onclick="backToChat()" style="
                background: #00ff00;
                color: #000;
                padding: 10px 30px;
                border: none;
                cursor: pointer;
                font-weight: bold;
                font-size: 16px;
                margin-top: 20px;
            ">← Voltar ao Chat</button>
        </div>
    `;

    updateStatus('Modo offline - servidor de sessões não disponível', 'warn');
}

function viewSessionWithURL(sessionId) {
    // Atualiza URL para o formato completo
    window.history.pushState(null, '', `/-Users-2a-Desktop-neo4j-agent-claude-code-sdk/${sessionId}`);
    viewSession(sessionId);
}

async function viewSession(sessionId) {
    updateStatus(`Carregando sessão ${sessionId}...`, 'info');

    try {
        // Detecta projeto da URL
        const path = window.location.pathname;
        let apiUrl = `/api/sessions/${sessionId}`;

        if (path.includes('-Users-2a-Desktop-neo4j-agent-claude-code-sdk')) {
            apiUrl = `/api/projects/-Users-2a-Desktop-neo4j-agent-claude-code-sdk/sessions/${sessionId}`;
        }

        const response = await fetch(apiUrl);

        if (!response.ok) {
            throw new Error('Sessão não encontrada');
        }

        const jsonlData = await response.text();
        displaySession(sessionId, jsonlData);
    } catch (error) {
        log(`❌ Erro ao carregar sessão: ${error.message}`);
        updateStatus('Erro ao carregar sessão', 'error');
    }
}

function displaySession(sessionId, jsonlData) {
    const messages = parseJSONL(jsonlData);
    const messagesDiv = document.getElementById('messages');

    messagesDiv.innerHTML = `
        <div style="
            padding: 10px;
            background: rgba(0, 255, 0, 0.1);
            border-bottom: 1px solid #00ff00;
            position: sticky;
            top: 0;
            z-index: 10;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <button onclick="loadSessionsList()" style="
                        background: transparent;
                        color: #00ff00;
                        border: 1px solid #00ff00;
                        padding: 5px 10px;
                        cursor: pointer;
                        margin-right: 10px;
                    ">← Lista de Sessões</button>
                    <span style="color: #00ffff;">
                        Sessão: ${sessionId.substring(0, 8)}...
                    </span>
                </div>
                <button onclick="backToChat()" style="
                    background: #00ff00;
                    color: #000;
                    padding: 5px 15px;
                    border: none;
                    cursor: pointer;
                    font-weight: bold;
                ">Chat</button>
            </div>
        </div>
    `;

    // Renderiza mensagens
    messages.forEach(msg => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${msg.role === 'user' ? 'info' : 'success'}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const timestamp = msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString('pt-BR') : '';

        if (msg.role === 'user') {
            contentDiv.innerHTML = `
                <span style="color: #00ffff">👤 USER ${timestamp ? `[${timestamp}]` : ''}:</span><br>
                ${escapeHtml(msg.content)}
            `;
        } else {
            contentDiv.innerHTML = `
                <span style="color: #00ff00">🤖 CLAUDE ${timestamp ? `[${timestamp}]` : ''}:</span>
                ${msg.tokens ? `
                    <span style="font-size: 10px; color: #666;">
                        (${msg.tokens.input}→${msg.tokens.output} tokens)
                    </span>
                ` : ''}
                <br>
                ${renderMarkdown(msg.content)}
            `;
        }

        messageDiv.appendChild(contentDiv);
        messagesDiv.appendChild(messageDiv);
    });

    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    updateStatus(`Sessão carregada: ${messages.length} mensagens`, 'success');
}

function parseJSONL(jsonlData) {
    const messages = [];
    const lines = jsonlData.split('\n').filter(l => l.trim());

    lines.forEach(line => {
        try {
            const entry = JSON.parse(line);

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
                let content = '';
                let tokens = null;

                if (entry.message.content) {
                    entry.message.content.forEach(block => {
                        if (block.type === 'text') {
                            content += block.text;
                        } else if (block.type === 'tool_use') {
                            content += `\n[🔧 ${block.name}]\n`;
                        }
                    });
                }

                if (entry.message.usage) {
                    tokens = {
                        input: entry.message.usage.input_tokens,
                        output: entry.message.usage.output_tokens
                    };
                }

                if (content) {
                    messages.push({
                        id: entry.uuid,
                        role: 'assistant',
                        content: content,
                        timestamp: entry.timestamp,
                        tokens: tokens
                    });
                }
            }
        } catch (e) {
            // Ignora linhas inválidas
        }
    });

    return messages;
}

function backToChat() {
    operationMode = 'chat';
    const messagesDiv = document.getElementById('messages');
    messagesDiv.innerHTML = '';

    // Volta URL para raiz
    window.history.pushState(null, '', '/');

    const input = document.getElementById('messageInput');
    if (input) {
        input.disabled = false;
        input.placeholder = 'Digite sua mensagem...';
    }

    updateStatus('Chat ativado - envie mensagens livremente!', 'success');
    log('✅ Voltou ao modo chat');
}

function showSessions() {
    operationMode = 'viewer';

    const input = document.getElementById('messageInput');
    if (input) {
        input.disabled = true;
        input.placeholder = '🔒 Modo visualização de sessões';
    }

    loadSessionsList();
    log('📁 Entrando no modo visualização de sessões');
}

// =====================================================
// INICIALIZAÇÃO
// =====================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Chat Unificado iniciado!');

    // Adiciona controles de navegação
    const container = document.querySelector('.container');
    if (container && !document.getElementById('navigation-bar')) {
        const navBar = document.createElement('div');
        navBar.id = 'navigation-bar';
        navBar.style.cssText = `
            padding: 10px;
            background: rgba(0, 255, 0, 0.1);
            border-bottom: 1px solid #00ff00;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        `;
        navBar.innerHTML = `
            <div>
                <span style="color: #00ff00; font-weight: bold;">
                    🔧 Neo4j Agent Chat + Claude SDK Viewer
                </span>
            </div>
            <div>
                <button onclick="showSessions()" style="
                    background: transparent;
                    color: #00ff00;
                    border: 1px solid #00ff00;
                    padding: 5px 15px;
                    cursor: pointer;
                    margin-right: 10px;
                ">📁 Ver Sessões</button>
                <button onclick="backToChat()" style="
                    background: #00ff00;
                    color: #000;
                    padding: 5px 15px;
                    border: none;
                    cursor: pointer;
                    font-weight: bold;
                ">💬 Chat</button>
            </div>
        `;
        container.insertBefore(navBar, container.firstChild);
    }

    // Detecta modo baseado na URL
    const path = window.location.pathname;

    // Roteamento melhorado
    // /Users-2a-Desktop-neo4j-agent-claude-code-sdk -> lista de sessões
    // /Users-2a-Desktop-neo4j-agent-claude-code-sdk/[uuid] -> sessão específica
    // /[uuid] -> sessão específica (compatibilidade)

    if (path === '/-Users-2a-Desktop-neo4j-agent-claude-code-sdk' ||
        path === '/-Users-2a-Desktop-neo4j-agent-claude-code-sdk/') {
        // Mostra lista de sessões do projeto
        operationMode = 'viewer';
        showSessions();
    } else if (path.startsWith('/-Users-2a-Desktop-neo4j-agent-claude-code-sdk/')) {
        // Extrai o UUID após o caminho do projeto
        const sessionMatch = path.match(/\/([a-f0-9-]{36})/);
        if (sessionMatch) {
            const sessionId = sessionMatch[1];
            operationMode = 'viewer';
            viewSession(sessionId);
        } else {
            // URL inválida, mostra lista
            operationMode = 'viewer';
            showSessions();
        }
    } else if (path.match(/^\/[a-f0-9-]{36}$/)) {
        // Compatibilidade: apenas UUID
        const sessionId = path.match(/([a-f0-9-]{36})/)[1];
        operationMode = 'viewer';
        viewSession(sessionId);
    } else {
        // Página inicial - modo chat
        operationMode = 'chat';
        updateActiveRequestsIndicator();
        testConnection();
    }

    // Enter para enviar
    const input = document.getElementById('messageInput');
    if (input) {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey && operationMode === 'chat') {
                e.preventDefault();
                sendMessage();
            }
        });

        if (operationMode === 'chat') {
            input.focus();
        }
    }

    updateStatus('Sistema pronto!', 'success');
    log('✅ Sistema iniciado com chat e visualizador de sessões!');
});

// Exportar funções globais
window.sendMessage = sendMessage;
window.testConnection = testConnection;
window.cancelAllRequests = cancelAllRequests;
window.showSessions = showSessions;
window.backToChat = backToChat;
window.viewSession = viewSession;
window.viewSessionWithURL = viewSessionWithURL;
window.loadSessionsList = loadSessionsList;