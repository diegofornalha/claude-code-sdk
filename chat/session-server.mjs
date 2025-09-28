/**
 * Servidor de Sessões do Claude Code SDK
 * Serve os arquivos .jsonl como API REST
 */

import express from 'express';
import cors from 'cors';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;

// Caminho dos arquivos de sessão do Claude
const CLAUDE_PROJECTS_PATH = '/Users/2a/.claude/projects/-Users-2a-Desktop-neo4j-agent-claude-code-sdk';

// Middleware
app.use(cors());
app.use(express.json());

/**
 * Lista todas as sessões disponíveis
 */
app.get('/api/sessions/list', async (req, res) => {
    try {
        const files = await fs.readdir(CLAUDE_PROJECTS_PATH);
        const sessions = [];

        for (const file of files) {
            if (file.endsWith('.jsonl')) {
                const filePath = path.join(CLAUDE_PROJECTS_PATH, file);
                const stats = await fs.stat(filePath);
                const sessionId = file.replace('.jsonl', '');

                // Lê primeira linha para preview
                let preview = '';
                let messageCount = 0;

                try {
                    const content = await fs.readFile(filePath, 'utf-8');
                    const lines = content.split('\n').filter(l => l.trim());
                    messageCount = lines.length;

                    // Busca primeira mensagem do usuário para preview
                    for (const line of lines) {
                        try {
                            const entry = JSON.parse(line);
                            if (entry.type === 'user' && entry.message?.content) {
                                const text = typeof entry.message.content === 'string'
                                    ? entry.message.content
                                    : entry.message.content[0]?.text || '';
                                preview = text.substring(0, 100);
                                break;
                            }
                        } catch (e) {
                            // Ignora linhas inválidas
                        }
                    }
                } catch (e) {
                    console.error('Erro ao ler preview:', e);
                }

                sessions.push({
                    id: sessionId,
                    file: file,
                    size: stats.size,
                    created: stats.birthtime,
                    modified: stats.mtime,
                    messageCount: messageCount,
                    preview: preview
                });
            }
        }

        // Ordena por data de modificação (mais recente primeiro)
        sessions.sort((a, b) => new Date(b.modified) - new Date(a.modified));

        res.json(sessions);
    } catch (error) {
        console.error('Erro ao listar sessões:', error);
        res.status(500).json({ error: 'Erro ao listar sessões' });
    }
});

/**
 * Lê uma sessão específica
 */
app.get('/api/sessions/read/:sessionId', async (req, res) => {
    try {
        const { sessionId } = req.params;
        const filePath = path.join(CLAUDE_PROJECTS_PATH, `${sessionId}.jsonl`);

        const content = await fs.readFile(filePath, 'utf-8');
        res.type('text/plain').send(content);
    } catch (error) {
        console.error('Erro ao ler sessão:', error);
        if (error.code === 'ENOENT') {
            res.status(404).json({ error: 'Sessão não encontrada' });
        } else {
            res.status(500).json({ error: 'Erro ao ler sessão' });
        }
    }
});

/**
 * Busca em todas as sessões
 */
app.get('/api/sessions/search', async (req, res) => {
    try {
        const { q } = req.query;
        if (!q) {
            return res.status(400).json({ error: 'Query parameter "q" is required' });
        }

        const files = await fs.readdir(CLAUDE_PROJECTS_PATH);
        const results = [];

        for (const file of files) {
            if (file.endsWith('.jsonl')) {
                const filePath = path.join(CLAUDE_PROJECTS_PATH, file);
                const content = await fs.readFile(filePath, 'utf-8');

                if (content.toLowerCase().includes(q.toLowerCase())) {
                    const sessionId = file.replace('.jsonl', '');
                    const lines = content.split('\n').filter(l => l.trim());

                    // Encontra contexto da busca
                    let matchContext = '';
                    for (const line of lines) {
                        if (line.toLowerCase().includes(q.toLowerCase())) {
                            try {
                                const entry = JSON.parse(line);
                                if (entry.message?.content) {
                                    const text = typeof entry.message.content === 'string'
                                        ? entry.message.content
                                        : JSON.stringify(entry.message.content);

                                    if (text.toLowerCase().includes(q.toLowerCase())) {
                                        matchContext = text.substring(0, 200);
                                        break;
                                    }
                                }
                            } catch (e) {
                                // Ignora
                            }
                        }
                    }

                    results.push({
                        sessionId: sessionId,
                        file: file,
                        matchContext: matchContext
                    });
                }
            }
        }

        res.json({
            query: q,
            resultsCount: results.length,
            results: results
        });
    } catch (error) {
        console.error('Erro ao buscar:', error);
        res.status(500).json({ error: 'Erro ao buscar nas sessões' });
    }
});

/**
 * Estatísticas gerais
 */
app.get('/api/sessions/stats', async (req, res) => {
    try {
        const files = await fs.readdir(CLAUDE_PROJECTS_PATH);
        let totalSessions = 0;
        let totalMessages = 0;
        let totalSize = 0;

        for (const file of files) {
            if (file.endsWith('.jsonl')) {
                totalSessions++;
                const filePath = path.join(CLAUDE_PROJECTS_PATH, file);
                const stats = await fs.stat(filePath);
                totalSize += stats.size;

                const content = await fs.readFile(filePath, 'utf-8');
                const lines = content.split('\n').filter(l => l.trim());
                totalMessages += lines.length;
            }
        }

        res.json({
            totalSessions,
            totalMessages,
            totalSize,
            averageMessagesPerSession: totalSessions > 0 ? Math.round(totalMessages / totalSessions) : 0,
            averageSize: totalSessions > 0 ? Math.round(totalSize / totalSessions) : 0
        });
    } catch (error) {
        console.error('Erro ao calcular estatísticas:', error);
        res.status(500).json({ error: 'Erro ao calcular estatísticas' });
    }
});

// Servir arquivos estáticos do chat
app.use(express.static(__dirname));

// Rota catch-all para SPA
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
    console.log(`
╔════════════════════════════════════════════════╗
║   🚀 Servidor de Sessões Claude Code SDK      ║
║   Rodando em: http://localhost:${PORT}           ║
║                                                ║
║   Endpoints disponíveis:                      ║
║   • GET /api/sessions/list                    ║
║   • GET /api/sessions/read/:id                ║
║   • GET /api/sessions/search?q=termo          ║
║   • GET /api/sessions/stats                   ║
╚════════════════════════════════════════════════╝
    `);
});