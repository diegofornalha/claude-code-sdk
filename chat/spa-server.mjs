#!/usr/bin/env node
/**
 * Servidor SPA com suporte a rotas e API de sessões
 */

import express from 'express';
import cors from 'cors';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;

// Diretório de projetos do Claude
const CLAUDE_PROJECTS_BASE = '/Users/2a/.claude/projects';

// Middleware
app.use(cors());
app.use(express.json());

// =====================================================
// API ENDPOINTS
// =====================================================

// Lista todos os projetos disponíveis
app.get('/api/projects', async (req, res) => {
    try {
        const dirs = await fs.readdir(CLAUDE_PROJECTS_BASE);
        const projects = [];

        for (const dir of dirs) {
            if (dir.startsWith('.')) continue; // Ignora arquivos ocultos

            const projectPath = path.join(CLAUDE_PROJECTS_BASE, dir);
            const stats = await fs.stat(projectPath);

            if (stats.isDirectory()) {
                // Conta sessões no projeto
                const files = await fs.readdir(projectPath);
                const sessionCount = files.filter(f => f.endsWith('.jsonl')).length;

                projects.push({
                    name: dir,
                    path: projectPath,
                    sessionCount: sessionCount,
                    modified: stats.mtime
                });
            }
        }

        projects.sort((a, b) => new Date(b.modified) - new Date(a.modified));
        res.json(projects);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Lista sessões de um projeto específico
app.get('/api/projects/:projectName/sessions', async (req, res) => {
    try {
        const projectPath = path.join(CLAUDE_PROJECTS_BASE, req.params.projectName);
        const files = await fs.readdir(projectPath);
        const sessions = [];

        for (const file of files) {
            if (!file.endsWith('.jsonl')) continue;

            const filePath = path.join(projectPath, file);
            const stats = await fs.stat(filePath);

            // Lê primeira mensagem do usuário para preview
            let firstUserMessage = '';
            let messageCount = 0;

            try {
                const content = await fs.readFile(filePath, 'utf-8');
                const lines = content.split('\n').filter(l => l.trim());
                messageCount = lines.length;

                for (const line of lines) {
                    try {
                        const entry = JSON.parse(line);
                        if (entry.type === 'user' && entry.message?.content) {
                            firstUserMessage = typeof entry.message.content === 'string'
                                ? entry.message.content
                                : entry.message.content[0]?.text || '';
                            break;
                        }
                    } catch (e) {
                        // Ignora erros de parse
                    }
                }
            } catch (e) {
                // Ignora erros
            }

            sessions.push({
                id: file.replace('.jsonl', ''),
                size: stats.size,
                modified: stats.mtime,
                messageCount: messageCount,
                preview: firstUserMessage.substring(0, 150)
            });
        }

        sessions.sort((a, b) => new Date(b.modified) - new Date(a.modified));
        res.json(sessions);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Lê conteúdo de uma sessão
app.get('/api/projects/:projectName/sessions/:sessionId', async (req, res) => {
    try {
        const filePath = path.join(
            CLAUDE_PROJECTS_BASE,
            req.params.projectName,
            `${req.params.sessionId}.jsonl`
        );
        const content = await fs.readFile(filePath, 'utf-8');
        res.type('text/plain').send(content);
    } catch (error) {
        res.status(404).json({ error: 'Session not found' });
    }
});

// API de sessões simples (compatibilidade)
app.get('/api/sessions', async (req, res) => {
    // Redireciona para o projeto padrão
    const defaultProject = '-Users-2a-Desktop-neo4j-agent-claude-code-sdk';
    res.redirect(`/api/projects/${defaultProject}/sessions`);
});

app.get('/api/sessions/:id', async (req, res) => {
    const defaultProject = '-Users-2a-Desktop-neo4j-agent-claude-code-sdk';
    res.redirect(`/api/projects/${defaultProject}/sessions/${req.params.id}`);
});

// =====================================================
// ARQUIVOS ESTÁTICOS E SPA
// =====================================================

// Servir arquivos estáticos ESPECÍFICOS primeiro
app.get('/styles.css', (req, res) => {
    res.sendFile(path.join(__dirname, 'styles.css'));
});

app.get('/app-unified.js', (req, res) => {
    res.sendFile(path.join(__dirname, 'app-unified.js'));
});

app.get('/app-complete.js', (req, res) => {
    res.sendFile(path.join(__dirname, 'app-complete.js'));
});

app.get('/app-no-limit.js', (req, res) => {
    res.sendFile(path.join(__dirname, 'app-no-limit.js'));
});

app.get('/manifest.json', (req, res) => {
    res.sendFile(path.join(__dirname, 'manifest.json'));
});

// Rota específica para /projects
app.get('/projects', (req, res) => {
    res.sendFile(path.join(__dirname, 'projects.html'));
});

// IMPORTANTE: Catch-all para SPA - sempre retorna index.html
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// =====================================================
// INICIALIZAÇÃO
// =====================================================

app.listen(PORT, () => {
    console.log(`
╔════════════════════════════════════════════════════════════════╗
║   🚀 Servidor SPA + API de Sessões Claude                     ║
║   Rodando em: http://localhost:${PORT}                            ║
║                                                                ║
║   📁 Rotas de Navegação:                                      ║
║   • http://localhost:${PORT}/                                     ║
║   • http://localhost:${PORT}/[project-name]                       ║
║   • http://localhost:${PORT}/[project-name]/[session-id]          ║
║                                                                ║
║   🔌 API Endpoints:                                           ║
║   • GET /api/projects                                         ║
║   • GET /api/projects/:name/sessions                          ║
║   • GET /api/projects/:name/sessions/:id                      ║
║                                                                ║
║   📂 Diretório de projetos:                                   ║
║   ${CLAUDE_PROJECTS_BASE}                           ║
╚════════════════════════════════════════════════════════════════╝
    `);
});