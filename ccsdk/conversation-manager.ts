/**
 * Gerenciador Centralizado de Conversas
 * Mantém todo o histórico em um único arquivo JSONL organizado
 */

import { promises as fs } from 'fs';
import * as path from 'path';
import { Message } from './types';

export interface ConversationEntry {
  timestamp: string;
  sessionId: string;
  messageId: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  metadata?: {
    tokens?: number;
    cost?: number;
    model?: string;
    context?: any;
    toolCalls?: any[];
  };
}

export interface ConversationSession {
  sessionId: string;
  projectId: string;
  startedAt: string;
  lastActivity: string;
  messageCount: number;
  totalTokens?: number;
  totalCost?: number;
  status: 'active' | 'completed' | 'paused';
}

export class ConversationManager {
  private readonly baseDir: string;
  private readonly projectId: string;
  private readonly mainFile: string;
  private readonly sessionsFile: string;
  private readonly maxFileSize = 50 * 1024 * 1024; // 50MB para rotação
  private currentSession: ConversationSession | null = null;
  private writeQueue: ConversationEntry[] = [];
  private isWriting = false;

  // ID unificado para todas as sessões (similar ao cc-sdk-chat)
  private readonly UNIFIED_SESSION_ID = "00000000-0000-0000-0000-000000000001";
  // Controlar via variável de ambiente ou sempre usar modo unificado
  private readonly useUnifiedSession = process.env.UNIFIED_SESSION !== 'false';

  constructor(projectId: string = 'neo4j-agent-claude-code-sdk') {
    this.projectId = projectId;

    // Diretório centralizado para conversas
    this.baseDir = path.join(
      process.env.HOME || '',
      '.claude',
      'projects',
      `-Users-2a-Desktop-${projectId.replace(/\//g, '-')}`
    );

    // Arquivo principal JSONL único
    this.mainFile = path.join(this.baseDir, 'conversations.jsonl');

    // Arquivo de metadados das sessões
    this.sessionsFile = path.join(this.baseDir, 'sessions.json');

    // Log do modo de sessão
    console.log('🔧 ConversationManager iniciado em modo:',
      this.useUnifiedSession ? 'SESSÃO UNIFICADA' : 'múltiplas sessões');
    if (this.useUnifiedSession) {
      console.log('🆔 ID de sessão unificado:', this.UNIFIED_SESSION_ID);
    }

    this.initialize();
  }

  /**
   * Inicializa o sistema de arquivos
   */
  private async initialize() {
    try {
      // Criar diretório se não existir
      await fs.mkdir(this.baseDir, { recursive: true });

      // Verificar se arquivo principal existe
      try {
        await fs.access(this.mainFile);
      } catch {
        // Criar arquivo vazio se não existir
        await fs.writeFile(this.mainFile, '');
        console.log('📝 Arquivo de conversas criado:', this.mainFile);
      }

      // Carregar ou criar sessões
      await this.loadSessions();

    } catch (error) {
      console.error('❌ Erro ao inicializar ConversationManager:', error);
    }
  }

  /**
   * Carrega metadados das sessões
   */
  private async loadSessions(): Promise<Map<string, ConversationSession>> {
    const sessions = new Map<string, ConversationSession>();

    try {
      const data = await fs.readFile(this.sessionsFile, 'utf-8');
      const sessionsArray = JSON.parse(data);

      sessionsArray.forEach((session: ConversationSession) => {
        sessions.set(session.sessionId, session);
      });
    } catch {
      // Arquivo não existe ainda
    }

    return sessions;
  }

  /**
   * Salva metadados das sessões
   */
  private async saveSessions(sessions: Map<string, ConversationSession>) {
    const sessionsArray = Array.from(sessions.values());
    await fs.writeFile(this.sessionsFile, JSON.stringify(sessionsArray, null, 2));
  }

