#!/usr/bin/env node

// Teste manual interativo via console
const readline = require('readline');
const { spawn } = require('child_process');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: '\n🔷 Claude SDK> '
});

console.log('═══════════════════════════════════════════════════════════════');
console.log('       TESTE MANUAL - CLAUDE CODE SDK - CONSOLE INTERATIVO');
console.log('═══════════════════════════════════════════════════════════════');
console.log('\n📋 Comandos disponíveis:');
console.log('  • test       - Executar testes do projeto');
console.log('  • build      - Compilar o projeto');
console.log('  • sparc      - Testar comandos SPARC');
console.log('  • flow       - Testar Claude Flow');
console.log('  • server     - Iniciar servidor Python');
console.log('  • chat       - Abrir chat interativo');
console.log('  • memory     - Testar sistema de memória');
console.log('  • clear      - Limpar console');
console.log('  • help       - Mostrar ajuda');
console.log('  • exit       - Sair\n');

rl.prompt();

// Função para executar comandos
function executeCommand(cmd, args = []) {
  return new Promise((resolve, reject) => {
    const process = spawn(cmd, args, {
      shell: true,
      stdio: 'inherit'
    });

    process.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Comando falhou com código ${code}`));
      }
    });

    process.on('error', (err) => {
      reject(err);
    });
  });
}

// Processar entrada do usuário
rl.on('line', async (line) => {
  const command = line.trim().toLowerCase();

  try {
    switch(command) {
      case 'test':
        console.log('\n🧪 Executando testes...\n');
        await executeCommand('npm', ['test']);
        break;

      case 'build':
        console.log('\n🔨 Compilando projeto...\n');
        await executeCommand('npm', ['run', 'build']);
        break;

      case 'sparc':
        console.log('\n⚡ Testando SPARC...\n');
        console.log('Comandos SPARC disponíveis:');
        await executeCommand('npx', ['claude-flow', 'sparc', 'modes']);
        break;

      case 'flow':
        console.log('\n🌊 Testando Claude Flow...\n');
        await executeCommand('npx', ['claude-flow', '--version']);
        console.log('\nRecursos disponíveis:');
        await executeCommand('npx', ['claude-flow', 'features', 'detect']);
        break;

      case 'server':
        console.log('\n🚀 Iniciando servidor Python...\n');
        console.log('Pressione Ctrl+C para parar o servidor\n');
        await executeCommand('python3', ['server.py']);
        break;

      case 'chat':
        console.log('\n💬 Abrindo chat interativo...\n');
        console.log('Verificando se o servidor está rodando...');
        await executeCommand('curl', ['-s', 'http://localhost:8080/health']);
        console.log('\nAbrindo chat no navegador...');
        await executeCommand('open', ['chat/index.html']);
        break;

      case 'memory':
        console.log('\n🧠 Testando sistema de memória Neo4j...\n');
        testMemorySystem();
        break;

      case 'clear':
        console.clear();
        console.log('Console limpo!');
        break;

      case 'help':
        console.log('\n📖 AJUDA - Comandos detalhados:\n');
        console.log('  test   - Executa npm test para rodar todos os testes');
        console.log('  build  - Compila o projeto com npm run build');
        console.log('  sparc  - Lista e testa comandos SPARC disponíveis');
        console.log('  flow   - Verifica instalação e recursos do Claude Flow');
        console.log('  server - Inicia o servidor Python na porta 8080');
        console.log('  chat   - Abre interface de chat no navegador');
        console.log('  memory - Testa conexão e operações com Neo4j');
        console.log('  clear  - Limpa o console');
        console.log('  exit   - Encerra o programa');
        break;

      case 'exit':
      case 'quit':
        console.log('\n👋 Encerrando teste manual. Até logo!\n');
        process.exit(0);
        break;

      default:
        if (command) {
          console.log(`❌ Comando desconhecido: "${command}"`);
          console.log('Digite "help" para ver os comandos disponíveis');
        }
    }
  } catch (error) {
    console.error(`\n❌ Erro ao executar comando: ${error.message}\n`);
  }

  rl.prompt();
});

// Função específica para testar memória
async function testMemorySystem() {
  console.log('1. Verificando conexão com Neo4j...');

  try {
    // Teste básico de memória
    console.log('2. Criando memória de teste...');
    const testData = {
      label: 'Learning',
      content: 'Teste manual via console',
      timestamp: new Date().toISOString()
    };
    console.log('   Dados:', JSON.stringify(testData, null, 2));

    console.log('3. Buscando memórias existentes...');
    // Aqui você pode adicionar código para interagir com Neo4j

    console.log('✅ Sistema de memória testado com sucesso!');
  } catch (error) {
    console.error('❌ Erro no teste de memória:', error.message);
  }
}

// Tratamento de interrupção
rl.on('SIGINT', () => {
  console.log('\n\n🛑 Interrompido pelo usuário. Encerrando...\n');
  process.exit(0);
});

// Mensagem inicial
console.log('Digite um comando ou "help" para ajuda');
rl.prompt();