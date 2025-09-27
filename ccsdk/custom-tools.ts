/**
 * Custom MCP Tools para Neo4j Agent
 *
 * Define as ferramentas customizadas que Claude pode usar
 * para interagir com o grafo de conhecimento
 */

import { Tool } from '@anthropic-ai/claude-code';

/**
 * Tool para extrair conhecimento
 */
export const extractKnowledgeTool: Tool = {
  name: 'extract_knowledge',
  description: 'Extrai conceitos e relacionamentos de um texto',
  inputSchema: {
    type: 'object',
    properties: {
      text: {
        type: 'string',
        description: 'Texto para analisar'
      },
      context: {
        type: 'object',
        description: 'Contexto do bootcamp',
        properties: {
          currentScore: { type: 'number' },
          week: { type: 'number' },
          gaps: {
            type: 'array',
            items: { type: 'string' }
          }
        }
      }
    },
    required: ['text']
  },
  handler: async (args) => {
    // Extrair conceitos do texto
    const concepts = extractConcepts(args.text);
    const relationships = findRelationships(concepts);

    // Calcular impacto no bootcamp
    const bootcampImpact = calculateImpact(concepts, args.context);

    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          concepts,
          relationships,
          bootcampImpact
        })
      }]
    };
  }
};

/**
 * Tool para analisar gaps
 */
export const analyzeGapsTool: Tool = {
  name: 'analyze_gaps',
  description: 'Analisa gaps de conhecimento no bootcamp',
  inputSchema: {
    type: 'object',
    properties: {
      userId: {
        type: 'string',
        description: 'ID do usuário'
      }
    }
  },
  handler: async (args) => {
    // Gaps críticos do bootcamp
    const gaps = [
      {
        name: 'MCP Protocol',
        urgency: 'CRITICAL',
        scoreImpact: 15,
        blockedConcepts: ['Neo4j Agent', 'Custom Tools'],
        resources: [
          'CONCEITOS/04_mcp_protocol.md',
          'examples/gap_1_mcp_tools_tutorial.py'
        ]
      },
      {
        name: 'Hooks System',
        urgency: 'HIGH',
        scoreImpact: 10,
        blockedConcepts: ['Production Code', 'Validation'],
        resources: [
          'CONCEITOS/05_hook_system.md',
          'examples/gap_2_hooks_tutorial.py'
        ]
      }
    ];

    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          gaps,
          totalImpact: 25,
          recommendation: 'Focar em MCP Protocol primeiro'
        })
      }]
    };
  }
};

/**
 * Tool para gerar caminho de aprendizado
 */
export const learningPathTool: Tool = {
  name: 'generate_learning_path',
  description: 'Gera caminho otimizado de aprendizado',
  inputSchema: {
    type: 'object',
    properties: {
      currentScore: {
        type: 'number',
        description: 'Score atual'
      },
      targetScore: {
        type: 'number',
        description: 'Score alvo'
      },
      availableWeeks: {
        type: 'number',
        description: 'Semanas disponíveis'
      }
    },
    required: ['currentScore', 'targetScore']
  },
  handler: async (args) => {
    const path = [];
    let currentScore = args.currentScore;

    // Caminho otimizado para Score 100
    if (currentScore < 60) {
      path.push({
        step: 'Fundamentos',
        concepts: ['ClaudeSDKClient', 'Tool Permissions'],
        scoreGain: 15,
        weeks: 2
      });
      currentScore += 15;
    }

    if (currentScore < 75) {
      path.push({
        step: 'MCP Protocol',
        concepts: ['MCP Tools', 'Custom Tools', 'Return Format'],
        scoreGain: 15,
        weeks: 2
      });
      currentScore += 15;
    }

    if (currentScore < 85) {
      path.push({
        step: 'Hooks System',
        concepts: ['Pre Hooks', 'Post Hooks', 'Validation'],
        scoreGain: 10,
        weeks: 1
      });
      currentScore += 10;
    }

    if (currentScore < 100) {
      path.push({
        step: 'Projeto Final',
        concepts: ['TypeScript Validation', 'Neo4j Agent'],
        scoreGain: 15,
        weeks: 3
      });
    }

    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          path,
          totalWeeks: path.reduce((sum, p) => sum + (p.weeks || 0), 0),
          finalScore: args.targetScore,
          feasible: true
        })
      }]
    };
  }
};

/**
 * Tool para sintetizar aprendizados
 */
export const synthesizeLearningTool: Tool = {
  name: 'synthesize_learning',
  description: 'Sintetiza e consolida aprendizados',
  inputSchema: {
    type: 'object',
    properties: {
      timeframe: {
        type: 'string',
        description: 'Período para sintetizar (week, month, all)'
      }
    }
  },
  handler: async (args) => {
    const synthesis = {
      period: args.timeframe || 'week',
      keyLearnings: [
        'Hackathon Flow Blockchain Agents é agnóstico de linguagem',
        'MCP permite ferramentas customizadas',
        'Python e TypeScript validam conhecimento'
      ],
      conceptsMastered: [
        'query() function',
        'Async patterns'
      ],
      conceptsInProgress: [
        'ClaudeSDKClient'
      ],
      gapsIdentified: [
        'MCP Protocol',
        'Hooks System'
      ],
      insights: [
        'Validação cruzada acelera aprendizado',
        'Conceitos agnósticos são mais importantes que sintaxe',
        'Neo4j é melhor que Gmail para aprender'
      ],
      nextActions: [
        'Estudar MCP Protocol',
        'Implementar primeira MCP tool',
        'Validar em TypeScript'
      ]
    };

    return {
      content: [{
        type: 'text',
        text: JSON.stringify(synthesis)
      }]
    };
  }
};

// Funções auxiliares
function extractConcepts(text: string): any[] {
  const concepts = [];
  const keywords = {
    'query': { type: 'skill', score: 5 },
    'MCP': { type: 'gap', score: 15 },
    'hooks': { type: 'gap', score: 10 },
    'async': { type: 'concept', score: 3 },
    'stateless': { type: 'concept', score: 3 },
    'stateful': { type: 'concept', score: 3 }
  };

  for (const [keyword, info] of Object.entries(keywords)) {
    if (text.toLowerCase().includes(keyword.toLowerCase())) {
      concepts.push({
        name: keyword,
        ...info,
        foundAt: text.toLowerCase().indexOf(keyword.toLowerCase())
      });
    }
  }

  return concepts;
}

function findRelationships(concepts: any[]): any[] {
  const relationships = [];

  for (let i = 0; i < concepts.length - 1; i++) {
    relationships.push({
      from: concepts[i].name,
      to: concepts[i + 1].name,
      type: 'RELATES_TO',
      strength: 0.7
    });
  }

  return relationships;
}

function calculateImpact(concepts: any[], context: any): any {
  const totalScore = concepts.reduce((sum, c) => sum + (c.score || 0), 0);
  const addressesGap = concepts.some(c => c.type === 'gap');

  return {
    scoreGain: totalScore,
    addressesGap,
    bringsToMilestone: (context?.currentScore || 45) + totalScore >= 60
  };
}

// Exportar todas as tools
export const customTools = [
  extractKnowledgeTool,
  analyzeGapsTool,
  learningPathTool,
  synthesizeLearningTool
];