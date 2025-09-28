#!/usr/bin/env node
/**
 * Script para testar o sistema de sessão unificada
 */

const { ConversationManager } = require('./conversation-manager.js');

async function testUnifiedSession() {
    console.log('🧪 Testando sistema de sessão unificada...\n');

    // Criar instância do ConversationManager
    const manager = new ConversationManager('neo4j-agent-claude-code-sdk');

    // Aguardar inicialização
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Teste 1: Criar primeira sessão
    console.log('📝 Teste 1: Criando primeira sessão...');
    const session1 = await manager.startSession();
    console.log(`   ID da sessão 1: ${session1}`);

    // Teste 2: Criar segunda sessão (deve retornar o mesmo ID)
    console.log('\n📝 Teste 2: Criando segunda sessão...');
    const session2 = await manager.startSession();
    console.log(`   ID da sessão 2: ${session2}`);

    // Teste 3: Verificar se os IDs são iguais
    console.log('\n✅ Verificação:');
    if (session1 === session2) {
        console.log('   ✓ IDs de sessão são IGUAIS (modo unificado funcionando!)');
        console.log(`   ID unificado: ${session1}`);
    } else {
        console.log('   ✗ IDs de sessão são DIFERENTES (problema no modo unificado)');
        console.log(`   Sessão 1: ${session1}`);
        console.log(`   Sessão 2: ${session2}`);
    }

    // Teste 4: Adicionar algumas mensagens
    console.log('\n📝 Teste 4: Adicionando mensagens...');
    await manager.addMessage({
        role: 'user',
        content: 'Teste de mensagem do usuário'
    });

    await manager.addMessage({
        role: 'assistant',
        content: 'Teste de resposta do assistente'
    });

    const history = await manager.getSessionHistory(session1);
    console.log(`   Total de mensagens na sessão: ${history.length}`);

    // Teste 5: Buscar sessões
    console.log('\n📝 Teste 5: Buscando todas as sessões...');
    const sessions = await manager.listSessions();
    console.log(`   Total de sessões encontradas: ${sessions.length}`);
    sessions.forEach(s => {
        console.log(`   - Sessão ${s.sessionId}: ${s.messageCount} mensagens`);
    });

    console.log('\n✅ Teste concluído!');
    console.log('   O sistema está usando sessão unificada com ID fixo.');
    console.log('   Todas as conversas serão mantidas na mesma sessão.\n');
}

// Executar teste
testUnifiedSession().catch(console.error);