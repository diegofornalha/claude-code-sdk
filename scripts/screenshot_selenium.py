#!/usr/bin/env python3
"""
Captura screenshot usando Selenium WebDriver
"""

import os
import time
import uuid
from datetime import datetime

def capture_with_selenium():
    """Captura screenshot usando Selenium."""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service

        print("🚀 Iniciando captura com Selenium...")

        # Configurações do Chrome
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')  # Modo headless
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1280,800')

        # Inicializa o driver
        driver = webdriver.Chrome(options=chrome_options)

        try:
            # Navega para a página
            print("📍 Navegando para http://localhost:8080/")
            driver.get("http://localhost:8080/")

            # Aguarda a página carregar
            wait = WebDriverWait(driver, 10)
            message_input = wait.until(
                EC.presence_of_element_located((By.ID, "messageInput"))
            )

            # Digite uma mensagem
            print("⌨️ Digitando mensagem...")
            message_input.send_keys("Olá! Este é um teste automatizado com Selenium.")

            # Clica no botão enviar
            print("🖱️ Enviando mensagem...")
            send_button = driver.find_element(By.ID, "sendButton")
            send_button.click()

            # Aguarda a resposta
            print("⏳ Aguardando resposta do assistente...")
            try:
                wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "message.assistant"))
                )
                time.sleep(2)  # Aguarda a resposta completar
            except:
                print("⚠️ Timeout aguardando resposta")

            # Captura o screenshot
            screenshot_path = "/tmp/chat_selenium.png"
            driver.save_screenshot(screenshot_path)
            print(f"✅ Screenshot salvo em: {screenshot_path}")

            driver.quit()
            return screenshot_path

        except Exception as e:
            print(f"❌ Erro durante captura: {e}")
            driver.quit()
            return None

    except ImportError:
        print("❌ Selenium não está instalado.")
        print("\nPara instalar:")
        print("  pip install selenium")
        print("\nTambém é necessário ter o ChromeDriver:")
        print("  brew install chromedriver")
        return None

def capture_with_pyautogui():
    """Captura screenshot usando PyAutoGUI."""
    try:
        import pyautogui

        print("🚀 Capturando tela com PyAutoGUI...")

        # Captura a tela toda
        screenshot = pyautogui.screenshot()

        # Salva o screenshot
        screenshot_path = "/tmp/chat_pyautogui.png"
        screenshot.save(screenshot_path)

        print(f"✅ Screenshot salvo em: {screenshot_path}")
        return screenshot_path

    except ImportError:
        print("❌ PyAutoGUI não está instalado.")
        print("\nPara instalar:")
        print("  pip install pyautogui pillow")
        return None

def capture_with_mss():
    """Captura screenshot usando MSS (mais rápido)."""
    try:
        import mss

        print("🚀 Capturando tela com MSS...")

        with mss.mss() as sct:
            # Captura o monitor principal
            monitor = sct.monitors[0]  # 0 = todos os monitores, 1 = monitor principal

            # Captura
            screenshot = sct.grab(monitor)

            # Salva usando mss.tools
            screenshot_path = "/tmp/chat_mss.png"
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=screenshot_path)

        print(f"✅ Screenshot salvo em: {screenshot_path}")
        return screenshot_path

    except ImportError:
        print("❌ MSS não está instalado.")
        print("\nPara instalar:")
        print("  pip install mss")
        return None

if __name__ == "__main__":
    print("🔍 Testando diferentes métodos de captura de screenshot...")
    print("=" * 60)

    # Tenta Selenium primeiro (melhor para páginas web)
    result = capture_with_selenium()

    # Se falhar, tenta MSS (mais rápido)
    if not result:
        print("\n" + "-" * 40)
        result = capture_with_mss()

    # Se falhar, tenta PyAutoGUI
    if not result:
        print("\n" + "-" * 40)
        result = capture_with_pyautogui()

    if result:
        print("\n🎉 Screenshot capturado com sucesso!")
        print(f"📸 Arquivo: {result}")
    else:
        print("\n❌ Não foi possível capturar o screenshot.")
        print("\n📦 Instale uma das seguintes bibliotecas:")
        print("  • pip install selenium (+ brew install chromedriver)")
        print("  • pip install mss")
        print("  • pip install pyautogui pillow")