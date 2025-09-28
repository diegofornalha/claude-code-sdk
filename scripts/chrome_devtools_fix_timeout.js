/**
 * CÓDIGO PARA EXECUTAR NO CHROME DEVTOOLS
 *
 * Como usar:
 * 1. Abra http://localhost:8080/ no Chrome
 * 2. Pressione F12 para abrir DevTools
 * 3. Vá para aba Console
 * 4. Cole e execute este código
 */

// ==========================================
// COPIE A PARTIR DAQUI
// ==========================================

(function fixTimeout() {
    console.log('🔧 Corrigindo timeout do chat...');

    // 1. Aumentar timeout global para 10 minutos
    window.CHAT_CONFIG = window.CHAT_CONFIG || {};
    window.CHAT_CONFIG.TIMEOUT = 10 * 60 * 1000; // 10 minutos

    // 2. Interceptar e modificar fetch para adicionar timeout maior
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        console.log('📡 Interceptando request...');

        // Se for request do chat, adicionar timeout maior
        if (args[0] && args[0].includes && args[0].includes('/api/chat')) {
            // Adicionar AbortController com timeout maior
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10 * 60 * 1000);

            // Modificar opções
            if (args[1]) {
                args[1].signal = controller.signal;
            } else {
                args[1] = { signal: controller.signal };
            }

            // Limpar timeout quando completar
            return originalFetch.apply(this, args).finally(() => {
                clearTimeout(timeoutId);
            });
        }

        return originalFetch.apply(this, args);
    };

    // 3. Modificar a função sendMessage existente
    if (window.sendMessage) {
        const originalSendMessage = window.sendMessage;
        window.sendMessage = async function() {
            console.log('📤 Enviando com timeout estendido...');

            // Backup do timeout original
            const originalTimeout = window.TIMEOUT || 300000;

            // Setar novo timeout
            window.TIMEOUT = 10 * 60 * 1000;

            try {
                // Chamar função original
                await originalSendMessage.apply(this, arguments);
            } finally {
                // Restaurar timeout original (opcional)
                // window.TIMEOUT = originalTimeout;
            }
        };
    }

    // 4. Adicionar indicador visual de timeout estendido
    const statusDiv = document.createElement('div');
    statusDiv.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        background: #4CAF50;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        z-index: 10000;
        font-family: monospace;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    `;
    statusDiv.innerHTML = '⏱️ Timeout: 10 min';
    document.body.appendChild(statusDiv);

    // Remover após 5 segundos
    setTimeout(() => statusDiv.remove(), 5000);

    // 5. Monitorar requests longas
    let requestCount = 0;
    const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
            if (entry.name.includes('/api/chat')) {
                const duration = entry.duration / 1000; // em segundos
                console.log(`⏰ Request durou: ${duration.toFixed(2)}s`);

                if (duration > 60) {
                    console.warn(`⚠️ Request longa detectada: ${duration.toFixed(2)}s`);
                }
            }
        }
    });
    observer.observe({ entryTypes: ['resource'] });

    // 6. Adicionar botão de cancelar request
    const cancelBtn = document.createElement('button');
    cancelBtn.textContent = '⛔ Cancelar Request';
    cancelBtn.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #f44336;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
        z-index: 10000;
        font-weight: bold;
        display: none;
    `;

    cancelBtn.onclick = () => {
        if (window.currentAbortController) {
            window.currentAbortController.abort();
            console.log('❌ Request cancelada manualmente');
            cancelBtn.style.display = 'none';
        }
    };
    document.body.appendChild(cancelBtn);

    // Mostrar botão durante requests
    const originalFetch2 = window.fetch;
    window.fetch = function(...args) {
        if (args[0] && args[0].includes && args[0].includes('/api/chat')) {
            cancelBtn.style.display = 'block';

            return originalFetch2.apply(this, args).finally(() => {
                cancelBtn.style.display = 'none';
            });
        }
        return originalFetch2.apply(this, args);
    };

    console.log('✅ Timeout corrigido!');
    console.log('📌 Configurações aplicadas:');
    console.log('  • Timeout aumentado para 10 minutos');
    console.log('  • Monitoramento de requests longas ativo');
    console.log('  • Botão de cancelar disponível');
    console.log('');
    console.log('💡 Agora você pode fazer perguntas que usam muitos subagentes!');
})();

// ==========================================
// COPIE ATÉ AQUI
// ==========================================