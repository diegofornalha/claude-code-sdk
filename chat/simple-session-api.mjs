#!/usr/bin/env node
/**
 * API Simplificada para Sessões Claude
 */

import express from 'express';
import cors from 'cors';
import { promises as fs } from 'fs';
import path from 'path';

const app = express();
const PORT = 3002;

const CLAUDE_PROJECTS = '/Users/2a/.claude/projects/-Users-2a-Desktop-neo4j-agent-claude-code-sdk';

app.use(cors());
app.use(express.json());

// Rota principal - lista sessões
app.get('/api/sessions', async (req, res) => {
    try {
        const files = await fs.readdir(CLAUDE_PROJECTS);
        const sessions = [];

        for (const file of files) {
            if (!file.endsWith('.jsonl')) continue;

            const filePath = path.join(CLAUDE_PROJECTS, file);
            const stats = await fs.stat(filePath);

            // Lê primeira mensagem do usuário
            let firstUserMessage = '';
            try {
                const content = await fs.readFile(filePath, 'utf-8');
                const lines = content.split('\n');

                for (const line of lines) {
                    if (!line) continue;
                    const entry = JSON.parse(line);
                    if (entry.type === 'user' && entry.message?.content) {
                        firstUserMessage = typeof entry.message.content === 'string'
                            ? entry.message.content
                            : entry.message.content[0]?.text || '';
                        break;
                    }
                }
            } catch (e) {
                // Ignora erros de parse
            }

            sessions.push({
                id: file.replace('.jsonl', ''),
                size: stats.size,
                modified: stats.mtime,
                preview: firstUserMessage.substring(0, 100)
            });
        }

        sessions.sort((a, b) => new Date(b.modified) - new Date(a.modified));
        res.json(sessions);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Lê uma sessão específica
app.get('/api/sessions/:id', async (req, res) => {
    try {
        const filePath = path.join(CLAUDE_PROJECTS, `${req.params.id}.jsonl`);
        const content = await fs.readFile(filePath, 'utf-8');
        res.type('text/plain').send(content);
    } catch (error) {
        res.status(404).json({ error: 'Session not found' });
    }
});

app.listen(PORT, () => {
    console.log(`✅ API rodando em http://localhost:${PORT}/api/sessions`);
});