import { useReducer, useRef, useCallback, useEffect } from 'react';

// Tipos
export interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
    tokens?: { input?: number; output?: number };
    cost?: number;
}

export interface StreamResponse {
    type: 'session_migrated' | 'processing' | 'text_chunk' | 'tool_use' | 'result' | 'error';
    session_id?: string;
    content?: string;
    tool?: string;
    input_tokens?: number;
    output_tokens?: number;
    cost_usd?: number;
    error?: string;
}

// Estado do chat
interface ChatState {
    messages: ChatMessage[];
    isStreaming: boolean;
    currentStreamContent: string;
    sessionId: string | null;
    tokenInfo: { input?: number; output?: number } | null;
    costInfo: number | null;
    isProcessing: boolean;
    isTyping: boolean;
}

// Ações
type ChatAction =
    | { type: 'SET_SESSION'; sessionId: string }
    | { type: 'ADD_MESSAGE'; message: ChatMessage }
    | { type: 'START_STREAMING' }
    | { type: 'START_PROCESSING' }
    | { type: 'STOP_PROCESSING' }
    | { type: 'UPDATE_STREAM_CONTENT'; content: string }
    | { type: 'APPEND_STREAM_CONTENT'; content: string }
    | { type: 'START_TYPING' }
    | { type: 'STOP_TYPING' }
    | { type: 'UPDATE_TOKEN_INFO'; tokens: { input?: number; output?: number } }
    | { type: 'UPDATE_COST_INFO'; cost: number }
    | { type: 'FINISH_STREAMING'; message?: ChatMessage }
    | { type: 'CLEAR_SESSION' }
    | { type: 'INTERRUPT_STREAMING' };

// Reducer
function chatReducer(state: ChatState, action: ChatAction): ChatState {
    switch (action.type) {
        case 'SET_SESSION':
            return { ...state, sessionId: action.sessionId };

        case 'ADD_MESSAGE':
            return { ...state, messages: [...state.messages, action.message] };

        case 'START_STREAMING':
            return {
                ...state,
                isStreaming: true,
                currentStreamContent: '',
                tokenInfo: null,
                costInfo: null,
                isTyping: false
            };

        case 'START_PROCESSING':
            return { ...state, isProcessing: true };

        case 'STOP_PROCESSING':
            return { ...state, isProcessing: false };

        case 'START_TYPING':
            return { ...state, isTyping: true };

        case 'STOP_TYPING':
            return { ...state, isTyping: false };

        case 'UPDATE_STREAM_CONTENT':
            return { ...state, currentStreamContent: action.content };

        case 'APPEND_STREAM_CONTENT':
            return { ...state, currentStreamContent: state.currentStreamContent + action.content };

        case 'UPDATE_TOKEN_INFO':
            return { ...state, tokenInfo: action.tokens };

        case 'UPDATE_COST_INFO':
            return { ...state, costInfo: action.cost };

        case 'FINISH_STREAMING':
            const newState = {
                ...state,
                isStreaming: false,
                currentStreamContent: '',
                tokenInfo: null,
                costInfo: null,
                isProcessing: false,
                isTyping: false
            };

            if (action.message) {
                newState.messages = [...state.messages, action.message];
            }

            return newState;

        case 'CLEAR_SESSION':
            return {
                ...state,
                messages: [],
                currentStreamContent: '',
                isStreaming: false,
                tokenInfo: null,
                costInfo: null,
                isProcessing: false,
                isTyping: false
            };

        case 'INTERRUPT_STREAMING':
            return {
                ...state,
                isStreaming: false,
                isProcessing: false,
                isTyping: false
            };

        default:
            return state;
    }
}

