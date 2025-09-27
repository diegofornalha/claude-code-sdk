/**
 * Session Manager para Neo4j Agent
 * Gerencia sessões de conhecimento
 */

import { BootcampProgress, KnowledgeNode, Message } from './types';

export class SessionManager {
  private sessionId: string;
  private messages: Message[] = [];
  private context: Map<string, any> = new Map();
  private progress: BootcampProgress;

  constructor(userId: string = 'diego-fornalha') {
    this.sessionId = this.generateSessionId();
    this.progress = this.initializeProgress();
    this.context.set('userId', userId);
    this.context.set('sessionStart', new Date().toISOString());
  }

  private generateSessionId(): string {
    return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private initializeProgress(): BootcampProgress {
    return {
      current_score: 45,
      target_score: 100,
      current_week: 1,
      total_weeks: 12,
      completed_concepts: ['query() function', 'Async Patterns'],
      gaps: ['MCP Protocol', 'Hooks System'],
      next_milestone: 'MCP Tools (Score 60)'
    };
  }

  public addMessage(message: Message): void {
    this.messages.push(message);

    // Limitar histórico a 100 mensagens
    if (this.messages.length > 100) {
      this.messages = this.messages.slice(-100);
    }
  }

  public getMessages(): Message[] {
    return this.messages;
  }

  public getRecentMessages(count: number = 10): Message[] {
    return this.messages.slice(-count);
  }

  public updateProgress(updates: Partial<BootcampProgress>): void {
    this.progress = {
      ...this.progress,
      ...updates
    };
    this.context.set('lastProgressUpdate', new Date().toISOString());
  }

  public getProgress(): BootcampProgress {
    return this.progress;
  }

  public setContext(key: string, value: any): void {
    this.context.set(key, value);
  }

  public getContext(key?: string): any {
    if (key) {
      return this.context.get(key);
    }

    // Retornar todo o contexto
    const fullContext: Record<string, any> = {};
    this.context.forEach((value, key) => {
      fullContext[key] = value;
    });
    return fullContext;
  }

  public getSessionSummary() {
    return {
      sessionId: this.sessionId,
      messageCount: this.messages.length,
      progress: this.progress,
      context: this.getContext(),
      duration: this.calculateDuration()
    };
  }

  private calculateDuration(): string {
    const start = new Date(this.context.get('sessionStart'));
    const now = new Date();
    const diff = now.getTime() - start.getTime();
    const minutes = Math.floor(diff / 60000);
    return `${minutes} minutos`;
  }

  public exportSession(): string {
    return JSON.stringify({
      sessionId: this.sessionId,
      messages: this.messages,
      progress: this.progress,
      context: this.getContext(),
      exported: new Date().toISOString()
    }, null, 2);
  }

  public clear(): void {
    this.messages = [];
    this.context.clear();
    this.sessionId = this.generateSessionId();
    this.progress = this.initializeProgress();
  }
}