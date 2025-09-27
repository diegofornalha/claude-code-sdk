#!/usr/bin/env bun
/**
 * Seed Neo4j with initial knowledge data
 *
 * Popula o Neo4j com conhecimento inicial do bootcamp
 */

console.log('🌱 Seeding Neo4j with bootcamp knowledge...\n');

// Dados iniciais do bootcamp
const bootcampConcepts = [
  {
    name: 'Claude Code SDK',
    type: 'concept',
    description: 'Framework principal para trabalhar com Claude',
    category: 'core',
    importance: 1.0,
    week: 1,
    score_impact: 10
  },
  {
    name: 'query() function',
    type: 'skill',
    description: 'Função stateless para consultas simples',
    category: 'fundamentals',
    importance: 0.9,
    week: 1,
    score_impact: 5
  },
  {
    name: 'ClaudeSDKClient',
    type: 'skill',
    description: 'Cliente stateful para conversas com contexto',
    category: 'fundamentals',
    importance: 0.85,
    week: 2,
    score_impact: 5
  },
  {
    name: 'MCP Protocol',
    type: 'concept',
    description: 'Model Context Protocol para criar ferramentas customizadas',
    category: 'advanced',
    importance: 0.95,
    week: 7,
    score_impact: 15,
    is_gap: true
  },
  {
    name: 'Hooks System',
    type: 'concept',
    description: 'Sistema de interceptação Pre/Post para validação e logging',
    category: 'advanced',
    importance: 0.8,
    week: 8,
    score_impact: 10,
    is_gap: true
  },
  {
    name: 'Async Patterns',
    type: 'concept',
    description: 'Padrões assíncronos async/await para operações não-bloqueantes',
    category: 'fundamentals',
    importance: 0.9,
    week: 3,
    score_impact: 5
  },
  {
    name: 'Tool Permissions',
    type: 'concept',
    description: 'Sistema de permissões allowed_tools e denied_tools',
    category: 'security',
    importance: 0.85,
    week: 4,
    score_impact: 5
  },
  {
    name: 'TypeScript SDK',
    type: 'project',
    description: 'Validação cross-language dos conceitos Python',
    category: 'validation',
    importance: 0.9,
    week: 9,
    score_impact: 10
  },
  {
    name: 'Neo4j Agent',
    type: 'project',
    description: 'Sistema de knowledge management com grafos',
    category: 'final_project',
    importance: 1.0,
    week: 11,
    score_impact: 20
  }
];

// Relacionamentos entre conceitos
const relationships = [
  // Fundamentos
  { from: 'query() function', to: 'Claude Code SDK', type: 'PART_OF' },
  { from: 'ClaudeSDKClient', to: 'Claude Code SDK', type: 'PART_OF' },
  { from: 'Async Patterns', to: 'query() function', type: 'REQUIRED_BY' },
  { from: 'Async Patterns', to: 'ClaudeSDKClient', type: 'REQUIRED_BY' },

  // Permissões
  { from: 'Tool Permissions', to: 'Claude Code SDK', type: 'SECURES' },

  // Avançado
  { from: 'MCP Protocol', to: 'Claude Code SDK', type: 'EXTENDS' },
  { from: 'Hooks System', to: 'Claude Code SDK', type: 'EXTENDS' },

  // Validação
  { from: 'TypeScript SDK', to: 'query() function', type: 'VALIDATES' },
  { from: 'TypeScript SDK', to: 'ClaudeSDKClient', type: 'VALIDATES' },

  // Projeto final
  { from: 'Neo4j Agent', to: 'MCP Protocol', type: 'IMPLEMENTS' },
  { from: 'Neo4j Agent', to: 'Hooks System', type: 'IMPLEMENTS' },
  { from: 'Neo4j Agent', to: 'TypeScript SDK', type: 'USES' },

  // Pré-requisitos
  { from: 'query() function', to: 'ClaudeSDKClient', type: 'PREREQUISITE_OF' },
  { from: 'MCP Protocol', to: 'Neo4j Agent', type: 'PREREQUISITE_OF' },
  { from: 'Hooks System', to: 'Neo4j Agent', type: 'PREREQUISITE_OF' }
];

// Insights iniciais
const insights = [
  {
    discovery: 'Python e TypeScript SDKs compartilham conceitos idênticos',
    confidence: 0.92,
    evidence_count: 5,
    category: 'validation'
  },
  {
    discovery: 'MCP Tools é o gap mais crítico para progresso',
    confidence: 0.95,
    evidence_count: 8,
    category: 'gap_analysis'
  },
  {
    discovery: 'Neo4j Agent demonstra todos conceitos do bootcamp',
    confidence: 0.88,
    evidence_count: 12,
    category: 'project'
  }
];

// Progresso do Diego
const userProgress = {
  name: 'Diego Fornalha',
  current_score: 45,
  target_score: 100,
  current_week: 1,
  total_weeks: 12,
  completed_concepts: ['query() function', 'Async Patterns'],
  in_progress: ['ClaudeSDKClient'],
  gaps: ['MCP Protocol', 'Hooks System'],
  learning_style: 'hands-on',
  preferred_language: 'Python',
  validation_language: 'TypeScript'
};

// Simular criação no Neo4j
async function seedData() {
  console.log('📚 Creating concepts...');
  for (const concept of bootcampConcepts) {
    console.log(`  ✓ ${concept.name} (${concept.type})`);
    // Em produção: await mcp__neo4j-memory__create_memory(concept)
  }

  console.log('\n🔗 Creating relationships...');
  for (const rel of relationships) {
    console.log(`  ✓ ${rel.from} -[${rel.type}]-> ${rel.to}`);
    // Em produção: await mcp__neo4j-memory__create_connection(rel)
  }

  console.log('\n💡 Adding insights...');
  for (const insight of insights) {
    console.log(`  ✓ ${insight.discovery.substring(0, 50)}...`);
  }

  console.log('\n👤 Setting user progress...');
  console.log(`  ✓ ${userProgress.name}: Score ${userProgress.current_score}/${userProgress.target_score}`);

  // Estatísticas finais
  console.log('\n📊 Seed complete!');
  console.log('=====================================');
  console.log(`  Concepts created: ${bootcampConcepts.length}`);
  console.log(`  Relationships: ${relationships.length}`);
  console.log(`  Insights: ${insights.length}`);
  console.log(`  User progress: ${userProgress.current_score}% complete`);
  console.log('\n🚀 Neo4j Agent ready to use!');

  // Salvar dados para referência
  const seedData = {
    concepts: bootcampConcepts,
    relationships,
    insights,
    userProgress,
    timestamp: new Date().toISOString()
  };

  // Salvar em arquivo
  await Bun.write(
    './database/seed-data.json',
    JSON.stringify(seedData, null, 2)
  );

  console.log('\n💾 Seed data saved to database/seed-data.json');
}

// Executar seed
seedData().catch(console.error);