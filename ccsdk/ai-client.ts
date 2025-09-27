/**
 * AI Client para Neo4j Agent
 * Usa Claude Code SDK corretamente com query()
 */

// Imports CORRETOS do Claude Code SDK
import { query, ClaudeCodeOptions } from '@anthropic-ai/claude-code';

export class AIClient {
  private options: ClaudeCodeOptions;

  constructor() {
    // Configurações CORRETAS do Claude
    this.options = {
      // Não existe model em ClaudeCodeOptions
      systemPrompt: this.getSystemPrompt(),
      allowedTools: [
        'mcp__neo4j-memory__search_memories',
        'mcp__neo4j-memory__create_memory',
        'mcp__neo4j-memory__create_connection',
        'mcp__neo4j-memory__update_memory',
        'mcp__neo4j-memory__get_context_for_task',
        'mcp__neo4j-memory__learn_from_result',
        'mcp__neo4j-memory__suggest_best_approach'
      ]
    };
  }

  private getSystemPrompt(): string {
    return `
You are a Knowledge Management Assistant specialized in the Claude Code SDK Bootcamp.

Your role is to:
1. Help users navigate their learning journey
2. Track progress through the bootcamp (current score: 45/100)
3. Identify knowledge gaps (especially MCP Tools and Hooks)
4. Connect concepts across Python and TypeScript
5. Generate insights from the knowledge graph

Key Context:
- User: Diego Fornalha
- Current Week: 1/12
- Critical Gaps: MCP Protocol, Hooks System
- Goal: Reach Score 100 (Expert level)

When answering:
- Be concise and practical
- Reference specific bootcamp materials
- Suggest next steps based on current progress
- Connect concepts to show relationships
- Use Neo4j to store and retrieve knowledge

Available Neo4j MCP Tools:
- search_memories: Find existing knowledge
- create_memory: Add new concepts
- create_connection: Link related concepts
- get_context_for_task: Get relevant context
- learn_from_result: Record learnings
- suggest_best_approach: Get recommendations

Always maintain focus on the bootcamp progress and practical application.
    `;
  }

  /**
   * Processar query sobre conhecimento usando query() corretamente
   */
  async processKnowledgeQuery(queryText: string, context?: any) {
    try {
      // Buscar contexto relevante no Neo4j
      const relevantContext = await this.searchRelevantKnowledge(queryText);

      // Adicionar contexto do bootcamp
      const bootcampContext = this.getBootcampContext();

      // Construir prompt completo
      const fullPrompt = `
Context:
- Relevant Knowledge: ${JSON.stringify(relevantContext)}
- Bootcamp Status: ${JSON.stringify(bootcampContext)}
- Additional Context: ${JSON.stringify(context || {})}

User Query: ${queryText}

Please provide a helpful response focused on the bootcamp progress.
      `;

      // Usar query() CORRETAMENTE
      const responses: string[] = [];

      // query() retorna um AsyncGenerator
      for await (const message of query(fullPrompt, this.options)) {
        if (message.result) {
          responses.push(message.result);
        }
      }

      const response = responses.join('\n');

      // Registrar aprendizado
      await this.recordLearning(queryText, response);

      return response;
    } catch (error) {
      console.error('Error processing query:', error);
      throw error;
    }
  }

  /**
   * Buscar conhecimento relevante (mock por enquanto)
   */
  private async searchRelevantKnowledge(queryText: string) {
    console.log('🔍 Searching relevant knowledge for:', queryText);

    // Em produção, usaria MCP tool real
    // Por enquanto retorna mock
    return {
      concepts: [
        'Claude Code SDK é agnóstico de linguagem',
        'MCP Tools retornam {"content": [...]}',
        'Hooks interceptam Pre/Post execução'
      ],
      gaps: ['MCP Protocol', 'Hooks System'],
      suggestions: [
        'Revisar CONCEITOS/*.md',
        'Implementar exercício Python',
        'Validar em TypeScript'
      ]
    };
  }

  /**
   * Contexto atual do bootcamp
   */
  private getBootcampContext() {
    return {
      user: 'Diego Fornalha',
      current_score: 45,
      target_score: 100,
      week: 1,
      total_weeks: 12,
      next_milestone: 'MCP Tools (Score 60)',
      current_gaps: ['MCP Protocol', 'Hooks System'],
      completed: ['query() function', 'Async Patterns'],
      in_progress: ['ClaudeSDKClient']
    };
  }

  /**
   * Registrar aprendizado no Neo4j (mock por enquanto)
   */
  private async recordLearning(queryText: string, response: string) {
    console.log('✅ Recording learning:', {
      query: queryText.substring(0, 50),
      timestamp: new Date().toISOString()
    });

    // Em produção usaria: mcp__neo4j-memory__learn_from_result
    return true;
  }

  /**
   * Analisar texto e extrair conhecimento
   */
  async extractKnowledge(text: string) {
    const prompt = `
Analyze this text and extract:
1. Key concepts related to Claude Code SDK
2. Relationships between concepts
3. Bootcamp relevance (score impact)
4. Identified gaps or learning opportunities

Text: ${text}

Return structured knowledge for the Neo4j graph.
    `;

    return this.processKnowledgeQuery(prompt);
  }

  /**
   * Gerar insights do conhecimento acumulado
   */
  async generateInsights() {
    const prompt = `
Based on the current knowledge graph:
1. What patterns are emerging?
2. What connections are most important?
3. What gaps need urgent attention?
4. What's the optimal learning path?

Current context:
- Score: 45/100
- Week: 1/12
- Gaps: MCP, Hooks
    `;

    return this.processKnowledgeQuery(prompt);
  }

  /**
   * Sugerir próximos passos
   */
  async suggestNextSteps() {
    const prompt = `
Given current progress (Score 45/100, Week 1/12):
1. What should be the immediate next step?
2. Which concept will have the most impact?
3. Should we focus on Python or TypeScript?
4. How to address the MCP gap?

Provide actionable recommendations.
    `;

    return this.processKnowledgeQuery(prompt);
  }
}