/**
 * Script para remover service workers problemáticos
 * Execute este código no Console do Chrome DevTools em http://localhost:8080/
 */

// Função para desregistrar todos os service workers
async function cleanupServiceWorkers() {
    console.log('🔧 Iniciando limpeza de Service Workers...');

    try {
        // 1. Listar todos os service workers registrados
        const registrations = await navigator.serviceWorker.getRegistrations();

        if (registrations.length === 0) {
            console.log('✅ Nenhum Service Worker encontrado');
            return;
        }

        console.log(`📋 Encontrados ${registrations.length} Service Worker(s):`);

        // 2. Desregistrar cada service worker
        for (const registration of registrations) {
            console.log(`  🗑️ Removendo: ${registration.scope}`);
            const success = await registration.unregister();
            if (success) {
                console.log(`  ✅ Removido com sucesso: ${registration.scope}`);
            } else {
                console.log(`  ❌ Falha ao remover: ${registration.scope}`);
            }
        }

        // 3. Limpar caches
        console.log('\n📦 Limpando caches...');
        const cacheNames = await caches.keys();

        for (const cacheName of cacheNames) {
            console.log(`  🗑️ Removendo cache: ${cacheName}`);
            await caches.delete(cacheName);
        }

        console.log('\n✅ Limpeza completa!');
        console.log('🔄 Recarregue a página para aplicar as mudanças');

        // 4. Opcional: Recarregar automaticamente
        setTimeout(() => {
            if (confirm('Deseja recarregar a página agora?')) {
                window.location.reload(true);
            }
        }, 1000);

    } catch (error) {
        console.error('❌ Erro durante limpeza:', error);
    }
}

// Executar automaticamente
cleanupServiceWorkers();

// Adicionar função global para uso futuro
window.cleanupServiceWorkers = cleanupServiceWorkers;