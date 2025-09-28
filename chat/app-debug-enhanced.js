/**
 * Neo4j Agent Chat - DEBUG ULTRA COMPLETO
 * Versão com debug máximo para desenvolvimento
 */

// Configuração
const CONFIG = {
    API_URL: 'http://localhost:8080',
    RETRY_DELAYS: [1000, 2000, 4000, 8000],
    CONNECTION_TIMEOUT: 10 * 60 * 1000,
    DEBUG_MODE: true // Ativar debug completo
};

// Gerenciamento de requisições múltiplas
const activeRequests = new Map();
let requestIdCounter = 0;
let currentStreamingMessageDiv = null;

// Estatísticas globais para debug
const stats = {
    totalSent: 0,
    totalReceived: 0,
    totalChunks: 0,
    totalBytes: 0,
    errors: 0,
    timeouts: 0,
    startTime: Date.now()
};

// Funções auxiliares
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// LOG APRIMORADO COM CORES E CATEGORIAS
function log(message, type = 'info', data = null) {
    const debugPanel = document.getElementById('debug');
    const now = new Date();
    const timestamp = now.toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        fractionalSecondDigits: 3
    });

    // Emojis por tipo
    const icons = {
        info: 'ℹ️',
        success: '✅',
        error: '❌',
        warning: '⚠️',
        network: '🌐',
        stream: '📡',
        chunk: '📝',
        session: '🔑',
        processing: '⏳',
        metrics: '📊',
        debug: '🔍'
    };

    const icon = icons[type] || '📌';
    let entry = `[${timestamp}] ${icon} ${message}`;

    // Adicionar dados extras se fornecidos
    if (data) {
        if (typeof data === 'object') {
            entry += ` | ${JSON.stringify(data, null, 2)}`;
        } else {
            entry += ` | ${data}`;
        }
    }

    if (debugPanel) {
        debugPanel.textContent += '\n' + entry;
        debugPanel.scrollTop = debugPanel.scrollHeight;
    }

    // Também logar no console para debug
    if (CONFIG.DEBUG_MODE) {
        console.log(`%c${entry}`, `color: ${getColorForType(type)}`);
    }
}

function getColorForType(type) {
    const colors = {
        info: '#00ffff',
        success: '#00ff00',
        error: '#ff0000',
        warning: '#ffff00',
        network: '#ff00ff',
        stream: '#00ff88',
        chunk: '#88ff00',
        session: '#ff8800',
        processing: '#8888ff',
        metrics: '#ff0088',
        debug: '#888888'
    };
    return colors[type] || '#ffffff';
}

function updateStatus(message, type = 'info') {
    const statusPanel = document.getElementById('status');
    if (statusPanel) {
        statusPanel.className = `debug-panel ${type}`;
        statusPanel.textContent = `[STATUS] ${message}`;
    }

    // Logar mudanças de status
    log(`Status: ${message}`, 'debug');
}

// Métricas em tempo real
function updateMetrics() {
    const runtime = Math.floor((Date.now() - stats.startTime) / 1000);
    const avgChunkSize = stats.totalChunks > 0 ? Math.floor(stats.totalBytes / stats.totalChunks) : 0;

    log(`Métricas: Runtime=${runtime}s | Enviadas=${stats.totalSent} | Recebidas=${stats.totalReceived} | Chunks=${stats.totalChunks} | Bytes=${stats.totalBytes} | Média/chunk=${avgChunkSize}B`, 'metrics');
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
        log(`Mensagem adicionada ao DOM: RequestID=${requestId}`, 'debug');
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

    // Log de requisições ativas
    if (count > 0) {
        const ids = Array.from(activeRequests.keys()).join(', ');
        log(`Requisições ativas: ${count} [IDs: ${ids}]`, 'debug');
    }
}

