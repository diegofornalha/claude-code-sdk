import React, { useState } from 'react';

interface Concept {
  id: string;
  name: string;
  type: string;
  completed: boolean;
  scoreImpact: number;
  connections?: string[];
}

interface KnowledgeExplorerProps {
  concepts: Concept[];
  onConceptSelect: (concept: Concept) => void;
}

export const KnowledgeExplorer: React.FC<KnowledgeExplorerProps> = ({
  concepts,
  onConceptSelect
}) => {
  const [selectedType, setSelectedType] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredConcepts = concepts.filter(concept => {
    const matchesType = selectedType === 'all' || concept.type === selectedType;
    const matchesSearch = concept.name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesType && matchesSearch;
  });

  const conceptTypes = ['all', 'concept', 'skill', 'gap', 'project', 'insight'];

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'gap': return '#dc3545';
      case 'skill': return '#28a745';
      case 'concept': return '#667eea';
      case 'project': return '#ffc107';
      case 'insight': return '#17a2b8';
      default: return '#6c757d';
    }
  };

  return (
    <div className="knowledge-explorer">
      <div className="explorer-header">
        <h2>🗺️ Explorador de Conhecimento</h2>
        <p>Navegue pelos conceitos do bootcamp</p>
      </div>

      <div className="explorer-controls">
        <input
          type="text"
          placeholder="Buscar conceitos..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />

        <div className="type-filters">
          {conceptTypes.map(type => (
            <button
              key={type}
              className={`type-filter ${selectedType === type ? 'active' : ''}`}
              onClick={() => setSelectedType(type)}
            >
              {type === 'all' ? 'Todos' : type}
            </button>
          ))}
        </div>
      </div>

      <div className="concepts-grid">
        {filteredConcepts.map(concept => (
          <div
            key={concept.id}
            className={`concept-card ${concept.completed ? 'completed' : ''}`}
            onClick={() => onConceptSelect(concept)}
            style={{ borderColor: getTypeColor(concept.type) }}
          >
            <div className="concept-header">
              <span className="concept-type" style={{ background: getTypeColor(concept.type) }}>
                {concept.type}
              </span>
              {concept.completed && <span className="completed-badge">✅</span>}
            </div>

            <h3>{concept.name}</h3>

            <div className="concept-meta">
              <span className="score-impact">
                +{concept.scoreImpact} pts
              </span>
              {concept.connections && (
                <span className="connections">
                  🔗 {concept.connections.length} conexões
                </span>
              )}
            </div>

            {concept.type === 'gap' && (
              <div className="gap-warning">
                ⚠️ Gap crítico - Resolver urgente!
              </div>
            )}
          </div>
        ))}
      </div>

      {filteredConcepts.length === 0 && (
        <div className="no-results">
          <p>Nenhum conceito encontrado</p>
        </div>
      )}

      <style jsx>{`
        .knowledge-explorer {
          padding: 20px;
        }

        .explorer-header {
          margin-bottom: 30px;
        }

        .explorer-header h2 {
          color: #495057;
          margin-bottom: 10px;
        }

        .explorer-controls {
          margin-bottom: 30px;
        }

        .search-input {
          width: 100%;
          padding: 12px;
          border: 2px solid #dee2e6;
          border-radius: 8px;
          font-size: 16px;
          margin-bottom: 20px;
        }

        .type-filters {
          display: flex;
          gap: 10px;
          flex-wrap: wrap;
        }

        .type-filter {
          padding: 8px 16px;
          border: 1px solid #dee2e6;
          border-radius: 20px;
          background: white;
          cursor: pointer;
          transition: all 0.3s;
        }

        .type-filter.active {
          background: #667eea;
          color: white;
          border-color: #667eea;
        }

        .concepts-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
          gap: 20px;
        }

        .concept-card {
          background: white;
          padding: 20px;
          border-radius: 12px;
          border: 2px solid;
          cursor: pointer;
          transition: all 0.3s;
          position: relative;
        }

        .concept-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }

        .concept-card.completed {
          opacity: 0.8;
        }

        .concept-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: 10px;
        }

        .concept-type {
          padding: 4px 12px;
          border-radius: 12px;
          color: white;
          font-size: 12px;
          font-weight: 600;
          text-transform: uppercase;
        }

        .concept-card h3 {
          margin: 15px 0;
          color: #495057;
        }

        .concept-meta {
          display: flex;
          justify-content: space-between;
          font-size: 14px;
          color: #6c757d;
        }

        .gap-warning {
          margin-top: 10px;
          padding: 8px;
          background: #fff3cd;
          border-radius: 8px;
          color: #856404;
          font-size: 14px;
          font-weight: 600;
        }

        .no-results {
          text-align: center;
          padding: 40px;
          color: #6c757d;
        }
      `}</style>
    </div>
  );
};