/**
 * Neo4j Agent Chat - JavaScript Application
 * Modularized with ES6+ features and performance optimizations
 */

// Configuration
const CONFIG = {
    API_URL: 'http://localhost:8080',
    RETRY_DELAYS: [1000, 2000, 4000, 8000],
    DEBOUNCE_DELAY: 300,
    MESSAGE_BATCH_SIZE: 10,
    CACHE_KEY: 'neo4j_chat_messages',
    SESSION_KEY: 'neo4j_chat_session',
    MAX_CACHE_SIZE: 100,
    CONNECTION_TIMEOUT: 10 * 60 * 1000,  // Aumentado de 5 para 10 minutos para suportar múltiplos subagentes
    LONG_OPERATION_THRESHOLD: 30000  // 30 segundos para considerar operação longa
};

// Utility functions
const Utils = {
    escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;")
            .replace(/\//g, "&#x2F;");
    },

    sanitizeText(text) {
        if (!text) return '';
        text = this.escapeHtml(text);
        text = text.replace(/<script[^>]*>.*?<\/script>/gi, '');
        text = text.replace(/on\w+\s*=\s*["'][^"']*["']/gi, '');
        text = text.replace(/javascript:/gi, '');
        text = text.replace(/data:/gi, '');
        return text;
    },

    decodeHtmlEntities(text) {
        const textArea = document.createElement('textarea');
        textArea.innerHTML = text;
        return textArea.value;
    },

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Global variables
let sessionId = null;
// Gerenciamento de múltiplas requisições simultâneas
const activeRequests = new Map(); // Armazena requisições ativas por ID
let requestIdCounter = 0; // Contador para IDs únicos
let currentStreamingMessageDiv = null;

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('Neo4j Agent Chat - Modern JS loaded');

    // Esconder botão cancelar inicialmente
    updateActiveRequestsIndicator();

    // Initialize connection test
    testConnectionSilent();

    // Focus input
    const input = document.getElementById('messageInput');
    if (input) {
        input.focus();

        // Enter to send
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    }
});

// Main functions (global for onclick handlers)
window.sendMessage = sendMessage;
window.testConnection = testConnection;

function log(message, type = 'info') {
    const debugPanel = document.getElementById('debug');
    const timestamp = new Date().toLocaleTimeString();
    debugPanel.innerHTML += `\n[${timestamp}] ${message}`;
    debugPanel.scrollTop = debugPanel.scrollHeight;
    console.log(`[DEBUG] ${message}`);
}

function updateStatus(message, type = 'info') {
    const statusPanel = document.getElementById('status');
    statusPanel.className = `debug-panel ${type}`;
    statusPanel.textContent = `[STATUS] ${message}`;
}

