#!/usr/bin/env python3
"""
Captura screenshot da página de teste usando Playwright
"""

import asyncio
import sys

async def capture_screenshot():
    """Captura screenshot da página de teste."""

    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            # Navega para a página
            print("Navegando para http://localhost:8080/test...")
            await page.goto("http://localhost:8080/test")

            # Aguarda a página carregar
            await page.wait_for_load_state("networkidle")

            # Clica no botão de teste
            print("Clicando no botão de teste...")
            await page.click("#testBtn")

            # Aguarda a resposta aparecer
            await page.wait_for_timeout(3000)

            # Captura screenshot
            screenshot_path = "/tmp/chat_test_playwright.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"✅ Screenshot salvo em: {screenshot_path}")

            await browser.close()
            return screenshot_path

    except ImportError:
        print("❌ Playwright não está instalado.")
        print("Tentando com requests + captura manual...")

        # Fallback: abrir no navegador padrão
        import webbrowser
        import time

        url = "http://localhost:8080/test"
        print(f"Abrindo {url} no navegador...")
        webbrowser.open(url)

        print("\n📸 Para capturar screenshot:")
        print("1. No macOS: Cmd + Shift + 4 (selecione a área)")
        print("2. No macOS: Cmd + Shift + 3 (tela toda)")
        print("3. No macOS: Cmd + Shift + 5 (opções de captura)")

        return None

if __name__ == "__main__":
    result = asyncio.run(capture_screenshot())
    if result:
        print(f"\n🎉 Screenshot capturado com sucesso!")