// Cancelar todas as requisições
function cancelAllRequests() {
    if (activeRequests.size === 0) {
        log('Nenhuma requisição ativa para cancelar', 'warning');
        updateStatus('Nenhuma requisição ativa', 'info');
        return;
    }

    const count = activeRequests.size;
    log(`Cancelando ${count} requisição(ões)...`, 'warning');

    activeRequests.forEach((request, id) => {
        log(`Cancelando requisição #${id}`, 'warning');
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

// FUNÇÃO PRINCIPAL COM DEBUG COMPLETO
async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();

    if (!message) {
        log('Mensagem vazia ignorada', 'warning');
        return;
    }

    // Criar nova requisição com ID único
    const requestId = ++requestIdCounter;
    const localAbortController = new AbortController();
    const requestStartTime = Date.now();

    // Armazenar requisição ativa
    activeRequests.set(requestId, {
        abortController: localAbortController,
        timeout: null,
        startTime: requestStartTime,
        message: message
    });

    stats.totalSent++;

    log(`═══════════════════════════════════════`, 'info');
    log(`NOVA REQUISIÇÃO #${requestId}`, 'network');
    log(`Mensagem: "${message}"`, 'info');
    log(`Tamanho: ${message.length} caracteres`, 'debug');
    log(`═══════════════════════════════════════`, 'info');

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
                const elapsed = Math.floor((Date.now() - requestStartTime) / 1000);
                log(`TIMEOUT: Requisição #${requestId} após ${elapsed}s`, 'error');
                stats.timeouts++;
                request.abortController.abort();
                activeRequests.delete(requestId);
                updateActiveRequestsIndicator();
            }
        }, CONFIG.CONNECTION_TIMEOUT);

        activeRequests.get(requestId).timeout = timeoutId;

        // LOG DO PAYLOAD
        const payload = { message };
        log(`Payload enviado:`, 'network', payload);

        const fetchStartTime = Date.now();

        log(`Iniciando fetch para ${CONFIG.API_URL}/api/chat`, 'network');

        const response = await fetch(`${CONFIG.API_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
            signal: localAbortController.signal
        });

        const fetchTime = Date.now() - fetchStartTime;
        log(`Resposta recebida em ${fetchTime}ms - Status: ${response.status}`, 'network');

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        // Headers da resposta
        log(`Content-Type: ${response.headers.get('content-type')}`, 'debug');
        log(`Headers:`, 'debug', Object.fromEntries(response.headers.entries()));

        updateStatus(`Recebendo resposta #${requestId}...`, 'info');

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let fullResponse = '';
        let chunkCount = 0;
        let totalBytesReceived = 0;

        log(`Stream iniciado para requisição #${requestId}`, 'stream');

        while (true) {
            const { done, value } = await reader.read();
            if (done) {
                log(`Stream finalizado - Total de chunks: ${chunkCount}`, 'stream');
                break;
            }

            const chunkSize = value.length;
            totalBytesReceived += chunkSize;
            chunkCount++;
            stats.totalChunks++;
            stats.totalBytes += chunkSize;

            log(`Chunk #${chunkCount} recebido: ${chunkSize} bytes | Total: ${totalBytesReceived} bytes`, 'stream');

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.trim() === '') continue;

                log(`Linha raw: "${line.substring(0, 100)}${line.length > 100 ? '...' : ''}"`, 'debug');

                if (line.startsWith('data: ')) {
                    try {
                        const jsonStr = line.slice(6);
                        const data = JSON.parse(jsonStr);

                        // LOG COMPLETO DO EVENTO
                        log(`EVENTO [${data.type}]`, 'stream', {
                            type: data.type,
                            session_id: data.session_id,
                            content_length: data.content?.length,
                            raw: jsonStr.substring(0, 200)
                        });

                        // Processar por tipo
                        if (data.type === 'session_created') {
                            log(`SESSÃO CRIADA: ${data.session_id}`, 'session');
                        }
                        else if (data.type === 'processing') {
                            log('PROCESSAMENTO INICIADO', 'processing');
                            updateStatus('Claude está processando...', 'info');
                        }
                        else if (data.type === 'content') {
                            const content = data.content || '';
                            fullResponse += content;
                            updateStreamingMessage(fullResponse);

                            // Log detalhado do chunk
                            if (content.length > 0) {
                                log(`CHUNK DE TEXTO [${content.length} chars]: "${content.substring(0, 50)}${content.length > 50 ? '...' : ''}"`, 'chunk');
                            }
                        }
                        else if (data.type === 'result') {
                            log(`RESULTADO: Tokens entrada=${data.input_tokens} | saída=${data.output_tokens} | custo=$${data.cost_usd}`, 'metrics');
                        }
                        else if (data.type === 'done') {
                            const elapsed = Math.floor((Date.now() - requestStartTime) / 1000);
                            log(`RESPOSTA COMPLETA #${requestId} em ${elapsed}s`, 'success');
                            stats.totalReceived++;

                            updateStatus('Resposta recebida', 'success');
                            currentStreamingMessageDiv = null;

                            // Limpar requisição
                            const req = activeRequests.get(requestId);
                            if (req && req.timeout) {
                                clearTimeout(req.timeout);
                            }
                            activeRequests.delete(requestId);
                            updateActiveRequestsIndicator();

                            // Métricas finais
                            updateMetrics();
                            break;
                        }
                        else {
                            log(`EVENTO DESCONHECIDO: ${data.type}`, 'warning', data);
                        }
                    } catch (err) {
                        log(`ERRO ao parsear JSON: ${err.message}`, 'error', {
                            linha: line,
                            erro: err.message
                        });
                    }
                } else {
                    log(`Linha não SSE ignorada: "${line}"`, 'debug');
                }
            }
        }

        if (!fullResponse) {
            log('Resposta vazia recebida', 'warning');
            updateStatus('Resposta vazia', 'error');
        }

    } catch (error) {
        stats.errors++;
        const elapsed = Math.floor((Date.now() - requestStartTime) / 1000);

        if (error.name === 'AbortError') {
            log(`Requisição #${requestId} cancelada após ${elapsed}s`, 'warning');
            updateStatus('Requisição cancelada', 'warn');
        } else {
            log(`ERRO #${requestId} após ${elapsed}s: ${error.message}`, 'error', {
                name: error.name,
                message: error.message,
                stack: error.stack
            });
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

        log(`Requisição #${requestId} finalizada`, 'debug');
        log(`═══════════════════════════════════════`, 'info');
    }
}

