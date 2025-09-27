import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { KnowledgeNode, Relationship, BootcampProgress, GapAnalysis, LearningPath } from '../../ccsdk/types';

interface KnowledgeContextType {
  // Estado
  nodes: KnowledgeNode[];
  relationships: Relationship[];
  progress: BootcampProgress;
  gaps: GapAnalysis | null;
  learningPath: LearningPath | null;
  isConnected: boolean;
  loading: boolean;
  error: string | null;

  // Ações
  fetchKnowledge: () => Promise<void>;
  createNode: (node: Partial<KnowledgeNode>) => Promise<void>;
  updateNode: (id: string, updates: Partial<KnowledgeNode>) => Promise<void>;
  deleteNode: (id: string) => Promise<void>;
  createRelationship: (rel: Relationship) => Promise<void>;
  analyzeGaps: () => Promise<void>;
  generateLearningPath: () => Promise<void>;
  syncWithNeo4j: () => Promise<void>;
  searchNodes: (query: string) => Promise<KnowledgeNode[]>;
  updateProgress: (updates: Partial<BootcampProgress>) => void;
}

const KnowledgeContext = createContext<KnowledgeContextType | undefined>(undefined);

export const useKnowledge = () => {
  const context = useContext(KnowledgeContext);
  if (!context) {
    throw new Error('useKnowledge must be used within a KnowledgeProvider');
  }
  return context;
};

interface KnowledgeProviderProps {
  children: ReactNode;
}

export const KnowledgeProvider: React.FC<KnowledgeProviderProps> = ({ children }) => {
  const [nodes, setNodes] = useState<KnowledgeNode[]>([]);
  const [relationships, setRelationships] = useState<Relationship[]>([]);
  const [progress, setProgress] = useState<BootcampProgress>({
    current_score: 45,
    target_score: 100,
    current_week: 1,
    total_weeks: 12,
    completed_concepts: ['query() function', 'Async Patterns'],
    gaps: ['MCP Protocol', 'Hooks System'],
    next_milestone: 'MCP Tools (Score 60)'
  });
  const [gaps, setGaps] = useState<GapAnalysis | null>(null);
  const [learningPath, setLearningPath] = useState<LearningPath | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // WebSocket para sincronização real-time
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:4000');

    ws.onopen = () => {
      console.log('✅ Connected to Knowledge Graph');
      setIsConnected(true);
      ws.send(JSON.stringify({ type: 'sync_request' }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    ws.onclose = () => {
      console.log('❌ Disconnected from Knowledge Graph');
      setIsConnected(false);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Connection error with Knowledge Graph');
    };

    return () => {
      ws.close();
    };
  }, []);

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'knowledge_update':
        setNodes(data.nodes || []);
        setRelationships(data.relationships || []);
        break;

      case 'progress_update':
        setProgress(data.progress);
        break;

      case 'gaps_analysis':
        setGaps(data.gaps);
        break;

      case 'learning_path':
        setLearningPath(data.path);
        break;

      case 'error':
        setError(data.message);
        break;

      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const fetchKnowledge = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:4000/api/knowledge');
      if (!response.ok) throw new Error('Failed to fetch knowledge');

      const data = await response.json();
      setNodes(data.nodes || []);
      setRelationships(data.relationships || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch knowledge');
    } finally {
      setLoading(false);
    }
  };

  const createNode = async (node: Partial<KnowledgeNode>) => {
    try {
      const response = await fetch('http://localhost:4000/api/knowledge/node', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(node)
      });

      if (!response.ok) throw new Error('Failed to create node');

      const newNode = await response.json();
      setNodes(prev => [...prev, newNode]);

      // Atualizar progresso se for conceito do bootcamp
      if (newNode.properties.bootcamp_related) {
        updateProgress({
          current_score: progress.current_score + (newNode.properties.score_impact || 5)
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create node');
    }
  };

  const updateNode = async (id: string, updates: Partial<KnowledgeNode>) => {
    try {
      const response = await fetch(`http://localhost:4000/api/knowledge/node/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });

      if (!response.ok) throw new Error('Failed to update node');

      const updatedNode = await response.json();
      setNodes(prev => prev.map(n => n.id === id ? updatedNode : n));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update node');
    }
  };

  const deleteNode = async (id: string) => {
    try {
      const response = await fetch(`http://localhost:4000/api/knowledge/node/${id}`, {
        method: 'DELETE'
      });

      if (!response.ok) throw new Error('Failed to delete node');

      setNodes(prev => prev.filter(n => n.id !== id));
      setRelationships(prev => prev.filter(r => r.from !== id && r.to !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete node');
    }
  };

  const createRelationship = async (rel: Relationship) => {
    try {
      const response = await fetch('http://localhost:4000/api/knowledge/relationship', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(rel)
      });

      if (!response.ok) throw new Error('Failed to create relationship');

      const newRel = await response.json();
      setRelationships(prev => [...prev, newRel]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create relationship');
    }
  };

  const analyzeGaps = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:4000/api/bootcamp/gaps');
      if (!response.ok) throw new Error('Failed to analyze gaps');

      const gapsData = await response.json();
      setGaps(gapsData);

      // Atualizar gaps no progresso
      if (gapsData.gaps) {
        const gapNames = gapsData.gaps.map((g: any) => g.name);
        updateProgress({ gaps: gapNames });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze gaps');
    } finally {
      setLoading(false);
    }
  };

  const generateLearningPath = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:4000/api/bootcamp/learning-path', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          currentScore: progress.current_score,
          targetScore: progress.target_score,
          weeksAvailable: progress.total_weeks - progress.current_week,
          gaps: progress.gaps
        })
      });

      if (!response.ok) throw new Error('Failed to generate learning path');

      const path = await response.json();
      setLearningPath(path);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate learning path');
    } finally {
      setLoading(false);
    }
  };

  const syncWithNeo4j = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:4000/api/knowledge/sync', {
        method: 'POST'
      });

      if (!response.ok) throw new Error('Failed to sync with Neo4j');

      const data = await response.json();
      setNodes(data.nodes || []);
      setRelationships(data.relationships || []);

      console.log('✅ Synced with Neo4j:', {
        nodes: data.nodes?.length || 0,
        relationships: data.relationships?.length || 0
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to sync with Neo4j');
    } finally {
      setLoading(false);
    }
  };

  const searchNodes = async (query: string): Promise<KnowledgeNode[]> => {
    try {
      const response = await fetch(`http://localhost:4000/api/knowledge/search?q=${encodeURIComponent(query)}`);
      if (!response.ok) throw new Error('Search failed');

      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      return [];
    }
  };

  const updateProgress = (updates: Partial<BootcampProgress>) => {
    setProgress(prev => {
      const newProgress = { ...prev, ...updates };

      // Enviar atualização via WebSocket
      if (isConnected) {
        const ws = new WebSocket('ws://localhost:4000');
        ws.onopen = () => {
          ws.send(JSON.stringify({
            type: 'update_progress',
            progress: newProgress
          }));
          ws.close();
        };
      }

      return newProgress;
    });
  };

  const value: KnowledgeContextType = {
    nodes,
    relationships,
    progress,
    gaps,
    learningPath,
    isConnected,
    loading,
    error,
    fetchKnowledge,
    createNode,
    updateNode,
    deleteNode,
    createRelationship,
    analyzeGaps,
    generateLearningPath,
    syncWithNeo4j,
    searchNodes,
    updateProgress
  };

  return (
    <KnowledgeContext.Provider value={value}>
      {children}
    </KnowledgeContext.Provider>
  );
};