// Hook customizado
export function useStreamingChat() {
    const [state, dispatch] = useReducer(chatReducer, {
        messages: [],
        isStreaming: false,
        currentStreamContent: '',
        sessionId: null,
        tokenInfo: null,
        costInfo: null,
        isProcessing: false,
        isTyping: false
    });

    const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const typingQueueRef = useRef<string[]>([]);
    const eventSourceRef = useRef<EventSource | null>(null);

    // Inicializa API
    const initializeAPI = useCallback(async () => {
        try {
            // Criar nova sessão
            const response = await fetch('http://localhost:4001/api/session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    context: {
                        user: 'User',
                        score: 45,
                        week: 1,
                        gaps: ['MCP Protocol', 'Hooks System']
                    }
                })
            });

            if (response.ok) {
                const data = await response.json();
                if (data.sessionId) {
                    dispatch({ type: 'SET_SESSION', sessionId: data.sessionId });
                }
            }
        } catch (error) {
            console.error('Erro ao inicializar API:', error);
        }
    }, []);

    // Processar fila de digitação
    const processTypingQueue = useCallback(() => {
        if (typingQueueRef.current.length === 0) {
            dispatch({ type: 'STOP_TYPING' });
            return;
        }

        dispatch({ type: 'START_TYPING' });
        const chunk = typingQueueRef.current.shift()!;

        dispatch({ type: 'APPEND_STREAM_CONTENT', content: chunk });

        // Continua processando
        typingTimeoutRef.current = setTimeout(processTypingQueue, 50);
    }, []);

    // Adiciona à fila de digitação
    const addToTypingQueue = useCallback((content: string) => {
        // Divide em chunks menores para efeito de digitação
        const chunks = content.match(/.{1,5}/g) || [content];
        typingQueueRef.current.push(...chunks);

        if (!state.isTyping && typingQueueRef.current.length > 0) {
            processTypingQueue();
        }
    }, [state.isTyping, processTypingQueue]);

    // Limpa fila
    const clearTypingQueue = useCallback(() => {
        typingQueueRef.current = [];
        if (typingTimeoutRef.current) {
            clearTimeout(typingTimeoutRef.current);
            typingTimeoutRef.current = null;
        }
        dispatch({ type: 'STOP_TYPING' });
    }, []);

    // Enviar mensagem com streaming
    const sendMessage = useCallback(async (message: string) => {
        clearTypingQueue();

        // Adiciona mensagem do usuário
        const userMessage: ChatMessage = {
            role: 'user',
            content: message,
            timestamp: new Date()
        };

        dispatch({ type: 'ADD_MESSAGE', message: userMessage });
        dispatch({ type: 'START_STREAMING' });
        dispatch({ type: 'START_PROCESSING' });

        let finalContent = '';
        let finalTokens: { input?: number; output?: number } | null = null;
        let finalCost: number | null = null;

        try {
            // Conectar ao SSE endpoint
            if (eventSourceRef.current) {
                eventSourceRef.current.close();
            }

            const params = new URLSearchParams({
                message: message,
                sessionId: state.sessionId || 'new',
                useNeo4j: 'true'
            });

            eventSourceRef.current = new EventSource(
                `http://localhost:4001/api/chat/stream?${params}`
            );

            eventSourceRef.current.onmessage = (event) => {
                const data: StreamResponse = JSON.parse(event.data);

                switch (data.type) {
                    case 'session_migrated':
                        if (data.session_id) {
                            dispatch({ type: 'SET_SESSION', sessionId: data.session_id });
                        }
                        break;

                    case 'processing':
                        dispatch({ type: 'START_PROCESSING' });
                        break;

                    case 'text_chunk':
                        dispatch({ type: 'STOP_PROCESSING' });
                        if (data.content) {
                            addToTypingQueue(data.content);
                            finalContent += data.content;
                        }
                        break;

                    case 'tool_use':
                        const toolMsg = `\n🔧 Usando: ${data.tool}\n`;
                        addToTypingQueue(toolMsg);
                        finalContent += toolMsg;
                        break;

                    case 'result':
                        if (data.input_tokens !== undefined) {
                            finalTokens = {
                                input: data.input_tokens,
                                output: data.output_tokens
                            };
                            dispatch({ type: 'UPDATE_TOKEN_INFO', tokens: finalTokens });
                        }
                        if (data.cost_usd !== undefined) {
                            finalCost = data.cost_usd;
                            dispatch({ type: 'UPDATE_COST_INFO', cost: finalCost });
                        }
                        break;
                }
            };

            eventSourceRef.current.onerror = (error) => {
                console.error('SSE error:', error);
                eventSourceRef.current?.close();

                // Aguarda digitação terminar
                setTimeout(() => {
                    if (finalContent) {
                        const assistantMessage: ChatMessage = {
                            role: 'assistant',
                            content: finalContent,
                            timestamp: new Date(),
                            tokens: finalTokens || undefined,
                            cost: finalCost || undefined
                        };
                        dispatch({ type: 'FINISH_STREAMING', message: assistantMessage });
                    } else {
                        dispatch({ type: 'FINISH_STREAMING' });
                    }
                }, 100);
            };

        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            dispatch({ type: 'STOP_PROCESSING' });
            clearTypingQueue();

            // Fallback para resposta local
            const errorMessage: ChatMessage = {
                role: 'assistant',
                content: 'Desculpe, houve um erro ao processar sua mensagem. Verifique se o backend está rodando na porta 4000.',
                timestamp: new Date()
            };
            dispatch({ type: 'FINISH_STREAMING', message: errorMessage });
        }
    }, [state.sessionId, clearTypingQueue, addToTypingQueue]);

    // Limpar sessão
    const clearSession = useCallback(async () => {
        clearTypingQueue();

        if (state.sessionId) {
            try {
                await fetch(`http://localhost:4001/api/session/${state.sessionId}`, {
                    method: 'DELETE'
                });
            } catch (error) {
                console.error('Erro ao limpar sessão:', error);
            }
        }

        dispatch({ type: 'CLEAR_SESSION' });
    }, [state.sessionId, clearTypingQueue]);

    // Interromper streaming
    const interruptStreaming = useCallback(async () => {
        if (!state.isStreaming) return;

        clearTypingQueue();

        if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
        }

        if (state.currentStreamContent) {
            const partialMessage: ChatMessage = {
                role: 'assistant',
                content: state.currentStreamContent + '\n\n[Interrompido]',
                timestamp: new Date()
            };
            dispatch({ type: 'FINISH_STREAMING', message: partialMessage });
        } else {
            dispatch({ type: 'INTERRUPT_STREAMING' });
        }
    }, [state.isStreaming, state.currentStreamContent, clearTypingQueue]);

    // Cleanup
    const cleanup = useCallback(async () => {
        clearTypingQueue();

        if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
        }

        if (state.sessionId) {
            try {
                await fetch(`http://localhost:4001/api/session/${state.sessionId}`, {
                    method: 'DELETE'
                });
            } catch (error) {
                console.error('Erro ao deletar sessão:', error);
            }
        }
    }, [state.sessionId, clearTypingQueue]);

    // Cleanup automático
    useEffect(() => {
        return () => {
            clearTypingQueue();
            if (eventSourceRef.current) {
                eventSourceRef.current.close();
            }
        };
    }, [clearTypingQueue]);

    return {
        ...state,
        initializeAPI,
        sendMessage,
        clearSession,
        interruptStreaming,
        cleanup
    };
}