// Teste de conexão com debug
async function testConnection() {
    log('═══════════════════════════════════════', 'info');
    log('TESTE DE CONEXÃO INICIADO', 'network');
    updateStatus('Testando conexão...', 'info');

    const startTime = Date.now();

    try {
        log(`Testando: ${CONFIG.API_URL}/api/health`, 'network');

        const response = await fetch(`${CONFIG.API_URL}/api/health`);
        const elapsed = Date.now() - startTime;

        log(`Resposta em ${elapsed}ms - Status: ${response.status}`, 'network');

        const data = await response.json();

        log('Resposta do health check:', 'success', data);

        if (data.status === 'healthy') {
            log('API CONECTADA E FUNCIONANDO!', 'success');
            updateStatus('API conectada', 'success');
        } else {
            throw new Error('API não está saudável');
        }
    } catch (error) {
        log(`ERRO DE CONEXÃO: ${error.message}`, 'error', {
            name: error.name,
            message: error.message,
            stack: error.stack
        });
        updateStatus('Erro de conexão', 'error');
    }

    log('═══════════════════════════════════════', 'info');
}

// Inicialização com debug completo
document.addEventListener('DOMContentLoaded', () => {
    console.log('%c🚀 CHAT INICIADO - DEBUG ULTRA COMPLETO 🚀', 'color: #00ff00; font-size: 20px; font-weight: bold');

    log('═══════════════════════════════════════', 'info');
    log('🚀 SISTEMA INICIADO - DEBUG COMPLETO 🚀', 'success');
    log(`Configuração:`, 'debug', CONFIG);
    log(`User Agent: ${navigator.userAgent}`, 'debug');
    log(`Plataforma: ${navigator.platform}`, 'debug');
    log(`Idioma: ${navigator.language}`, 'debug');
    log('═══════════════════════════════════════', 'info');

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
        log('Input configurado - Enter para enviar', 'debug');
    }

    updateStatus('Sistema pronto - Debug completo ativo', 'success');
    log('Sistema pronto para uso com debug completo!', 'success');
    log('Você pode enviar múltiplas mensagens simultaneamente', 'info');

    // Atualizar métricas a cada 10 segundos
    setInterval(updateMetrics, 10000);
});

// Exportar funções globais
window.sendMessage = sendMessage;
window.testConnection = testConnection;
window.cancelAllRequests = cancelAllRequests;
window.debugStats = () => {
    log('═══════════════════════════════════════', 'info');
    log('ESTATÍSTICAS COMPLETAS', 'metrics');
    log(`Runtime: ${Math.floor((Date.now() - stats.startTime) / 1000)}s`, 'metrics');
    log(`Mensagens enviadas: ${stats.totalSent}`, 'metrics');
    log(`Respostas recebidas: ${stats.totalReceived}`, 'metrics');
    log(`Total de chunks: ${stats.totalChunks}`, 'metrics');
    log(`Total de bytes: ${stats.totalBytes}`, 'metrics');
    log(`Erros: ${stats.errors}`, 'metrics');
    log(`Timeouts: ${stats.timeouts}`, 'metrics');
    log(`Requisições ativas: ${activeRequests.size}`, 'metrics');
    log('═══════════════════════════════════════', 'info');
    return stats;
};