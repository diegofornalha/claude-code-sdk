#!/usr/bin/env node
/**
 * 📜 Servidor para visualizar conversas do Claude
 * Permite acessar conversas salvas em ~/.claude/projects/
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');

const PORT = 3001;
const CLAUDE_DIR = path.join(os.homedir(), '.claude', 'projects');

const server = http.createServer((req, res) => {
    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');

    const url = new URL(req.url, `http://localhost:${PORT}`);

    // Route para listar todos os projetos
    if (url.pathname === '/api/projects') {
        fs.readdir(CLAUDE_DIR, (err, files) => {
            if (err) {
                res.writeHead(404);
                res.end(JSON.stringify({ error: 'Claude directory not found' }));
                return;
            }

            const projects = files.filter(f => f.startsWith('-'));
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(projects));
        });
        return;
    }

    // Route para listar conversas de um projeto
    if (url.pathname.startsWith('/api/conversations/')) {
        const projectPath = decodeURIComponent(url.pathname.replace('/api/conversations/', ''));
        const projectDir = path.join(CLAUDE_DIR, projectPath);

        fs.readdir(projectDir, (err, files) => {
            if (err) {
                res.writeHead(404);
                res.end(JSON.stringify({ error: 'Project not found' }));
                return;
            }

            const conversations = files
                .filter(f => f.endsWith('.jsonl'))
                .map(f => {
                    const stats = fs.statSync(path.join(projectDir, f));
                    return {
                        id: f.replace('.jsonl', ''),
                        file: f,
                        size: stats.size,
                        modified: stats.mtime
                    };
                })
                .sort((a, b) => new Date(b.modified) - new Date(a.modified));

            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(conversations));
        });
        return;
    }

    // Route para ler uma conversa específica
    if (url.pathname.startsWith('/api/conversation/')) {
        const parts = url.pathname.replace('/api/conversation/', '').split('/');
        const conversationId = parts.pop();
        const projectPath = parts.join('/');
        const filePath = path.join(CLAUDE_DIR, projectPath, conversationId + '.jsonl');

        fs.readFile(filePath, 'utf8', (err, data) => {
            if (err) {
                res.writeHead(404);
                res.end(JSON.stringify({ error: 'Conversation not found' }));
                return;
            }

            const messages = data.trim().split('\n').map(line => {
                try {
                    return JSON.parse(line);
                } catch (e) {
                    return null;
                }
            }).filter(Boolean);

            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(messages));
        });
        return;
    }

    // Página principal ou visualizador de conversa
    const html = `<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Conversations Viewer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            color: #fff;
            min-height: 100vh;
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }

        h1 {
            margin-bottom: 30px;
            color: #00ff88;
            display: flex;
            align-items: center;
            gap: 15px;
            font-size: 2em;
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
        }

        .projects-list, .conversations-list {
            display: grid;
            gap: 15px;
            margin-bottom: 30px;
        }

        .project-item, .conversation-item {
            background: rgba(26, 26, 26, 0.8);
            padding: 15px 20px;
            border-radius: 10px;
            border: 1px solid rgba(0, 255, 136, 0.2);
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .project-item:hover, .conversation-item:hover {
            background: rgba(0, 255, 136, 0.1);
            border-color: #00ff88;
            transform: translateX(5px);
        }

        .conversation-item .info {
            display: flex;
            gap: 20px;
            align-items: center;
            color: #888;
            font-size: 0.9em;
        }

        .message {
            margin: 20px 0;
            padding: 20px;
            border-radius: 10px;
            background: rgba(26, 26, 26, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.1);
            animation: fadeIn 0.3s;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.user {
            background: linear-gradient(135deg, rgba(0, 51, 34, 0.9), rgba(0, 102, 68, 0.9));
            border-color: rgba(0, 255, 136, 0.3);
        }

        .message.assistant {
            background: linear-gradient(135deg, rgba(0, 17, 51, 0.9), rgba(0, 34, 102, 0.9));
            border-color: rgba(100, 149, 237, 0.3);
        }

        .role {
            font-weight: bold;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.1em;
        }

        .message.user .role { color: #00ff88; }
        .message.assistant .role { color: #6495ed; }

        .content {
            white-space: pre-wrap;
            line-height: 1.8;
            font-size: 0.95em;
            color: rgba(255, 255, 255, 0.9);
        }

        .content code {
            background: rgba(0, 0, 0, 0.5);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Fira Code', monospace;
        }

        .content pre {
            background: rgba(0, 0, 0, 0.5);
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 10px 0;
        }

        .loading {
            text-align: center;
            padding: 60px;
            color: #666;
            font-size: 1.2em;
        }

        .error {
            color: #ff4444;
            padding: 30px;
            text-align: center;
            background: rgba(255, 68, 68, 0.1);
            border-radius: 10px;
            border: 1px solid rgba(255, 68, 68, 0.3);
        }

        .back-button {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid #00ff88;
            color: #00ff88;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            margin-bottom: 20px;
            transition: all 0.3s;
        }

        .back-button:hover {
            background: rgba(0, 255, 136, 0.2);
            transform: translateX(-5px);
        }

        .timestamp {
            color: #666;
            font-size: 0.85em;
            margin-top: 10px;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }

        .stat-card {
            background: rgba(0, 255, 136, 0.1);
            padding: 15px;
            border-radius: 8px;
            border: 1px solid rgba(0, 255, 136, 0.3);
            text-align: center;
        }

        .stat-value {
            font-size: 2em;
            color: #00ff88;
            font-weight: bold;
        }

        .stat-label {
            color: #888;
            font-size: 0.9em;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📜 Claude Conversations Viewer</h1>
        <div id="content" class="loading">Carregando...</div>
    </div>

    <script>
        const pathParts = window.location.pathname.split('/').filter(Boolean);
        const container = document.getElementById('content');

        // Função para escapar HTML
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Função para formatar timestamp
        function formatTime(date) {
            return new Date(date).toLocaleString('pt-BR');
        }

        // Função para formatar tamanho de arquivo
        function formatSize(bytes) {
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            if (bytes === 0) return '0 Bytes';
            const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
            return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
        }

        // Se estamos na raiz, listar projetos
        if (pathParts.length === 0) {
            fetch('/api/projects')
                .then(r => r.json())
                .then(projects => {
                    container.innerHTML = \`
                        <h2>📁 Projetos Disponíveis</h2>
                        <div class="projects-list">
                            \${projects.map(p => \`
                                <div class="project-item" onclick="window.location.href='/\${p}'">
                                    <span>📂 \${p}</span>
                                    <span>➜</span>
                                </div>
                            \`).join('')}
                        </div>
                    \`;
                })
                .catch(err => {
                    container.innerHTML = '<div class="error">Erro ao carregar projetos: ' + err.message + '</div>';
                });
        }
        // Se temos apenas o projeto, listar conversas
        else if (pathParts.length === 1) {
            const project = pathParts[0];
            fetch(\`/api/conversations/\${project}\`)
                .then(r => r.json())
                .then(conversations => {
                    if (!conversations || conversations.length === 0) {
                        container.innerHTML = \`
                            <a href="/" class="back-button">← Voltar</a>
                            <div class="error">Nenhuma conversa encontrada neste projeto</div>
                        \`;
                        return;
                    }

                    container.innerHTML = \`
                        <a href="/" class="back-button">← Voltar</a>
                        <h2>💬 Conversas em \${project}</h2>
                        <div class="stats">
                            <div class="stat-card">
                                <div class="stat-value">\${conversations.length}</div>
                                <div class="stat-label">Total de Conversas</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">\${formatSize(conversations.reduce((a, c) => a + c.size, 0))}</div>
                                <div class="stat-label">Tamanho Total</div>
                            </div>
                        </div>
                        <div class="conversations-list">
                            \${conversations.map(c => \`
                                <div class="conversation-item" onclick="window.location.href='/\${project}/\${c.id}'">
                                    <span>💬 \${c.id.substring(0, 8)}...</span>
                                    <div class="info">
                                        <span>📏 \${formatSize(c.size)}</span>
                                        <span>🕐 \${formatTime(c.modified)}</span>
                                    </div>
                                </div>
                            \`).join('')}
                        </div>
                    \`;
                })
                .catch(err => {
                    container.innerHTML = \`
                        <a href="/" class="back-button">← Voltar</a>
                        <div class="error">Erro ao carregar conversas: \${err.message}</div>
                    \`;
                });
        }
        // Se temos projeto e conversa, mostrar mensagens
        else if (pathParts.length === 2) {
            const [project, conversationId] = pathParts;
            fetch(\`/api/conversation/\${project}/\${conversationId}\`)
                .then(r => r.json())
                .then(messages => {
                    if (!messages || messages.length === 0) {
                        container.innerHTML = \`
                            <a href="/\${project}" class="back-button">← Voltar</a>
                            <div class="error">Nenhuma mensagem encontrada</div>
                        \`;
                        return;
                    }

                    const userMessages = messages.filter(m => m.role === 'user').length;
                    const assistantMessages = messages.filter(m => m.role === 'assistant').length;

                    container.innerHTML = \`
                        <a href="/\${project}" class="back-button">← Voltar para conversas</a>
                        <h2>💬 Conversa \${conversationId.substring(0, 8)}...</h2>
                        <div class="stats">
                            <div class="stat-card">
                                <div class="stat-value">\${messages.length}</div>
                                <div class="stat-label">Total de Mensagens</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">\${userMessages}</div>
                                <div class="stat-label">Mensagens do Usuário</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">\${assistantMessages}</div>
                                <div class="stat-label">Respostas do Assistant</div>
                            </div>
                        </div>
                        \${messages.map((msg, idx) => \`
                            <div class="message \${msg.role}">
                                <div class="role">
                                    \${msg.role === 'user' ? '👤 Usuário' : '🤖 Assistant'}
                                </div>
                                <div class="content">\${escapeHtml(msg.content || '')}</div>
                                \${msg.timestamp ? \`<div class="timestamp">⏰ \${formatTime(msg.timestamp)}</div>\` : ''}
                            </div>
                        \`).join('')}
                    \`;
                })
                .catch(err => {
                    container.innerHTML = \`
                        <a href="/\${project}" class="back-button">← Voltar</a>
                        <div class="error">Erro ao carregar conversa: \${err.message}</div>
                    \`;
                });
        }
    </script>
</body>
</html>`;

    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(html);
});

server.listen(PORT, () => {
    console.log('='.repeat(60));
    console.log('📜 CLAUDE CONVERSATIONS VIEWER');
    console.log('='.repeat(60));
    console.log(`📡 Servidor rodando na porta ${PORT}`);
    console.log(`🔗 Acesse: http://localhost:${PORT}`);
    console.log(`📁 Lendo conversas de: ${CLAUDE_DIR}`);
    console.log('='.repeat(60));
    console.log('💡 Navegue pelos projetos e conversas');
    console.log('🛑 Pressione Ctrl+C para parar');
    console.log('='.repeat(60));
});

server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
        console.error(`❌ Erro: Porta ${PORT} já está em uso`);
        console.log('Tente parar o processo existente ou use outra porta');
    } else {
        console.error(`❌ Erro ao iniciar servidor: ${err.message}`);
    }
    process.exit(1);
});