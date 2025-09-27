import React, { useState, useEffect } from 'react';
import './App.css';

const App: React.FC = () => {
  const [activeView, setActiveView] = useState<'dashboard' | 'timeline'>('dashboard');
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [wsStatus, setWsStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');

  // Detectar mudanças na URL
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash;
      if (hash === '#timeline') setActiveView('timeline');
      else if (hash === '#dashboard') setActiveView('dashboard');
    };

    // Verificar hash inicial
    handleHashChange();

    // Escutar mudanças
    window.addEventListener('hashchange', handleHashChange);

    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  // Verificar status do backend
  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        const response = await fetch('http://localhost:4001/api/health');
        if (response.ok) {
          setBackendStatus('online');
        } else {
          setBackendStatus('offline');
        }
      } catch (error) {
        setBackendStatus('offline');
      }
    };

    // Verificar WebSocket
    const checkWebSocket = () => {
      const ws = new WebSocket('ws://localhost:4001');

      ws.onopen = () => {
        setWsStatus('connected');
        ws.close();
      };

      ws.onerror = () => {
        setWsStatus('disconnected');
      };

      ws.onclose = () => {
        if (wsStatus === 'connecting') {
          setWsStatus('disconnected');
        }
      };
    };

    // Verificação inicial
    checkBackendStatus();
    checkWebSocket();

    // Verificar a cada 5 segundos
    const interval = setInterval(() => {
      checkBackendStatus();
      checkWebSocket();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const bootcampData = {
    user: 'User',
    score: 45,
    targetScore: 100,
    week: 1,
    totalWeeks: 12,
    gaps: ['MCP Protocol', 'Hooks System'],
    completedConcepts: ['query() function', 'Async Patterns'],
    nextMilestone: 'MCP Tools (Score 60)'
  };


  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🚀 Neo4j Knowledge Agent</h1>
        <p>Neo4j Agent Chat Interface</p>
      </header>

      <nav className="app-nav">
        <button
          className={activeView === 'dashboard' ? 'active' : ''}
          onClick={() => setActiveView('dashboard')}
        >
          📊 Dashboard
        </button>
        <button
          className={activeView === 'timeline' ? 'active' : ''}
          onClick={() => setActiveView('timeline')}
        >
          📅 Timeline
        </button>
      </nav>

      <main className="app-main">
        {activeView === 'dashboard' && (
          <div className="dashboard-view">
            <div className="score-card">
              <h2>Score Atual</h2>
              <div className="score-display">
                <span className="current-score">{bootcampData.score}</span>
                <span className="divider">/</span>
                <span className="target-score">{bootcampData.targetScore}</span>
              </div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${bootcampData.score}%` }}
                />
              </div>
            </div>

            <div className="info-grid">
              <div className="info-card">
                <h3>📅 Semana</h3>
                <p>{bootcampData.week} de {bootcampData.totalWeeks}</p>
              </div>

              <div className="info-card">
                <h3>🎯 Próximo Marco</h3>
                <p>{bootcampData.nextMilestone}</p>
              </div>

              <div className="info-card">
                <h3>🔌 Status do Sistema</h3>
                <div className="status-indicators">
                  <div className="status-item">
                    <span className="status-label">Backend API:</span>
                    <span className={`status-value ${backendStatus}`}>
                      {backendStatus === 'checking' && '⏳ Verificando...'}
                      {backendStatus === 'online' && '🟢 Online'}
                      {backendStatus === 'offline' && '🔴 Offline'}
                    </span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">WebSocket:</span>
                    <span className={`status-value ${wsStatus}`}>
                      {wsStatus === 'connecting' && '⏳ Conectando...'}
                      {wsStatus === 'connected' && '🟢 Conectado'}
                      {wsStatus === 'disconnected' && '🔴 Desconectado'}
                    </span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">Porta:</span>
                    <span className="status-value">4001</span>
                  </div>
                </div>
              </div>

              <div className="info-card completed">
                <h3>✅ Conceitos Completos</h3>
                <ul>
                  {bootcampData.completedConcepts.map(concept => (
                    <li key={concept}>{concept}</li>
                  ))}
                </ul>
              </div>
            </div>

          </div>
        )}


        {activeView === 'timeline' && (
          <div className="timeline-view">
            <h2>📅 Timeline Detalhada do Bootcamp</h2>
            <div className="timeline">
              {/* Dia 1-2: Fundamentos */}
              <div className="timeline-item completed">
                <div className="timeline-marker">✅</div>
                <div className="timeline-content">
                  <h3>Dia 1-2: Fundamentos Hackathon Flow Blockchain Agents</h3>
                  <p>✅ query() function básica<br/>
                  ✅ ClaudeCodeOptions config<br/>
                  ✅ async/await patterns<br/>
                  <span className="score-badge">+15 pts</span></p>
                </div>
              </div>

              {/* Dia 3-4: Conceitos Avançados */}
              <div className="timeline-item completed">
                <div className="timeline-marker">✅</div>
                <div className="timeline-content">
                  <h3>Dia 3-4: Conceitos Avançados</h3>
                  <p>✅ Stateless vs Stateful<br/>
                  ✅ Error handling patterns<br/>
                  ✅ Retry mechanisms<br/>
                  <span className="score-badge">+10 pts</span></p>
                </div>
              </div>

              {/* Dia 5-6: Ferramentas Nativas */}
              <div className="timeline-item current">
                <div className="timeline-marker">🔵</div>
                <div className="timeline-content">
                  <h3>Dia 5-6: Ferramentas Nativas</h3>
                  <p>🔵 File operations (read/write)<br/>
                  🔵 Search tools (grep/glob)<br/>
                  🔵 System commands<br/>
                  <span className="score-badge">+10 pts</span></p>
                </div>
              </div>

              {/* Dia 7-9: MCP Tools */}
              <div className="timeline-item">
                <div className="timeline-marker">⭕</div>
                <div className="timeline-content">
                  <h3>Dia 7-9: MCP Tools Customizadas</h3>
                  <p>⭕ @tool decorator<br/>
                  ⭕ input_schema definition<br/>
                  ⭕ MCP protocol integration<br/>
                  <span className="score-badge">+20 pts</span></p>
                </div>
              </div>

              {/* Dia 10-12: Hooks System */}
              <div className="timeline-item">
                <div className="timeline-marker">⭕</div>
                <div className="timeline-content">
                  <h3>Dia 10-12: Hooks System</h3>
                  <p>⭕ HookMatcher patterns<br/>
                  ⭕ PreToolUse hooks<br/>
                  ⭕ PostToolUse hooks<br/>
                  <span className="score-badge">+15 pts</span></p>
                </div>
              </div>

              {/* Dia 13-15: ClaudeSDKClient */}
              <div className="timeline-item">
                <div className="timeline-marker">⭕</div>
                <div className="timeline-content">
                  <h3>Dia 13-15: ClaudeSDKClient</h3>
                  <p>⭕ Sessões persistentes<br/>
                  ⭕ send_message() / receive_response()<br/>
                  ⭕ Contexto de memória<br/>
                  <span className="score-badge">+15 pts</span></p>
                </div>
              </div>

              {/* Dia 16-18: Streaming & Real-time */}
              <div className="timeline-item">
                <div className="timeline-marker">⭕</div>
                <div className="timeline-content">
                  <h3>Dia 16-18: Streaming & Real-time</h3>
                  <p>⭕ Streaming responses<br/>
                  ⭕ WebSocket integration<br/>
                  ⭕ Real-time updates<br/>
                  <span className="score-badge">+10 pts</span></p>
                </div>
              </div>

              {/* Dia 19-21: Multi-Agent */}
              <div className="timeline-item">
                <div className="timeline-marker">⭕</div>
                <div className="timeline-content">
                  <h3>Dia 19-21: Multi-Agent System</h3>
                  <p>⭕ Task tool orchestration<br/>
                  ⭕ Subagents coordination<br/>
                  ⭕ Agent communication<br/>
                  <span className="score-badge">+15 pts</span></p>
                </div>
              </div>

              {/* Dia 22-25: Projeto Final */}
              <div className="timeline-item">
                <div className="timeline-marker">🎯</div>
                <div className="timeline-content">
                  <h3>Dia 22-25: Projeto Final Neo4j</h3>
                  <p>🎯 Aplicação completa<br/>
                  🎯 Integração Neo4j MCP<br/>
                  🎯 Knowledge graph<br/>
                  <span className="score-badge">+25 pts</span></p>
                </div>
              </div>
            </div>
          </div>
        )}

      </main>

      <footer className="app-footer">
        <p>Neo4j Knowledge Agent © 2024 | Bootcamp Hackathon Flow Blockchain Agents | Score: {bootcampData.score}/100</p>
      </footer>
    </div>
  );
};

export default App;