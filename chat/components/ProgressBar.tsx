import React from 'react';
import { useBootcampStore } from '../store/bootcampStore';

interface Milestone {
  score: number;
  label: string;
  description: string;
  icon: string;
}

export const ProgressBar: React.FC = () => {
  const { progress } = useBootcampStore();

  const milestones: Milestone[] = [
    { score: 0, label: 'Iniciante', description: 'Começando a jornada', icon: '🌱' },
    { score: 40, label: 'Básico', description: 'Fundamentos sólidos', icon: '🌿' },
    { score: 60, label: 'Intermediário', description: 'MCP Tools dominado', icon: '🌳' },
    { score: 75, label: 'Avançado', description: 'Hooks e Client', icon: '🚀' },
    { score: 90, label: 'Expert', description: 'Pronto para produção', icon: '⭐' },
    { score: 100, label: 'Master', description: 'Claude Code SDK Bootcamp Expert', icon: '🏆' }
  ];

  const getCurrentMilestone = () => {
    return milestones.filter(m => m.score <= progress.current_score).pop() || milestones[0];
  };

  const getNextMilestone = () => {
    return milestones.find(m => m.score > progress.current_score) || milestones[milestones.length - 1];
  };

  const currentMilestone = getCurrentMilestone();
  const nextMilestone = getNextMilestone();
  const progressPercentage = (progress.current_score / progress.target_score) * 100;

  // Calcular dias estimados
  const weeksRemaining = progress.total_weeks - progress.current_week;
  const averageScorePerWeek = progress.current_score / progress.current_week;
  const estimatedWeeksToTarget = Math.ceil((progress.target_score - progress.current_score) / averageScorePerWeek);

  return (
    <div className="progress-bar-container">
      <div className="progress-header">
        <h3>📊 Progresso no Sistema</h3>
        <div className="user-info">
          <span className="user-name">User</span>
          <span className="current-level">{currentMilestone.icon} {currentMilestone.label}</span>
        </div>
      </div>

      <div className="score-display">
        <div className="current-score">
          <span className="score-number">{progress.current_score}</span>
          <span className="score-label">Score Atual</span>
        </div>
        <div className="score-arrow">→</div>
        <div className="target-score">
          <span className="score-number">{progress.target_score}</span>
          <span className="score-label">Meta</span>
        </div>
      </div>

      <div className="progress-track">
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${progressPercentage}%` }}
          >
            <span className="progress-percentage">{Math.round(progressPercentage)}%</span>
          </div>
        </div>

        <div className="milestones">
          {milestones.map((milestone) => {
            const position = (milestone.score / 100) * 100;
            const isPassed = milestone.score <= progress.current_score;
            const isCurrent = milestone === currentMilestone;

            return (
              <div
                key={milestone.score}
                className={`milestone ${isPassed ? 'passed' : ''} ${isCurrent ? 'current' : ''}`}
                style={{ left: `${position}%` }}
              >
                <div className="milestone-marker">
                  <span className="milestone-icon">{milestone.icon}</span>
                </div>
                <div className="milestone-info">
                  <span className="milestone-score">{milestone.score}</span>
                  <span className="milestone-label">{milestone.label}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="progress-details">
        <div className="detail-card">
          <h4>📅 Tempo</h4>
          <p>Semana {progress.current_week} de {progress.total_weeks}</p>
          <span className="detail-sub">
            {weeksRemaining} semanas restantes
          </span>
        </div>

        <div className="detail-card">
          <h4>🎯 Próximo Marco</h4>
          <p>{nextMilestone.label} ({nextMilestone.score} pts)</p>
          <span className="detail-sub">
            Faltam {nextMilestone.score - progress.current_score} pontos
          </span>
        </div>

        <div className="detail-card">
          <h4>⚡ Velocidade</h4>
          <p>{averageScorePerWeek.toFixed(1)} pts/semana</p>
          <span className="detail-sub">
            ETA: {estimatedWeeksToTarget} semanas
          </span>
        </div>
      </div>

      <div className="concepts-section">
        <div className="completed-concepts">
          <h4>✅ Conceitos Dominados ({progress.completed_concepts.length})</h4>
          <div className="concept-list">
            {progress.completed_concepts.map(concept => (
              <span key={concept} className="concept-tag completed">
                {concept}
              </span>
            ))}
          </div>
        </div>

        <div className="gap-concepts">
          <h4>⚠️ Gaps Críticos ({progress.gaps.length})</h4>
          <div className="concept-list">
            {progress.gaps.map(gap => (
              <span key={gap} className="concept-tag gap">
                {gap}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="next-steps">
        <h4>🚀 Próximos Passos</h4>
        <div className="step-cards">
          <div className="step-card urgent">
            <span className="step-icon">🔥</span>
            <div className="step-content">
              <strong>Urgente: Resolver Gap MCP Protocol</strong>
              <p>Tutorial em gap_1_mcp_tools_tutorial.py</p>
              <span className="impact">+15 pontos</span>
            </div>
          </div>

          <div className="step-card">
            <span className="step-icon">📚</span>
            <div className="step-content">
              <strong>Continuar Exercício 1</strong>
              <p>query() function básica</p>
              <span className="impact">+5 pontos</span>
            </div>
          </div>

          <div className="step-card">
            <span className="step-icon">🎯</span>
            <div className="step-content">
              <strong>Meta: {progress.next_milestone}</strong>
              <p>Desbloquear ferramentas avançadas</p>
              <span className="impact">Score 60</span>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .progress-bar-container {
          padding: 30px;
          background: white;
          border-radius: 16px;
          box-shadow: 0 4px 16px rgba(0,0,0,0.1);
          max-width: 1200px;
          margin: 0 auto;
        }

        .progress-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 30px;
        }

        .progress-header h3 {
          margin: 0;
          color: #495057;
        }

        .user-info {
          display: flex;
          gap: 20px;
          align-items: center;
        }

        .user-name {
          font-weight: 600;
          color: #495057;
        }

        .current-level {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          padding: 6px 16px;
          border-radius: 20px;
          font-size: 14px;
          font-weight: 600;
        }

        .score-display {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 30px;
          margin-bottom: 40px;
        }

        .current-score, .target-score {
          text-align: center;
        }

        .score-number {
          display: block;
          font-size: 48px;
          font-weight: bold;
          color: #495057;
        }

        .current-score .score-number {
          color: #667eea;
        }

        .target-score .score-number {
          color: #28a745;
        }

        .score-label {
          display: block;
          margin-top: 5px;
          color: #6c757d;
          font-size: 14px;
        }

        .score-arrow {
          font-size: 32px;
          color: #dee2e6;
        }

        .progress-track {
          position: relative;
          margin-bottom: 60px;
        }

        .progress-bar {
          height: 24px;
          background: #e9ecef;
          border-radius: 12px;
          overflow: hidden;
          position: relative;
        }

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
          transition: width 0.5s ease;
          display: flex;
          align-items: center;
          justify-content: flex-end;
          padding-right: 10px;
        }

        .progress-percentage {
          color: white;
          font-weight: bold;
          font-size: 14px;
        }

        .milestones {
          position: relative;
          height: 80px;
          margin-top: 20px;
        }

        .milestone {
          position: absolute;
          transform: translateX(-50%);
          text-align: center;
          transition: all 0.3s;
        }

        .milestone-marker {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: white;
          border: 3px solid #dee2e6;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 5px;
        }

        .milestone.passed .milestone-marker {
          border-color: #28a745;
          background: #d4edda;
        }

        .milestone.current .milestone-marker {
          border-color: #667eea;
          background: #e8eaf6;
          box-shadow: 0 0 0 8px rgba(102, 126, 234, 0.1);
        }

        .milestone-icon {
          font-size: 20px;
        }

        .milestone-info {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }

        .milestone-score {
          font-size: 12px;
          color: #6c757d;
        }

        .milestone-label {
          font-size: 11px;
          font-weight: 600;
          color: #495057;
        }

        .progress-details {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 20px;
          margin-bottom: 30px;
        }

        .detail-card {
          background: #f8f9fa;
          padding: 20px;
          border-radius: 12px;
          text-align: center;
        }

        .detail-card h4 {
          margin: 0 0 10px;
          color: #495057;
          font-size: 16px;
        }

        .detail-card p {
          margin: 0;
          font-size: 20px;
          font-weight: bold;
          color: #667eea;
        }

        .detail-sub {
          display: block;
          margin-top: 5px;
          font-size: 12px;
          color: #6c757d;
        }

        .concepts-section {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
          margin-bottom: 30px;
        }

        .completed-concepts, .gap-concepts {
          background: #f8f9fa;
          padding: 20px;
          border-radius: 12px;
        }

        .concepts-section h4 {
          margin: 0 0 15px;
          color: #495057;
          font-size: 16px;
        }

        .concept-list {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .concept-tag {
          padding: 6px 12px;
          border-radius: 16px;
          font-size: 13px;
          font-weight: 500;
        }

        .concept-tag.completed {
          background: #d4edda;
          color: #155724;
        }

        .concept-tag.gap {
          background: #f8d7da;
          color: #721c24;
        }

        .next-steps {
          background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
          padding: 25px;
          border-radius: 12px;
        }

        .next-steps h4 {
          margin: 0 0 20px;
          color: #495057;
        }

        .step-cards {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 15px;
        }

        .step-card {
          background: white;
          padding: 15px;
          border-radius: 10px;
          display: flex;
          gap: 15px;
          align-items: start;
          transition: transform 0.3s, box-shadow 0.3s;
        }

        .step-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        .step-card.urgent {
          border-left: 4px solid #dc3545;
        }

        .step-icon {
          font-size: 24px;
        }

        .step-content {
          flex: 1;
        }

        .step-content strong {
          display: block;
          margin-bottom: 5px;
          color: #495057;
        }

        .step-content p {
          margin: 0;
          font-size: 14px;
          color: #6c757d;
        }

        .impact {
          display: inline-block;
          margin-top: 8px;
          padding: 4px 8px;
          background: #e8eaf6;
          color: #667eea;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 600;
        }
      `}</style>
    </div>
  );
};