  /**
   * Inicia ou retoma uma sessão
   */
  public async startSession(sessionId?: string): Promise<string> {
    const sessions = await this.loadSessions();

    // Usar sessionId fornecido ou criar novo
    const id = sessionId || this.generateSessionId();

    // Verificar se sessão existe
    if (sessions.has(id)) {
      this.currentSession = sessions.get(id)!;
      this.currentSession.status = 'active';
      this.currentSession.lastActivity = new Date().toISOString();
    } else {
      // Criar nova sessão
      this.currentSession = {
        sessionId: id,
        projectId: this.projectId,
        startedAt: new Date().toISOString(),
        lastActivity: new Date().toISOString(),
        messageCount: 0,
        totalTokens: 0,
        totalCost: 0,
        status: 'active'
      };

      sessions.set(id, this.currentSession);
    }

    await this.saveSessions(sessions);

    console.log('🚀 Sessão iniciada:', id);
    return id;
  }

  /**
   * Adiciona mensagem à conversa
   */
  public async addMessage(
    role: 'user' | 'assistant' | 'system',
    content: string,
    metadata?: any
  ): Promise<void> {
    if (!this.currentSession) {
      await this.startSession();
    }

    const entry: ConversationEntry = {
      timestamp: new Date().toISOString(),
      sessionId: this.currentSession!.sessionId,
      messageId: this.generateMessageId(),
      role,
      content,
      metadata
    };

    // Adicionar à fila de escrita
    this.writeQueue.push(entry);

    // Atualizar metadados da sessão
    this.currentSession!.messageCount++;
    this.currentSession!.lastActivity = entry.timestamp;

    if (metadata?.tokens) {
      this.currentSession!.totalTokens = (this.currentSession!.totalTokens || 0) + metadata.tokens;
    }

    if (metadata?.cost) {
      this.currentSession!.totalCost = (this.currentSession!.totalCost || 0) + metadata.cost;
    }

    // Processar fila de escrita
    await this.processWriteQueue();
  }

  /**
   * Processa fila de escrita de forma assíncrona
   */
  private async processWriteQueue() {
    if (this.isWriting || this.writeQueue.length === 0) {
      return;
    }

    this.isWriting = true;

    try {
      // Pegar todas as mensagens da fila
      const entries = [...this.writeQueue];
      this.writeQueue = [];

      // Converter para JSONL
      const jsonlContent = entries
        .map(entry => JSON.stringify(entry))
        .join('\n') + '\n';

      // Verificar tamanho do arquivo para rotação
      const stats = await fs.stat(this.mainFile);

      if (stats.size > this.maxFileSize) {
        await this.rotateFile();
      }

      // Adicionar ao arquivo principal
      await fs.appendFile(this.mainFile, jsonlContent);

      // Salvar metadados atualizados
      const sessions = await this.loadSessions();
      if (this.currentSession) {
        sessions.set(this.currentSession.sessionId, this.currentSession);
        await this.saveSessions(sessions);
      }

      console.log(`✅ ${entries.length} mensagem(s) salva(s) no histórico`);

    } catch (error) {
      console.error('❌ Erro ao processar fila de escrita:', error);
      // Recolocar mensagens na fila em caso de erro
      this.writeQueue.unshift(...this.writeQueue);
    } finally {
      this.isWriting = false;
    }
  }

  /**
   * Rotaciona arquivo quando fica muito grande
   */
  private async rotateFile() {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const archiveFile = path.join(this.baseDir, `conversations-${timestamp}.jsonl`);

    // Mover arquivo atual para arquivo de arquivo
    await fs.rename(this.mainFile, archiveFile);

    // Criar novo arquivo principal
    await fs.writeFile(this.mainFile, '');

    console.log('📦 Arquivo rotacionado para:', archiveFile);
  }

  /**
   * Busca mensagens no histórico
   */
  public async searchMessages(
    query: {
      sessionId?: string;
      role?: string;
      startDate?: Date;
      endDate?: Date;
      limit?: number;
    }
  ): Promise<ConversationEntry[]> {
    const results: ConversationEntry[] = [];

    try {
      const content = await fs.readFile(this.mainFile, 'utf-8');
      const lines = content.split('\n').filter(line => line.trim());

      for (const line of lines) {
        try {
          const entry = JSON.parse(line) as ConversationEntry;

          // Aplicar filtros
          if (query.sessionId && entry.sessionId !== query.sessionId) continue;
          if (query.role && entry.role !== query.role) continue;

          if (query.startDate && new Date(entry.timestamp) < query.startDate) continue;
          if (query.endDate && new Date(entry.timestamp) > query.endDate) continue;

          results.push(entry);

          if (query.limit && results.length >= query.limit) break;
        } catch {
          // Ignorar linhas inválidas
        }
      }
    } catch (error) {
      console.error('❌ Erro ao buscar mensagens:', error);
    }

    return results;
  }

