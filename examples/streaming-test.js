#!/usr/bin/env node

const { EventEmitter } = require('events');

// Simula um stream de dados com chunks
class DataStreamer extends EventEmitter {
  constructor() {
    super();
    this.chunks = [
      '🚀 Iniciando processamento...',
      '📦 Chunk 1: Preparando ambiente',
      '🔄 Chunk 2: Conectando ao servidor',
      '⚡ Chunk 3: Processando dados [████____] 40%',
      '⚡ Chunk 4: Processando dados [██████__] 60%',
      '⚡ Chunk 5: Processando dados [████████] 100%',
      '✨ Chunk 6: Analisando resultados',
      '🎯 Chunk 7: Aplicando transformações',
      '💾 Chunk 8: Salvando no banco de dados',
      '📊 Chunk 9: Gerando estatísticas',
      '✅ Chunk 10: Processo concluído com sucesso!'
    ];
  }

  startStreaming() {
    console.log('\n════════════════════════════════════════════');
    console.log('       TESTE DE LOGS EM TEMPO REAL');
    console.log('════════════════════════════════════════════\n');

    let index = 0;
    const streamInterval = setInterval(() => {
      if (index < this.chunks.length) {
        const chunk = this.chunks[index];
        const timestamp = new Date().toISOString().slice(11, 23);

        // Emite o evento com o chunk
        this.emit('chunk', chunk, timestamp);

        // Mostra o chunk no console com formatação
        console.log(`[${timestamp}] ${chunk}`);

        // Simula processamento adicional para alguns chunks
        if (index === 3 || index === 4 || index === 5) {
          const progress = ((index - 2) / 3) * 100;
          this.emit('progress', progress);
        }

        index++;
      } else {
        clearInterval(streamInterval);
        this.emit('end');
        console.log('\n════════════════════════════════════════════');
        console.log('         STREAMING FINALIZADO');
        console.log('════════════════════════════════════════════\n');
      }
    }, 500); // Emite um chunk a cada 500ms
  }
}

// Função para processar logs em lote
function processBatchLogs() {
  console.log('\n🔥 Modo: PROCESSAMENTO EM LOTE\n');

  const batchSize = 3;
  const totalItems = 15;
  let processed = 0;

  const processBatch = () => {
    const remaining = totalItems - processed;
    const currentBatch = Math.min(batchSize, remaining);

    console.log(`📦 Processando lote: ${processed + 1}-${processed + currentBatch} de ${totalItems}`);

    for (let i = 0; i < currentBatch; i++) {
      const itemNumber = processed + i + 1;
      const timestamp = new Date().toISOString().slice(11, 23);
      console.log(`  [${timestamp}] Item ${itemNumber}: Processado ✓`);
    }

    processed += currentBatch;

    if (processed < totalItems) {
      setTimeout(processBatch, 1000);
    } else {
      console.log('\n✅ Todos os lotes processados!\n');

      // Inicia o streaming após o processamento em lote
      setTimeout(startStreamingMode, 2000);
    }
  };

  processBatch();
}

// Função para iniciar modo streaming
function startStreamingMode() {
  console.log('\n🌊 Modo: STREAMING EM TEMPO REAL\n');

  const streamer = new DataStreamer();

  // Adiciona listeners para eventos
  streamer.on('chunk', (data, time) => {
    // Poderia processar cada chunk aqui
  });

  streamer.on('progress', (percent) => {
    console.log(`    📊 Progresso: ${percent.toFixed(0)}%`);
  });

  streamer.on('end', () => {
    console.log('📈 Estatísticas do Streaming:');
    console.log('   - Total de chunks: 11');
    console.log('   - Tempo total: ~5.5 segundos');
    console.log('   - Taxa de transmissão: 2 chunks/seg\n');

    // Demonstra logs coloridos
    setTimeout(demonstrateColoredLogs, 2000);
  });

  streamer.startStreaming();
}

// Função para demonstrar logs coloridos
function demonstrateColoredLogs() {
  console.log('\n🎨 Modo: LOGS COM CORES E ESTILOS\n');

  // Cores ANSI
  const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    dim: '\x1b[2m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m'
  };

  console.log(`${colors.green}✅ Sucesso:${colors.reset} Operação completada`);
  console.log(`${colors.yellow}⚠️  Aviso:${colors.reset} Cache expirado`);
  console.log(`${colors.red}❌ Erro:${colors.reset} Falha na conexão`);
  console.log(`${colors.cyan}ℹ️  Info:${colors.reset} Sistema iniciado`);
  console.log(`${colors.magenta}🔍 Debug:${colors.reset} Variável X = 42`);
  console.log(`${colors.blue}${colors.bright}🚀 Destaque:${colors.reset} Novo recurso disponível`);

  console.log('\n' + colors.dim + '── Fim do teste de logs em tempo real ──' + colors.reset + '\n');
}

// Função principal
function main() {
  console.clear(); // Limpa o console

  console.log('╔════════════════════════════════════════════╗');
  console.log('║     DEMONSTRAÇÃO DE LOGS EM TEMPO REAL    ║');
  console.log('╚════════════════════════════════════════════╝\n');

  console.log('Este script demonstra diferentes técnicas de logging:');
  console.log('1. Processamento em lote');
  console.log('2. Streaming em tempo real com chunks');
  console.log('3. Logs coloridos e formatados\n');

  console.log('Iniciando em 2 segundos...\n');

  // Inicia com processamento em lote
  setTimeout(processBatchLogs, 2000);
}

// Executa o script
if (require.main === module) {
  main();
}

module.exports = { DataStreamer };