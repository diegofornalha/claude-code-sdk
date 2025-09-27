import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MessageProps {
  message: {
    id: string;
    type: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: string;
  };
}

export const MessageRenderer: React.FC<MessageProps> = ({ message }) => {
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className={`message ${message.type}`}>
      <div className="message-header">
        <span className="message-type">
          {message.type === 'user' ? '👤 Você' :
           message.type === 'assistant' ? '🤖 Claude' : '⚙️ Sistema'}
        </span>
        <span className="message-time">{formatTime(message.timestamp)}</span>
      </div>

      <div className="message-content">
        {message.type === 'assistant' ? (
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.content}
          </ReactMarkdown>
        ) : (
          <p>{message.content}</p>
        )}
      </div>

      <style jsx>{`
        .message {
          margin-bottom: 20px;
          animation: slideIn 0.3s ease;
        }

        .message.user {
          margin-left: 20%;
        }

        .message.assistant {
          margin-right: 20%;
        }

        .message-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: 8px;
          font-size: 14px;
          color: #6c757d;
        }

        .message-content {
          padding: 15px;
          border-radius: 12px;
          background: #f8f9fa;
        }

        .message.user .message-content {
          background: #e3f2fd;
          border-left: 4px solid #667eea;
        }

        .message.assistant .message-content {
          background: #f3e5f5;
          border-left: 4px solid #764ba2;
        }

        .message.system .message-content {
          background: #fff3cd;
          border-left: 4px solid #ffc107;
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
};