  /**
   * Obtém resumo da sessão atual
   */
  public getSessionSummary(): ConversationSession | null {
    return this.currentSession;
  }

  /**
   * Lista todas as sessões
   */
  public async listSessions(): Promise<ConversationSession[]> {
    const sessions = await this.loadSessions();
    return Array.from(sessions.values());
  }

  /**
   * Obtém mensagens de uma sessão específica
   */
  public async getSessionMessages(sessionId: string): Promise<ConversationEntry[]> {
    return this.searchMessages({ sessionId });
  }

  /**
   * Pausa sessão atual
   */
  public async pauseSession() {
    if (this.currentSession) {
      this.currentSession.status = 'paused';

      const sessions = await this.loadSessions();
      sessions.set(this.currentSession.sessionId, this.currentSession);
      await this.saveSessions(sessions);

      console.log('⏸️ Sessão pausada:', this.currentSession.sessionId);
    }
  }

  /**
   * Completa sessão atual
   */
  public async completeSession() {
    if (this.currentSession) {
      this.currentSession.status = 'completed';

      const sessions = await this.loadSessions();
      sessions.set(this.currentSession.sessionId, this.currentSession);
      await this.saveSessions(sessions);

      console.log('✅ Sessão completada:', this.currentSession.sessionId);
      this.currentSession = null;
    }
  }

  /**
   * Gera ID único para sessão
   * No modo unificado, sempre retorna o mesmo ID
   */
  private generateSessionId(): string {
    // Se modo unificado estiver ativo, usar sempre o mesmo ID
    if (this.useUnifiedSession) {
      return this.UNIFIED_SESSION_ID;
    }

    // Caso contrário, gerar ID único (comportamento original)
    const timestamp = Date.now().toString(36);
    const random = Math.random().toString(36).substr(2, 9);
    return `${timestamp}-${random}`;
  }

  /**
   * Gera ID único para mensagem
   */
  private generateMessageId(): string {
    return `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Obtém estatísticas do histórico
   */
  public async getStatistics(): Promise<{
    totalSessions: number;
    totalMessages: number;
    totalTokens: number;
    totalCost: number;
    averageMessagesPerSession: number;
    mostActiveSession: ConversationSession | null;
  }> {
    const sessions = await this.loadSessions();
    const allSessions = Array.from(sessions.values());

    const totalMessages = allSessions.reduce((sum, s) => sum + s.messageCount, 0);
    const totalTokens = allSessions.reduce((sum, s) => sum + (s.totalTokens || 0), 0);
    const totalCost = allSessions.reduce((sum, s) => sum + (s.totalCost || 0), 0);

    const mostActiveSession = allSessions.length > 0
      ? allSessions.reduce((max, s) => s.messageCount > max.messageCount ? s : max)
      : null;

    return {
      totalSessions: allSessions.length,
      totalMessages,
      totalTokens,
      totalCost,
      averageMessagesPerSession: allSessions.length > 0 ? totalMessages / allSessions.length : 0,
      mostActiveSession
    };
  }

  /**
   * Limpa sessões antigas (opcional)
   */
  public async cleanupOldSessions(daysToKeep: number = 30): Promise<number> {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);

    const sessions = await this.loadSessions();
    let removedCount = 0;

    for (const [id, session] of sessions) {
      if (new Date(session.lastActivity) < cutoffDate) {
        sessions.delete(id);
        removedCount++;
      }
    }

    if (removedCount > 0) {
      await this.saveSessions(sessions);
      console.log(`🧹 ${removedCount} sessões antigas removidas`);
    }

    return removedCount;
  }
}

// Exportar instância singleton
export const conversationManager = new ConversationManager();