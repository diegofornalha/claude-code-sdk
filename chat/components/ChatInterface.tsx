import React, { useState, useRef, useEffect } from 'react';
import { MessageRenderer } from './MessageRenderer';

interface ChatInterfaceProps {
  onSendMessage: (message: any) => void;
  bootcampContext: {
    score: number;
    week: number;
    gaps: string[];
    nextMilestone: string;
  };
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  onSendMessage,
  bootcampContext
}) => {
  const [messages, setMessages] = useState<any[]>([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = () => {
    if (!inputText.trim()) return;

    // Adicionar mensagem do usuário
    const userMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputText,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);

    // Enviar via WebSocket com contexto do bootcamp
    onSendMessage({
      type: 'claude_query',
      payload: {
        query: inputText,
        context: bootcampContext
      }
    });

    setInputText('');
    setIsTyping(true);

    // Simular resposta (remover quando WebSocket estiver conectado)
    setTimeout(() => {
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: generateMockResponse(inputText, bootcampContext),
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, assistantMessage]);
      setIsTyping(false);
    }, 1500);
  };

  const generateMockResponse = (query: string, context: any) => {
    const lowerQuery = query.toLowerCase();

    if (lowerQuery.includes('mcp')) {
      return `## 🔧 MCP Protocol - Gap Crítico

MCP (Model Context Protocol) é seu maior gap atual!

**Impacto**: +15 pontos no score
**Urgência**: ALTA

### O que você precisa saber:
1. MCP permite criar ferramentas customizadas
2. Retorno obrigatório: \`{"content": [...]}\`
3. Funciona em qualquer linguagem

### Próximos passos:
1. Estudar \`CONCEITOS/04_mcp_protocol.md\`
2. Implementar primeira MCP tool
3. Testar no Neo4j Agent

Resolver este gap te leva para Score 60!`;
    }

    if (lowerQuery.includes('progresso') || lowerQuery.includes('score')) {
      return `## 📊 Seu Progresso no Bootcamp

**Score Atual**: ${context.score}/100 (${context.score}%)
**Semana**: ${context.week}/12
**Próximo Marco**: ${context.nextMilestone}

### Gaps Identificados:
${context.gaps.map(gap => `- ⚠️ ${gap}`).join('\n')}

### Recomendação:
Foque em MCP Protocol esta semana para desbloquear +15 pontos!`;
    }

    if (lowerQuery.includes('hook')) {
      return `## 🪝 Hooks System

Hooks interceptam execução ANTES ou DEPOIS de ações.

**Tipos**:
- \`PreToolUse\`: Validar antes
- \`PostToolUse\`: Processar depois

**Retorno**:
- \`None\` = permite
- \`{behavior: "deny"}\` = bloqueia

Este é seu segundo gap crítico (+10 pontos).`;
    }

    return `Entendi sua pergunta sobre "${query}".

Com base no seu contexto atual (Score ${context.score}, Semana ${context.week}),
sugiro focar nos gaps críticos: ${context.gaps.join(', ')}.

Use comandos específicos como:
- "explique MCP"
- "mostre meu progresso"
- "como resolver hooks"`;
  };

  const suggestedQuestions = [
    'Qual meu progresso no bootcamp?',
    'Explique MCP Protocol',
    'Como funcionam Hooks?',
    'Mostre o caminho para Score 100',
    'Quais conceitos já dominei?'
  ];

  return (
    <div className="chat-interface">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <h3>👋 Bem-vindo ao Neo4j Knowledge Agent!</h3>
            <p>Eu ajudo você a navegar pelo bootcamp Hackathon Flow Blockchain Agents.</p>

            <div className="suggested-questions">
              <p>Perguntas sugeridas:</p>
              {suggestedQuestions.map((question, i) => (
                <button
                  key={i}
                  className="suggestion-chip"
                  onClick={() => setInputText(question)}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map(msg => (
              <MessageRenderer key={msg.id} message={msg} />
            ))}
            {isTyping && (
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <div className="input-container">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Pergunte sobre o bootcamp, MCP, hooks, ou seu progresso..."
          className="chat-input"
        />
        <button
          onClick={handleSendMessage}
          className="send-button"
          disabled={!inputText.trim()}
        >
          Enviar
        </button>
      </div>

      <div className="context-bar">
        <span>Score: {bootcampContext.score}/100</span>
        <span>•</span>
        <span>Semana {bootcampContext.week}/12</span>
        <span>•</span>
        <span>Gaps: {bootcampContext.gaps.length}</span>
      </div>
    </div>
  );
};