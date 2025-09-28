/**
 * Neo4j Agent Chat - SEM LIMITAÇÕES
 * Versão atualizada que permite múltiplas mensagens simultâneas
 */

// Configuração
const CONFIG = {
    API_URL: 'http://localhost:8080',
    RETRY_DELAYS: [1000, 2000, 4000, 8000],
    CONNECTION_TIMEOUT: 10 * 60 * 1000
};

// Gerenciamento de requisições múltiplas
const activeRequests = new Map();
let requestIdCounter = 0;
let currentStreamingMessageDiv = null;

// Funções auxiliares
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

// Atualizar indicador de requisições ativas
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

// Cancelar todas as requisições
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

// FUNÇÃO PRINCIPAL - SEM LIMITAÇÕES!
async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();

    if (!message) {
        log('⚠️ Mensagem vazia', 'error');
        return;
    }

    // Criar nova requisição com ID único
    const requestId = ++requestIdCounter;
    const localAbortController = new AbortController();

    // Armazenar requisição ativa
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
        // Timeout para requisições longas
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

                        if (data.type === 'content') {
                            fullResponse += data.content || '';
                            updateStreamingMessage(fullResponse);
                        } else if (data.type === 'done') {
                            log(`✅ Resposta #${requestId} completa`);
                            updateStatus('Resposta recebida', 'success');
                            currentStreamingMessageDiv = null;

                            // Limpar requisição
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
        // Limpar requisição
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

// Teste de conexão
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

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Chat SEM LIMITAÇÕES iniciado!');

    // Esconder botão cancelar inicialmente
    updateActiveRequestsIndicator();

    // Testar conexão
    testConnection();

    // Enter para enviar
    const input = document.getElementById('messageInput');
    if (input) {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        input.focus();
    }

    updateStatus('Pronto - Envie múltiplas mensagens!', 'success');
    log('✅ Sistema iniciado SEM LIMITAÇÕES!');
    log('🚀 Você pode enviar quantas mensagens quiser simultaneamente!');
});

// Exportar funções globais
window.sendMessage = sendMessage;
window.testConnection = testConnection;
window.cancelAllRequests = cancelAllRequests;