/**
 * Types para o Neo4j Agent
 */

export interface KnowledgeNode {
  id: string;
  label: string;
  properties: {
    name: string;
    type: 'concept' | 'skill' | 'insight' | 'project' | 'gap';
    description: string;
    category?: string;
    importance?: number;
    bootcamp_related?: boolean;
    score_impact?: number;
    created_at: string;
    updated_at?: string;
    user?: string;
  };
}

export interface Relationship {
  from: string;
  to: string;
  type: string;
  properties?: Record<string, any>;
}

export interface BootcampProgress {
  current_score: number;
  target_score: number;
  current_week: number;
  total_weeks: number;
  completed_concepts: string[];
  gaps: string[];
  next_milestone: string;
}

export interface LearningPath {
  steps: Array<{
    name: string;
    concepts: string[];
    scoreGain: number;
    weeks: number;
  }>;
  totalWeeks: number;
  finalScore: number;
  feasible: boolean;
}

export interface GapAnalysis {
  gaps: Array<{
    name: string;
    urgency: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
    scoreImpact: number;
    blockedConcepts: string[];
    resources: string[];
  }>;
  totalImpact: number;
  recommendation: string;
}

export interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface WebSocketMessage {
  type: string;
  payload?: any;
  error?: string;
}