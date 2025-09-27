#!/usr/bin/env python3
"""
Captura screenshot de janela específica usando MSS e detecção de janela
"""

import mss
import mss.tools
from PIL import Image
import numpy as np
import time

def find_browser_window():
    """
    Tenta encontrar a janela do navegador analisando a tela.
    """
    import Quartz
    import Quartz.CoreGraphics as CG

    # Lista todas as janelas
    window_list = CG.CGWindowListCopyWindowInfo(
        CG.kCGWindowListOptionOnScreenOnly | CG.kCGWindowListExcludeDesktopElements,
        CG.kCGNullWindowID
    )

    browser_windows = []
    browser_apps = ['Safari', 'Google Chrome', 'Firefox', 'Arc', 'Brave Browser', 'Microsoft Edge']

    for window in window_list:
        owner_name = window.get('kCGWindowOwnerName', '')
        window_name = window.get('kCGWindowName', '')
        bounds = window.get('kCGWindowBounds', {})

        # Verifica se é um navegador
        if owner_name in browser_apps:
            # Verifica se tem localhost no título
            if 'localhost' in window_name or 'Chat' in window_name or '3333' in window_name or '8888' in window_name:
                browser_windows.append({
                    'app': owner_name,
                    'title': window_name,
                    'bounds': bounds
                })
                print(f"✅ Encontrada janela: {owner_name} - {window_name}")

    return browser_windows

def capture_window_area(bounds):
    """
    Captura uma área específica da tela.
    """
    with mss.mss() as sct:
        # Define a área para capturar
        monitor = {
            "top": int(bounds['Y']),
            "left": int(bounds['X']),
            "width": int(bounds['Width']),
            "height": int(bounds['Height'])
        }

        # Captura
        screenshot = sct.grab(monitor)

        # Salva
        screenshot_path = f"/tmp/browser_window_mss.png"
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=screenshot_path)

        return screenshot_path

def capture_with_focus():
    """
    Captura com foco na área central da tela (onde geralmente está o navegador).
    """
    with mss.mss() as sct:
        # Pega o monitor principal
        monitor = sct.monitors[1]  # 1 = monitor principal

        # Define uma área central (80% da tela, centralizada)
        width = int(monitor['width'] * 0.8)
        height = int(monitor['height'] * 0.8)
        left = int(monitor['width'] * 0.1)
        top = int(monitor['height'] * 0.1)

        focused_monitor = {
            "top": top,
            "left": left,
            "width": width,
            "height": height
        }

        # Captura
        screenshot = sct.grab(focused_monitor)

        # Salva
        screenshot_path = "/tmp/browser_focused_mss.png"
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=screenshot_path)

        print(f"✅ Screenshot da área central salvo em: {screenshot_path}")
        return screenshot_path

if __name__ == "__main__":
    print("🔍 Procurando janelas do navegador...")
    print("=" * 60)

    try:
        # Tenta encontrar janela do navegador
        windows = find_browser_window()

        if windows:
            # Captura a primeira janela encontrada
            window = windows[0]
            print(f"\n📸 Capturando janela: {window['app']} - {window['title']}")
            screenshot_path = capture_window_area(window['bounds'])
            print(f"✅ Screenshot salvo em: {screenshot_path}")
        else:
            print("⚠️ Nenhuma janela de navegador com localhost encontrada")
            print("\n📸 Capturando área central da tela...")
            screenshot_path = capture_with_focus()

        print("\n🎉 Captura concluída!")
        print(f"📸 Visualize em: {screenshot_path}")

    except Exception as e:
        print(f"❌ Erro: {e}")
        print("\n🔧 Tentando captura alternativa da área central...")
        try:
            screenshot_path = capture_with_focus()
            print(f"✅ Screenshot alternativo salvo!")
        except Exception as e2:
            print(f"❌ Erro na captura alternativa: {e2}")