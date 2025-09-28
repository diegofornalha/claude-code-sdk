#!/usr/bin/env node

/**
 * Script para testar o chat usando Puppeteer
 * Simula interação com o Chrome DevTools
 */

const puppeteer = require('puppeteer');

(async () => {
    console.log('🚀 Iniciando teste do chat com Chrome automation...\n');

    try {
        // Lança o navegador
        const browser = await puppeteer.launch({
            headless: false,  // Mostra o navegador
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });

        const page = await browser.newPage();

        // Navega para o chat
        console.log('📍 Navegando para http://localhost:8080/...');
        await page.goto('http://localhost:8080/', {
            waitUntil: 'networkidle2',
            timeout: 30000
        });

        // Aguarda o campo de mensagem carregar
        console.log('⏳ Aguardando campo de mensagem...');
        await page.waitForSelector('#messageInput', { timeout: 10000 });

        // Digite "Oi" no campo
        console.log('⌨️ Digitando "Oi" no campo de mensagem...');
        await page.type('#messageInput', 'Oi', { delay: 100 });

        // Clica no botão enviar
        console.log('🖱️ Clicando no botão enviar...');
        await page.click('#sendButton');

        // Aguarda resposta (procura por elemento com classe message-assistant)
        console.log('⏳ Aguardando resposta do assistente...');
        await page.waitForSelector('.message-assistant', { timeout: 15000 });

        // Captura a resposta
        const response = await page.evaluate(() => {
            const messages = document.querySelectorAll('.message-assistant');
            if (messages.length > 0) {
                const lastMessage = messages[messages.length - 1];
                return lastMessage.textContent;
            }
            return null;
        });

        console.log('\n✅ Teste bem-sucedido!');
        console.log('📩 Mensagem enviada: "Oi"');
        console.log('📨 Resposta recebida:', response || '[Resposta em processamento]');

        // Tira screenshot
        await page.screenshot({ path: 'chat_test_screenshot.png' });
        console.log('📸 Screenshot salvo: chat_test_screenshot.png');

        // Aguarda um pouco antes de fechar
        await new Promise(resolve => setTimeout(resolve, 3000));

        await browser.close();
        console.log('\n🎉 Teste concluído com sucesso!');

    } catch (error) {
        console.error('❌ Erro durante o teste:', error.message);
        process.exit(1);
    }
})();