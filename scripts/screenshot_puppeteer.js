#!/usr/bin/env node

/**
 * Captura screenshot usando Puppeteer (headless Chrome)
 */

const puppeteer = require('puppeteer');

async function captureScreenshot() {
    console.log('🚀 Iniciando captura com Puppeteer...');

    let browser;
    try {
        // Inicia o navegador
        browser = await puppeteer.launch({
            headless: 'new', // Usa o novo modo headless
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });

        const page = await browser.newPage();

        // Define viewport
        await page.setViewport({
            width: 1280,
            height: 800,
            deviceScaleFactor: 2 // Para retina display
        });

        // Navega para a página
        console.log('📍 Navegando para http://localhost:8080/');
        await page.goto('http://localhost:8080/', {
            waitUntil: 'networkidle2'
        });

        // Aguarda o formulário carregar
        await page.waitForSelector('#messageInput', { timeout: 5000 });

        // Digite uma mensagem
        console.log('⌨️ Digitando mensagem...');
        await page.type('#messageInput', 'Olá! Este é um teste automatizado.');

        // Clica no botão enviar
        console.log('🖱️ Enviando mensagem...');
        await page.click('#sendButton');

        // Aguarda a resposta
        console.log('⏳ Aguardando resposta...');
        await page.waitForSelector('.message.assistant', {
            timeout: 10000
        }).catch(() => {
            console.log('⚠️ Timeout aguardando resposta');
        });

        // Aguarda um pouco para garantir que a resposta está completa
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Captura o screenshot
        const screenshotPath = '/tmp/chat_puppeteer.png';
        await page.screenshot({
            path: screenshotPath,
            fullPage: true
        });

        console.log(`✅ Screenshot salvo em: ${screenshotPath}`);

        await browser.close();
        return screenshotPath;

    } catch (error) {
        console.error('❌ Erro:', error.message);
        if (browser) await browser.close();
        return null;
    }
}

// Executa
if (require.main === module) {
    captureScreenshot().then(path => {
        if (path) {
            console.log('\n🎉 Screenshot capturado com sucesso!');
            console.log(`   Visualize em: ${path}`);
        }
        process.exit(0);
    }).catch(error => {
        console.error('Erro fatal:', error);
        process.exit(1);
    });
}

module.exports = { captureScreenshot };