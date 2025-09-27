import React, { useEffect, useState } from 'react';
import { useBootcampStore } from '../store/bootcampStore';

interface Insight {
  id: string;
  title: string;
  description: string;
  type: 'pattern' | 'recommendation' | 'warning' | 'achievement';
  impact: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
  source?: string;
  actionable?: boolean;
  relatedConcepts?: string[];
}

export const InsightDashboard: React.FC = () => {
  const { insights, generateInsights, progress } = useBootcampStore();
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<'all' | 'critical' | 'actionable'>('all');

  useEffect(() => {
    handleGenerateInsights();
  }, [progress.current_score]);

  const handleGenerateInsights = async () => {
    setLoading(true);
    await generateInsights();
    setLoading(false);
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'pattern': return '🔍';
      case 'recommendation': return '💡';
      case 'warning': return '⚠️';
      case 'achievement': return '🏆';
      default: return '📊';
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'critical': return '#dc3545';
      case 'high': return '#ff6b6b';
      case 'medium': return '#ffc107';
      case 'low': return '#28a745';
      default: return '#6c757d';
    }
  };

  const filteredInsights = insights.filter(insight => {
    if (filter === 'critical') return insight.impact === 'critical' || insight.impact === 'high';
    if (filter === 'actionable') return insight.actionable;
    return true;
  });

  const criticalInsights = insights.filter(i => i.impact === 'critical').length;
  const actionableInsights = insights.filter(i => i.actionable).length;

  return (
    <div className="insight-dashboard">
      <div className="dashboard-header">
        <h2>🎯 Central de Insights</h2>
        <p>Análises e recomendações para seu progresso</p>

        <div className="insights-stats">
          <div className="stat-card critical">
            <span className="stat-number">{criticalInsights}</span>
            <span className="stat-label">Críticos</span>
          </div>
          <div className="stat-card actionable">
            <span className="stat-number">{actionableInsights}</span>
            <span className="stat-label">Acionáveis</span>
          </div>
          <div className="stat-card total">
            <span className="stat-number">{insights.length}</span>
            <span className="stat-label">Total</span>
          </div>
        </div>
      </div>

      <div className="dashboard-controls">
        <div className="filter-buttons">
          <button
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            Todos
          </button>
          <button
            className={`filter-btn ${filter === 'critical' ? 'active' : ''}`}
            onClick={() => setFilter('critical')}
          >
            Críticos
          </button>
          <button
            className={`filter-btn ${filter === 'actionable' ? 'active' : ''}`}
            onClick={() => setFilter('actionable')}
          >
            Acionáveis
          </button>
        </div>

        <button
          className="generate-btn"
          onClick={handleGenerateInsights}
          disabled={loading}
        >
          {loading ? '⏳ Gerando...' : '🔄 Gerar Novos Insights'}
        </button>
      </div>

      <div className="insights-grid">
        {filteredInsights.length === 0 ? (
          <div className="no-insights">
            <p>Nenhum insight disponível no momento</p>
            <button onClick={handleGenerateInsights}>
              Gerar Insights Agora
            </button>
          </div>
        ) : (
          filteredInsights.map(insight => (
            <div
              key={insight.id}
              className={`insight-card ${insight.impact}`}
              style={{ borderLeftColor: getImpactColor(insight.impact) }}
            >
              <div className="insight-header">
                <span className="insight-icon">{getInsightIcon(insight.type)}</span>
                <h3>{insight.title}</h3>
                {insight.actionable && (
                  <span className="actionable-badge">Ação Requerida</span>
                )}
              </div>

              <p className="insight-description">{insight.description}</p>

              {insight.relatedConcepts && insight.relatedConcepts.length > 0 && (
                <div className="related-concepts">
                  <span className="label">Conceitos Relacionados:</span>
                  <div className="concept-tags">
                    {insight.relatedConcepts.map(concept => (
                      <span key={concept} className="concept-tag">
                        {concept}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="insight-footer">
                <span className="insight-source">{insight.source || 'Sistema'}</span>
                <span className="insight-time">
                  {new Date(insight.timestamp).toLocaleString('pt-BR')}
                </span>
              </div>

              {insight.actionable && (
                <button className="action-button">
                  Tomar Ação →
                </button>
              )}
            </div>
          ))
        )}
      </div>

      {/* Seção de Insights Prioritários */}
      {criticalInsights > 0 && (
        <div className="priority-section">
          <h3>🚨 Atenção Imediata Necessária</h3>
          <div className="priority-list">
            {insights
              .filter(i => i.impact === 'critical')
              .slice(0, 3)
              .map(insight => (
                <div key={insight.id} className="priority-item">
                  <span className="priority-icon">⚡</span>
                  <div>
                    <strong>{insight.title}</strong>
                    <p>{insight.description}</p>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      <style jsx>{`
        .insight-dashboard {
          padding: 20px;
          max-width: 1400px;
          margin: 0 auto;
        }

        .dashboard-header {
          text-align: center;
          margin-bottom: 30px;
        }

        .dashboard-header h2 {
          color: #495057;
          margin-bottom: 10px;
        }

        .insights-stats {
          display: flex;
          gap: 20px;
          justify-content: center;
          margin-top: 20px;
        }

        .stat-card {
          background: white;
          padding: 20px 30px;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          text-align: center;
        }

        .stat-card.critical {
          border-top: 3px solid #dc3545;
        }

        .stat-card.actionable {
          border-top: 3px solid #667eea;
        }

        .stat-card.total {
          border-top: 3px solid #28a745;
        }

        .stat-number {
          display: block;
          font-size: 32px;
          font-weight: bold;
          color: #495057;
        }

        .stat-label {
          display: block;
          margin-top: 5px;
          color: #6c757d;
          font-size: 14px;
        }

        .dashboard-controls {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 30px;
        }

        .filter-buttons {
          display: flex;
          gap: 10px;
        }

        .filter-btn {
          padding: 10px 20px;
          border: 1px solid #dee2e6;
          background: white;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.3s;
        }

        .filter-btn.active {
          background: #667eea;
          color: white;
          border-color: #667eea;
        }

        .generate-btn {
          padding: 10px 20px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 600;
        }

        .generate-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .insights-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          gap: 20px;
          margin-bottom: 40px;
        }

        .insight-card {
          background: white;
          border-radius: 12px;
          padding: 20px;
          border-left: 4px solid;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          transition: transform 0.3s, box-shadow 0.3s;
        }

        .insight-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }

        .insight-header {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 15px;
        }

        .insight-icon {
          font-size: 24px;
        }

        .insight-header h3 {
          flex: 1;
          margin: 0;
          color: #495057;
          font-size: 18px;
        }

        .actionable-badge {
          background: #667eea;
          color: white;
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 600;
        }

        .insight-description {
          color: #6c757d;
          line-height: 1.6;
          margin-bottom: 15px;
        }

        .related-concepts {
          margin: 15px 0;
        }

        .related-concepts .label {
          display: block;
          font-size: 12px;
          color: #6c757d;
          margin-bottom: 8px;
        }

        .concept-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .concept-tag {
          background: #f0f2f5;
          padding: 4px 10px;
          border-radius: 12px;
          font-size: 12px;
          color: #495057;
        }

        .insight-footer {
          display: flex;
          justify-content: space-between;
          font-size: 12px;
          color: #adb5bd;
          margin-top: 15px;
        }

        .action-button {
          width: 100%;
          margin-top: 15px;
          padding: 10px;
          background: #667eea;
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 600;
          transition: background 0.3s;
        }

        .action-button:hover {
          background: #764ba2;
        }

        .no-insights {
          grid-column: 1 / -1;
          text-align: center;
          padding: 60px 20px;
          color: #6c757d;
        }

        .no-insights button {
          margin-top: 20px;
          padding: 12px 30px;
          background: #667eea;
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 600;
        }

        .priority-section {
          background: #fff3cd;
          border-radius: 12px;
          padding: 20px;
          margin-top: 40px;
        }

        .priority-section h3 {
          color: #856404;
          margin-bottom: 20px;
        }

        .priority-list {
          display: flex;
          flex-direction: column;
          gap: 15px;
        }

        .priority-item {
          display: flex;
          gap: 15px;
          align-items: start;
          background: white;
          padding: 15px;
          border-radius: 8px;
        }

        .priority-icon {
          font-size: 24px;
        }

        .priority-item strong {
          display: block;
          margin-bottom: 5px;
          color: #495057;
        }

        .priority-item p {
          margin: 0;
          color: #6c757d;
          font-size: 14px;
        }
      `}</style>
    </div>
  );
};