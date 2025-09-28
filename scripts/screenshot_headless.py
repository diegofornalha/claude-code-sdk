#!/usr/bin/env python3
"""
Captura screenshot usando Chrome headless (renderiza sem mostrar na tela)
"""

import os
import time
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException

def setup_chrome_driver():
    """Configura o Chrome driver com opções headless."""
    chrome_options = Options()

    # Modo headless - renderiza sem mostrar janela
    chrome_options.add_argument('--headless=new')

    # Outras configurações úteis
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1280,800')
    chrome_options.add_argument('--force-device-scale-factor=2')  # Retina quality

    # Desabilita notificações
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--disable-popup-blocking')

    return chrome_options

def capture_chat_screenshot():
    """Captura screenshot do chat em modo headless."""

    print("🚀 Iniciando captura em modo headless...")
    print("=" * 60)

    driver = None
    try:
        # Configura o driver
        chrome_options = setup_chrome_driver()

        # Tenta criar o driver
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except WebDriverException:
            print("⚠️ ChromeDriver não encontrado. Tentando com Safari...")
            # Fallback para Safari
            from selenium.webdriver.safari.options import Options as SafariOptions
            safari_options = SafariOptions()
            driver = webdriver.Safari(options=safari_options)

        print("✅ Driver inicializado")

        # Navega para a página
        print("📍 Navegando para http://localhost:8080/")
        driver.get("http://localhost:8080/")

        # Aguarda a página carregar
        wait = WebDriverWait(driver, 10)

        # Aguarda o campo de mensagem estar presente
        print("⏳ Aguardando página carregar...")
        message_input = wait.until(
            EC.presence_of_element_located((By.ID, "messageInput"))
        )

        # Gera session ID
        session_id = str(uuid.uuid4())

        # Executa JavaScript para criar sessão e enviar mensagem
        print("💬 Enviando mensagem de teste...")
        driver.execute_script(f"""
            // Cria sessão
            fetch('http://localhost:8080/api/sessions', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ session_id: '{session_id}' }})
            }}).then(() => {{
                // Envia mensagem
                document.getElementById('messageInput').value = 'Olá! Este é um teste automatizado.';
                document.getElementById('sendButton').click();
            }});
        """)

        # Aguarda resposta aparecer
        print("⏳ Aguardando resposta do assistente...")
        time.sleep(5)  # Aguarda processar

        try:
            # Tenta aguardar elemento de resposta
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "assistant"))
            )
            print("✅ Resposta recebida")
        except:
            print("⚠️ Timeout aguardando resposta (continuando mesmo assim)")

        # Captura screenshot
        screenshot_path = "/tmp/chat_headless.png"
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot salvo em: {screenshot_path}")

        # Também captura o HTML para debug
        html_path = "/tmp/chat_headless.html"
        with open(html_path, 'w') as f:
            f.write(driver.page_source)
        print(f"📄 HTML salvo em: {html_path}")

        driver.quit()
        return screenshot_path

    except Exception as e:
        print(f"❌ Erro: {e}")
        if driver:
            driver.quit()
        return None

if __name__ == "__main__":
    print("🎯 CAPTURA DE SCREENSHOT EM MODO HEADLESS")
    print("Este modo renderiza a página sem mostrar na tela")
    print()

    screenshot = capture_chat_screenshot()

    if screenshot:
        print("\n✅ SUCESSO!")
        print(f"📸 Screenshot capturado: {screenshot}")
        print("\n💡 Dica: O modo headless renderiza a página completa")
        print("   sem depender do que está visível na tela.")
    else:
        print("\n❌ Falha na captura")
        print("\n📦 Possíveis soluções:")
        print("  1. Instalar ChromeDriver: brew install chromedriver")
        print("  2. Permitir ChromeDriver: Configurações > Privacidade > Permitir ChromeDriver")
        print("  3. Usar Safari: Ativar 'Permitir Automação Remota' no menu Desenvolvedor")