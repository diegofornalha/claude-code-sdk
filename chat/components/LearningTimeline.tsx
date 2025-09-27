import React, { useState } from 'react';
import { useBootcampStore } from '../store/bootcampStore';

interface TimelineEvent {
  id: string;
  week: number;
  date: string;
  title: string;
  description: string;
  type: 'milestone' | 'concept' | 'gap' | 'exercise' | 'achievement';
  status: 'completed' | 'current' | 'upcoming';
  scoreImpact?: number;
  concepts?: string[];
  resources?: string[];
}

export const LearningTimeline: React.FC = () => {
  const { progress, learningPath } = useBootcampStore();
  const [expandedWeek, setExpandedWeek] = useState<number | null>(progress.current_week);

  // Gerar eventos da timeline baseado no progresso
  const generateTimelineEvents = (): TimelineEvent[] => {
    const events: TimelineEvent[] = [];

    // Semanas já completadas
    for (let week = 1; week < progress.current_week; week++) {
      events.push({
        id: `week-${week}`,
        week,
        date: `Semana ${week}`,
        title: getWeekTitle(week),
        description: getWeekDescription(week),
        type: 'milestone',
        status: 'completed',
        scoreImpact: 5,
        concepts: getWeekConcepts(week)
      });
    }

    // Semana atual
    events.push({
      id: `week-${progress.current_week}`,
      week: progress.current_week,
      date: `Semana ${progress.current_week} (ATUAL)`,
      title: getWeekTitle(progress.current_week),
      description: `Em progresso: ${progress.completed_concepts.length} conceitos completos`,
      type: 'milestone',
      status: 'current',
      scoreImpact: 10,
      concepts: progress.completed_concepts,
      resources: ['CONCEITOS/', 'exercicios_praticos_pt_br.py']
    });

    // Próximas semanas
    for (let week = progress.current_week + 1; week <= 12; week++) {
      events.push({
        id: `week-${week}`,
        week,
        date: `Semana ${week}`,
        title: getWeekTitle(week),
        description: getWeekDescription(week),
        type: 'milestone',
        status: 'upcoming',
        scoreImpact: getWeekScoreImpact(week),
        concepts: getWeekConcepts(week)
      });
    }

    // Adicionar gaps como eventos críticos
    progress.gaps.forEach(gap => {
      events.push({
        id: `gap-${gap}`,
        week: progress.current_week,
        date: 'URGENTE',
        title: `⚠️ Gap: ${gap}`,
        description: 'Precisa ser resolvido para continuar progresso',
        type: 'gap',
        status: 'current',
        scoreImpact: 15,
        resources: gap === 'MCP Protocol' ?
          ['gap_1_mcp_tools_tutorial.py'] :
          ['gap_2_hooks_tutorial.py']
      });
    });

    return events.sort((a, b) => a.week - b.week);
  };

  const getWeekTitle = (week: number): string => {
    const titles: { [key: number]: string } = {
      1: 'Fundamentos do SDK',
      2: 'Query e Async Patterns',
      3: 'ClaudeCodeOptions',
      4: 'Ferramentas Nativas',
      5: 'MCP Tools',
      6: 'Hooks System',
      7: 'Cliente Stateful',
      8: 'Streaming e Real-time',
      9: 'Multi-Agent',
      10: 'Projetos Práticos',
      11: 'Otimização',
      12: 'Projeto Final'
    };
    return titles[week] || `Semana ${week}`;
  };

  const getWeekDescription = (week: number): string => {
    const descriptions: { [key: number]: string } = {
      1: 'Introdução ao Claude Code SDK e configuração',
      2: 'Dominando query() e padrões assíncronos',
      3: 'Configurações avançadas e otimização',
      4: 'File, Search, System tools',
      5: 'Criando e usando MCP Tools customizadas',
      6: 'Interceptando e controlando execução',
      7: 'Sessions, contexto e persistência',
      8: 'Respostas em streaming e WebSockets',
      9: 'Orquestração com Task tool',
      10: 'Aplicações práticas completas',
      11: 'Performance e best practices',
      12: 'Projeto de graduação'
    };
    return descriptions[week] || '';
  };

  const getWeekConcepts = (week: number): string[] => {
    const concepts: { [key: number]: string[] } = {
      1: ['query()', 'ClaudeCodeOptions', 'async/await'],
      2: ['Async generators', 'Error handling', 'Retry patterns'],
      3: ['temperature', 'allowed_tools', 'system_prompt'],
      4: ['Read/Write', 'Grep/Glob', 'Bash'],
      5: ['@tool decorator', 'input_schema', 'MCP protocol'],
      6: ['HookMatcher', 'PreToolUse', 'PostToolUse'],
      7: ['ClaudeSDKClient', 'send_message()', 'receive_response()'],
      8: ['Streaming', 'WebSocket', 'Real-time updates'],
      9: ['Task tool', 'Subagents', 'Orchestration'],
      10: ['Full applications', 'Integration patterns'],
      11: ['Caching', 'Optimization', 'Monitoring'],
      12: ['Final project', 'Presentation', 'Certification']
    };
    return concepts[week] || [];
  };

  const getWeekScoreImpact = (week: number): number => {
    if (week <= 3) return 5;
    if (week <= 6) return 10;
    if (week <= 9) return 8;
    return 7;
  };

  const getEventIcon = (type: string): string => {
    switch (type) {
      case 'milestone': return '🎯';
      case 'concept': return '📚';
      case 'gap': return '⚠️';
      case 'exercise': return '💪';
      case 'achievement': return '🏆';
      default: return '📍';
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'completed': return '#28a745';
      case 'current': return '#667eea';
      case 'upcoming': return '#dee2e6';
      default: return '#6c757d';
    }
  };

  const events = generateTimelineEvents();

  return (
    <div className="learning-timeline">
      <div className="timeline-header">
        <h2>📅 Linha do Tempo do Bootcamp</h2>
        <div className="timeline-progress">
          <div className="progress-info">
            <span>Semana {progress.current_week} de {progress.total_weeks}</span>
            <span className="score">Score: {progress.current_score}/100</span>
          </div>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${(progress.current_week / progress.total_weeks) * 100}%` }}
            />
          </div>
        </div>
      </div>

      <div className="timeline-container">
        <div className="timeline-line" />

        {events.map((event, index) => (
          <div
            key={event.id}
            className={`timeline-event ${event.status} ${event.type}`}
            style={{ borderColor: getStatusColor(event.status) }}
          >
            <div className="event-marker" style={{ background: getStatusColor(event.status) }}>
              {event.status === 'current' && <span className="pulse" />}
            </div>

            <div className="event-content">
              <div
                className="event-header"
                onClick={() => setExpandedWeek(
                  expandedWeek === event.week ? null : event.week
                )}
              >
                <span className="event-icon">{getEventIcon(event.type)}</span>
                <div className="event-title">
                  <h3>{event.title}</h3>
                  <span className="event-date">{event.date}</span>
                </div>
                {event.scoreImpact && (
                  <span className="score-impact">+{event.scoreImpact} pts</span>
                )}
              </div>

              <p className="event-description">{event.description}</p>

              {expandedWeek === event.week && (
                <div className="event-details">
                  {event.concepts && event.concepts.length > 0 && (
                    <div className="detail-section">
                      <h4>📚 Conceitos:</h4>
                      <div className="concept-list">
                        {event.concepts.map(concept => (
                          <span key={concept} className="concept-badge">
                            {concept}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {event.resources && event.resources.length > 0 && (
                    <div className="detail-section">
                      <h4>📖 Recursos:</h4>
                      <ul className="resource-list">
                        {event.resources.map(resource => (
                          <li key={resource}>{resource}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {event.status === 'current' && (
                    <div className="action-buttons">
                      <button className="action-btn primary">
                        Continuar Estudando →
                      </button>
                      <button className="action-btn secondary">
                        Ver Exercícios
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>

            {event.type === 'gap' && (
              <div className="gap-alert">
                <span>⚡ Resolver urgentemente para desbloquear progresso!</span>
              </div>
            )}
          </div>
        ))}

        <div className="timeline-end">
          <div className="end-marker">🎓</div>
          <h3>Certificação Claude Code SDK Expert</h3>
          <p>Score 100/100 - Domínio completo do SDK</p>
        </div>
      </div>

      <style jsx>{`
        .learning-timeline {
          padding: 20px;
          max-width: 1000px;
          margin: 0 auto;
        }

        .timeline-header {
          text-align: center;
          margin-bottom: 40px;
        }

        .timeline-header h2 {
          color: #495057;
          margin-bottom: 20px;
        }

        .timeline-progress {
          background: white;
          padding: 20px;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .progress-info {
          display: flex;
          justify-content: space-between;
          margin-bottom: 10px;
          color: #495057;
        }

        .score {
          font-weight: bold;
          color: #667eea;
        }

        .progress-bar {
          height: 8px;
          background: #e9ecef;
          border-radius: 4px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
          transition: width 0.3s;
        }

        .timeline-container {
          position: relative;
          padding-left: 40px;
        }

        .timeline-line {
          position: absolute;
          left: 20px;
          top: 0;
          bottom: 0;
          width: 2px;
          background: #dee2e6;
        }

        .timeline-event {
          position: relative;
          margin-bottom: 30px;
          background: white;
          border-radius: 12px;
          padding: 20px;
          border-left: 4px solid;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          transition: transform 0.3s, box-shadow 0.3s;
        }

        .timeline-event:hover {
          transform: translateX(4px);
          box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }

        .event-marker {
          position: absolute;
          left: -44px;
          width: 16px;
          height: 16px;
          border-radius: 50%;
          border: 3px solid white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }

        .event-marker .pulse {
          position: absolute;
          top: -8px;
          left: -8px;
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: #667eea;
          opacity: 0.4;
          animation: pulse 2s infinite;
        }

        @keyframes pulse {
          0% {
            transform: scale(0.8);
            opacity: 0.4;
          }
          50% {
            transform: scale(1.2);
            opacity: 0.2;
          }
          100% {
            transform: scale(0.8);
            opacity: 0.4;
          }
        }

        .event-header {
          display: flex;
          align-items: center;
          gap: 12px;
          cursor: pointer;
          margin-bottom: 10px;
        }

        .event-icon {
          font-size: 24px;
        }

        .event-title {
          flex: 1;
        }

        .event-title h3 {
          margin: 0;
          color: #495057;
          font-size: 18px;
        }

        .event-date {
          font-size: 12px;
          color: #6c757d;
        }

        .score-impact {
          background: #28a745;
          color: white;
          padding: 4px 12px;
          border-radius: 12px;
          font-size: 14px;
          font-weight: 600;
        }

        .event-description {
          color: #6c757d;
          margin: 10px 0;
        }

        .event-details {
          margin-top: 20px;
          padding-top: 20px;
          border-top: 1px solid #e9ecef;
        }

        .detail-section {
          margin-bottom: 20px;
        }

        .detail-section h4 {
          color: #495057;
          margin-bottom: 10px;
          font-size: 14px;
        }

        .concept-list {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .concept-badge {
          background: #f0f2f5;
          padding: 4px 12px;
          border-radius: 12px;
          font-size: 12px;
          color: #495057;
        }

        .resource-list {
          margin: 0;
          padding-left: 20px;
          color: #6c757d;
          font-size: 14px;
        }

        .action-buttons {
          display: flex;
          gap: 10px;
          margin-top: 20px;
        }

        .action-btn {
          padding: 10px 20px;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 600;
          transition: all 0.3s;
        }

        .action-btn.primary {
          background: #667eea;
          color: white;
        }

        .action-btn.primary:hover {
          background: #764ba2;
        }

        .action-btn.secondary {
          background: #f0f2f5;
          color: #495057;
        }

        .action-btn.secondary:hover {
          background: #dee2e6;
        }

        .gap-alert {
          background: #fff3cd;
          border-radius: 8px;
          padding: 10px;
          margin-top: 15px;
          text-align: center;
          color: #856404;
          font-size: 14px;
          font-weight: 600;
        }

        .timeline-end {
          text-align: center;
          padding: 30px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border-radius: 12px;
          margin-top: 40px;
        }

        .end-marker {
          font-size: 48px;
          margin-bottom: 10px;
        }

        .timeline-end h3 {
          margin: 10px 0;
          color: white;
        }

        .timeline-end p {
          opacity: 0.9;
        }

        .timeline-event.gap {
          border-left-color: #dc3545 !important;
          background: #fff5f5;
        }

        .timeline-event.current {
          border-left-width: 6px;
        }

        .timeline-event.completed {
          opacity: 0.8;
        }
      `}</style>
    </div>
  );
};