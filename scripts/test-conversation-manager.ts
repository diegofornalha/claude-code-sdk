#!/usr/bin/env tsx

/**
 * Script de teste para o ConversationManager
 * Demonstra o uso centralizado do histórico de conversas
 */

import { conversationManager } from '../ccsdk/conversation-manager';

async function main() {
  console.log('🧪 Testando ConversationManager...\n');

  // 1. Iniciar sessão
  console.log('1️⃣ Iniciando nova sessão...');
  const sessionId = await conversationManager.startSession();
  console.log('   ✅ Sessão criada:', sessionId);

  // 2. Adicionar algumas mensagens
  console.log('\n2️⃣ Adicionando mensagens ao histórico...');

  await conversationManager.addMessage('user', 'Como funciona o Claude Code SDK?', {
    timestamp: new Date().toISOString()
  });
  console.log('   ✅ Mensagem do usuário adicionada');

  await conversationManager.addMessage('assistant',
    'O Claude Code SDK é uma ferramenta poderosa que permite integração com o Claude através de uma API assíncrona usando a função query().',
    {
      tokens: 25,
      model: 'claude-3',
      timestamp: new Date().toISOString()
    }
  );
  console.log('   ✅ Resposta do assistente adicionada');

  await conversationManager.addMessage('user', 'E sobre MCP Tools?', {
    timestamp: new Date().toISOString()
  });
  console.log('   ✅ Segunda mensagem do usuário adicionada');

  await conversationManager.addMessage('assistant',
    'MCP Tools são ferramentas do Model Context Protocol que retornam dados estruturados em formato {"content": [...]}. Você precisa entender este formato para o bootcamp.',
    {
      tokens: 30,
      model: 'claude-3',
      timestamp: new Date().toISOString()
    }
  );
  console.log('   ✅ Segunda resposta do assistente adicionada');

  // 3. Buscar mensagens da sessão
  console.log('\n3️⃣ Recuperando mensagens da sessão...');
  const messages = await conversationManager.getSessionMessages(sessionId);
  console.log(`   📊 Total de mensagens na sessão: ${messages.length}`);

  messages.forEach((msg, idx) => {
    console.log(`   ${idx + 1}. [${msg.role}]: ${msg.content.substring(0, 50)}...`);
  });

  // 4. Obter resumo da sessão
  console.log('\n4️⃣ Resumo da sessão atual:');
  const summary = conversationManager.getSessionSummary();
  if (summary) {
    console.log('   📝 ID:', summary.sessionId);
    console.log('   💬 Mensagens:', summary.messageCount);
    console.log('   🪙 Tokens:', summary.totalTokens || 0);
    console.log('   ⏱️ Status:', summary.status);
  }

  // 5. Listar todas as sessões
  console.log('\n5️⃣ Listando todas as sessões:');
  const allSessions = await conversationManager.listSessions();
  console.log(`   📚 Total de sessões: ${allSessions.length}`);

  allSessions.forEach((session, idx) => {
    console.log(`   ${idx + 1}. Sessão ${session.sessionId.substring(0, 8)}... (${session.messageCount} msgs)`);
  });

  // 6. Obter estatísticas gerais
  console.log('\n6️⃣ Estatísticas gerais:');
  const stats = await conversationManager.getStatistics();
  console.log('   📈 Total de sessões:', stats.totalSessions);
  console.log('   💬 Total de mensagens:', stats.totalMessages);
  console.log('   🪙 Total de tokens:', stats.totalTokens);
  console.log('   📊 Média msgs/sessão:', stats.averageMessagesPerSession.toFixed(1));

  // 7. Pausar sessão
  console.log('\n7️⃣ Pausando sessão...');
  await conversationManager.pauseSession();
  console.log('   ⏸️ Sessão pausada com sucesso');

  // 8. Demonstrar arquivo único
  console.log('\n8️⃣ Arquivo JSONL centralizado:');
  const projectPath = `/Users/2a/.claude/projects/-Users-2a-Desktop-neo4j-agent-claude-code-sdk`;
  console.log(`   📁 Local: ${projectPath}/conversations.jsonl`);
  console.log(`   📝 Sessões: ${projectPath}/sessions.json`);
  console.log('\n✨ Todas as conversas estão sendo salvas em um único arquivo JSONL!');
  console.log('   Isso evita múltiplos arquivos separados e mantém tudo organizado.');

  console.log('\n✅ Teste concluído com sucesso!');
}

// Executar teste
main().catch(console.error);