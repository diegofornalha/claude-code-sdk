import { create } from 'zustand';

interface Concept {
  id: string;
  name: string;
  type: 'concept' | 'skill' | 'insight' | 'project' | 'gap';
  completed: boolean;
  scoreImpact: number;
  week: number;
}

interface BootcampStore {
  // Estado do bootcamp
  score: number;
  targetScore: number;
  week: number;
  totalWeeks: number;

  // Conceitos e gaps
  concepts: Concept[];
  gaps: string[];
  completedConcepts: string[];

  // Usuário
  userName: string;
  userEmail: string;

  // Ações
  updateProgress: (progress: any) => void;
  completeConcept: (conceptId: string) => void;
  addGap: (gap: string) => void;
  resolveGap: (gap: string) => void;
  incrementScore: (points: number) => void;
  setWeek: (week: number) => void;
}

export const useBootcampStore = create<BootcampStore>((set, get) => ({
  // Estado inicial
  score: 45,
  targetScore: 100,
  week: 1,
  totalWeeks: 12,

  concepts: [
    {
      id: 'query-function',
      name: 'query() function',
      type: 'skill',
      completed: true,
      scoreImpact: 5,
      week: 1
    },
    {
      id: 'async-patterns',
      name: 'Async Patterns',
      type: 'concept',
      completed: true,
      scoreImpact: 5,
      week: 1
    },
    {
      id: 'claude-sdk-client',
      name: 'ClaudeSDKClient',
      type: 'skill',
      completed: false,
      scoreImpact: 5,
      week: 2
    },
    {
      id: 'mcp-protocol',
      name: 'MCP Protocol',
      type: 'gap',
      completed: false,
      scoreImpact: 15,
      week: 7
    },
    {
      id: 'hooks-system',
      name: 'Hooks System',
      type: 'gap',
      completed: false,
      scoreImpact: 10,
      week: 8
    }
  ],

  gaps: ['MCP Protocol', 'Hooks System'],
  completedConcepts: ['query() function', 'Async Patterns'],

  userName: 'User',
  userEmail: 'user@example.com',

  // Ações
  updateProgress: (progress) => set((state) => ({
    score: progress.current_score || state.score,
    week: progress.current_week || state.week,
    completedConcepts: progress.completed_concepts || state.completedConcepts,
    gaps: progress.gaps || state.gaps
  })),

  completeConcept: (conceptId) => set((state) => {
    const concept = state.concepts.find(c => c.id === conceptId);
    if (!concept || concept.completed) return state;

    const newConcepts = state.concepts.map(c =>
      c.id === conceptId ? { ...c, completed: true } : c
    );

    const newCompletedConcepts = [...state.completedConcepts, concept.name];
    const newScore = state.score + concept.scoreImpact;

    // Remover gap se foi resolvido
    const newGaps = concept.type === 'gap'
      ? state.gaps.filter(g => g !== concept.name)
      : state.gaps;

    return {
      concepts: newConcepts,
      completedConcepts: newCompletedConcepts,
      score: Math.min(newScore, 100),
      gaps: newGaps
    };
  }),

  addGap: (gap) => set((state) => ({
    gaps: state.gaps.includes(gap) ? state.gaps : [...state.gaps, gap]
  })),

  resolveGap: (gap) => set((state) => ({
    gaps: state.gaps.filter(g => g !== gap)
  })),

  incrementScore: (points) => set((state) => ({
    score: Math.min(state.score + points, 100)
  })),

  setWeek: (week) => set({ week: Math.min(week, 12) })
}));