function renderMarkdown(text) {
    if (text.includes('&quot;') || text.includes('&lt;') || text.includes('&gt;') || text.includes('&amp;')) {
        text = Utils.decodeHtmlEntities(text);
    }

    return text
        .replace(/^### (.*?)$/gm, '<h3>$1</h3>')
        .replace(/^## (.*?)$/gm, '<h2>$1</h2>')
        .replace(/^# (.*?)$/gm, '<h1>$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/```([\s\S]*?)```/g, '<pre style="background:#0a0a0a;padding:10px;border:1px solid #00ff00;overflow-x:auto;">$1</pre>')
        .replace(/`([^`]+)`/g, '<code style="background:#0a0a0a;padding:2px 4px;border:1px solid #00ff00;">$1</code>')
        .replace(/^- (.*?)$/gm, '• $1')
        .replace(/\n/g, '<br>');
}

function addMessage(content, isUser = false, requestId = null) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'info' : 'success'}`;

    // Adicionar ID da requisição se fornecido
    if (requestId) {
        messageDiv.setAttribute('data-request-id', requestId);
    }

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    if (!isUser) {
        const renderedContent = renderMarkdown(content);
        contentDiv.innerHTML = `<span style="color: #00ff00">🤖 CLAUDE:</span><br>${renderedContent}`;

        // Para mensagens do Claude, configura como mensagem de streaming atual
        currentStreamingMessageDiv = messageDiv;
    } else {
        const safeContent = Utils.sanitizeText(content).replace(/\n/g, '<br>');
        contentDiv.innerHTML = `<span style="color: #00ffff">👤 USER:</span><br>${safeContent}`;
    }

    messageDiv.appendChild(contentDiv);

    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-btn';
    copyBtn.textContent = '📋';
    copyBtn.onclick = () => copyMessage(content, copyBtn);

    messageDiv.appendChild(copyBtn);
    messagesDiv.appendChild(messageDiv);

    // Scroll behavior:
    // For user messages, scroll to bottom to show the message
    // For Claude messages, scroll to show the beginning of Claude's response
    if (isUser) {
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    } else {
        // Scroll to show the Claude message header at the top of visible area
        // with a small offset to show previous context
        messageDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    return messageDiv;
}

function updateStreamingMessage(content, isUser = false) {
    if (!currentStreamingMessageDiv) {
        addMessage(content, isUser);
        return;
    }

    const contentDiv = currentStreamingMessageDiv.querySelector('.message-content');
    if (contentDiv) {
        const renderedContent = renderMarkdown(content);
        contentDiv.innerHTML = `<span style="color: #00ff00">🤖 CLAUDE:</span><br>${renderedContent}`;

        const copyBtn = currentStreamingMessageDiv.querySelector('.copy-btn');
        if (copyBtn) {
            copyBtn.onclick = () => copyMessage(content, copyBtn);
        }

        // Smart scroll behavior during streaming:
        // 1. Keep the beginning of Claude's message visible
        // 2. Show enough content to read comfortably (about 80% of viewport)
        // 3. Don't jump around - maintain stable reading position
        const messagesDiv = document.getElementById('messages');
        const messageRect = currentStreamingMessageDiv.getBoundingClientRect();
        const containerRect = messagesDiv.getBoundingClientRect();

        // Calculate if message is getting too long for viewport
        const messageHeight = currentStreamingMessageDiv.offsetHeight;
        const viewportHeight = messagesDiv.clientHeight;
        const idealReadingHeight = viewportHeight * 0.8; // 80% of viewport for comfortable reading

        // If message is still small, let it grow naturally
        if (messageHeight <= idealReadingHeight) {
            // Keep the message start visible with some context
            if (messageRect.top < containerRect.top) {
                currentStreamingMessageDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        } else {
            // Message is long - maintain reading position
            // Only auto-scroll if user manually scrolled to follow the stream
            const isFollowing = messagesDiv.scrollHeight - messagesDiv.scrollTop <= messagesDiv.clientHeight + 100;

            if (isFollowing) {
                // User wants to follow - scroll to show last 80% of viewport
                const targetScroll = messagesDiv.scrollHeight - viewportHeight + (viewportHeight * 0.2);
                messagesDiv.scrollTop = targetScroll;
            }
            // Otherwise maintain current position for stable reading
        }
    }
}

async function copyMessage(text, button) {
    try {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = renderMarkdown(text);
        const plainText = tempDiv.textContent || tempDiv.innerText || text;

        await navigator.clipboard.writeText(plainText);

        const originalText = button.textContent;
        button.textContent = '✅ Copiado!';
        button.classList.add('copied');

        setTimeout(() => {
            button.textContent = originalText;
            button.classList.remove('copied');
        }, 2000);

        log('Mensagem copiada para clipboard');
    } catch (err) {
        log('Erro ao copiar: ' + err.message, 'error');
    }
}

// Função para atualizar indicador de requisições ativas
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

// Função para cancelar todas as requisições ativas
function cancelAllRequests() {
    if (activeRequests.size === 0) {
        log('ℹ️ Nenhuma requisição ativa para cancelar');
        updateStatus('Nenhuma requisição ativa', 'info');
        return;
    }

    const count = activeRequests.size;
    log(`🛑 Cancelando ${count} requisição(ões) ativa(s)...`);

    // Cancelar cada requisição
    activeRequests.forEach((request, id) => {
        if (request.abortController) {
            request.abortController.abort();
        }
        if (request.timeout) {
            clearTimeout(request.timeout);
        }
    });

    // Limpar o Map
    activeRequests.clear();

    updateStatus(`${count} requisição(ões) cancelada(s)`, 'warn');
    log(`✅ ${count} requisição(ões) cancelada(s) com sucesso`);
    updateActiveRequestsIndicator();
}

async function sendMessage() {
    // Permitir múltiplas mensagens simultâneas
    const requestId = ++requestIdCounter;
    const localAbortController = new AbortController();
    let localResponseTimeout = null;

    // Armazenar a requisição ativa
    activeRequests.set(requestId, {
        abortController: localAbortController,
        timeout: null
    });

    const input = document.getElementById('messageInput');
    let message = input.value.trim();

    if (!message) {
        log('⚠️ Mensagem vazia', 'error');
        return;
    }

    if (message.length > 50000) {
        log('⚠️ Mensagem muito longa (máximo 50.000 caracteres)', 'error');
        updateStatus('Mensagem muito longa', 'error');
        return;
    }

    log(`📤 Enviando: "${message}"`);
    addMessage(message, true, requestId);
    input.value = '';
    updateStatus(`Enviando mensagem #${requestId}...`, 'info');

    // Mostrar número de requisições ativas
    log(`📊 Requisições ativas: ${activeRequests.size}`);
    updateActiveRequestsIndicator();

    currentStreamingMessageDiv = null;

    const payload = {
        message: message,
        project_id: 'neo4j-agent'
    };

    if (sessionId) {
        payload.session_id = sessionId;
    }

    log(`Payload: ${JSON.stringify(payload)}`);

    try {
        // Cada requisição tem seu próprio AbortController

        localResponseTimeout = setTimeout(() => {
            const request = activeRequests.get(requestId);
            if (request && request.abortController) {
                const timeoutMinutes = CONFIG.CONNECTION_TIMEOUT / (60 * 1000);
                log(`⚠️ Timeout da resposta #${requestId} (${timeoutMinutes} min)`, 'warn');
                request.abortController.abort();
                activeRequests.delete(requestId);
            }
        }, CONFIG.CONNECTION_TIMEOUT);

        // Atualizar o timeout na requisição ativa
        const request = activeRequests.get(requestId);
        if (request) {
            request.timeout = localResponseTimeout;
        }

        const response = await fetch(`${CONFIG.API_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload),
            signal: localAbortController.signal
        });

        log(`Response status: ${response.status}`);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        updateStatus('Recebendo resposta...', 'info');

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

                        if (data.type === 'session_created' && data.session_id) {
                            sessionId = data.session_id;
                            log(`📌 Sessão criada: ${data.session_id}`);
                        }
                        else if (data.type === 'processing') {
                            log('⏳ Processando...');
                            updateStatus('Claude está processando...', 'info');
                        }
                        else if (data.type === 'content' || data.type === 'text' || data.type === 'text_chunk') {
                            let content = data.content || data.text || '';

                            // Acumula o texto completo
                            fullResponse += content;

                            // Exibe incrementalmente - cada chunk adiciona ao que já existe
                            if (!currentStreamingMessageDiv) {
                                // Cria o div inicial se não existir
                                addMessage(content, false, requestId);
                            } else {
                                // Atualiza com o texto completo acumulado
                                updateStreamingMessage(fullResponse, false);
                            }

                            if (content.length > 15) {
                                const preview = content.substring(0, 30).replace(/\n/g, ' ');
                                log(`📝 Chunk: ${preview}${content.length > 30 ? '...' : ''}`);
                            }
                        }
                        else if (data.type === 'done') {
                            log('✅ Resposta completa');
                            updateStatus('Resposta recebida', 'success');
                            if (fullResponse) {
                                updateStreamingMessage(fullResponse, false);
                            }
                            currentStreamingMessageDiv = null;

                            // Limpar requisição específica
                            const req = activeRequests.get(requestId);
                            if (req && req.timeout) {
                                clearTimeout(req.timeout);
                            }
                            activeRequests.delete(requestId);
                            updateActiveRequestsIndicator();
                            break;
                        }
                        else if (data.type === 'tool_use') {
                            let toolName = data.name || 'ferramenta';
                            if (Array.isArray(toolName)) {
                                toolName = toolName[0] || 'ferramenta';
                            } else if (typeof toolName !== 'string') {
                                toolName = String(toolName);
                            }
                            log(`📡 tool_use: ${toolName}`);
                            updateStatus(`Usando ferramenta: ${toolName}...`, 'info');
                        }
                        else if (data.type === 'tool_result') {
                            log(`🔧 tool_result recebido`);
                        }
                        else if (data.type === 'error') {
                            log(`❌ Erro: ${data.error}`, 'error');
                            updateStatus('Erro na resposta', 'error');
                            break;
                        }
                    } catch (err) {
                        log(`⚠️ Erro ao parsear: ${err.message}`, 'error');
                    }
                }
            }
        }

        if (!fullResponse) {
            log('⚠️ Resposta vazia', 'error');
            updateStatus('Resposta vazia', 'error');
        }

    } catch (error) {
        if (error.name === 'AbortError') {
            log('⚠️ Requisição cancelada por timeout', 'warn');
            updateStatus('Timeout - tente novamente', 'warn');
        } else if (error.message === 'Failed to fetch') {
            log('❌ Conexão perdida com o servidor', 'error');
            updateStatus('Servidor desconectado - verifique o backend', 'error');
            setTimeout(() => {
                testConnectionSilent();
            }, 2000);
        } else {
            log(`❌ Erro: ${error.message}`, 'error');
            updateStatus(`Erro: ${error.message}`, 'error');
            addMessage(`Erro: ${error.message}`, false);
        }
    } finally {
        // Limpar requisição específica
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
    log('Testando conexão com API...');

    try {
        const healthResponse = await fetch(`${CONFIG.API_URL}/api/health`);
        if (healthResponse.ok) {
            const health = await healthResponse.json();
            log(`✅ Health OK: ${JSON.stringify(health)}`, 'success');
            updateStatus('API Online', 'success');
        } else {
            log(`❌ Health falhou: ${healthResponse.status}`, 'error');
            updateStatus('API Offline', 'error');
        }

        const sdkResponse = await fetch(`${CONFIG.API_URL}/api/sdk-status`);
        if (sdkResponse.ok) {
            const sdk = await sdkResponse.json();
            log(`✅ SDK Status: ${JSON.stringify(sdk)}`, 'success');
        } else {
            log(`❌ SDK Status falhou: ${sdkResponse.status}`, 'error');
        }

    } catch (error) {
        log(`❌ Erro de conexão: ${error.message}`, 'error');
        updateStatus('Erro de Conexão', 'error');
    }
}

async function testConnectionSilent() {
    try {
        const response = await fetch(`${CONFIG.API_URL}/api/health`);
        if (response.ok) {
            updateStatus('✅ Conectado ao backend', 'success');
        } else {
            updateStatus('⚠️ Backend offline', 'error');
        }
    } catch (error) {
        updateStatus('❌ Erro de conexão', 'error');
    }
}